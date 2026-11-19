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

int HVD_CurrentProjection(int run, int attempt)
{
    return HVD_Run() == run && GetLocalInt(HVD_Module(),"hvd_gate_attempt") == attempt;
}

void HVD_EndProjection(int run, int attempt)
{
    if (!HVD_CurrentProjection(run,attempt)) return;
    int slot;
    for (slot = 1; slot <= 3; ++slot)
        HVD_Extinguish("hvd_ray_display" + IntToString(slot));
}

void HVD_ResolveGate(int run, int attempt, int seals, int lenses)
{
    if (!HVD_CurrentProjection(run,attempt)) return;
    object module = HVD_Module();
    object area = GetObjectByTag("hvd_gate");
    if (HVD_GateContents() != seals || HVD_FilterCode() != lenses)
    {
        HVD_EndProjection(run,attempt);
        HVD_AreaMessage(area,"Soustava se při měření pohnula. Až bude seřízená, použij spoušť znovu.");
        return;
    }
    int order = GetLocalInt(module,"hvd_order");
    if (seals != 10 * order + HVD_ShutterSign(order) ||
        lenses != GetLocalInt(module,"hvd_lens_order"))
    {
        HVD_EndProjection(run,attempt);
        HVD_AreaMessage(area,"Světlo se v ostění rozlomilo. Srovnej stopy o pečetích se zápisem o clonách.");
        HVD_Trap(GetObjectByTag("hvd_gatespark"),2);
        return;
    }
    HVD_Reveal("hvd_final_gate");
    if (!GetIsObjectValid(GetLocalObject(module,"hvd_final_gate"))) return;
    SetLocalInt(module,"hvd_gate_open",TRUE);
    HVD_AreaMessage(area,"Tři paprsky se spojily. Brána na schodech se otevřela.");
}

void HVD_OpenGate(object player)
{
    object module = HVD_Module();
    if (GetLocalInt(module,"hvd_gate_open"))
    {
        SendMessageToPC(player,"Brána je otevřená. Odtud už vede schodiště k poslední hlídce.");
        return;
    }
    int seals = HVD_GateContents();
    if (!seals)
    {
        SendMessageToPC(player,"Převod potřebuje přesně jednu platnou pečeť v každém sloupu i v závoře.");
        return;
    }
    int west = HVD_FilterAt(1);
    int center = HVD_FilterAt(2);
    int east = HVD_FilterAt(3);
    if (west == center || west == east || center == east)
    {
        SendMessageToPC(player,"V každém sloupu musí svítit jiný znak. Seřiď clony páčkami na bocích.");
        return;
    }
    int attempt = GetLocalInt(module,"hvd_gate_attempt") + 1;
    SetLocalInt(module,"hvd_gate_attempt",attempt);
    int slot;
    for (slot = 1; slot <= 3; ++slot)
    {
        string suffix = IntToString(slot);
        HVD_ShowSeal(slot);
        HVD_PlacePart("hvd_ray_display" + suffix,"hvd_ray" + suffix + IntToString(HVD_FilterAt(slot)),
                      "hvd_final_gate",0.0);
    }
    HVD_ShowSeal(4);
    HVD_AreaMessage(GetArea(player),"Čočky zachytily světlo. Paprsky stoupají po schodech.");
    DelayCommand(1.8,HVD_ResolveGate(HVD_Run(),attempt,seals,HVD_FilterCode()));
    DelayCommand(5.2,HVD_EndProjection(HVD_Run(),attempt));
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
    AssignCommand(chime, PlaySound("as_cv_gongring1"));
    HVD_MarkLine(area, GetPosition(chime), GetPosition(nearest), VFX_IMP_SONIC);
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(64, DAMAGE_TYPE_SONIC), nearest);
    HVD_AreaMessage(area, "Ozvučnice vyslala zvukový výboj. Větrné tělo se rozkmitalo.");
}

void HVD_EndLabTrial(int run, int trial)
{
    if (HVD_Run() == run && GetLocalInt(HVD_Module(),"hvd_lab_trial") == trial)
        HVD_Extinguish("hvd_lab_light");
}

void HVD_TestOptics(object player)
{
    object module = HVD_Module();
    int trial = GetLocalInt(module,"hvd_lab_trial") + 1;
    SetLocalInt(module,"hvd_lab_trial",trial);
    HVD_PlacePart("hvd_lab_light","hvd_lab_trace","hvd_lab_switch",0.0);
    DelayCommand(5.0,HVD_EndLabTrial(HVD_Run(),trial));
    SendMessageToPC(player,"Odraz rozsvítil levou rysku II a pravou III. V kopuli nastav západní clonu na II a východní na III. "
                   +"Záložní zrcadlo pro Poslední stupeň je v pouzdře u pracovního stolu.");
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
