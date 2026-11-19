#include "hvd_core"

float HVD_Dot(vector a, vector b)
{
    return a.x * b.x + a.y * b.y;
}

float HVD_Distance(vector a, vector b)
{
    vector delta = a - b;
    return sqrt(HVD_Dot(delta, delta));
}

float HVD_LineDistance(vector p, vector a, vector b)
{
    vector span = b - a;
    float length = HVD_Dot(span, span);
    if (length < 0.01) return HVD_Distance(p, a);
    float along = HVD_Dot(p - a, span) / length;
    if (along < 0.0) along = 0.0;
    if (along > 1.0) along = 1.0;
    return HVD_Distance(p, a + along * span);
}

int HVD_Covered(object area, vector origin, vector target)
{
    object slab = GetFirstObjectInArea(area);
    while (GetIsObjectValid(slab))
    {
        if (GetLocalInt(slab, "cover"))
        {
            vector point = GetPosition(slab);
            if (HVD_Distance(point, target) < 4.2 && HVD_LineDistance(point, origin, target) < 1.5 &&
                HVD_Dot(point - origin, target - point) > 0.0) return TRUE;
        }
        slab = GetNextObjectInArea(area);
    }
    return FALSE;
}

void HVD_Spark(object area, vector at, int effectId, float size = 1.0)
{
    location surface = Location(area, at, 0.0);
    float height = GetGroundHeight(surface);
    if (height > -5.9) at.z = height + 0.05;
    ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(effectId, FALSE, size), Location(area, at, 0.0));
}

void HVD_MarkLine(object area, vector start, vector end, int effectId)
{
    int step;
    int count = FloatToInt(HVD_Distance(start, end) / 3.0) + 1;
    if (count > 16) count = 16;
    for (step = 0; step <= count; ++step)
        HVD_Spark(area, start + (IntToFloat(step) / IntToFloat(count)) * (end - start), effectId, 0.7);
}

void HVD_MarkRing(object area, vector center, float radius, int visual)
{
    int index;
    for (index = 0; index < 8; ++index)
    {
        float angle = IntToFloat(index) * 0.785398;
        HVD_Spark(area, center + Vector(cos(angle) * radius, sin(angle) * radius, 0.0), visual, 0.65);
    }
}

int HVD_SafeStep(object player, vector center, float metres, int pull)
{
    vector start = GetPosition(player);
    vector delta = start - center;
    delta.z = 0.0;
    if (HVD_Dot(delta, delta) < 0.1) return FALSE;
    if (pull && HVD_Dot(delta, delta) < metres * metres) return FALSE;
    float direction = metres;
    if (pull) direction = -metres;
    vector end = start + direction * VectorNormalize(delta);
    object area = GetArea(player);
    location destination = Location(area, end, GetFacing(player));
    float height = GetGroundHeight(destination);
    if (abs(FloatToInt(10.0 * (height - start.z))) > 9) return FALSE;
    int material = GetSurfaceMaterial(destination);
    location halfway = Location(area, start + 0.5 * (end - start), 0.0);
    if (Get2DAString("surfacemat", "Walk", material) != "1" ||
        Get2DAString("surfacemat", "Walk", GetSurfaceMaterial(halfway)) != "1") return FALSE;
    if (!LineOfSightVector(start + Vector(0.0, 0.0, 1.0), end + Vector(0.0, 0.0, 1.0))) return FALSE;
    end.z = height;
    AssignCommand(player, JumpToLocation(Location(area, end, GetFacing(player))));
    return TRUE;
}

void HVD_Strike(object target, object source, int amount, int damageType, int dc = 29, int push = 0)
{
    int save = ReflexSave(target, dc, SAVING_THROW_TYPE_NONE, source);
    if (save) amount /= 2;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(amount, damageType), target);
    if (push && !save && !GetIsDead(target))
        HVD_SafeStep(target, GetPosition(source), 1.8, FALSE);
}

void HVD_HitLine(object source, vector start, vector end, float width, int amount, int damageType, int push)
{
    if (!GetIsObjectValid(source) || GetIsDead(source) || GetLocalInt(source, "hvd_yield")) return;
    object area = GetArea(source);
    HVD_MarkLine(area, start, end, VFX_IMP_PULSE_COLD);
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        vector position = GetPosition(player);
        if (HVD_PlayerIn(player, area) && HVD_LineDistance(position, start, end) < width &&
            !HVD_Covered(area, start, position))
            HVD_Strike(player, source, amount, damageType, 30, push);
        player = GetNextPC();
    }
}

void HVD_Vortex(object source, vector center)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    object area = GetArea(source);
    HVD_Spark(area, center, VFX_FNF_SOUND_BURST_SILENT);
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, area) && HVD_Distance(GetPosition(player), center) < 3.2 &&
            !HVD_Covered(area, GetPosition(source), GetPosition(player)))
            HVD_Strike(player, source, 29, DAMAGE_TYPE_BLUDGEONING);
        player = GetNextPC();
    }
}

