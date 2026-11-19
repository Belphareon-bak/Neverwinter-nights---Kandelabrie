#include "hvd_core"

void main()
{
    int slot = GetLocalInt(OBJECT_SELF,"slot");
    if (slot < 1 || slot > 4) return;
    int contents = HVD_SocketContents(slot);
    object player = GetLastDisturbed();
    if (HVD_IsPlayer(player) && GetInventoryDisturbType() == INVENTORY_DISTURB_TYPE_ADDED)
    {
        if (contents < 0)
            SendMessageToPC(player,"V patici jsou dvě raznice. Vyjmi jednu, aby dosedla ta druhá.");
        else if (!HVD_SealSign(GetInventoryDisturbItem()))
            SendMessageToPC(player,"Převod snímá pouze platnou pečeť nebeské hlídky z této výpravy.");
        else
            SendMessageToPC(player,"Do mosazné objímky dosedla pečeť se znakem " + HVD_Sign(contents) + ".");
    }
    HVD_ShowSeal(slot);
}
