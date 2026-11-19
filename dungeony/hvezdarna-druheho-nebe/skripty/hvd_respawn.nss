#include "hvd_core"

void main()
{
    object player = GetLastRespawnButtonPresser();
    if (!GetIsPC(player)) return;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectResurrection(), player);
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(GetMaxHitPoints(player)), player);
    HVD_Jump(player, "hvd_start");
}
