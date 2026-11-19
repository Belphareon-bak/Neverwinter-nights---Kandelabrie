#include "hvd_final"

object PlayerOnTrigger(object trigger)
{
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_IsPlayer(player) && HVD_InBox(trigger, player)) return player;
        player = GetNextPC();
    }
    return OBJECT_INVALID;
}

void main()
{
    if (!HVD_AreaCount(OBJECT_SELF))
    {
        if (GetTag(OBJECT_SELF) == "hvd_top" && !GetLocalInt(HVD_Module(), "hvd_won") &&
            GetIsObjectValid(GetLocalObject(HVD_Module(), "hvd_boss"))) HVD_ResetBoss();
        return;
    }
    HVD_ActivateArea(OBJECT_SELF);
    object trigger = GetFirstObjectInArea(OBJECT_SELF, OBJECT_TYPE_TRIGGER);
    while (GetIsObjectValid(trigger))
    {
        object next = GetNextObjectInArea(OBJECT_SELF, OBJECT_TYPE_TRIGGER);
        int kind = GetLocalInt(trigger, "hazard");
        if (kind)
        {
            object player = PlayerOnTrigger(trigger);
            if (GetIsObjectValid(player))
            {
                if (kind == 3) HVD_BossStart(player);
                else HVD_Trap(trigger, kind);
            }
        }
        trigger = next;
    }
}
