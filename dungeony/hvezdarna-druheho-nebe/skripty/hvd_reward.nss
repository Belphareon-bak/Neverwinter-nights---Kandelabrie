#include "hvd_core"

void main()
{
    if (GetInventoryDisturbType() != INVENTORY_DISTURB_TYPE_REMOVED) return;
    object item = GetInventoryDisturbItem();
    string resource = GetResRef(item);
    if ((resource != "hvd_cloak" && resource != "hvd_badge") ||
        GetLocalString(item, "hvd_stock_from") != GetTag(OBJECT_SELF)) return;
    object player = GetLastDisturbed();
    if (!HVD_IsPlayer(player)) return;
    if (!GetLocalInt(HVD_Module(), "hvd_won") || GetLocalInt(player, "hvd_final_reward") == HVD_Run())
    {
        object returned = CopyItem(item, OBJECT_SELF, TRUE);
        if (GetItemPossessor(returned) == OBJECT_SELF)
        {
            DestroyObject(item);
            SendMessageToPC(player, "Z poslední služby patří každému jeden plášť nebo jedna spona.");
        }
        return;
    }
    SetLocalInt(player, "hvd_final_reward", HVD_Run());
    DeleteLocalString(item, "hvd_stock_from");
    GiveXPToCreature(player, 500);
}