object HVD_WindAlly(object source)
{
    object area = GetArea(source);
    object candidate = OBJECT_INVALID;
    object best = OBJECT_INVALID;
    float range = 16.0;
    candidate = GetFirstObjectInArea(area);
    while (GetIsObjectValid(candidate))
    {
        int role = GetLocalInt(candidate, "role");
        if (candidate != source && role && role <= 4 && role != 3 && !GetIsDead(candidate) &&
            GetDistanceBetween(source, candidate) < range && LineOfSightObject(source, candidate))
        {
            best = candidate;
            range = GetDistanceBetween(source, candidate);
        }
        candidate = GetNextObjectInArea(area);
    }
    return best;
}

void HVD_RemoveWindWard(object ally)
{
    effect ward = GetFirstEffect(ally);
    while (GetIsEffectValid(ward))
    {
        if (GetEffectTag(ward) == "hvd_wind_ward") RemoveEffect(ally, ward);
        ward = GetNextEffect(ally);
    }
}

void HVD_CheckWard(object caster, object ally, int ticks)
{
    if (!GetIsObjectValid(ally) || GetIsDead(ally)) return;
    if (!GetIsObjectValid(caster) || GetIsDead(caster) || GetArea(caster) != GetArea(ally) ||
        HVD_Covered(GetArea(ally), GetPosition(caster), GetPosition(ally)) ||
        !LineOfSightObject(caster, ally) || GetDistanceBetween(caster, ally) > 17.0)
    {
        HVD_RemoveWindWard(ally);
        return;
    }
    if (ticks > 0) DelayCommand(0.7, HVD_CheckWard(caster, ally, ticks - 1));
}

void HVD_WindWard(object caster, object ally)
{
    if (!GetIsObjectValid(caster) || GetIsDead(caster) || !GetIsObjectValid(ally) || GetIsDead(ally) ||
        GetArea(caster) != GetArea(ally) || !LineOfSightObject(caster, ally) ||
        HVD_Covered(GetArea(ally), GetPosition(caster), GetPosition(ally)) ||
        GetDistanceBetween(caster, ally) > 17.0) return;
    HVD_RemoveWindWard(ally);
    effect ward = EffectDamageImmunityIncrease(DAMAGE_TYPE_BLUDGEONING, 30);
    ward = EffectLinkEffects(ward, EffectDamageImmunityIncrease(DAMAGE_TYPE_PIERCING, 30));
    ward = EffectLinkEffects(ward, EffectDamageImmunityIncrease(DAMAGE_TYPE_SLASHING, 30));
    ward = EffectLinkEffects(ward, EffectBeam(VFX_BEAM_SILENT_LIGHTNING, caster, BODY_NODE_CHEST));
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, TagEffect(ExtraordinaryEffect(ward), "hvd_wind_ward"), ally, 7.0);
    DelayCommand(0.7, HVD_CheckWard(caster, ally, 9));
}

void HVD_VirPull(object source, vector center)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    object area = GetArea(source);
    HVD_MarkRing(area, center, 7.0, VFX_IMP_SONIC);
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        vector position = GetPosition(player);
        float distance = HVD_Distance(position, center);
        if (HVD_PlayerIn(player, area) && distance > 2.4 && distance < 9.0 &&
            !HVD_Covered(area, center, position) && !ReflexSave(player, 31, SAVING_THROW_TYPE_NONE, source))
            HVD_SafeStep(player, center, 2.0, TRUE);
        player = GetNextPC();
    }
}

void HVD_VirBurst(object source, vector center)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    object area = GetArea(source);
    HVD_MarkRing(area, center, 7.0, VFX_FNF_SOUND_BURST_SILENT);
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        vector position = GetPosition(player);
        float distance = HVD_Distance(position, center);
        if (HVD_PlayerIn(player, area) && distance >= 2.4 && distance < 8.5 &&
            !HVD_Covered(area, center, position))
            HVD_Strike(player, source, 42, DAMAGE_TYPE_BLUDGEONING, 31, TRUE);
        player = GetNextPC();
    }
    effect exposed = EffectLinkEffects(EffectACDecrease(5), EffectVisualEffect(VFX_DUR_AURA_CYAN));
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, ExtraordinaryEffect(exposed), source, 4.5);
    HVD_AreaMessage(area, "Bouřný vír se rozevřel. Jeho jádro je odkryté.");
}

void HVD_Cooldown(object mob, float seconds, float windup = 3.1)
{
    SetLocalInt(mob, "hvd_cast", TRUE);
    SetLocalInt(mob, "hvd_aim", TRUE);
    DelayCommand(windup, DeleteLocalInt(mob, "hvd_aim"));
    DelayCommand(seconds, DeleteLocalInt(mob, "hvd_cast"));
}

