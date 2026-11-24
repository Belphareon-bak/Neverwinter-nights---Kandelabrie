#include "hvd_core"

void main()
{
    if (GetInventoryDisturbType() != INVENTORY_DISTURB_TYPE_REMOVED) return;
    object item = GetInventoryDisturbItem();
    if (GetLocalString(item, "hvd_stock_from") != GetTag(OBJECT_SELF)) return;
    object player = GetLastDisturbed();
    if (!HVD_IsPlayer(player)) return;
    int current = GetLocalInt(item, "hvd_run") == HVD_Run();
    if (!current || !GetLocalInt(HVD_Module(), "hvd_won") || GetLocalInt(player, "hvd_final_reward") == HVD_Run())
    {
        if (current) CopyItem(item, OBJECT_SELF, TRUE);
        DestroyObject(item);
        SendMessageToPC(player, "Za opravu si každý může vzít jeden předmět ze všech schránek dohromady.");
        return;
    }
    SetLocalInt(player, "hvd_final_reward", HVD_Run());
    DeleteLocalString(item, "hvd_stock_from");
    GiveXPToCreature(player, 500);
}
