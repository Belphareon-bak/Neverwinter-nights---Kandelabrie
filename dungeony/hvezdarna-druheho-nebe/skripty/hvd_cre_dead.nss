#include "hvd_final"

void main()
{
    object area = GetArea(OBJECT_SELF);
    int role = GetLocalInt(OBJECT_SELF, "role");
    if (role == 7 || role == 8) AssignCommand(area, DelayCommand(0.3, HVD_GuardVictory(area)));
    if (GetLocalString(OBJECT_SELF, "hvd_group") == "bourna") HVD_RefreshStormMusic(area);
    int seal = GetLocalInt(OBJECT_SELF, "hvd_seal");
    if (seal)
    {
        SetLocalInt(HVD_Module(), "hvd_ready" + IntToString(seal), TRUE);
        HVD_AreaMessage(area, "Strážce padl. Nyní lze vyzvednout pečeť " + HVD_Sign(seal) + ".");
    }
    if (ResManGetAliasFor("pwfxp", RESTYPE_NCS) != "")
    {
        ExecuteScript("pwfxp", OBJECT_SELF);
        return;
    }

    int xp = 125;
    if (GetLocalInt(OBJECT_SELF, "hvd_elite")) xp = 275;
    else if (HVD_WindyArea(area)) xp = 185;
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, area) && GetDistanceBetween(player, OBJECT_SELF) < 36.0)
            GiveXPToCreature(player, xp);
        player = GetNextPC();
    }
}
