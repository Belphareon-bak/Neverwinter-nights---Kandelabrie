object HVD_Module()
{
    return GetModule();
}

int HVD_Run()
{
    return GetLocalInt(HVD_Module(), "hvd_run");
}

int HVD_IsPlayer(object player)
{
    return GetIsPC(player) && !GetIsDM(player) && !GetIsDead(player);
}

int HVD_PlayerIn(object player, object area)
{
    return HVD_IsPlayer(player) && GetArea(player) == area;
}

int HVD_AreaCount(object area)
{
    int count = 0;
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, area)) ++count;
        player = GetNextPC();
    }
    return count;
}

void HVD_AreaMessage(object area, string message)
{
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, area)) SendMessageToPC(player, message);
        player = GetNextPC();
    }
}

object HVD_NearPlayer(object source, float range, int farthest = FALSE)
{
    object best = OBJECT_INVALID;
    float bestDistance = range;
    if (farthest) bestDistance = -1.0;
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, GetArea(source)))
        {
            float distance = GetDistanceBetween(source, player);
            if (distance <= range && LineOfSightObject(source, player) &&
                ((farthest && distance > bestDistance) || (!farthest && distance <= bestDistance)))
            {
                bestDistance = distance;
                best = player;
            }
        }
        player = GetNextPC();
    }
    return best;
}

void HVD_Jump(object player, string marker)
{
    object point = GetWaypointByTag(marker);
    if (!GetIsObjectValid(point)) return;
    AssignCommand(player, ClearAllActions());
    AssignCommand(player, ActionJumpToLocation(GetLocation(point)));
}

void HVD_TurnOptics()
{
    object module = HVD_Module();
    int west = GetLocalInt(module, "hvd_dial1");
    int east = GetLocalInt(module, "hvd_dial2");
    object tube = GetObjectByTag("hvd_refractor");
    float heading = IntToFloat((west - 1) * 17 + (east - 2) * 9);
    SetObjectVisualTransform(tube, OBJECT_VISUAL_TRANSFORM_ROTATE_Z, heading,
                             OBJECT_VISUAL_TRANSFORM_LERP_SMOOTHSTEP, 0.6);
    SetObjectVisualTransform(GetObjectByTag("hvd_dial_w"), OBJECT_VISUAL_TRANSFORM_ROTATE_Z,
                             IntToFloat(west * 120), OBJECT_VISUAL_TRANSFORM_LERP_SMOOTHSTEP, 0.5);
    SetObjectVisualTransform(GetObjectByTag("hvd_dial_e"), OBJECT_VISUAL_TRANSFORM_ROTATE_Z,
                             IntToFloat(east * 120), OBJECT_VISUAL_TRANSFORM_LERP_SMOOTHSTEP, 0.5);
}

void HVD_Reveal(string marker)
{
    object point = GetWaypointByTag(marker);
    object module = HVD_Module();
    if (!GetIsObjectValid(point) || GetIsObjectValid(GetLocalObject(module, marker))) return;
    location entrance = GetLocation(point);
    ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_FNF_MYSTICAL_EXPLOSION, FALSE, 0.85),
                          entrance);
    object portal = CreateObject(OBJECT_TYPE_PLACEABLE, "hvd_gateway", entrance);
    if (GetIsObjectValid(portal)) SetLocalObject(module, marker, portal);
}

void HVD_Extinguish(string marker)
{
    object portal = GetLocalObject(HVD_Module(), marker);
    if (GetIsObjectValid(portal)) DestroyObject(portal);
    DeleteLocalObject(HVD_Module(), marker);
}

int HVD_Digit(int code, int slot)
{
    if (slot == 1) return code / 100;
    if (slot == 2) return (code / 10) % 10;
    return code % 10;
}

string HVD_Sign(int sign)
{
    if (sign == 1) return "Kotva";
    if (sign == 2) return "Křídlo";
    if (sign == 3) return "Kopí";
    if (sign == 4) return "Lucerna";
    return "prázdná";
}

int HVD_Order(int previous)
{
    int choice = Random(24 - (previous > 0));
    int first;
    int second;
    int third;
    for (first = 1; first <= 4; ++first)
    {
        for (second = 1; second <= 4; ++second)
        {
            if (first == second) continue;
            for (third = 1; third <= 4; ++third)
            {
                if (first == third || second == third) continue;
                int candidate = 100 * first + 10 * second + third;
                if (candidate == previous) continue;
                if (choice == 0) return candidate;
                --choice;
            }
        }
    }
    return 123;
}

string HVD_Clue(int kind)
{
    object module = HVD_Module();
    int solution = GetLocalInt(module, "hvd_order");
    if (kind == 1)
    {
        int absent = 10 - HVD_Digit(solution, 1) - HVD_Digit(solution, 2) - HVD_Digit(solution, 3);
        return "Pečeť mimo službu – " + HVD_Sign(absent) + ". Všechny ostatní stoupaly.";
    }
    int first = GetLocalInt(module, "hvd_pair") + 1;
    int lower = HVD_Digit(solution, first);
    int upper = HVD_Digit(solution, first + 1);
    if (kind == 2) return HVD_Sign(upper) + " patří bezprostředně nad pečeť " + HVD_Sign(lower) + ".";
    int anchor = HVD_Digit(solution, first + GetLocalInt(module, "hvd_anchor"));
    int other = HVD_Digit(solution, 5 - first * 2);
    string comparison = " výše než pečeť ";
    if (first == 2) comparison = " níže než pečeť ";
    return HVD_Sign(other) + " patří" + comparison + HVD_Sign(anchor) + ".";
}

