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

void HVD_ThrowBolt(object source, object target)
{
    if (!GetIsObjectValid(source) || GetIsDead(source) || !HVD_PlayerIn(target, GetArea(source)) ||
        GetDistanceBetween(source, target) > 24.0 || !LineOfSightObject(source, target)) return;

    effect bolt = EffectBeam(VFX_BEAM_LIGHTNING, source, BODY_NODE_HAND);
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, bolt, target, 1.0);
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_LIGHTNING_S), target);
    int elite = GetLocalInt(source, "elite");
    HVD_Strike(target, source, d10(5), DAMAGE_TYPE_ELECTRICAL, elite ? 34 : 29);
}

void HVD_HitLine(object source, vector start, vector end, float width, int amount, int damageType)
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
            HVD_Strike(player, source, amount, damageType, 30);
        player = GetNextPC();
    }
}

void HVD_Whirlwind(object source)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    int dc = GetLocalInt(source, "whirlwind_dc");
    int dice = GetLocalInt(source, "whirlwind_dice");
    if (!dc || !dice) return;

    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_PULSE_WIND), source);
    location center = GetLocation(source);
    effect damage = EffectDamage(d3(dice), DAMAGE_TYPE_SLASHING);
    object target = GetFirstObjectInShape(SHAPE_SPHERE, RADIUS_SIZE_LARGE, center, TRUE, OBJECT_TYPE_CREATURE);
    while (GetIsObjectValid(target))
    {
        if (!GetIsDead(target) && !GetIsDM(target) && GetIsEnemy(target, source) &&
            !ReflexSave(target, dc, SAVING_THROW_TYPE_NONE, source))
        {
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectKnockdown(), target, RoundsToSeconds(2));
            DelayCommand(0.01, ApplyEffectToObject(DURATION_TYPE_INSTANT, damage, target));
        }
        target = GetNextObjectInShape(SHAPE_SPHERE, RADIUS_SIZE_LARGE, center, TRUE, OBJECT_TYPE_CREATURE);
    }
}

int HVD_WindAlly(object source, object ally)
{
    int role = GetLocalInt(ally, "role");
    return role >= 1 && role <= 4 && !GetIsDead(ally) &&
           GetLocalString(ally, "hvd_group") == GetLocalString(source, "hvd_group") &&
           GetIsFriend(ally, source);
}

void HVD_RemoveWindWard(object ally)
{
    effect ward = GetFirstEffect(ally);
    while (GetIsEffectValid(ward))
    {
        if (GetEffectTag(ward) == "hvd_wind_ward")
        {
            RemoveEffect(ally, ward);
            return;
        }
        ward = GetNextEffect(ally);
    }
}

void HVD_FrostAura(object source)
{
    location center = GetLocation(source);
    object target = GetFirstObjectInShape(SHAPE_SPHERE, 4.0, center, TRUE, OBJECT_TYPE_CREATURE);
    while (GetIsObjectValid(target))
    {
        if (!GetIsDead(target) && !GetIsDM(target) && GetIsEnemy(target, source))
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(d6(4), DAMAGE_TYPE_COLD), target);
        target = GetNextObjectInShape(SHAPE_SPHERE, 4.0, center, TRUE, OBJECT_TYPE_CREATURE);
    }
}

void HVD_WindAura(object source)
{
    effect ward = EffectAttackIncrease(3);
    ward = EffectLinkEffects(ward, EffectDamageImmunityIncrease(DAMAGE_TYPE_BLUDGEONING, 30));
    ward = EffectLinkEffects(ward, EffectDamageImmunityIncrease(DAMAGE_TYPE_PIERCING, 30));
    ward = EffectLinkEffects(ward, EffectDamageImmunityIncrease(DAMAGE_TYPE_SLASHING, 30));
    ward = TagEffect(ExtraordinaryEffect(ward), "hvd_wind_ward");

    location center = GetLocation(source);
    object ally = GetFirstObjectInShape(SHAPE_SPHERE, 7.0, center, TRUE, OBJECT_TYPE_CREATURE);
    while (GetIsObjectValid(ally))
    {
        if (ally != source && HVD_WindAlly(source, ally))
        {
            HVD_RemoveWindWard(ally);
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, ward, ally, 6.3);
        }
        ally = GetNextObjectInShape(SHAPE_SPHERE, 7.0, center, TRUE, OBJECT_TYPE_CREATURE);
    }
}

void HVD_PulseAura(object source)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    if (HVD_AreaCount(GetArea(source)))
    {
        if (GetLocalInt(source, "role") == 2) HVD_FrostAura(source);
        else HVD_WindAura(source);
    }
    DelayCommand(RoundsToSeconds(1), HVD_PulseAura(source));
}

