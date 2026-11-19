#include "hvd_final"

void main()
{
    object player = GetLastUsedBy();
    object target = OBJECT_SELF;
    object module = HVD_Module();
    if (!HVD_IsPlayer(player)) return;
    string operation = GetLocalString(target, "action");

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
    if (operation == "gate_filter")
    {
        HVD_RotateFilter(player, GetLocalInt(target, "slot"));
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
    if (operation == "rest")
    {
        HVD_Rest(player);
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
    if (operation == "read")
    {
        SendMessageToPC(player, GetDescription(target));
        return;
    }
    if (operation == "study_pin")
    {
        if (!GetLocalInt(module,"hvd_study_open"))
        {
            HVD_OpenPassage("hvd_study_open");
            HVD_Extinguish("hvd_study_cover");
            HVD_AreaMessage(GetArea(player),"Povolila západka. V bočním výklenku zajela skříň do zdiva.");
        }
        return;
    }
    if (operation == "study_turn")
    {
        if (!GetLocalInt(module,"hvd_study_link"))
        {
            HVD_OpenPassage("hvd_study_link");
            HVD_Extinguish("hvd_comm_cover");
            HVD_Extinguish("hvd_dome_cover");
            HVD_AreaMessage(GetArea(player),"Převod stáhl obě zadní clony. Z průchodu je vidět slabé světlo refraktoru.");
        }
        return;
    }
    if (operation == "eave_pin")
    {
        if (!GetLocalInt(module,"hvd_eave_open"))
        {
            HVD_OpenPassage("hvd_eave_open");
            HVD_Extinguish("hvd_eave_cover");
            HVD_Extinguish("hvd_eavetop_cover");
            HVD_AreaMessage(GetArea(player),"Protizávaží vyzdvihlo západní kryt. Pod schody se ukázal servisní průlez.");
        }
        return;
    }
    if (operation == "eave_brake")
    {
        if (!GetLocalInt(module,"hvd_eave_safe"))
        {
            SetLocalInt(module,"hvd_eave_safe",TRUE);
            ApplyEffectAtLocation(DURATION_TYPE_INSTANT,EffectVisualEffect(VFX_IMP_PULSE_COLD),GetLocation(target));
            HVD_AreaMessage(GetArea(player),"Klapka se zaklesla. Vítr teď uniká kamenným kanálem pod lávkou.");
        }
        return;
    }
    if (operation == "testbeam")
    {
        HVD_TestOptics(player);
        return;
    }
    if (operation == "disarm")
    {
        string flag = GetLocalString(target, "flag");
        if (flag == "hvd_hall_off" && GetLocalInt(module,flag))
        {
            SendMessageToPC(player,"Vysílače jsou odpojené. Čočky na obou stěnách zakrývají zavřené clony.");
            return;
        }
        if (GetSkillRank(SKILL_DISABLE_TRAP, player) >= GetLocalInt(target, "skill") ||
            GetLocalInt(module, "hvd_notes") || GetTag(GetArea(player)) == "hvd_gate")
        {
            if (flag == "hvd_chest_off" && !GetLocalInt(module, flag))
            {
                HVD_Stock(GetObjectByTag("hvd_guard_cache"), "hvd_glass");
                SendMessageToPC(player, "Pojistka odsunula falešné dno ve schránce strážnice.");
            }
            SetLocalInt(module, flag, TRUE);
            if (flag == "hvd_hall_off")
            {
                HVD_UpdateHallLights();
                HVD_AreaMessage(GetArea(player),"Pojistka zavřela všechny tři clony. Paprsková chodba je bezpečná.");
            }
            else SendMessageToPC(player, "Clona přerušila zdroj výboje.");
        }
        else SendMessageToPC(player,"Západku seřiď se zneškodňováním pastí 15 nebo podle sešitu ze zkušebního stolu v dolní dílně.");
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
