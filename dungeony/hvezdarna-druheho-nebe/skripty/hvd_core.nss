const int HVD_GUARD_IDLE = 0;
const int HVD_GUARD_DUEL = 1;
const int HVD_GUARD_OFFER = 2;
const int HVD_GUARD_REPAIR = 3;
const int HVD_GUARD_COMBAT = 4;
const int HVD_GUARD_VICTORY = 5;
const string HVD_ITHREN_KEY = "hvd_ithrenkey";
const string HVD_WIND_EFFECT = "hvd_upper_wind";

object HVD_Module()
{
    return GetModule();
}

int HVD_GuardState()
{
    return GetLocalInt(HVD_Module(), "hvd_guard_state");
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

int HVD_WindyArea(object area)
{
    string tag = GetTag(area);
    return tag == "hvd_steps" || tag == "hvd_walks";
}

void HVD_RemoveUpperWind(object player)
{
    effect current = GetFirstEffect(player);
    while (GetIsEffectValid(current))
    {
        effect next = GetNextEffect(player);
        if (GetEffectTag(current) == HVD_WIND_EFFECT) RemoveEffect(player, current);
        current = next;
    }
}

void HVD_UpdateUpperWind(object player, object area)
{
    HVD_RemoveUpperWind(player);
    if (!HVD_WindyArea(area) || !HVD_PlayerIn(player, area) ||
        GetLocalInt(HVD_Module(), "hvd_repair_done") ||
        GetIsImmune(player, IMMUNITY_TYPE_MOVEMENT_SPEED_DECREASE)) return;

    effect wind = TagEffect(ExtraordinaryEffect(EffectMovementSpeedDecrease(15)), HVD_WIND_EFFECT);
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, wind, player, 12.0);
}

void HVD_UpdateAreaWind(object area)
{
    if (!HVD_WindyArea(area)) return;
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (GetArea(player) == area) HVD_UpdateUpperWind(player, area);
        player = GetNextPC();
    }
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