object HVD_WoundedAlly(object source, float range, int threshold)
{
    location center = GetLocation(source);
    object ally = GetFirstObjectInShape(SHAPE_SPHERE, range, center, TRUE, OBJECT_TYPE_CREATURE);
    object worst = OBJECT_INVALID;
    while (GetIsObjectValid(ally))
    {
        if (HVD_WindAlly(source, ally))
        {
            int vitality = 100 * GetCurrentHitPoints(ally) / GetMaxHitPoints(ally);
            if (vitality < threshold)
            {
                worst = ally;
                threshold = vitality;
            }
        }
        ally = GetNextObjectInShape(SHAPE_SPHERE, range, center, TRUE, OBJECT_TYPE_CREATURE);
    }
    return worst;
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

void HVD_VirBurst(object source)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    object area = GetArea(source);
    HVD_Whirlwind(source);
    effect exposed = EffectLinkEffects(EffectACDecrease(5), EffectVisualEffect(VFX_DUR_AURA_CYAN));
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, ExtraordinaryEffect(exposed), source, 5.0);
    HVD_AreaMessage(area, "Bouřný vír se rozevřel. Jeho jádro je odkryté.");
}

void HVD_VirStorm(object source)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    AssignCommand(source, ActionCastSpellAtLocation(SPELL_STORM_OF_VENGEANCE, GetLocation(source),
                                                   METAMAGIC_ANY, TRUE, PROJECTILE_PATH_TYPE_DEFAULT, TRUE));
}

void HVD_Cooldown(object mob, float seconds, float windup = 3.1)
{
    SetLocalInt(mob, "hvd_cast", TRUE);
    SetLocalInt(mob, "hvd_aim", TRUE);
    DelayCommand(windup, DeleteLocalInt(mob, "hvd_aim"));
    DelayCommand(seconds, DeleteLocalInt(mob, "hvd_cast"));
}

void HVD_NatureBalance(object source)
{
    if (!GetIsObjectValid(source) || GetIsDead(source)) return;
    int casterLevel = GetLocalInt(source, "nature_caster_level");
    int dc = 18 + GetAbilityModifier(ABILITY_CHARISMA, source);
    location center = GetLocation(source);
    ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_FNF_NATURES_BALANCE), center);
    object target = GetFirstObjectInShape(SHAPE_SPHERE, RADIUS_SIZE_LARGE, center, FALSE, OBJECT_TYPE_CREATURE);
    while (GetIsObjectValid(target))
    {
        if (!GetIsDead(target) && !GetIsDM(target))
        {
            if (GetIsFriend(target, source))
            {
                SignalEvent(target, EventSpellCastAt(source, SPELL_NATURES_BALANCE, FALSE));
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(d8(3) + casterLevel), target);
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_HEALING_L), target);
            }
            else if (GetIsEnemy(target, source))
            {
                SignalEvent(target, EventSpellCastAt(source, SPELL_NATURES_BALANCE));
                if (!WillSave(target, dc, SAVING_THROW_TYPE_SPELL, source))
                {
                    effect breach = EffectLinkEffects(EffectSpellResistanceDecrease(d4(casterLevel / 5)),
                                                       EffectVisualEffect(VFX_DUR_CESSATE_NEGATIVE));
                    breach = SetEffectCasterLevel(SetEffectSpellId(breach, SPELL_NATURES_BALANCE), casterLevel);
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, breach, target, RoundsToSeconds(casterLevel / 3));
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_BREACH), target);
                }
            }
        }
        target = GetNextObjectInShape(SHAPE_SPHERE, RADIUS_SIZE_LARGE, center, FALSE, OBJECT_TYPE_CREATURE);
    }
}

