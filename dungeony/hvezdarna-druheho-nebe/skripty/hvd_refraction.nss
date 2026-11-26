const int HVD_REPAIR_OPTICS = 9;

void HVD_RepairJournal(object player)
{
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_won"))
        AddJournalQuestEntry("hvd_clona_quest", 30, player, FALSE);
    else if (GetLocalInt(module, "hvd_repair_done"))
        AddJournalQuestEntry("hvd_clona_quest", 20, player, FALSE);
    else if (HVD_GuardState() == HVD_GUARD_REPAIR)
        AddJournalQuestEntry("hvd_clona_quest", 10, player, FALSE);
    else
        RemoveJournalQuestEntry("hvd_clona_quest", player, FALSE);
}

void HVD_RepairJournals()
{
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (!GetIsDM(player)) HVD_RepairJournal(player);
        player = GetNextPC();
    }
}

int HVD_RepairMark(int index)
{
    return GetLocalInt(HVD_Module(), "hvd_rep_mark" + IntToString(index));
}

int HVD_RepairMode(int index)
{
    object mount = GetWaypointByTag("hvd_rep_m" + IntToString(index));
    return GetLocalInt(mount, "mode" + IntToString(HVD_RepairMark(index)));
}

string HVD_RepairKeyTag()
{
    return HVD_ITHREN_KEY + "_" + IntToString(HVD_Run());
}

void HVD_ResetRepairDoor()
{
    object door = GetObjectByTag("hvd_repairdoor");
    if (GetIsOpen(door)) AssignCommand(door, ActionCloseDoor(door));
    SetLockKeyTag(door, HVD_RepairKeyTag());
    SetLocked(door, TRUE);
}

void HVD_RepairDoorHint(object player)
{
    if (!GetLocked(GetObjectByTag("hvd_repairdoor")))
        SendMessageToPC(player, "Zámek servisních dveří je odemčený.");
    else if (HVD_GuardState() == HVD_GUARD_REPAIR)
        SendMessageToPC(player, "Servis otevře držitel Ithrenova klíče. Pro náhradu požádej Ithrena na Posledním stupni.");
    else
        SendMessageToPC(player, "Kamenné dveře jsou zamčené. Klíč svěřuje Ithren po čestné zkoušce.");
}

int HVD_RepairLine()
{
    return HVD_Run() % 2 ? 1 : 2;
}

void HVD_RepairOutletHint(object player)
{
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_repair_done"))
        SendMessageToPC(player, "Světlovod vede purpurovou až k Poslední lucerně. Ohlas opravu Ithrenovi.");
    else if (GetResRef(GetLocalObject(module, "hvd_output_iris")) == "hvd_iris_open")
        SendMessageToPC(player, "Zelený čtverec svítí. Clona je otevřená a světlovod čeká na purpurový paprsek.");
    else
        SendMessageToPC(player, "Clona je zavřená. Horní znak " + (HVD_RepairLine() == 1 ? "Slunce" : "Hvězdy") +
            " označuje čidlo, které má Zelená pojistka výstupu osvítit.");
}

void HVD_RepairBoard(int opened, int received)
{
    HVD_PlacePart("hvd_board_line", HVD_RepairLine() == 1 ? "hvd_board_sun" : "hvd_board_star", "hvd_outlet_panel", 0.0);
    if (opened) HVD_PlacePart("hvd_board_ready", "hvd_board_green", "hvd_outlet_panel", 0.0);
    else HVD_Extinguish("hvd_board_ready");
    if (received) HVD_PlacePart("hvd_board_received", "hvd_board_purp", "hvd_outlet_panel", 0.0);
    else HVD_Extinguish("hvd_board_received");
}

void HVD_RepairSignals()
{
    int index;
    for (index = 1; index <= 2; ++index)
    {
        string tag = "hvd_ward" + IntToString(index);
        if (GetLocalInt(HVD_Module(), "hvd_repair_done"))
            HVD_PlacePart(tag, "hvd_wardglow", tag, 0.0);
        else
            HVD_Extinguish(tag);
    }
}

void HVD_RepairRay(int index, int live, int color = 0, int sealed = FALSE)
{
    string slot = IntToString(index);
    string part = "hvd_repair_ray" + slot;
    if (!live)
    {
        HVD_Extinguish(part);
        return;
    }
    string resource = "hvd_rp" + slot + IntToString(HVD_RepairMark(index));
    if (sealed) resource = "hvd_rq" + IntToString(color);
    else if (color) resource += IntToString(color);
    HVD_PlacePart(part, resource, "hvd_rep_m" + slot, 0.0);
}

void HVD_StopRepairBells(int run)
{
    if (HVD_Run() != run) return;
    SoundObjectStop(GetObjectByTag("hvd_sfx_outbell"));
    SoundObjectStop(GetObjectByTag("hvd_sfx_topbell"));
}

