#include "zks_core"

void main()
{
    object player = GetEnteringObject();
    if (!ZKS_Player(player)) return;
    SendMessageToPC(player, "Zkušebna dobrodruhů. U kroniky nebo mistryně nastavíš XP a přesvědčení. " +
        "Zbrojnice je na západě, bestiář a kolbiště na východě.");
}
