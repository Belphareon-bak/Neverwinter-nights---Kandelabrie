#include "hvd_core"

int StartingConditional()
{
    return HVD_GuardState() == HVD_GUARD_IDLE;
}
