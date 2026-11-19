#include "hvd_core"

void main()
{
    object player = GetModuleItemAcquiredBy();
    object item = GetModuleItemAcquired();
    if (!HVD_IsPlayer(player) || GetObjectType(item) != OBJECT_TYPE_ITEM) return;
    string resource = GetResRef(item);
    if (GetStringLeft(resource, 9) != "hvd_book_") return;
    if (GetLocalInt(item, "hvd_run") != HVD_Run())
    {
        DestroyObject(item);
        SendMessageToPC(player, "Tenhle zápis je ze starší výpravy. Vyhledej aktuální svazek.");
        return;
    }
    int clue = GetLocalInt(item, "hvd_clue");
    if (clue) SetLocalInt(HVD_Module(), "hvd_clue" + IntToString(clue), TRUE);
    if (resource == "hvd_book_return" || resource == "hvd_book_optic")
        SetLocalInt(HVD_Module(), "hvd_notes", TRUE);
}
