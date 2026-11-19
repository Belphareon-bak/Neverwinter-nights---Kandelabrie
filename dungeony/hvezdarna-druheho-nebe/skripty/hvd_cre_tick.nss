#include "hvd_final"

void main()
{
    if (GetLocalInt(OBJECT_SELF, "role") == 7) HVD_BossThink(OBJECT_SELF);
    else HVD_MobThink(OBJECT_SELF);
}
