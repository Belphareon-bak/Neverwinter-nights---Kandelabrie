#include "zks_data"

int ZKS_Player(object player)
{
    return GetIsPC(player) && !GetIsDM(player);
}

int ZKS_In(object player, string tag)
{
    return ZKS_Player(player) && GetTag(GetArea(player)) == tag;
}

void ZKS_Jump(object player, string destination)
{
    object marker = GetWaypointByTag(destination);
    if (!GetIsObjectValid(marker)) return;
    int token = NuiFindWindow(player, "zksPanel");
    if (token) NuiDestroy(player, token);
    AssignCommand(player, ClearAllActions());
    AssignCommand(player, ActionJumpToLocation(GetLocation(marker)));
}

void ZKS_Rest(object player)
{
    if (GetIsDead(player) || GetIsInCombat(player))
    {
        SendMessageToPC(player, "Odpočinout si můžeš mimo boj.");
        return;
    }
    ForceRest(player);
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(GetMaxHitPoints(player)), player);
    SendMessageToPC(player, "Životy a schopnosti pro další zkoušku jsou obnovené.");
}

int ZKS_LevelXP(int level)
{
    if (level < 2) return 0;
    return 500 * level * (level - 1);
}

void ZKS_SetLevel(object player, int level)
{
    if (!ZKS_In(player, "zks_hall") || GetIsDead(player) || level < 0 || level > 40) return;
    int before = GetHitDice(player);
    int xp = ZKS_LevelXP(level);
    SetXP(player, xp);
    if (GetXP(player) != xp)
    {
        SendMessageToPC(player, "Hra změnu XP nepřijala. Ukonči boj nebo přeměnu a zkus to znovu.");
        return;
    }
    if (level > before)
        SendMessageToPC(player, "Nastaveno " + IntToString(xp) + " XP. Dokonči zvýšení úrovně v okně postavy.");
    else SendMessageToPC(player, "Nastaveno " + IntToString(xp) + " XP. Úroveň " + IntToString(GetHitDice(player)) + ".");
}

void ZKS_AdjustAxis(object player, int target, int lawAxis)
{
    int attempt;
    int positive = ALIGNMENT_GOOD;
    int negative = ALIGNMENT_EVIL;
    if (lawAxis) { positive = ALIGNMENT_LAWFUL; negative = ALIGNMENT_CHAOTIC; }
    // The engine attenuates changes near an extreme. Re-read its value after each shift.
    for (attempt = 0; attempt < 8; ++attempt)
    {
        int current = GetGoodEvilValue(player);
        if (lawAxis) current = GetLawChaosValue(player);
        if (current == target) return;
        if (target > current) AdjustAlignment(player, positive, target - current, FALSE);
        else AdjustAlignment(player, negative, current - target, FALSE);
    }
}

void ZKS_Alignment(object player, int align)
{
    if (!ZKS_In(player, "zks_hall") || align < 0 || align > 8) return;
    int order = 100 - (align / 3) * 50;
    int moral = 100 - (align % 3) * 50;
    ZKS_AdjustAxis(player, order, TRUE);
    ZKS_AdjustAxis(player, moral, FALSE);
}

object ZKS_Receive(object player, string key, int quantity = 1)
{
    if (!ZKS_In(player, "zks_armory") || GetIsDead(player)) return OBJECT_INVALID;
    object item = CreateItemOnObject(key, player, quantity);
    if (!GetIsObjectValid(item) || GetItemPossessor(item) != player)
    {
        if (GetIsObjectValid(item)) DestroyObject(item);
        SendMessageToPC(player, "Uvolni místo v inventáři a zkus výdej znovu.");
        return OBJECT_INVALID;
    }
    return item;
}

int ZKS_Element(int choice)
{
    if (choice == 1) return IP_CONST_DAMAGETYPE_FIRE;
    if (choice == 2) return IP_CONST_DAMAGETYPE_COLD;
    if (choice == 3) return IP_CONST_DAMAGETYPE_ELECTRICAL;
    if (choice == 4) return IP_CONST_DAMAGETYPE_ACID;
    return IP_CONST_DAMAGETYPE_SONIC;
}

