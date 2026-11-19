void main()
{
    object player = GetLastPlayerDied();
    if (GetIsPC(player))
        PopUpDeathGUIPanel(player, TRUE, TRUE, 0, "Návrat do horského noclehu. Postup výpravy je uložený.");
}
