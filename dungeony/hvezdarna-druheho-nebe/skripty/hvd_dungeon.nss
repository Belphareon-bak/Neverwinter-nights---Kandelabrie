#include "hvd_combat"

int HVD_InBox(object trigger, object player)
{
    vector position = GetPosition(player);
    return GetArea(player) == GetArea(trigger) &&
        position.x >= IntToFloat(GetLocalInt(trigger, "x0")) &&
        position.x <= IntToFloat(GetLocalInt(trigger, "x1")) &&
        position.y >= IntToFloat(GetLocalInt(trigger, "y0")) &&
        position.y <= IntToFloat(GetLocalInt(trigger, "y1"));
}

void HVD_TrapLine(object trigger, int visual)
{
    vector left = GetPosition(trigger);
    vector right = left;
    if (GetLocalInt(trigger, "axis"))
    {
        left.y = IntToFloat(GetLocalInt(trigger, "y0"));
        right.y = IntToFloat(GetLocalInt(trigger, "y1"));
    }
    else
    {
        left.x = IntToFloat(GetLocalInt(trigger, "x0"));
        right.x = IntToFloat(GetLocalInt(trigger, "x1"));
    }
    HVD_MarkLine(GetArea(trigger), left, right, visual);
}

int HVD_TrapDisabled(object trigger)
{
    string flag = GetLocalString(trigger, "flag");
    return flag != "" && GetLocalInt(HVD_Module(), flag);
}

void HVD_TrapBurst(object trigger, int kind, int run)
{
    if (HVD_Run() != run || HVD_TrapDisabled(trigger)) return;
    object area = GetArea(trigger);
    HVD_TrapLine(trigger, VFX_IMP_PULSE_COLD);
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_IsPlayer(player) && HVD_InBox(trigger, player) &&
            !HVD_Covered(area, GetPosition(trigger), GetPosition(player)))
        {
            if (kind == 1) HVD_Strike(player, trigger, 26, DAMAGE_TYPE_BLUDGEONING, 27, TRUE);
            else HVD_Strike(player, trigger, 34, DAMAGE_TYPE_DIVINE, 29);
        }
        player = GetNextPC();
    }
}

void HVD_Trap(object trigger, int kind)
{
    if (!GetIsObjectValid(trigger) || !kind || HVD_TrapDisabled(trigger) ||
        GetLocalInt(trigger, "hvd_busy") == HVD_Run()) return;
    object area = GetArea(trigger);
    SetLocalInt(trigger, "hvd_busy", HVD_Run());
    if (kind == 1) HVD_AreaMessage(area, "Praporky se napnuly. Kameny ukryjí družinu před poryvem.");
    else HVD_AreaMessage(area, "Po dlažbě běží bledá čára. Ustup z vyznačeného pruhu.");
    HVD_TrapLine(trigger, VFX_IMP_SONIC);
    DelayCommand(2.8, HVD_TrapBurst(trigger, kind, HVD_Run()));
    DelayCommand(8.5, DeleteLocalInt(trigger, "hvd_busy"));
}

void HVD_OpenGate(object player)
{
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_gate_open"))
    {
        SendMessageToPC(player, "Brána už je otevřená. Za ní vede poslední stupeň.");
        return;
    }
    int slot;
    int code;
    for (slot = 1; slot <= 3; ++slot)
    {
        int sign = GetLocalInt(module, "hvd_slot" + IntToString(slot));
        if (!sign || !GetIsObjectValid(HVD_HeldSeal(sign)))
        {
            SendMessageToPC(player, "Každá patice potřebuje jednu pečeť z této výpravy. U rozpisu lze znovu vydat ztracené.");
            return;
        }
        code = code * 10 + sign;
    }
    if (code != GetLocalInt(module, "hvd_order"))
    {
        HVD_AreaMessage(GetArea(player), "Brána sestavu odmítla. Znovu přečti stopy od noclehu k reliéfu.");
        HVD_Trap(GetObjectByTag("hvd_gatespark"), 2);
        return;
    }
    SetLocalInt(module, "hvd_gate_open", TRUE);
    HVD_Reveal("hvd_final_gate");
    HVD_AreaMessage(GetArea(player), "Tři patice zazářily. Světlo se spojilo v bránu na vrcholu schodů.");
}

void HVD_Rest(object player)
{
    object area = GetArea(player);
    object monster = GetFirstObjectInArea(area);
    while (GetIsObjectValid(monster))
    {
        if (GetLocalInt(monster, "hvd_managed") && !GetIsDead(monster) && GetDistanceBetween(player, monster) < 18.0)
        {
            SendMessageToPC(player, "Stráže jsou moc blízko. Ustup dál do bezpečí.");
            return;
        }
        monster = GetNextObjectInArea(area);
    }
    ForceRest(player);
    SendMessageToPC(player, "Družina má chvíli na odpočinek.");
}

