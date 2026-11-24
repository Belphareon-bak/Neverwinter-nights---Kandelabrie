#include "hvd_final"

void main()
{
    object player = GetLastSpeaker();
    if (HVD_GuardCanTalk(player)) BeginConversation(HVD_GuardDialogue(), player);
}
