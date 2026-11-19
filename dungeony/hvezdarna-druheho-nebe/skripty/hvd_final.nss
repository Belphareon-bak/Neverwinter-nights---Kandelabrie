#include "hvd_dungeon"

void HVD_BossStart(object player)
{
    object module = HVD_Module();
    if (!GetLocalInt(module, "hvd_gate_open") || GetLocalInt(module, "hvd_won") ||
        GetIsObjectValid(GetLocalObject(module, "hvd_boss"))) return;
    object boss = HVD_MobAt("hvd_ithren", GetWaypointByTag("hvd_boss_home"), 0, TRUE);
    if (!GetIsObjectValid(boss)) return;
    SetLocalObject(module, "hvd_boss", boss);
    SetLocalInt(boss, "hvd_phase", 1);
    HVD_AreaMessage(GetArea(player), "Ithren: Dokud svítí její znamení, schody zůstanou otevřené.");
    AssignCommand(boss, ActionAttack(player));
}

int HVD_Lane(vector position)
{
    if (position.x < 27.5) return 1;
    if (position.x > 42.5) return 3;
    return 2;
}

void HVD_MarkLane(object area, int lane)
{
    float middle = 20.0 + IntToFloat(lane - 1) * 15.0;
    HVD_MarkLine(area, Vector(middle - 6.0, 31.0, 10.0), Vector(middle - 6.0, 51.5, 10.0), VFX_IMP_SONIC);
    HVD_MarkLine(area, Vector(middle + 6.0, 31.0, 10.0), Vector(middle + 6.0, 51.5, 10.0), VFX_IMP_SONIC);
}

void HVD_BossLane(object boss, int lane)
{
    if (!GetIsObjectValid(boss) || GetLocalInt(HVD_Module(), "hvd_won")) return;
    object area = GetArea(boss);
    vector origin = GetPosition(boss);
    float middle = 20.0 + IntToFloat(lane - 1) * 15.0;
    HVD_MarkLine(area, Vector(middle, 31.5, 10.0), Vector(middle, 51.5, 10.0), VFX_IMP_PULSE_COLD);
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        vector position = GetPosition(player);
        if (HVD_PlayerIn(player, area) && HVD_Lane(position) == lane && position.y >= 30.0 &&
            position.y < 55.0 && !HVD_Covered(area, origin, position))
            HVD_Strike(player, boss, 55, DAMAGE_TYPE_DIVINE, 34);
        player = GetNextPC();
    }
}

void HVD_ShutterWindow(object boss, float seconds)
{
    object module = HVD_Module();
    if (!GetIsObjectValid(boss) || !GetLocalInt(boss, "hvd_yield") || GetLocalInt(module, "hvd_won")) return;
    SetLocalInt(module, "hvd_shutter", TRUE);
    HVD_AreaMessage(GetArea(boss), "Ithren ustoupil od lucerny. Teď lze sklopit clonu.");
    DelayCommand(seconds, DeleteLocalInt(module, "hvd_shutter"));
}

int HVD_AddAlive(object boss, string field)
{
    object add = GetLocalObject(boss, field);
    return GetIsObjectValid(add) && !GetIsDead(add);
}

