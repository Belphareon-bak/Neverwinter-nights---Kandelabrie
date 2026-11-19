#include "hvd_core"

void main()
{
    if (!GetLocalInt(HVD_Module(), "hvd_won")) return;
    string resource = "hvd_badge";
    if (GetTag(OBJECT_SELF) == "hvd_cloak_reward") resource = "hvd_cloak";
    HVD_FillReward(OBJECT_SELF, resource, HVD_RewardCount());
}
