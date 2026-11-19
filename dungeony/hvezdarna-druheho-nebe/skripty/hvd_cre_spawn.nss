void main()
{
    int role = GetLocalInt(OBJECT_SELF, "role");
    if (role == 7)
    {
        SetImmortal(OBJECT_SELF, TRUE);
        SetObjectVisualTransform(OBJECT_SELF, OBJECT_VISUAL_TRANSFORM_SCALE, 1.22);
        return;
    }
    if (role == 3 || role == 6)
        ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(EffectVisualEffect(VFX_DUR_AURA_CYAN)), OBJECT_SELF);
}
