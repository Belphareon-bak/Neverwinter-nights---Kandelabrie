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

void HVD_PlacePart(string part, string resource, string anchor, float heading)
{
    object mount = GetObjectByTag(anchor);
    if (!GetIsObjectValid(mount)) return;
    object module = HVD_Module();
    object previous = GetLocalObject(module, part);
    float facing = GetFacing(mount) + heading;
    if (facing < 0.0) facing += 360.0;
    if (facing >= 360.0) facing -= 360.0;
    if (GetIsObjectValid(previous) && GetResRef(previous) == resource &&
        fabs(GetFacing(previous) - facing) < 0.1) return;
    location position = Location(GetArea(mount), GetPosition(mount), facing);
    object replacement = CreateObject(OBJECT_TYPE_PLACEABLE, resource, position);
    if (!GetIsObjectValid(replacement)) return;
    if (GetIsObjectValid(previous)) DestroyObject(previous);
    SetLocalObject(module, part, replacement);
}

void HVD_TurnOptics()
{
    object module = HVD_Module();
    int west = GetLocalInt(module, "hvd_dial1");
    int east = GetLocalInt(module, "hvd_dial2");
    float heading = IntToFloat((west - 1) * 17 + (east - 2) * 9);
    HVD_PlacePart("hvd_tube", "hvd_tube", "hvd_refractor", heading);
    HVD_PlacePart("hvd_needle_w", "hvd_needle", "hvd_dial_w", IntToFloat(west * 120));
    HVD_PlacePart("hvd_needle_e", "hvd_needle", "hvd_dial_e", IntToFloat(east * 120));
}

void HVD_Reveal(string marker)
{
    object point = GetWaypointByTag(marker);
    object module = HVD_Module();
    if (!GetIsObjectValid(point) || GetIsObjectValid(GetLocalObject(module, marker))) return;
    location entrance = GetLocation(point);
    ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_FNF_MYSTICAL_EXPLOSION, FALSE, 0.85),
                          entrance);
    string resource = marker == "hvd_final_gate" ? "hvd_zenith" : "hvd_gateway";
    object portal = CreateObject(OBJECT_TYPE_PLACEABLE, resource, entrance);
    if (GetIsObjectValid(portal)) SetLocalObject(module, marker, portal);
}

void HVD_Extinguish(string marker)
{
    object portal = GetLocalObject(HVD_Module(), marker);
    if (GetIsObjectValid(portal)) DestroyObject(portal);
    DeleteLocalObject(HVD_Module(), marker);
}

