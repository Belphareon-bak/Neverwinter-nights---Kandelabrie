#include "hvd_core"

int StartingConditional()
{
    object module = HVD_Module();
    return HVD_GuardState() == HVD_GUARD_REPAIR && GetLocalInt(module, "hvd_repair_done") &&
           !GetLocalInt(module, "hvd_won");
}
