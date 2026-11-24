#include "hvd_core"

void main()
{
    object player = GetClickingObject();
    if (!GetIsPC(player)) player = GetLastUsedBy();
    if (GetIsPC(player) && GetTag(OBJECT_SELF) == "hvd_repairdoor")
        HVD_RepairDoorHint(player);
    else if (GetIsPC(player))
        SendMessageToPC(player, "U patic slož tři pečetě a potvrď sestavu kamennou pákou.");
}