int HVD_SpinnerCast(object mob, float distance)
{
    int spell = -1;
    object healTarget = OBJECT_INVALID;
    if (!GetLocalInt(mob, "hvd_mantle_cast"))
    {
        SetLocalInt(mob, "hvd_mantle_cast", TRUE);
        spell = SPELL_SPELL_MANTLE;
    }
    else
    {
        if (!GetLocalInt(mob, "hvd_heal_cast")) healTarget = HVD_WoundedAlly(mob, 7.0, 45);
        if (GetIsObjectValid(healTarget))
        {
            SetLocalInt(mob, "hvd_heal_cast", TRUE);
            spell = SPELL_MASS_HEAL;
        }
        else if (!GetLocalInt(mob, "hvd_balance_cast") &&
                 (distance <= RADIUS_SIZE_LARGE || GetIsObjectValid(HVD_WoundedAlly(mob, RADIUS_SIZE_LARGE, 80))))
        {
            SetLocalInt(mob, "hvd_balance_cast", TRUE);
            spell = SPELL_NATURES_BALANCE;
        }
    }
    if (spell < 0) return FALSE;

    HVD_Cooldown(mob, 7.0, 3.4);
    AssignCommand(mob, ClearAllActions());
    if (spell == SPELL_MASS_HEAL)
        AssignCommand(mob, ActionCastSpellAtLocation(spell, GetLocation(healTarget), METAMAGIC_ANY,
                                                     FALSE, PROJECTILE_PATH_TYPE_DEFAULT, TRUE));
    else if (spell == SPELL_NATURES_BALANCE)
    {
        // The creature ability list caps caster level at 15 in the game.
        AssignCommand(mob, ActionPlayAnimation(ANIMATION_LOOPING_CONJURE1, 1.0, 2.5));
        HVD_AreaMessage(GetArea(mob), GetName(mob) + " sesílá Nature's Balance.");
        DelayCommand(2.5, HVD_NatureBalance(mob));
    }
    else AssignCommand(mob, ActionCastSpellAtObject(spell, mob));
    return TRUE;
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

void HVD_StopPursuit(object mob)
{
    int current = GetCurrentAction(mob);
    if (current == ACTION_ATTACKOBJECT || current == ACTION_MOVETOPOINT)
        AssignCommand(mob, ClearAllActions());
    DeleteLocalObject(mob, "hvd_pursuit");
    DeleteLocalLocation(mob, "hvd_pursuit_goal");
}

void HVD_RefreshPursuit(object mob)
{
    if (GetIsDead(mob)) return;
    object target = GetLocalObject(mob, "hvd_pursuit");
    if (!HVD_PlayerIn(target, GetArea(mob)))
    {
        HVD_StopPursuit(mob);
        DeleteLocalInt(mob, "hvd_pursuit_running");
        return;
    }

    if (!GetLocalInt(mob, "hvd_aim") &&
        (!LineOfSightObject(mob, target) ||
         (GetLocalInt(mob, "role") != 2 && GetDistanceBetween(mob, target) > RADIUS_SIZE_LARGE)))
    {
        location goal = GetLocation(target);
        location previous = GetLocalLocation(mob, "hvd_pursuit_goal");
        if (GetCurrentAction(mob) != ACTION_MOVETOPOINT || GetAreaFromLocation(previous) != GetArea(target) ||
            HVD_Distance(GetPositionFromLocation(previous), GetPositionFromLocation(goal)) >= 2.0)
        {
            SetLocalLocation(mob, "hvd_pursuit_goal", goal);
            AssignCommand(mob, ClearAllActions());
            AssignCommand(mob, ActionMoveToObject(target, TRUE, 2.5));
        }
    }
    DelayCommand(1.2, HVD_RefreshPursuit(mob));
}

object HVD_PursuePlayer(object mob)
{
    object area = GetArea(mob);
    object target = GetLocalObject(mob, "hvd_pursuit");
    if (!HVD_PlayerIn(target, area))
    {
        target = HVD_NearPlayer(mob, 28.0);
        if (!GetIsObjectValid(target))
        {
            HVD_StopPursuit(mob);
            return OBJECT_INVALID;
        }
        SetLocalObject(mob, "hvd_pursuit", target);
    }
    if (!GetLocalInt(mob, "hvd_pursuit_running"))
    {
        SetLocalInt(mob, "hvd_pursuit_running", TRUE);
        DelayCommand(0.01, HVD_RefreshPursuit(mob));
    }
    if (!LineOfSightObject(mob, target)) return OBJECT_INVALID;
    return target;
}

void HVD_ChangeThrowerWeapon(object mob, object dart, object target, int ready)
{
    SetLocalInt(mob, "hvd_change_weapon", TRUE);
    DelayCommand(1.0, DeleteLocalInt(mob, "hvd_change_weapon"));
    AssignCommand(mob, ClearAllActions());
    if (ready) AssignCommand(mob, ActionEquipItem(dart, INVENTORY_SLOT_RIGHTHAND));
    else AssignCommand(mob, ActionUnequipItem(dart));
    AssignCommand(mob, ActionAttack(target));
}

void HVD_ThrowerAttack(object mob, object target, float distance)
{
    if (GetLocalInt(mob, "hvd_change_weapon")) return;
    object held = GetItemInSlot(INVENTORY_SLOT_RIGHTHAND, mob);
    if (distance <= 4.0)
    {
        if (GetResRef(held) == "hvd_winddart")
            HVD_ChangeThrowerWeapon(mob, held, target, FALSE);
        else HVD_NormalAttack(mob, target);
        return;
    }

    object dart = GetItemPossessedBy(mob, "hvd_winddart");
    if (!GetIsObjectValid(dart))
    {
        dart = CreateItemOnObject("hvd_winddart", mob, 50);
        if (!GetIsObjectValid(dart)) return;
        SetDroppableFlag(dart, FALSE);
    }
    else if (GetItemStackSize(dart) < 10) SetItemStackSize(dart, 50);

    if (dart != held)
        HVD_ChangeThrowerWeapon(mob, dart, target, TRUE);
    else HVD_NormalAttack(mob, target);
}

void HVD_MobThink(object mob)
{
    int role = GetLocalInt(mob, "role");
    if (!role || role == 7 || GetIsDead(mob)) return;
    object area = GetArea(mob);
    object target = OBJECT_INVALID;
    if (role <= 3)
    {
        target = HVD_PursuePlayer(mob);
        if (!GetIsObjectValid(target)) return;
    }
    else
    {
        location home = GetLocalLocation(mob, "hvd_home");
        vector origin = GetPositionFromLocation(home);
        float leash = GetLocalFloat(mob, "hvd_leash");
        target = HVD_NearPlayer(mob, 28.0, role == 6, leash);
        if (!GetIsObjectValid(target) || HVD_Distance(GetPosition(mob), origin) > leash)
        {
            if (GetCurrentAction(mob) != ACTION_MOVETOPOINT)
            {
                AssignCommand(mob, ClearAllActions());
                if (GetIsObjectValid(GetAreaFromLocation(home)) && HVD_Distance(GetPosition(mob), origin) > 2.0)
                    AssignCommand(mob, ActionMoveToLocation(home, TRUE));
            }
            return;
        }
    }
    vector start = GetPosition(mob);
    vector aimed = GetPosition(target);
    float distance = HVD_Distance(start, aimed);
    if (role == 2)
    {
        HVD_ThrowerAttack(mob, target, distance);
        if (!GetLocalInt(mob, "hvd_cast") && distance > 4.0 && distance < 24.0)
        {
            HVD_Cooldown(mob, 7.5, 1.2);
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_SONIC), mob);
            DelayCommand(1.1, HVD_ThrowBolt(mob, target));
        }
        return;
    }
    if (GetLocalInt(mob, "hvd_cast"))
    {
        if (!GetLocalInt(mob, "hvd_aim") && (role != 6 || distance < 4.0))
            HVD_NormalAttack(mob, target);
        return;
    }
    if (role == 3 && HVD_SpinnerCast(mob, distance)) return;
    if (role == 1 && distance < RADIUS_SIZE_LARGE && !GetLocalInt(area, "hvd_push"))
    {
        AssignCommand(mob, ClearAllActions());
        HVD_Cooldown(mob, 10.0, 1.1);
        HVD_ReservePush(area, 13.0);
        HVD_MarkRing(area, start, RADIUS_SIZE_LARGE, VFX_IMP_SONIC);
        DelayCommand(1.0, HVD_Whirlwind(mob));
        return;
    }
    if (role == 4 && distance < 17.0 && !GetLocalInt(mob, "hvd_storm_cast"))
    {
        SetLocalInt(mob, "hvd_storm_cast", TRUE);
        AssignCommand(mob, ClearAllActions());
        HVD_Cooldown(mob, 5.0, 1.7);
        HVD_AreaMessage(area, "Bouřný vír svolává bouři nad podestou.");
        DelayCommand(1.6, HVD_VirStorm(mob));
        return;
    }
    if (role == 4 && distance < 10.5 && !GetLocalInt(area, "hvd_push"))
    {
        AssignCommand(mob, ClearAllActions());
        HVD_Cooldown(mob, 11.0, 5.2);
        HVD_ReservePush(area, 17.0);
        HVD_AreaMessage(area, "Kamínky se stáčejí k jádru. Bouřný vír začne vtahovat.");
        HVD_MarkRing(area, start, RADIUS_SIZE_LARGE, VFX_IMP_PULSE_COLD);
        DelayCommand(2.7, HVD_VirPull(mob, start));
        DelayCommand(4.9, HVD_VirBurst(mob));
        return;
    }
    if ((role == 5 && distance < 9.5) || role == 6)
    {
        AssignCommand(mob, ClearAllActions());
        HVD_Cooldown(mob, 8.5, 3.6);
        float range = 10.0;
        if (role == 6) range = distance;
        vector end = start + range * VectorNormalize(aimed - start);
        HVD_MarkLine(area, start, end, VFX_IMP_SONIC);
        string warning = "Kopiník zapřel kopí. Ustup z vyznačené výseče!";
        if (role == 6) warning = "Lucerna označila dráhu výboje!";
        HVD_AreaMessage(area, warning);
        int damage = 40;
        int type = DAMAGE_TYPE_PIERCING;
        if (role == 6) { damage = 43; type = DAMAGE_TYPE_DIVINE; }
        DelayCommand(3.4, HVD_HitLine(mob, start, end, 1.8, damage, type));
        return;
    }
    HVD_NormalAttack(mob, target);
}
