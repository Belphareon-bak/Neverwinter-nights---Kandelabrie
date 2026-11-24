#include "hvd_final"

object PlayerOnTrigger(object trigger, int searching)
{
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_IsPlayer(player) && HVD_InBox(trigger, player) &&
            (!searching || HVD_CanSearchSecret(player))) return player;
        player = GetNextPC();
    }
    return OBJECT_INVALID;
}

void main()
{
    HVD_UpdateAreaWind(OBJECT_SELF);
    HVD_RefreshStormMusic(OBJECT_SELF);
    if (!HVD_AreaCount(OBJECT_SELF))
    {
        if (GetTag(OBJECT_SELF) == "hvd_top" && !GetLocalInt(HVD_Module(), "hvd_won") &&
            (HVD_GuardState() == HVD_GUARD_COMBAT || HVD_GuardState() == HVD_GUARD_DUEL ||
             GetIsObjectValid(HVD_Guardian()))) HVD_ResetBoss();
        return;
    }
    if (GetTag(OBJECT_SELF) == "hvd_top" && HVD_LanternCharged() &&
        !GetIsObjectValid(GetLocalObject(HVD_Module(), "hvd_sun_caster"))) HVD_StartLantern();
    object trigger = GetFirstObjectInArea(OBJECT_SELF, OBJECT_TYPE_TRIGGER);
    while (GetIsObjectValid(trigger))
    {
        object next = GetNextObjectInArea(OBJECT_SELF, OBJECT_TYPE_TRIGGER);
        int kind = GetLocalInt(trigger, "hazard");
        string secret = GetLocalString(trigger, "secret");
        string group = GetLocalString(trigger, "encounter");
        if (group != "" && !HVD_EncounterActive(OBJECT_SELF, group))
        {
            object player = PlayerOnTrigger(trigger, FALSE);
            if (GetIsObjectValid(player)) HVD_ActivateEncounter(OBJECT_SELF, group, player);
        }
        else if (kind || secret != "")
        {
            object player = PlayerOnTrigger(trigger, secret != "");
            if (GetIsObjectValid(player))
            {
                if (secret != "") HVD_InspectSecret(player, secret);
                else if (kind == 3) HVD_GuardGreet(player);
                else HVD_Trap(trigger, kind);
            }
        }
        trigger = next;
    }
}