object HVD_NearPlayer(object source, float range, int farthest = FALSE, float leash = 0.0)
{
    location home = GetLocalLocation(source, "hvd_home");
    vector origin = GetPositionFromLocation(home);
    object best = OBJECT_INVALID;
    float bestDistance = range;
    if (farthest) bestDistance = -1.0;
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, GetArea(source)))
        {
            float distance = GetDistanceBetween(source, player);
            if (distance <= range && (leash <= 0.0 || VectorMagnitude(GetPosition(player) - origin) <= leash) &&
                LineOfSightObject(source, player) &&
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

void HVD_Travel(object player, object passage)
{
    if (GetLocalInt(passage, "repair_entry") &&
        (HVD_GuardState() != HVD_GUARD_REPAIR || GetLocked(GetObjectByTag("hvd_repairdoor")))) return;
    string requirement = GetLocalString(passage, "require");
    if (requirement != "" && !GetLocalInt(HVD_Module(), requirement))
    {
        if (GetLocalInt(passage, "hidden_route")) return;
        string hint = "Kamenný průchod je uzavřený.";
        if (requirement == "hvd_aligned") hint = "V oblouku chybí světlo. Seřiď optiku v kopuli.";
        if (requirement == "hvd_gate_open") hint = "Bránu otevře soustava tří sloupů. Spoušť a závora jsou pod schody.";
        SendMessageToPC(player, hint);
        return;
    }
    int minimum = GetLocalInt(passage, "minimum_level");
    if (GetHitDice(player) < minimum)
    {
        SendMessageToPC(player, "Služební průchod je přístupný od " + IntToString(minimum) + ". úrovně.");
        return;
    }
    string target = GetLocalString(passage, "target");
    if (target == "hvd_land_halls_r1" && GetLocked(GetObjectByTag("hvd_repairdoor")))
        target = "hvd_r1_safe_return";
    HVD_Jump(player, target);
}

void HVD_RefreshThresholds(string flag = "")
{
    object module = HVD_Module();
    int index = 0;
    object marker = GetObjectByTag("hvd_route", index);
    while (GetIsObjectValid(marker))
    {
        string required = GetLocalString(marker, "required");
        if (required != "" && (flag == "" || required == flag))
        {
            int open = GetLocalInt(module, required);
            object sill = GetLocalObject(marker, "hvd_sill");
            if (open && !GetIsObjectValid(sill))
            {
                sill = CreateObject(OBJECT_TYPE_PLACEABLE, GetLocalString(marker, "resource"), GetLocation(marker));
                SetLocalObject(marker, "hvd_sill", sill);
                if (GetIsObjectValid(sill) && GetLocalInt(marker, "secret"))
                {
                    SetName(sill, GetName(marker));
                    SetLocalString(sill, "action", "service_cross");
                    SetLocalString(sill, "target", GetLocalString(marker, "target"));
                    SetLocalString(sill, "require", required);
                    SetLocalInt(sill, "minimum_level", GetLocalInt(marker, "minimum_level"));
                    SetLocalInt(sill, "hidden_route", TRUE);
                }
            }
            if (!open && GetIsObjectValid(sill))
            {
                DestroyObject(sill);
                DeleteLocalObject(marker, "hvd_sill");
            }
            string view = GetLocalString(marker, "view");
            object continuation = GetLocalObject(marker, "hvd_view");
            if (open && view != "" && !GetIsObjectValid(continuation))
                SetLocalObject(marker, "hvd_view", CreateObject(OBJECT_TYPE_PLACEABLE, view, GetLocation(marker)));
            if (!open && GetIsObjectValid(continuation))
            {
                DestroyObject(continuation);
                DeleteLocalObject(marker, "hvd_view");
            }
            SetMapPinEnabled(marker, open);
        }
        marker = GetObjectByTag("hvd_route", ++index);
    }
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

int HVD_OpticMark(int side)
{
    int pair = GetLocalInt(HVD_Module(), "hvd_optics_pair");
    if (!pair) pair = 23; // Saves made before the optics could be randomized.
    return side == 1 ? pair / 10 : pair % 10;
}

string HVD_RomanMark(int mark)
{
    if (mark == 1) return "I";
    if (mark == 2) return "II";
    return "III";
}

string HVD_OpticsReading()
{
    return "Západní clona " + HVD_RomanMark(HVD_OpticMark(1)) +
           ", východní clona " + HVD_RomanMark(HVD_OpticMark(2)) + ".";
}

void HVD_TurnOptics()
{
    object module = HVD_Module();
    int west = GetLocalInt(module, "hvd_dial1");
    int east = GetLocalInt(module, "hvd_dial2");
    float heading = IntToFloat((west + 1 - HVD_OpticMark(1)) * 17 +
                               (east + 1 - HVD_OpticMark(2)) * 9);
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
    string resource = "hvd_gateway";
    if (marker == "hvd_optic_gate") resource = "hvd_stairview";
    if (marker == "hvd_final_gate") resource = "hvd_zenith";
    object portal = CreateObject(OBJECT_TYPE_PLACEABLE, resource, entrance);
    if (!GetIsObjectValid(portal)) return;
    SetLocalObject(module, marker, portal);
    if (marker == "hvd_final_gate")
        HVD_PlacePart("hvd_beyond_gate", "hvd_topview", marker, 0.0);
}

void HVD_Extinguish(string marker)
{
    object portal = GetLocalObject(HVD_Module(), marker);
    if (GetIsObjectValid(portal)) DestroyObject(portal);
    DeleteLocalObject(HVD_Module(), marker);
}

int HVD_LanternCharged()
{
    return HVD_GuardState() == HVD_GUARD_COMBAT && !GetLocalInt(HVD_Module(), "hvd_lamp_diverted");
}

void HVD_UpdateLastLight()
{
    object module = HVD_Module();
    int charged = HVD_LanternCharged();
    string appearance = "hvd_lampclosed";
    if (charged) appearance = "hvd_lampray";
    else if (GetLocalInt(module, "hvd_repair_done")) appearance = "hvd_lampguard";
    else if (HVD_GuardState() == HVD_GUARD_COMBAT && GetLocalInt(module, "hvd_lamp_diverted"))
        appearance = "hvd_lampdivert";
    HVD_PlacePart("hvd_last_light", appearance, "hvd_signal_home", 0.0);
    if (!charged)
    {
        object source = GetLocalObject(module, "hvd_sun_caster");
        if (GetIsObjectValid(source)) AssignCommand(source, ClearAllActions());
        HVD_Extinguish("hvd_sun_caster");
    }
}

void HVD_SecretCover(string part, string flag, string model)
{
    if (GetLocalInt(HVD_Module(), flag)) HVD_Extinguish(part);
    else HVD_PlacePart(part, model, part + "_home", 0.0);
}

void HVD_RefreshSecretCovers()
{
    HVD_SecretCover("hvd_rim_cover", "hvd_secret_rim", "hvd_sliprock");
    HVD_SecretCover("hvd_study_rim_cover", "hvd_secret_rim", "hvd_serviceslab");
    HVD_SecretCover("hvd_study_exit_cover", "hvd_secret_exit", "hvd_serviceslab");
    HVD_SecretCover("hvd_walks_cover", "hvd_secret_exit", "hvd_walks_rock");
}

void HVD_OpenPassage(string flag)
{
    if (GetLocalInt(HVD_Module(), flag)) return;
    SetLocalInt(HVD_Module(), flag, TRUE);
    HVD_RefreshThresholds(flag);
    if (flag == "hvd_aligned")
    {
        HVD_Extinguish("hvd_opt_lock");
        HVD_PlacePart("hvd_dome_ray", "hvd_domelight", "hvd_refractor", 0.0);
        HVD_Reveal("hvd_optic_gate");
    }
    if (GetStringLeft(flag, 11) == "hvd_secret_") HVD_RefreshSecretCovers();
    if (flag == "hvd_gate_open") HVD_Extinguish("hvd_gate_cover");
    if (flag == "hvd_won") HVD_UpdateLastLight();
}

int HVD_SecretLevel()
{
    return GetLocalInt(HVD_Module(), "hvd_secret_level");
}

int HVD_CanSearchSecret(object player)
{
    return GetHitDice(player) >= HVD_SecretLevel() && GetActionMode(player, ACTION_MODE_DETECT);
}

void HVD_InspectSecret(object player, string flag)
{
    if (flag == "" || GetLocalInt(HVD_Module(), flag) || !HVD_CanSearchSecret(player)) return;
    HVD_OpenPassage(flag);
    HVD_AreaMessage(GetArea(player), "Ve spáře nahmatáš zapuštěnou západku. Skalní deska se odsune.");
}

void HVD_ResetOpticalDoors()
{
    HVD_PlacePart("hvd_opt_lock","hvd_optcover","hvd_optic_gate",0.0);
    HVD_PlacePart("hvd_gate_cover","hvd_gateblind","hvd_final_gate",0.0);
}

int HVD_HallBranch()
{
    return GetLocalInt(HVD_Module(), "hvd_hall_branch");
}

void HVD_UpdateHallLights()
{
    int branch = HVD_HallBranch();
    int index = 1;
    string anchor = "hvd_hall_eye1";
    object eye = GetWaypointByTag(anchor);
    while (GetIsObjectValid(eye))
    {
        string resource = GetLocalInt(eye, "branch") == branch ? "hvd_ray_cut" : "hvd_ray_ready";
        HVD_PlacePart("hvd_hall_light"+IntToString(index),resource,anchor,0.0);
        anchor = "hvd_hall_eye"+IntToString(++index);
        eye = GetWaypointByTag(anchor);
    }
}

void HVD_RefreshHallPanel()
{
    int branch = HVD_HallBranch();
    int part;
    for (part = 1; part <= 3; ++part)
    {
        string index = IntToString(part);
        if (part == branch) HVD_PlacePart("hvd_led"+index,"hvd_panel_lit","hvd_hall_led"+index,0.0);
        else HVD_Extinguish("hvd_led"+index);
    }
    if (branch) HVD_PlacePart("hvd_hall_sink", "hvd_sinkglow", "hvd_hall_sink_home", 0.0);
    else HVD_Extinguish("hvd_hall_sink");
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
            if (resource == "hvd_book_dome")
                SetDescription(book, GetDescription(book) + "\n\nPřepis měření pro tuto výpravu\n" + HVD_OpticsReading());
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
        if ((resource == "hvd_mirror" || resource == "hvd_workkey" || resource == HVD_ITHREN_KEY ||
             GetStringLeft(resource, 9) == "hvd_book_") &&
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

void HVD_DestroyMobs(object area, string group = "")
{
    object storm = GetFirstObjectInArea(area, OBJECT_TYPE_AREA_OF_EFFECT);
    while (GetIsObjectValid(storm))
    {
        object nextStorm = GetNextObjectInArea(area, OBJECT_TYPE_AREA_OF_EFFECT);
        object caster = GetAreaOfEffectCreator(storm);
        if (GetLocalInt(caster, "hvd_managed") &&
            (group == "" || GetLocalString(caster, "hvd_group") == group)) DestroyObject(storm);
        storm = nextStorm;
    }
    object thing = GetFirstObjectInArea(area);
    while (GetIsObjectValid(thing))
    {
        object next = GetNextObjectInArea(area);
        if (GetLocalInt(thing, "hvd_managed") &&
            (group == "" || GetLocalString(thing, "hvd_group") == group)) DestroyObject(thing);
        thing = next;
    }
}

object HVD_MobAt(string resource, object spot, int seal = 0, int elite = 0, string group = "", int leash = 30)
{
    if (!GetIsObjectValid(spot)) return OBJECT_INVALID;
    object mob = CreateObject(OBJECT_TYPE_CREATURE, resource, GetLocation(spot));
    if (GetIsObjectValid(mob))
    {
        SetLocalInt(mob, "hvd_managed", TRUE);
        SetLocalInt(mob, "hvd_seal", seal);
        SetLocalInt(mob, "hvd_elite", elite);
        SetLocalString(mob, "hvd_group", group);
        SetLocalFloat(mob, "hvd_leash", IntToFloat(leash));
        SetLocalLocation(mob, "hvd_home", GetLocation(spot));
        if (elite && GetLocalInt(mob, "role") != 8)
        {
            int party = HVD_AreaCount(GetArea(spot));
            if (party > 4) party = 4;
            if (party > 1)
                ApplyEffectToObject(DURATION_TYPE_PERMANENT,
                    ExtraordinaryEffect(EffectTemporaryHitpoints(35 * (party - 1))), mob);
        }
    }
    return mob;
}

int HVD_EncounterActive(object area, string group)
{
    return GetLocalInt(area, "hvd_active_" + group);
}

#include "hvd_music"

int HVD_PackSize(int upper, int level, int count)
{
    if (!count) return 0;
    int size = count + 1;
    if (level >= (upper ? 39 : 36)) ++size;
    if (level >= (upper ? 40 : 38)) ++size;
    if (size > 4) return 4;
    return size;
}

int HVD_EncounterSize(object area, object leader)
{
    int count;
    int highest;
    object member = GetFirstFactionMember(leader, TRUE);
    while (GetIsObjectValid(member))
    {
        if (HVD_PlayerIn(member, area))
        {
            ++count;
            int level = GetHitDice(member);
            if (level > highest) highest = level;
        }
        member = GetNextFactionMember(leader, TRUE);
    }
    return HVD_PackSize(HVD_WindyArea(area), highest, count);
}

string HVD_EncounterCreature(int upper, int style, int slot)
{
    string strhavac = upper ? "hvd_elit_strh" : "hvd_strhavac";
    string vrhac = upper ? "hvd_elit_vrhac" : "hvd_vrhac";
    if (style == 5 || (style <= 3 && slot == 1) || (style == 1 && slot == 4)) return vrhac;
    if (style == 3 && slot == 3) return upper ? "hvd_elit_sprad" : "hvd_spradac";
    return strhavac;
}

int HVD_ChooseEncounterStyle(object area, string group)
{
    int used = GetLocalInt(area, "hvd_mixed_styles");
    int previous = GetLocalInt(area, "hvd_style_" + group);
    if (used == 7 && Random(2) == 0)
    {
        if (previous == 4) return 5;
        if (previous == 5) return 4;
        return 4 + Random(2);
    }
    if (used == 7) used = 0;

    int chosen;
    int options;
    int style;
    for (style = 1; style <= 3; ++style)
    {
        if (!(used & (1 << (style - 1))) && style != previous && Random(++options) == 0) chosen = style;
    }
    if (chosen) return chosen;
    return previous;
}

void HVD_RecordEncounterStyle(object area, string group, int style)
{
    int used = GetLocalInt(area, "hvd_mixed_styles");
    if (used == 7) used = 0;
    if (style <= 3) used = used | (1 << (style - 1));
    SetLocalInt(area, "hvd_mixed_styles", used);
    SetLocalInt(area, "hvd_style_" + group, style);
}

void HVD_ActivateEncounter(object area, string group, object player)
{
    object module = HVD_Module();
    if (group == "" || GetLocalInt(module, "hvd_repair_done") || !HVD_PlayerIn(player, area)) return;
    if (HVD_EncounterActive(area, group))
    {
        if (group == "bourna") HVD_RefreshStormMusic(area);
        return;
    }
    int size = HVD_EncounterSize(area, player);
    int slot = 1;
    string prefix = "hvs_" + group + "_";
    object spot = GetWaypointByTag(prefix + IntToString(slot));
    if (!size || !GetIsObjectValid(spot)) return;
    int firstSeal = GetLocalInt(spot, "seal");
    if (firstSeal && GetLocalInt(module, "hvd_ready" + IntToString(firstSeal))) return;
    int style = 0;
    if (!firstSeal) style = HVD_ChooseEncounterStyle(area, group);
    int upper = HVD_WindyArea(area);
    string state = "hvd_active_" + group;
    SetLocalInt(area, state, TRUE);
    while (slot <= size && GetIsObjectValid(spot) && GetArea(spot) == area)
    {
        string spawn = GetLocalString(spot, "spawn");
        if (!firstSeal) spawn = HVD_EncounterCreature(upper, style, slot);
        object mob = HVD_MobAt(spawn, spot, GetLocalInt(spot, "seal"), GetLocalInt(spot, "elite"),
                               group, GetLocalInt(spot, "leash"));
        if (!GetIsObjectValid(mob))
        {
            HVD_DestroyMobs(area, group);
            DeleteLocalInt(area, state);
            return;
        }
        spot = GetWaypointByTag(prefix + IntToString(++slot));
    }
    if (!firstSeal) HVD_RecordEncounterStyle(area, group, style);
    SetLocalInt(area, "hvd_wave", GetLocalInt(area, "hvd_wave") + 1);
    if (group == "bourna") HVD_RefreshStormMusic(area);
}

void HVD_ResetEncounters(object area)
{
    HVD_DestroyMobs(area);
    if (GetTag(area) == "hvd_steps") HVD_SetBattleTrack(area, HVD_MUSIC_WIND);
    object trigger = GetFirstObjectInArea(area, OBJECT_TYPE_TRIGGER);
    while (GetIsObjectValid(trigger))
    {
        string group = GetLocalString(trigger, "encounter");
        if (group != "") DeleteLocalInt(area, "hvd_active_" + group);
        trigger = GetNextObjectInArea(area, OBJECT_TYPE_TRIGGER);
    }
    DeleteLocalInt(area, "hvd_push");
}

void HVD_QuietExpedition()
{
    object area = GetFirstArea();
    while (GetIsObjectValid(area))
    {
        string tag = GetTag(area);
        if (tag == "hvd_halls" || tag == "hvd_works" || HVD_WindyArea(area))
        {
            HVD_ResetEncounters(area);
            HVD_UpdateAreaWind(area);
        }
        else if (tag == "hvd_top")
            HVD_DestroyMobs(area, "valkyries");
        area = GetNextArea();
    }
}

void HVD_ResetBoss()
{
    object module = HVD_Module();
    object area = GetObjectByTag("hvd_top");
    HVD_DestroyMobs(area);
    HVD_EndGuardMusic(area);
    DeleteLocalObject(module, "hvd_boss");
    int state = HVD_GuardState();
    if (state == HVD_GUARD_DUEL || state == HVD_GUARD_COMBAT)
    {
        DeleteLocalInt(module, "hvd_guard_state");
        if (!GetLocalInt(module, "hvd_mounted")) DeleteLocalInt(module, "hvd_lamp_diverted");
    }
    DeleteLocalInt(module, "hvd_valks_complete");
    HVD_UpdateLastLight();
    DeleteLocalInt(area, "hvd_push");
}

#include "hvd_stores"
#include "hvd_refraction"

void HVD_NewRun()
{
    object module = HVD_Module();
    int previous = GetCampaignInt("hvezdarna_nebe", "last_order");
    int order = HVD_Order(previous);
    int previousOptics = GetCampaignInt("hvezdarna_nebe", "last_optics_pair");
    int optics = HVD_LensOrder() / 10;
    while (optics == previousOptics) optics = HVD_LensOrder() / 10;
    int run = GetCampaignInt("hvezdarna_nebe", "last_run") + 1;
    SetCampaignInt("hvezdarna_nebe", "last_order", order);
    SetCampaignInt("hvezdarna_nebe", "last_optics_pair", optics);
    SetCampaignInt("hvezdarna_nebe", "last_run", run);
    SetLocalInt(module, "hvd_run", run);
    SetLocalInt(module, "hvd_order", order);
    SetLocalInt(module, "hvd_lens_order", HVD_LensOrder());
    SetLocalInt(module, "hvd_optics_pair", optics);
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
    DeleteLocalInt(module, "hvd_secret_rim");
    DeleteLocalInt(module, "hvd_secret_exit");
    DeleteLocalInt(module, "hvd_hall_branch");
    DeleteLocalInt(module, "hvd_lab_trial");
    DeleteLocalInt(module, "hvd_chest_off");
    DeleteLocalInt(module, "hvd_notes");
    DeleteLocalInt(module, "hvd_mounted");
    DeleteLocalInt(module, "hvd_guard_state");
    DeleteLocalInt(module, "hvd_lamp_diverted");
    HVD_ResetRepair();
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
    HVD_Extinguish("hvd_dome_ray");
    HVD_Extinguish("hvd_final_gate");
    HVD_Extinguish("hvd_beyond_gate");
    HVD_Extinguish("hvd_socket_mirror");
    HVD_Extinguish("hvd_lab_light");
    HVD_UpdateHallLights();
    HVD_RefreshHallPanel();
    HVD_ResetGate();
    HVD_TurnOptics();
    HVD_ResetOpticalDoors();
    HVD_RefreshSecretCovers();
    HVD_RefreshThresholds();
    HVD_ResetBoss();
    HVD_ResetStores();
    HVD_PlaceBooks();
    object area = GetFirstArea();
    while (GetIsObjectValid(area))
    {
        DeleteLocalInt(area, "hvd_mixed_styles");
        HVD_ResetEncounters(area);
        HVD_UpdateAreaWind(area);
        area = GetNextArea();
    }
}