void HVD_Dial(object player, int side)
{
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_aligned"))
    {
        SendMessageToPC(player, "Optika je seřízená. Schody vedou z kopule vzhůru.");
        return;
    }
    string variable = "hvd_dial" + IntToString(side);
    int angle = (GetLocalInt(module, variable) + 1) % 3;
    SetLocalInt(module, variable, angle);
    HVD_TurnOptics();
    SendMessageToPC(player, "Clona stojí na rysce " + IntToString(angle + 1) + ".");
}

void HVD_Optics(object player)
{
    object module = HVD_Module();
    int left = GetLocalInt(module, "hvd_dial1") + 1;
    int right = GetLocalInt(module, "hvd_dial2") + 1;
    if (GetLocalInt(module, "hvd_aligned"))
    {
        SendMessageToPC(player, "Kopule míří na druhé nebe. Přejdi k průchodu za objektivem.");
        return;
    }
    SendMessageToPC(player, "Stupnice objektivu – západ " + IntToString(left) + ", východ " + IntToString(right) + ".");
    if (left == 2 && right == 3)
    {
        SetLocalInt(module, "hvd_aligned", TRUE);
        HVD_AreaMessage(GetArea(player), "Ve skle se potkaly obě oblohy. Schody do nebe jsou průchodné.");
        HVD_MarkLine(GetArea(player), GetPosition(GetObjectByTag("hvd_refractor")),
                     GetPosition(GetWaypointByTag("hvd_optic_gate")), VFX_IMP_PULSE_COLD);
        HVD_Reveal("hvd_optic_gate");
    }
    else
    {
        SendMessageToPC(player, "Rysky na podstavci ukazují západ II a východ III.");
        HVD_Trap(GetObjectByTag("hvd_domeray"), 2);
    }
}

void HVD_Chime(object player, object chime)
{
    object area = GetArea(chime);
    object enemy = GetFirstObjectInArea(area);
    object nearest = OBJECT_INVALID;
    float range = 18.0;
    while (GetIsObjectValid(enemy))
    {
        int role = GetLocalInt(enemy, "role");
        float distance = GetDistanceBetween(chime, enemy);
        if (role > 0 && role <= 4 && !GetIsDead(enemy) && distance < range &&
            LineOfSightObject(chime, enemy))
        {
            nearest = enemy;
            range = distance;
        }
        enemy = GetNextObjectInArea(area);
    }
    if (!GetIsObjectValid(nearest))
    {
        SendMessageToPC(player, "V dosahu ozvučnice je klidný vzduch.");
        return;
    }
    if (GetLocalInt(chime, "hvd_chimed") == GetLocalInt(area, "hvd_wave"))
    {
        SendMessageToPC(player, "Ozvučnice pro tento střet už dozněla.");
        return;
    }
    SetLocalInt(chime, "hvd_chimed", GetLocalInt(area, "hvd_wave"));
    HVD_MarkLine(area, GetPosition(chime), GetPosition(nearest), VFX_IMP_SONIC);
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(64, DAMAGE_TYPE_SONIC), nearest);
    HVD_AreaMessage(area, "Ozvučnice vyslala zvukový výboj. Větrné tělo se rozkmitalo.");
}

object HVD_FindMirror()
{
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        object mirror = GetItemPossessedBy(player, "hvd_mirror");
        if (GetIsObjectValid(mirror) && GetLocalInt(mirror, "hvd_run") == HVD_Run()) return mirror;
        player = GetNextPC();
    }
    return OBJECT_INVALID;
}

void HVD_Mount(object player)
{
    if (GetLocalInt(HVD_Module(), "hvd_mounted"))
    {
        SendMessageToPC(player, "Zrcadlo je bezpečně zasazené.");
        return;
    }
    object mirror = HVD_FindMirror();
    if (!GetIsObjectValid(mirror))
    {
        SendMessageToPC(player, "Do patice patří přenosné zrcadlo z pouzdra ve zkušebně dolních dílen.");
        return;
    }
    DestroyObject(mirror);
    SetLocalInt(HVD_Module(), "hvd_mounted", TRUE);
    HVD_PlacePart("hvd_socket_mirror", "hvd_mirror_set", "hvd_mirror_mount", 0.0);
    HVD_AreaMessage(GetArea(player), "Zrcadlo zacvaklo do patice. Zachytí jeden výboj v závěru střetu s Ithrenem.");
}
