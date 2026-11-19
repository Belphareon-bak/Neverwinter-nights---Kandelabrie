#include "hvd_core"

void main()
{
    object area = GetArea(OBJECT_SELF);
    int seal = GetLocalInt(OBJECT_SELF, "hvd_seal");
    if (seal)
    {
        SetLocalInt(HVD_Module(), "hvd_ready" + IntToString(seal), TRUE);
        HVD_AreaMessage(area, "Stanoviště je volné. Nyní lze vyzvednout pečeť " + HVD_Sign(seal) + ".");
    }
    int xp = 125;
    if (GetLocalInt(OBJECT_SELF, "hvd_elite")) xp = 275;
    else if (GetTag(area) == "hvd_steps" || GetTag(area) == "hvd_walks") xp = 185;
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, area) && GetDistanceBetween(player, OBJECT_SELF) < 36.0)
            GiveXPToCreature(player, xp);
        player = GetNextPC();
    }
}