void HVD_ResetHidden()
{
    object module = HVD_Module();
    DeleteLocalInt(module,"hvd_study_open");
    DeleteLocalInt(module,"hvd_study_link");
    DeleteLocalInt(module,"hvd_eave_open");
    DeleteLocalInt(module,"hvd_eave_safe");
    HVD_PlacePart("hvd_study_cover","hvd_bookpanel","hvd_study_secret",0.0);
    HVD_PlacePart("hvd_comm_cover","hvd_stonepanel","hvd_comm_secret",0.0);
    HVD_PlacePart("hvd_dome_cover","hvd_stonepanel","hvd_dome_secret",0.0);
    HVD_PlacePart("hvd_eave_cover","hvd_stonepanel","hvd_eave_secret",0.0);
    HVD_PlacePart("hvd_eavetop_cover","hvd_stonepanel","hvd_eavetop_door",0.0);
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

int HVD_LensOrder()
{
    int west = Random(3) + 1;
    int center = Random(2) + 1;
    if (center >= west) ++center;
    return west * 100 + center * 10 + (6 - west - center);
}

int HVD_ShutterSign(int order)
{
    return 10 - HVD_Digit(order, 1) - HVD_Digit(order, 2) - HVD_Digit(order, 3);
}

string HVD_FilterName(int index)
{
    if (index == 1) return "Srpek";
    if (index == 2) return "Hvězda";
    return "Slunce";
}

string HVD_Clue(int kind)
{
    object module = HVD_Module();
    int signs = GetLocalInt(module, "hvd_order");
    int filters = GetLocalInt(module, "hvd_lens_order");
    int west = HVD_Digit(signs, 1);
    int shutter = HVD_ShutterSign(signs);
    if (kind == 1)
    {
        int low = west;
        int high = shutter;
        if (low > high)
        {
            low = shutter;
            high = west;
        }
        return "Z dvojice " + HVD_Sign(low) + " a " + HVD_Sign(high) +
            " šla jedna raznice do závory a druhá do jednoho z krajních sloupů. "
            + "Pečeť se znakem " + HVD_Sign(shutter) + " nesmí pod clonu se znakem " +
            HVD_FilterName(HVD_Digit(filters,1)) + ". Při poslední zkoušce by jí začalo měknout plnivo.";
    }
    string center = HVD_Sign(HVD_Digit(signs, 2));
    if (kind == 2)
        return "Vedle sebe svítily značky " + center + " a " + HVD_Sign(HVD_Digit(signs, 3)) +
            ". Značka " + center + " byla západněji a nad její raznicí svítila clona se znakem " +
            HVD_FilterName(HVD_Digit(filters, 2)) + ".";
    string outer = HVD_FilterName(HVD_Digit(filters, 1));
    return "Na skle se znakem " + outer + " zůstal otisk jedné ze dvou raznic uvedených v rozpisu z noclehu. "
        + "Tenhle filtr byl západněji než sklo se znakem " + HVD_FilterName(HVD_Digit(filters, 3)) + ".";
}

string HVD_TestGuide()
{
    object module = HVD_Module();
    int order = GetLocalInt(module, "hvd_order");
    int filters = GetLocalInt(module, "hvd_lens_order");
    return "ZKUŠEBNÍ LIST · Výprava " + IntToString(HVD_Run()) + "\n\n"
        + "Vezmi Kotvu v dílnách, Křídlo na schodech a Kopí s Lucernou na ochozech. "
        + "Otevři každý sloup a přesuň do něj příslušnou pečeť z inventáře. "
        + "Páčkou na boku sloupu nastav symbol, který má svítit na čelním skle.\n\n"
        + "Západní sloup: " + HVD_Sign(HVD_Digit(order,1)) + " · " + HVD_FilterName(HVD_Digit(filters,1)) + "\n"
        + "Střední sloup: " + HVD_Sign(HVD_Digit(order,2)) + " · " + HVD_FilterName(HVD_Digit(filters,2)) + "\n"
        + "Východní sloup: " + HVD_Sign(HVD_Digit(order,3)) + " · " + HVD_FilterName(HVD_Digit(filters,3)) + "\n"
        + "Závora u spouště: " + HVD_Sign(HVD_ShutterSign(order)) + "\n\n"
        + "Zatáhni za Spoušť tří paprsků a počkej, až se na schodišti spojí světlo. "
        + "Potom vystup do zjevené brány. Po nové výpravě otevři pouzdro pro nový list.";
}

string HVD_SealKey(int sign)
{
    return "hvd_seal" + IntToString(sign);
}

void HVD_PlaceBooks()
{
    int index = 0;
    object spot = GetObjectByTag("hvd_find", index);
    while (GetIsObjectValid(spot))
    {
        string resource = GetLocalString(spot, "find");
        object previous = GetLocalObject(HVD_Module(), resource);
        if (GetIsObjectValid(previous)) DestroyObject(previous);
        object book = CreateObject(OBJECT_TYPE_ITEM, resource, GetLocation(spot));
        if (GetIsObjectValid(book))
        {
            SetLocalObject(HVD_Module(), resource, book);
            SetLocalInt(book, "hvd_run", HVD_Run());
            int clue = GetLocalInt(spot, "clue");
            if (clue)
            {
                SetLocalInt(book, "hvd_clue", clue);
                SetDescription(book, GetDescription(book) + "\n\nZápis z poslední služby\n" + HVD_Clue(clue));
            }
        }
        spot = GetObjectByTag("hvd_find", ++index);
    }
}

int HVD_ValidSeal(object item, int sign)
{
    return GetIsObjectValid(item) && sign >= 1 && sign <= 4 &&
        GetResRef(item) == HVD_SealKey(sign) && GetLocalInt(item, "hvd_run") == HVD_Run() &&
        GetLocalInt(item, "hvd_serial") == GetLocalInt(HVD_Module(), HVD_SealKey(sign));
}

int HVD_SealSign(object item)
{
    if (GetStringLeft(GetResRef(item),8) != "hvd_seal") return 0;
    int sign = StringToInt(GetStringRight(GetResRef(item),1));
    if (HVD_ValidSeal(item,sign)) return sign;
    return 0;
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
        if ((resource == "hvd_mirror" || resource == "hvd_workkey" || GetStringLeft(resource, 9) == "hvd_book_") &&
            GetLocalInt(item, "hvd_run") != HVD_Run()) DestroyObject(item);
        item = next;
    }
}

object HVD_GateSocket(int slot)
{
    return GetObjectByTag("hvd_socket_" + IntToString(slot));
}