void HVD_ReleasePush(object area, int reservation)
{
    if (GetLocalInt(area, "hvd_push") == reservation) DeleteLocalInt(area, "hvd_push");
}

void HVD_ReservePush(object area, float duration)
{
    int reservation = GetLocalInt(area, "hvd_push_count") + 1;
    SetLocalInt(area, "hvd_push_count", reservation);
    SetLocalInt(area, "hvd_push", reservation);
    AssignCommand(area, DelayCommand(duration, HVD_ReleasePush(area, reservation)));
}

void HVD_NormalAttack(object mob, object target)
{
    if (GetAttackTarget(mob) != target && GetCurrentAction(mob) != ACTION_ATTACKOBJECT)
    {
        AssignCommand(mob, ClearAllActions());
        AssignCommand(mob, ActionAttack(target));
    }
}

void HVD_MobThink(object mob)
{
    int role = GetLocalInt(mob, "role");
    if (!role || role == 7 || GetIsDead(mob)) return;
    object area = GetArea(mob);
    object target = HVD_NearPlayer(mob, 28.0, role == 2 || role == 6);
    location home = GetLocalLocation(mob, "hvd_home");
    if (!GetIsObjectValid(target) || HVD_Distance(GetPosition(mob), GetPositionFromLocation(home)) > 30.0)
    {
        if (GetIsObjectValid(GetAreaFromLocation(home)) && HVD_Distance(GetPosition(mob), GetPositionFromLocation(home)) > 5.0 &&
            GetCurrentAction(mob) != ACTION_MOVETOPOINT)
        {
            AssignCommand(mob, ClearAllActions());
            AssignCommand(mob, ActionMoveToLocation(home, TRUE));
        }
        return;
    }
    vector start = GetPosition(mob);
    vector aimed = GetPosition(target);
    float distance = HVD_Distance(start, aimed);
    if (GetLocalInt(mob, "hvd_cast"))
    {
        if (!GetLocalInt(mob, "hvd_aim") && ((role != 2 && role != 3 && role != 6) || distance < 4.0))
            HVD_NormalAttack(mob, target);
        return;
    }
    if (role == 2 && distance > 4.0)
    {
        HVD_Cooldown(mob, 7.5);
        HVD_MarkRing(area, aimed, 3.0, VFX_IMP_SONIC);
        FloatingTextStringOnCreature("Pod nohama se zvedá vír!", target, FALSE);
        DelayCommand(2.8, HVD_Vortex(mob, aimed));
        return;
    }
    if (role == 3)
    {
        object ally = HVD_WindAlly(mob);
        if (GetIsObjectValid(ally))
        {
            HVD_Cooldown(mob, 12.0);
            HVD_MarkLine(area, start, GetPosition(ally), VFX_IMP_PULSE_COLD);
            HVD_AreaMessage(area, "Spřádač spojuje proud s jiným elementálem.");
            DelayCommand(2.6, HVD_WindWard(mob, ally));
            return;
        }
    }
    if (role == 4 && distance < 10.5 && !GetLocalInt(area, "hvd_push"))
    {
        AssignCommand(mob, ClearAllActions());
        HVD_Cooldown(mob, 11.0, 5.2);
        HVD_ReservePush(area, 5.8);
        HVD_AreaMessage(area, "Kamínky se stáčejí k jádru. Bouřný vír začne vtahovat.");
        HVD_MarkRing(area, start, 8.5, VFX_IMP_PULSE_COLD);
        DelayCommand(2.7, HVD_VirPull(mob, start));
        DelayCommand(4.9, HVD_VirBurst(mob, start));
        return;
    }
    if ((role == 1 && distance < 10.0 && !GetLocalInt(area, "hvd_push")) ||
        (role == 5 && distance < 9.5) || role == 6)
    {
        AssignCommand(mob, ClearAllActions());
        HVD_Cooldown(mob, 8.0);
        if (role == 1)
        {
            HVD_ReservePush(area, 3.3);
        }
        float range = 10.0;
        if (role == 6) range = distance;
        vector end = start + range * VectorNormalize(aimed - start);
        HVD_MarkLine(area, start, end, VFX_IMP_SONIC);
        string warning = "Prach vyznačil dráhu nárazu!";
        if (role == 5) warning = "Kopiník zapřel kopí. Ustup z vyznačené výseče!";
        if (role == 6) warning = "Lucerna označila dráhu výboje!";
        HVD_AreaMessage(area, warning);
        int damage = 34;
        int type = DAMAGE_TYPE_BLUDGEONING;
        if (role == 5) { damage = 40; type = DAMAGE_TYPE_PIERCING; }
        if (role == 6) { damage = 43; type = DAMAGE_TYPE_DIVINE; }
        DelayCommand(2.8, HVD_HitLine(mob, start, end, 1.8, damage, type, role == 1));
        return;
    }
    HVD_NormalAttack(mob, target);
}