string HVD_SealKey(int sign)
{
    return "hvd_seal" + IntToString(sign);
}

int HVD_ValidSeal(object item, int sign)
{
    return GetIsObjectValid(item) && sign >= 1 && sign <= 4 &&
        GetResRef(item) == HVD_SealKey(sign) && GetLocalInt(item, "hvd_run") == HVD_Run() &&
        GetLocalInt(item, "hvd_serial") == GetLocalInt(HVD_Module(), HVD_SealKey(sign));
}

void HVD_ClearTokens(object player)
{
    object item = GetFirstItemInInventory(player);
    while (GetIsObjectValid(item))
    {
        object next = GetNextItemInInventory(player);
        string resource = GetResRef(item);
        if (GetStringLeft(resource, 8) == "hvd_seal")
        {
            int sign = StringToInt(GetSubString(resource, 8, 1));
            if (!HVD_ValidSeal(item, sign)) DestroyObject(item);
        }
        if ((resource == "hvd_mirror" || resource == "hvd_workkey") &&
            GetLocalInt(item, "hvd_run") != HVD_Run()) DestroyObject(item);
        item = next;
    }
}

object HVD_HeldSeal(int sign)
{
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        object item = GetFirstItemInInventory(player);
        while (GetIsObjectValid(item))
        {
            if (HVD_ValidSeal(item, sign)) return item;
            item = GetNextItemInInventory(player);
        }
        player = GetNextPC();
    }
    return OBJECT_INVALID;
}

void HVD_Seal(object player, int sign)
{
    object module = HVD_Module();
    string key = HVD_SealKey(sign);
    if (sign > 1 && !GetLocalInt(module, "hvd_ready" + IntToString(sign)))
    {
        SendMessageToPC(player, "Pečeť ještě střeží její hlídka. Zpřístupní se po jejím poražení.");
        return;
    }
    if (GetIsObjectValid(HVD_HeldSeal(sign)))
    {
        SendMessageToPC(player, "Pečeť již drží někdo z výpravy.");
        return;
    }
    object item = CreateItemOnObject(key, player);
    if (!GetIsObjectValid(item) || GetItemPossessor(item) != player)
    {
        if (GetIsObjectValid(item)) DestroyObject(item);
        SendMessageToPC(player, "Uvolni místo v inventáři a vezmi pečeť znovu.");
        return;
    }
    int serial = GetLocalInt(module, key) + 1;
    SetLocalInt(module, key, serial);
    SetLocalInt(item, "hvd_serial", serial);
    SetLocalInt(item, "hvd_run", HVD_Run());
    SetLocalInt(module, "hvd_earned" + IntToString(sign), TRUE);
    SendMessageToPC(player, "Získána pečeť " + HVD_Sign(sign) + ".");
}

void HVD_Socket(object player, int slot, int sign)
{
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_gate_open")) return;
    if (slot < 1 || slot > 3 || (sign && !GetIsObjectValid(HVD_HeldSeal(sign)))) return;
    SetLocalInt(module, "hvd_slot" + IntToString(slot), sign);
    HVD_AreaMessage(GetArea(player), "Patice " + IntToString(slot) + " – " + HVD_Sign(sign) + ".");
    object marker = GetObjectByTag("hvd_socket_" + IntToString(slot));
    if (GetIsObjectValid(marker))
        ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_HOLY_AID), GetLocation(marker));
}

int HVD_SealInSocket(int sign)
{
    object module = HVD_Module();
    int slot;
    for (slot = 1; slot <= 3; ++slot)
    {
        if (GetLocalInt(module, "hvd_slot" + IntToString(slot)) == sign) return TRUE;
    }
    return FALSE;
}

void HVD_Cycle(object player, int slot)
{
    int current = GetLocalInt(HVD_Module(), "hvd_slot" + IntToString(slot));
    int offset;
    for (offset = 1; offset <= 5; ++offset)
    {
        int sign = (current + offset) % 5;
        if (!sign || (!HVD_SealInSocket(sign) && GetIsObjectValid(HVD_HeldSeal(sign))))
        {
            HVD_Socket(player, slot, sign);
            return;
        }
    }
}

void HVD_Recap(object player)
{
    object module = HVD_Module();
    int step;
    for (step = 1; step <= 3; ++step)
    {
        if (GetLocalInt(module, "hvd_clue" + IntToString(step)))
            SendMessageToPC(player, HVD_Clue(step));
        SendMessageToPC(player, "Patice " + IntToString(step) + " – " +
            HVD_Sign(GetLocalInt(module, "hvd_slot" + IntToString(step))) + ".");
    }
    for (step = 1; step <= 4; ++step)
    {
        if (GetLocalInt(module, "hvd_earned" + IntToString(step)) && !GetIsObjectValid(HVD_HeldSeal(step)))
            HVD_Seal(player, step);
    }
}