void HVD_BossThink(object boss)
{
    object module = HVD_Module();
    if (!GetIsObjectValid(boss) || GetLocalInt(module, "hvd_won")) return;
    object area = GetArea(boss);
    int phase = GetLocalInt(boss, "hvd_phase");
    int percent = 100 * GetCurrentHitPoints(boss) / GetMaxHitPoints(boss);
    if (phase == 1 && percent <= 74)
    {
        SetLocalInt(boss, "hvd_phase", 2);
        SetLocalObject(boss, "hvd_add1", HVD_MobAt("hvd_kopi", GetWaypointByTag("hvd_add_west")));
        SetLocalObject(boss, "hvd_add2", HVD_MobAt("hvd_svetlonos", GetWaypointByTag("hvd_add_east")));
        HVD_AreaMessage(area, "Ithren volá kopiníka a světlonoše. Boční podesty jsou vystavené jejich útokům.");
        return;
    }
    if (phase == 2 && percent <= 43 && !HVD_AddAlive(boss, "hvd_add1") && !HVD_AddAlive(boss, "hvd_add2"))
    {
        phase = 3;
        SetLocalInt(boss, "hvd_phase", phase);
        HVD_AreaMessage(area, "Ithren sevřel lucernu. Světlo se láme na dvě dráhy.");
    }
    if (phase == 3 && percent <= 13 && !GetLocalInt(boss, "hvd_yield"))
    {
        SetLocalInt(boss, "hvd_yield", TRUE);
        AssignCommand(boss, ClearAllActions());
        SetPlotFlag(boss, TRUE);
        HVD_AreaMessage(area, "Ithrenova obrana povolila. Přečkej výboje a dostaň se ke cloně.");
    }
    object target = HVD_NearPlayer(boss, 70.0);
    if (!GetIsObjectValid(target)) return;
    if (GetLocalInt(boss, "hvd_cast"))
    {
        if (!GetLocalInt(boss, "hvd_aim") && !GetLocalInt(boss, "hvd_yield"))
            HVD_NormalAttack(boss, target);
        return;
    }
    if (phase == 2)
    {
        HVD_NormalAttack(boss, target);
        return;
    }
    AssignCommand(boss, ClearAllActions());
    int first = HVD_Lane(GetPosition(target));
    int second = 1 + (first + Random(2)) % 3;
    if (phase == 1)
    {
        HVD_Cooldown(boss, 11.0, 3.5);
        HVD_MarkLane(area, first);
        HVD_AreaMessage(area, "Rozkaz k ústupu. Rozsvícená výseč " + IntToString(first) + " je v dráze nárazu.");
        DelayCommand(3.1, HVD_BossLane(boss, first));
        return;
    }
    HVD_Cooldown(boss, 15.0, 4.9);
    HVD_AreaMessage(area, "Poslední znamení. Výboje zasáhnou výseč " + IntToString(first) +
        " a potom výseč " + IntToString(second) + ".");
    HVD_MarkLane(area, first);
    HVD_MarkLane(area, second);
    int reflect = GetLocalInt(module, "hvd_mounted") && GetLocalInt(boss, "hvd_yield") &&
        !GetLocalInt(module, "hvd_mirror_used");
    DelayCommand(3.0, HVD_BossLane(boss, first));
    if (reflect)
    {
        SetLocalInt(module, "hvd_mirror_used", TRUE);
        HVD_AreaMessage(area, "Zrcadlo zachytilo světlo. Druhý výboj se rozpadne.");
        DelayCommand(3.3, HVD_ShutterWindow(boss, 9.0));
    }
    else
    {
        DelayCommand(4.9, HVD_BossLane(boss, second));
        DelayCommand(5.3, HVD_ShutterWindow(boss, 6.5));
    }
}

void HVD_CloseShutter(object player)
{
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_won"))
    {
        SendMessageToPC(player, "Volání utichlo. Z posledního stupně vede cesta na římsu.");
        return;
    }
    if (!GetLocalInt(module, "hvd_shutter"))
    {
        SendMessageToPC(player, "Ithren drží clonu. Překonej jeho obranu a vyčkej na doznění výbojů.");
        return;
    }
    HVD_OpenPassage("hvd_won");
    DeleteLocalInt(module, "hvd_shutter");
    object boss = GetLocalObject(module, "hvd_boss");
    if (GetIsObjectValid(boss))
    {
        AssignCommand(boss, ClearAllActions());
        ChangeToStandardFaction(boss, STANDARD_FACTION_COMMONER);
        SetObjectVisualTransform(boss, OBJECT_VISUAL_TRANSFORM_SCALE, 1.0);
        SetLocalInt(boss, "hvd_managed", TRUE);
    }
    object lamp = GetObjectByTag("hvd_last_lamp");
    if (GetIsObjectValid(lamp)) SetPlaceableIllumination(lamp, FALSE);
    HVD_OpenRewardStores();
    HVD_Reveal("hvd_summit_exit");
    HVD_AreaMessage(GetArea(player), "Odraz utichl. Ithren vidí prázdnou podestu a pomáhá zavřít horní bránu.");
    if (GetLocalInt(module, "hvd_notes"))
        HVD_AreaMessage(GetArea(player), "Z návratového zápisu lze vyčíst, kudy správkyně bezpečně sestoupila.");
    HVD_AreaMessage(GetArea(player), "U lucerny může každý člen zvolit jednu odměnu. Za ní vede cesta k noclehu.");
}
