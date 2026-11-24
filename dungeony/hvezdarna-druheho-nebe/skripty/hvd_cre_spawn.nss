#include "hvd_combat"

void main()
{
    int role = GetLocalInt(OBJECT_SELF, "role");
    if (role == 7)
    {
        SetImmortal(OBJECT_SELF, TRUE);
        SetObjectVisualTransform(OBJECT_SELF, OBJECT_VISUAL_TRANSFORM_SCALE, 1.09);
        return;
    }
    if (role >= 1 && role <= 4)
        ApplyEffectToObject(DURATION_TYPE_PERMANENT, TagEffect(ExtraordinaryEffect(EffectHaste()), "hvd_haste"),
                            OBJECT_SELF);
    if (role >= 1 && role <= 3)
        ApplyEffectToObject(DURATION_TYPE_PERMANENT,
            TagEffect(ExtraordinaryEffect(EffectSeeInvisible()), "hvd_see_invisible"), OBJECT_SELF);
    if (role == 1 || role == 2)
    {
        int strength = GetAbilityModifier(ABILITY_STRENGTH, OBJECT_SELF);
        if (strength > 0)
        {
            int bonus = strength < 6 ? strength : DAMAGE_BONUS_6 + strength - 6;
            if (bonus > DAMAGE_BONUS_20) bonus = DAMAGE_BONUS_20;
            effect damage = EffectDamageIncrease(bonus, DAMAGE_TYPE_BASE_WEAPON);
            ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(damage), OBJECT_SELF);
        }
    }
    if (GetLocalInt(OBJECT_SELF, "elite") && role != 1)
        SetObjectVisualTransform(OBJECT_SELF, OBJECT_VISUAL_TRANSFORM_SCALE, 1.15);
    if (role == 2)
        ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(EffectVisualEffect(VFX_DUR_AURA_COLD)), OBJECT_SELF);
    if (role == 3 || role == 6)
        ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(EffectVisualEffect(VFX_DUR_AURA_CYAN)), OBJECT_SELF);
    if (role == 2 || role == 3) DelayCommand(1.0, HVD_PulseAura(OBJECT_SELF));
}
