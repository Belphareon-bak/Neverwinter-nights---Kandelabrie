#include "hvd_core"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    if (!HVD_Run()) HVD_NewRun();
    HVD_ClearTokens(player);
    HVD_RepairJournal(player);
    HVD_UpdateUpperWind(player, GetArea(player));
    SendMessageToPC(player, "Hvězdárna druhého nebe. Nocleh má rozpis výpravy, zásoby a ohniště k odpočinku.");
    if (GetHitDice(player) < 34)
        SendMessageToPC(player, "Obsah je určen pro úrovně 34–40. V nabídce postav je připraven Radan Hvězdář (38).");
}