object HVD_ActiveSeal(int sign)
{
    int slot;
    for (slot = 1; slot <= 4; ++slot)
    {
        object chest = HVD_GateSocket(slot);
        object token = GetFirstItemInInventory(chest);
        while (GetIsObjectValid(token))
        {
            if (HVD_ValidSeal(token,sign)) return token;
            token = GetNextItemInInventory(chest);
        }
    }
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
    if (GetIsObjectValid(HVD_ActiveSeal(sign)))
    {
        SendMessageToPC(player, "Pečeť už je u člena výpravy nebo v předbraní.");
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

int HVD_SocketContents(int slot)
{
    object chest = HVD_GateSocket(slot);
    object token = GetFirstItemInInventory(chest);
    int contents;
    while (GetIsObjectValid(token))
    {
        int sign = HVD_SealSign(token);
        if (sign && contents) return -1;
        if (sign) contents = sign;
        token = GetNextItemInInventory(chest);
    }
    return contents;
}

void HVD_ShowSeal(int slot)
{
    string suffix = IntToString(slot);
    string part = "hvd_seal_display" + suffix;
    int sign = HVD_SocketContents(slot);
    if (sign > 0)
        HVD_PlacePart(part,"hvd_stamp" + IntToString(sign),"hvd_socket_" + suffix,0.0);
    else HVD_Extinguish(part);
    if (slot == 4)
        HVD_PlacePart("hvd_clamp_display",sign > 0 ? "hvd_clamp_up" : "hvd_clamp_down","hvd_socket_4",0.0);
}

int HVD_FilterAt(int slot)
{
    int index = GetLocalInt(HVD_Module(),"hvd_filter_state" + IntToString(slot));
    if (!index) return 1;
    return index;
}

void HVD_ShowFilter(int slot)
{
    string suffix = IntToString(slot);
    HVD_PlacePart("hvd_lens_display" + suffix,"hvd_lens" + IntToString(HVD_FilterAt(slot)),
                  "hvd_socket_" + suffix,0.0);
}

void HVD_RotateFilter(object player,int slot)
{
    object module = HVD_Module();
    if (GetLocalInt(module,"hvd_gate_open"))
    {
        SendMessageToPC(player,"Soustava právě drží otevřenou bránu.");
        return;
    }
    int index = HVD_FilterAt(slot) % 3 + 1;
    SetLocalInt(module,"hvd_filter_state" + IntToString(slot),index);
    HVD_ShowFilter(slot);
    SendMessageToPC(player,"V okruží zaklapla clona se znakem " + HVD_FilterName(index) + ".");
}

int HVD_GateContents()
{
    int code;
    int slot;
    for (slot = 1; slot <= 4; ++slot)
    {
        int sign = HVD_SocketContents(slot);
        if (sign < 1) return 0;
        code = code * 10 + sign;
    }
    return code;
}

int HVD_FilterCode()
{
    return HVD_FilterAt(1) * 100 + HVD_FilterAt(2) * 10 + HVD_FilterAt(3);
}

void HVD_ResetGate()
{
    object module = HVD_Module();
    DeleteLocalInt(module,"hvd_gate_attempt");
    int slot;
    for (slot = 1; slot <= 4; ++slot)
    {
        string suffix = IntToString(slot);
        object chest = HVD_GateSocket(slot);
        object token = GetFirstItemInInventory(chest);
        while (GetIsObjectValid(token))
        {
            object next = GetNextItemInInventory(chest);
            if (GetStringLeft(GetResRef(token),8) == "hvd_seal") DestroyObject(token);
            token = next;
        }
        HVD_Extinguish("hvd_seal_display" + suffix);
        if (slot <= 3)
        {
            HVD_Extinguish("hvd_ray_display" + suffix);
            DeleteLocalInt(module,"hvd_filter_state" + suffix);
            HVD_ShowFilter(slot);
        }
    }
    HVD_ShowSeal(4);
}

void HVD_Recap(object player)
{
    object module = HVD_Module();
    int step;
    for (step = 1; step <= 3; ++step)
    {
        if (GetLocalInt(module, "hvd_clue" + IntToString(step)))
            SendMessageToPC(player, HVD_Clue(step));
    }
    for (step = 1; step <= 4; ++step)
    {
        if (GetLocalInt(module, "hvd_earned" + IntToString(step)) && !GetIsObjectValid(HVD_ActiveSeal(step)))
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

#include "hvd_stores"

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
    SetLocalInt(module, "hvd_lens_order", HVD_LensOrder());
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
    DeleteLocalInt(module, "hvd_hall_off");
    DeleteLocalInt(module, "hvd_chest_off");
    DeleteLocalInt(module, "hvd_notes");
    DeleteLocalInt(module, "hvd_mounted");
    int index;
    for (index = 1; index <= 4; ++index)
    {
        string number = IntToString(index);
        DeleteLocalInt(module, "hvd_ready" + number);
        DeleteLocalInt(module, "hvd_earned" + number);
        DeleteLocalInt(module, "hvd_clue" + number);
        DeleteLocalInt(module, HVD_SealKey(index));
    }
    HVD_Extinguish("hvd_optic_gate");
    HVD_Extinguish("hvd_final_gate");
    HVD_Extinguish("hvd_summit_exit");
    HVD_Extinguish("hvd_socket_mirror");
    HVD_ResetGate();
    HVD_TurnOptics();
    HVD_ResetHidden();
    HVD_ResetBoss();
    HVD_ResetStores();
    HVD_PlaceBooks();
    object area = GetFirstArea();
    while (GetIsObjectValid(area))
    {
        if (GetLocalInt(area, "hvd_armed")) HVD_DestroyMobs(area);
        DeleteLocalInt(area, "hvd_armed");
        DeleteLocalInt(area, "hvd_empty");
        DeleteLocalInt(area, "hvd_push");
        if (HVD_AreaCount(area)) HVD_ActivateArea(area);
        area = GetNextArea();
    }
}
