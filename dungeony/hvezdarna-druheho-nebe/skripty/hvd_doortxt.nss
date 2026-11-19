void main()
{
    object player = GetClickingObject();
    if (GetIsPC(player))
        SendMessageToPC(player, "U patic slož tři pečetě a potvrď sestavu kamennou pákou.");
}