void HVD_RingRepairBells(int run)
{
    if (HVD_Run() != run || !GetLocalInt(HVD_Module(), "hvd_repair_done")) return;
    SoundObjectPlay(GetObjectByTag("hvd_sfx_outbell"));
    SoundObjectPlay(GetObjectByTag("hvd_sfx_topbell"));
    DelayCommand(2.6, HVD_StopRepairBells(run));
}

void HVD_TraceRepair(object player = OBJECT_INVALID)
{
    int live = HVD_GuardState() == HVD_GUARD_REPAIR;
    int index;
    for (index = 1; index <= HVD_REPAIR_OPTICS; ++index)
    {
        string slot = IntToString(index);
        string tag = "hvd_rep_m" + slot;
        float angle = GetLocalFloat(GetWaypointByTag(tag), "angle" + IntToString(HVD_RepairMark(index)));
        HVD_PlacePart("hvd_repair_head" + slot, "hvd_rm" + slot, tag, angle);
    }
    HVD_RepairRay(1, live);
    int detour = live && HVD_RepairMode(1) == 1;
    HVD_RepairRay(2, detour);
    int fed = detour && HVD_RepairMode(2) == 1;
    HVD_RepairRay(3, fed);
    HVD_OpticHum("hvd_sfx_prism", fed);

    int prism = fed ? HVD_RepairMode(3) : 0;
    int spectrum = prism == 1;
    HVD_RepairRay(4, spectrum);
    HVD_RepairRay(5, spectrum);
    HVD_RepairRay(6, spectrum || prism == 4);
    int green = spectrum ? HVD_RepairMode(5) : 0;
    int color = 0;
    if (spectrum && HVD_RepairMode(4) == 1) color += 1;
    if (green == 2) color += 2;
    if (prism && HVD_RepairMode(6) == 1) color += 4;
    HVD_RepairRay(7, color > 0, color);
    HVD_RepairRay(8, green == 1);

    int opened = green == 1 && HVD_RepairMode(8) == HVD_RepairLine();
    int output = color > 0 && HVD_RepairMode(7) == 1;
    int toLantern = output && HVD_RepairMode(9) == 1;
    int received = toLantern && opened && color == 5;
    HVD_PlacePart("hvd_output_iris", opened ? "hvd_iris_open" : "hvd_iris_closed", "hvd_sun_iris", 0.0);
    HVD_RepairRay(9, output, color, toLantern && !opened);
    HVD_RepairBoard(opened, received);

    object module = HVD_Module();
    if (received && !GetLocalInt(module, "hvd_repair_done"))
    {
        SetLocalInt(module, "hvd_repair_done", TRUE);
        HVD_QuietExpedition();
        HVD_RepairJournals();
        HVD_UpdateLastLight();
        HVD_RepairSignals();
        // Let the click of the mirror's latch precede the completion tone.
        int run = HVD_Run();
        DelayCommand(0.55, HVD_RingRepairBells(run));
        if (GetIsObjectValid(player))
            HVD_AreaMessage(GetArea(player),
                "Purpurový paprsek vstoupil do světlovodu. Vítr utichl a hlídky se rozešly. Ohlaste opravu Ithrenovi.");
    }
    else if (toLantern && GetIsObjectValid(player) && !GetLocalInt(module, "hvd_repair_done"))
        HVD_RepairOutletHint(player);
}

void HVD_ResetRepair()
{
    object module = HVD_Module();
    DeleteLocalInt(module, "hvd_repair_done");
    HVD_StopRepairBells(HVD_Run());
    int index;
    for (index = 1; index <= HVD_REPAIR_OPTICS; ++index)
    {
        string slot = IntToString(index);
        object mount = GetWaypointByTag("hvd_rep_m" + slot);
        SetLocalInt(module, "hvd_rep_mark" + slot, GetLocalInt(mount, "initial"));
    }
    HVD_ResetRepairDoor();
    HVD_TraceRepair();
    HVD_RepairSignals();
    HVD_RepairJournals();
}

void HVD_TurnRepair(object player, int index)
{
    if (index < 1 || index > HVD_REPAIR_OPTICS) return;
    if (HVD_GuardState() != HVD_GUARD_REPAIR)
    {
        SendMessageToPC(player, "Služební okruh povoluje Ithren. Nejdřív se vydej na Poslední stupeň.");
        return;
    }
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_repair_done"))
    {
        SendMessageToPC(player, "Seřízení drží ochrannou lucernu. Západka zajistila tuto polohu.");
        return;
    }
    string slot = IntToString(index);
    int mark = (HVD_RepairMark(index) + 1) % 3;
    SetLocalInt(module, "hvd_rep_mark" + slot, mark);
    object mount = GetWaypointByTag("hvd_rep_m" + slot);
    PlaySound("as_sw_lever1");
    SendMessageToPC(player, HVD_RomanMark(mark + 1) + " · " + GetLocalString(mount, "aim" + IntToString(mark)) + ".");
    HVD_TraceRepair(player);
}
