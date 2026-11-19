#include "hvd_final"

void main()
{
    object player = GetLastUsedBy();
    object target = OBJECT_SELF;
    object module = HVD_Module();
    if (!HVD_IsPlayer(player)) return;
    string operation = GetLocalString(target, "action");

    if (operation == "clue")
    {
        int clue = GetLocalInt(target, "clue");
        SetLocalInt(module, "hvd_clue" + IntToString(clue), TRUE);
        SendMessageToPC(player, HVD_Clue(clue));
        return;
    }
    if (operation == "recap")
    {
        HVD_Recap(player);
        return;
    }
    if (operation == "seal")
    {
        HVD_Seal(player, GetLocalInt(target, "seal"));
        return;
    }
    if (operation == "socket")
    {
        HVD_Cycle(player, GetLocalInt(target, "slot"));
        return;
    }
    if (operation == "gate")
    {
        HVD_OpenGate(player);
        return;
    }
    if (operation == "dial")
    {
        HVD_Dial(player, GetLocalInt(target, "dial"));
        return;
    }
    if (operation == "optics")
    {
        HVD_Optics(player);
        return;
    }
    if (operation == "chime")
    {
        HVD_Chime(player, target);
        return;
    }
    if (operation == "supply")
    {
        HVD_Supply(player);
        return;
    }
    if (operation == "rest")
    {
        HVD_Rest(player);
        return;
    }
    if (operation == "loot" || operation == "reward")
    {
        HVD_Loot(player, GetLocalInt(target, "loot"));
        return;
    }
    if (operation == "mirror")
    {
        HVD_GetMirror(player);
        return;
    }
    if (operation == "mount")
    {
        HVD_Mount(player);
        return;
    }
    if (operation == "shutter")
    {
        HVD_CloseShutter(player);
        return;
    }
    if (operation == "boss")
    {
        HVD_BossStart(player);
        return;
    }
    if (operation == "notes")
    {
        SendMessageToPC(player, GetDescription(target));
        HVD_WorkshopNotes(player);
        return;
    }
    if (operation == "read")
    {
        SendMessageToPC(player, GetDescription(target));
        return;
    }
    if (operation == "testbeam")
    {
        vector mirror = GetPosition(GetObjectByTag("hvd_lab_mirror"));
        HVD_MarkLine(GetArea(player), GetPosition(target), mirror, VFX_IMP_SONIC);
        HVD_MarkLine(GetArea(player), mirror, mirror + Vector(0.0, 6.0, 0.0), VFX_IMP_PULSE_COLD);
        SendMessageToPC(player, "Paprsek se odrazil od zrcadla. Stejná patice je u poslední lucerny.");
        return;
    }
    if (operation == "disarm")
    {
        if (GetSkillRank(SKILL_DISABLE_TRAP, player) >= GetLocalInt(target, "skill") ||
            GetLocalInt(module, "hvd_notes") || GetTag(GetArea(player)) == "hvd_gate")
        {
            SetLocalInt(module, GetLocalString(target, "flag"), TRUE);
            SendMessageToPC(player, "Clona přerušila zdroj výboje.");
        }
        else SendMessageToPC(player, "K ovládání pomůže zneškodňování pastí nebo nález v dílnách. " +
            "Servisní chodba vede mimo výboj.");
        return;
    }
    if (operation == "reset")
    {
        object member = GetFirstPC();
        object camp = GetWaypointByTag("hvd_start");
        while (GetIsObjectValid(member))
        {
            if (!GetIsDM(member) && (!HVD_PlayerIn(member, GetArea(camp)) || GetDistanceBetween(member, camp) > 17.0))
            {
                SendMessageToPC(player, "Před novou výpravou se všichni sejděte v noclehu.");
                return;
            }
            member = GetNextPC();
        }
        if (!GetLocalInt(player, "hvd_asked_reset"))
        {
            SetLocalInt(player, "hvd_asked_reset", TRUE);
            DelayCommand(10.0, DeleteLocalInt(player, "hvd_asked_reset"));
            SendMessageToPC(player, "Dalším použitím ukončíš tuto výpravu a otevřeš novou.");
            return;
        }
        DeleteLocalInt(player, "hvd_asked_reset");
        HVD_NewRun();
        HVD_AreaMessage(GetArea(player), "Hvězdárna připravila novou výpravu. Přečtěte si rozpis hlídky.");
    }
}