string ZKS_EffectName(int choice)
{
    if (choice == 1) return "Oheň";
    if (choice == 2) return "Chlad";
    if (choice == 3) return "Elektřina";
    if (choice == 4) return "Kyselina";
    if (choice == 5) return "Zvuk";
    if (choice == 6) return "Regenerace";
    if (choice == 7) return "Záchranné hody";
    if (choice == 8) return "Zámky a pasti";
    if (choice == 9) return "Síla střelby";
    return "Bez dalšího efektu";
}

void ZKS_Property(object item, itemproperty property)
{
    AddItemProperty(DURATION_TYPE_PERMANENT, property, item);
}

object ZKS_Equipment(object player, int index, int quality, int extra)
{
    json catalog = ZKS_GearCatalog();
    if (index < 0 || index >= JsonGetLength(catalog) || quality < 1 || quality > 5 || extra < 0 || extra > 9)
        return OBJECT_INVALID;
    json row = JsonArrayGet(catalog, index);
    int kind = JsonGetInt(JsonArrayGet(row, 2));
    int quantity = JsonGetInt(JsonArrayGet(row, 4));
    object item = ZKS_Receive(player, JsonGetString(JsonArrayGet(row, 0)), quantity);
    if (!GetIsObjectValid(item)) return OBJECT_INVALID;
    if (kind == 1) ZKS_Property(item, ItemPropertyEnhancementBonus(quality));
    if (kind == 2 || kind == 4) ZKS_Property(item, ItemPropertyAttackBonus(quality));
    if (kind == 3) ZKS_Property(item, ItemPropertyACBonus(quality));
    if (kind == 5 || kind == 4)
    {
        int physical = IP_CONST_DAMAGETYPE_BLUDGEONING;
        if (kind == 5 && GetBaseItemType(item) != BASE_ITEM_BULLET) physical = IP_CONST_DAMAGETYPE_PIERCING;
        ZKS_Property(item, ItemPropertyDamageBonus(physical, quality));
    }
    if (extra >= 1 && extra <= 5)
    {
        int element = ZKS_Element(extra);
        if (kind == 3) ZKS_Property(item, ItemPropertyDamageResistance(element, quality));
        else if (kind != 2)
        {
            int dice = 5 + quality;
            if (quality == 5) dice = IP_CONST_DAMAGEBONUS_1d12;
            ZKS_Property(item, ItemPropertyDamageBonus(element, dice));
        }
    }
    if (kind == 2 && extra == 9 && (GetBaseItemType(item) == BASE_ITEM_LONGBOW ||
        GetBaseItemType(item) == BASE_ITEM_SHORTBOW || GetBaseItemType(item) == BASE_ITEM_SLING))
        ZKS_Property(item, ItemPropertyMaxRangeStrengthMod(quality));
    if (kind == 3 && extra == 6) ZKS_Property(item, ItemPropertyRegeneration(quality));
    if (kind == 3 && extra == 7)
    {
        int save;
        for (save = 1; save <= 3; ++save) ZKS_Property(item, ItemPropertyBonusSavingThrow(save, quality));
    }
    if (kind == 3 && extra == 8)
    {
        ZKS_Property(item, ItemPropertySkillBonus(SKILL_OPEN_LOCK, 2 * quality));
        ZKS_Property(item, ItemPropertySkillBonus(SKILL_DISABLE_TRAP, 2 * quality));
    }
    string name = JsonGetString(JsonArrayGet(row, 3)) + " +" + IntToString(quality);
    if (extra) name += " · " + ZKS_EffectName(extra);
    SetName(item, name);
    return item;
}

string ZKS_Ability(int ability)
{
    if (ability == 0) return "Síla";
    if (ability == 1) return "Obratnost";
    if (ability == 2) return "Odolnost";
    if (ability == 3) return "Inteligence";
    if (ability == 4) return "Moudrost";
    if (ability == 5) return "Charisma";
    return "Všechny atributy";
}

