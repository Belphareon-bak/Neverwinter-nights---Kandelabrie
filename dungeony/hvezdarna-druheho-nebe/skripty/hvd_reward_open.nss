#include "hvd_core"

void main()
{
    if (!GetLocalInt(HVD_Module(), "hvd_won")) return;
    HVD_FillRewardChest(OBJECT_SELF);
}
