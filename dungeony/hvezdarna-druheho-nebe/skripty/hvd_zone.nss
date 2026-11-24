#include "hvd_final"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    string group = GetLocalString(OBJECT_SELF, "encounter");
    if (group != "")
    {
        if (HVD_InBox(OBJECT_SELF, player)) HVD_ActivateEncounter(GetArea(OBJECT_SELF), group, player);
        return;
    }
    string secret = GetLocalString(OBJECT_SELF, "secret");
    if (secret != "")
    {
        HVD_InspectSecret(player, secret);
        return;
    }
    int kind = GetLocalInt(OBJECT_SELF, "hazard");
    if (kind == 3) HVD_GuardGreet(player);
    else HVD_Trap(OBJECT_SELF, kind);
}
