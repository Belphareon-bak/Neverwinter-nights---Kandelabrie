#include "hvd_core"

void RespawnWhenEmpty(object area, int visit, int run)
{
    if (HVD_Run() != run || GetLocalInt(area, "hvd_visit") != visit || HVD_AreaCount(area)) return;
    if (GetTag(area) == "hvd_top")
    {
        if (!GetLocalInt(HVD_Module(), "hvd_won")) HVD_ResetBoss();
        return;
    }
    HVD_ResetEncounters(area);
}

void main()
{
    object player = GetExitingObject();
    if (!GetIsPC(player)) return;
    if (HVD_WindyArea(OBJECT_SELF)) HVD_RemoveUpperWind(player);
    float delay = 450.0;
    if (GetTag(OBJECT_SELF) == "hvd_top") delay = 1.0;
    DelayCommand(delay, RespawnWhenEmpty(OBJECT_SELF, GetLocalInt(OBJECT_SELF, "hvd_visit"), HVD_Run()));
}
