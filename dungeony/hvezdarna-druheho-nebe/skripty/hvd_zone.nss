#include "hvd_final"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    int kind = GetLocalInt(OBJECT_SELF, "hazard");
    if (kind == 3) HVD_BossStart(player);
    else HVD_Trap(OBJECT_SELF, kind);
}
