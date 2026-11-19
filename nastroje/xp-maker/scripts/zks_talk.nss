#include "zks_ui"

void main()
{
    object player = GetLastSpeaker();
    if (ZKS_In(player, "zks_hall")) ZKS_Open(player, 1);
}
