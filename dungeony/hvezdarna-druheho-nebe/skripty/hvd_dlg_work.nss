#include "hvd_core"

int StartingConditional()
{
    return HVD_GuardState() == HVD_GUARD_REPAIR && !GetLocalInt(HVD_Module(), "hvd_repair_done");
}
