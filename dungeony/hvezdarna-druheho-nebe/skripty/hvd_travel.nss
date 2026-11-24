#include "hvd_core"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    HVD_Travel(player, OBJECT_SELF);
}
