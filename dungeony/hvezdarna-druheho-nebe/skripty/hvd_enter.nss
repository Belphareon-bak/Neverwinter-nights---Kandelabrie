#include "hvd_core"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    int visit = GetLocalInt(OBJECT_SELF, "hvd_visit");
    SetLocalInt(OBJECT_SELF, "hvd_visit", visit + 1);
    HVD_ActivateArea(OBJECT_SELF);
}
