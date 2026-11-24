#include "hvd_final"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    HVD_UpdateUpperWind(player, OBJECT_SELF);
    int visit = GetLocalInt(OBJECT_SELF, "hvd_visit");
    SetLocalInt(OBJECT_SELF, "hvd_visit", visit + 1);
    if (GetTag(OBJECT_SELF) == "hvd_top") HVD_EnsureGuardian();
}
