#include "hvd_core"

void main()
{
    object player = GetEnteringObject();
    if (!HVD_IsPlayer(player)) return;
    if (!HVD_Run()) HVD_NewRun();
    HVD_ClearTokens(player);
    SendMessageToPC(player, "Hvězdárna druhého nebe. Nocleh má rozpis výpravy, zásoby a ohniště k odpočinku.");
    if (GetHitDice(player) < 35)
        SendMessageToPC(player, "Obsah je určen pro úrovně 35–40. V nabídce postav je připraven Radan Hvězdář (38).");
    HVD_ActivateArea(GetArea(player));
}
