#include "zks_core"

void ReturnAlive(object player)
{
    if (!GetIsObjectValid(player)) return;
    AssignCommand(player, ClearAllActions());
    effect resurrection = EffectResurrection();
    ApplyEffectToObject(DURATION_TYPE_INSTANT, resurrection, player);
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(GetMaxHitPoints(player)), player);
    if (GetTag(GetArea(player)) == "zks_arena") ZKS_Jump(player, "zks_arena_in");
    else ZKS_Jump(player, "zks_start");
    SendMessageToPC(player, "Zkouška skončila. Jsi zpět v bezpečí s plným zdravím.");
}

void main()
{
    object player = GetLastPlayerDied();
    if (ZKS_Player(player)) DelayCommand(0.8, ReturnAlive(player));
}