void HVD_DestroyMobs(object area)
{
    object thing = GetFirstObjectInArea(area);
    while (GetIsObjectValid(thing))
    {
        object next = GetNextObjectInArea(area);
        if (GetLocalInt(thing, "hvd_managed")) DestroyObject(thing);
        thing = next;
    }
}

object HVD_MobAt(string resource, object spot, int seal = 0, int elite = 0)
{
    if (!GetIsObjectValid(spot)) return OBJECT_INVALID;
    object mob = CreateObject(OBJECT_TYPE_CREATURE, resource, GetLocation(spot));
    if (GetIsObjectValid(mob))
    {
        SetLocalInt(mob, "hvd_managed", TRUE);
        SetLocalInt(mob, "hvd_seal", seal);
        SetLocalInt(mob, "hvd_elite", elite);
        SetLocalLocation(mob, "hvd_home", GetLocation(spot));
        if (HVD_AreaCount(GetArea(spot)) > 1)
        {
            int bonus = 35 * (HVD_AreaCount(GetArea(spot)) - 1);
            if (elite) bonus *= 2;
            ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(EffectTemporaryHitpoints(bonus)), mob);
        }
    }
    return mob;
}

void HVD_ActivateArea(object area)
{
    if (!GetIsObjectValid(area) || GetLocalInt(area, "hvd_armed")) return;
    SetLocalInt(area, "hvd_armed", TRUE);
    SetLocalInt(area, "hvd_wave", GetLocalInt(area, "hvd_wave") + 1);
    object spot = GetFirstObjectInArea(area);
    while (GetIsObjectValid(spot))
    {
        object next = GetNextObjectInArea(area);
        string spawn = GetLocalString(spot, "spawn");
        if (spawn != "")
            HVD_MobAt(spawn, spot, GetLocalInt(spot, "seal"), GetLocalInt(spot, "elite"));
        spot = next;
    }
}

void HVD_ResetBoss()
{
    object module = HVD_Module();
    object area = GetObjectByTag("hvd_top");
    HVD_DestroyMobs(area);
    DeleteLocalObject(module, "hvd_boss");
    DeleteLocalInt(module, "hvd_shutter");
    DeleteLocalInt(module, "hvd_mirror_used");
    DeleteLocalInt(area, "hvd_push");
    object lamp = GetObjectByTag("hvd_last_lamp");
    if (GetIsObjectValid(lamp)) SetPlaceableIllumination(lamp, TRUE);
}

void HVD_NewRun()
{
    object module = HVD_Module();
    int previous = GetCampaignInt("hvezdarna_nebe", "last_order");
    int order = HVD_Order(previous);
    int run = GetCampaignInt("hvezdarna_nebe", "last_run") + 1;
    SetCampaignInt("hvezdarna_nebe", "last_order", order);
    SetCampaignInt("hvezdarna_nebe", "last_run", run);
    SetLocalInt(module, "hvd_run", run);
    SetLocalInt(module, "hvd_order", order);
    SetLocalInt(module, "hvd_pair", Random(2));
    SetLocalInt(module, "hvd_anchor", Random(2));
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        HVD_ClearTokens(player);
        player = GetNextPC();
    }
    DeleteLocalInt(module, "hvd_won");
    DeleteLocalInt(module, "hvd_aligned");
    DeleteLocalInt(module, "hvd_dial1");
    DeleteLocalInt(module, "hvd_dial2");
    DeleteLocalInt(module, "hvd_gate_open");
    DeleteLocalInt(module, "hvd_shortcut");
    DeleteLocalInt(module, "hvd_work_link");
    DeleteLocalInt(module, "hvd_work_lock");
    DeleteLocalInt(module, "hvd_hall_off");
    DeleteLocalInt(module, "hvd_chest_off");
    DeleteLocalInt(module, "hvd_notes");
    DeleteLocalInt(module, "hvd_mirror_taken");
    DeleteLocalInt(module, "hvd_mounted");
    int index;
    for (index = 1; index <= 4; ++index)
    {
        string number = IntToString(index);
        DeleteLocalInt(module, "hvd_ready" + number);
        DeleteLocalInt(module, "hvd_earned" + number);
        DeleteLocalInt(module, "hvd_clue" + number);
        DeleteLocalInt(module, "hvd_slot" + number);
        DeleteLocalInt(module, HVD_SealKey(index));
    }
    HVD_Extinguish("hvd_optic_gate");
    HVD_Extinguish("hvd_final_gate");
    HVD_Extinguish("hvd_summit_exit");
    HVD_TurnOptics();
    HVD_ResetBoss();
    object area = GetFirstArea();
    while (GetIsObjectValid(area))
    {
        HVD_DestroyMobs(area);
        DeleteLocalInt(area, "hvd_armed");
        DeleteLocalInt(area, "hvd_empty");
        DeleteLocalInt(area, "hvd_push");
        if (HVD_AreaCount(area)) HVD_ActivateArea(area);
        area = GetNextArea();
    }
}