object ZKS_Jewel(object player, int type, int ability, int bonus)
{
    if (type < 0 || type > 1 || ability < 0 || ability > 6 || (bonus != 5 && bonus != 12)) return OBJECT_INVALID;
    string key = "zks_ring";
    string title = "Prsten";
    if (type == 1)
    {
        key = "zks_amulet";
        title = "Amulet";
    }
    object jewel = ZKS_Receive(player, key);
    if (!GetIsObjectValid(jewel)) return OBJECT_INVALID;
    int stat;
    for (stat = 0; stat < 6; ++stat)
    {
        if (ability == 6 || ability == stat) ZKS_Property(jewel, ItemPropertyAbilityBonus(stat, bonus));
    }
    SetName(jewel, title + " · " + ZKS_Ability(ability) + " +" + IntToString(bonus));
    return jewel;
}

object ZKS_Focus(object player, int caster, int tier)
{
    if (tier < 1 || tier > 5 || (caster != 1 && caster != 2 && caster != 3 && caster != 6 &&
        caster != 7 && caster != 9 && caster != 10)) return OBJECT_INVALID;
    if (tier == 5 && (caster == 6 || caster == 7)) return OBJECT_INVALID;
    object focus = ZKS_Receive(player, "zks_focus");
    if (!GetIsObjectValid(focus)) return OBJECT_INVALID;
    ZKS_Property(focus, ItemPropertyBonusLevelSpell(caster, tier));
    SetName(focus, "Ohnisko kouzel · kruh " + IntToString(tier));
    return focus;
}

string ZKS_SlotKey(int index)
{
    return "zks_spawn_" + IntToString(index);
}

int ZKS_Alive(object creature)
{
    return GetIsObjectValid(creature) && !GetIsDead(creature) && GetLocalInt(creature, "zks_monster");
}

int ZKS_Count(object area)
{
    int count;
    int slot;
    for (slot = 1; slot <= 12; ++slot)
    {
        if (ZKS_Alive(GetLocalObject(area, ZKS_SlotKey(slot)))) ++count;
    }
    return count;
}

int ZKS_Spawn(object player, int monster, int quantity)
{
    if (!ZKS_In(player, "zks_arena") || GetIsDead(player) || quantity < 1 || quantity > 8) return 0;
    json catalog = ZKS_Bestiary();
    if (monster < 0 || monster >= JsonGetLength(catalog)) return 0;
    string key = JsonGetString(JsonArrayGet(JsonArrayGet(catalog, monster), 0));
    object area = GetArea(player);
    int made;
    int slot;
    for (slot = 1; slot <= 12 && made < quantity; ++slot)
    {
        string marker = ZKS_SlotKey(slot);
        object previous = GetLocalObject(area, marker);
        if (ZKS_Alive(previous)) continue;
        if (GetIsObjectValid(previous)) DestroyObject(previous);
        object spot = GetWaypointByTag(marker);
        if (!GetIsObjectValid(spot)) continue;
        object foe = CreateObject(OBJECT_TYPE_CREATURE, key, GetLocation(spot));
        if (!GetIsObjectValid(foe)) continue;
        SetLocalObject(area, marker, foe);
        ++made;
    }
    return made;
}

void ZKS_Clear(object area)
{
    if (GetTag(area) != "zks_arena") return;
    object creature = GetFirstObjectInArea(area, OBJECT_TYPE_CREATURE);
    while (GetIsObjectValid(creature))
    {
        object next = GetNextObjectInArea(area, OBJECT_TYPE_CREATURE);
        if (!GetIsPC(creature) && (GetLocalInt(creature, "zks_monster") ||
            GetLocalInt(GetMaster(creature), "zks_monster"))) DestroyObject(creature);
        creature = next;
    }
    int slot;
    for (slot = 1; slot <= 12; ++slot) DeleteLocalObject(area, ZKS_SlotKey(slot));
}
