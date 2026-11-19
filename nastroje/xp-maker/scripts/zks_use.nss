#include "zks_ui"

void main()
{
    object player = GetLastUsedBy();
    if (!ZKS_Player(player)) return;
    string op = GetLocalString(OBJECT_SELF, "action");
    if (op == "character") ZKS_Open(player, 1);
    if (op == "gear")
    {
        int group = GetLocalInt(OBJECT_SELF, "group");
        if (group == 5) ZKS_Open(player, 4);
        else ZKS_Open(player, 2, group);
    }
    if (op == "bestiary") ZKS_Open(player, 3);
    if (op == "rest") ZKS_Rest(player);
    if (op == "read") SendMessageToPC(player, GetDescription(OBJECT_SELF));
    if (op == "pass") ZKS_Jump(player, GetLocalString(OBJECT_SELF, "target"));
}
