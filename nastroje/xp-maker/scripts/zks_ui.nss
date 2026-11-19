#include "nw_inc_nui"
#include "zks_core"

json ZKS_Line(json first, json second, json third = JSON_NULL, json fourth = JSON_NULL)
{
    json row = JsonArrayInsert(JsonArrayInsert(JsonArray(), first), second);
    if (JsonGetType(third) != JSON_TYPE_NULL) row = JsonArrayInsert(row, third);
    if (JsonGetType(fourth) != JSON_TYPE_NULL) row = JsonArrayInsert(row, fourth);
    return NuiHeight(NuiRow(row), 32.0);
}

json ZKS_Label(string text)
{
    return NuiLabel(JsonString(text), JsonInt(NUI_HALIGN_LEFT), JsonInt(NUI_VALIGN_MIDDLE));
}

json ZKS_Status(string bind)
{
    return NuiWidth(NuiHeight(NuiLabel(NuiBind(bind), JsonInt(NUI_HALIGN_LEFT), JsonInt(NUI_VALIGN_MIDDLE)), 30.0), 621.0);
}

json ZKS_Button(string title, string id, float width = 0.0)
{
    json button = NuiId(NuiButton(JsonString(title)), id);
    if (width > 0.0) button = NuiWidth(button, width);
    return button;
}

json ZKS_Options(json values, string selected)
{
    return NuiCombo(values, NuiBind(selected));
}

json ZKS_Add(json items, string label, int value)
{
    return JsonArrayInsert(items, NuiComboEntry(label, value));
}

json ZKS_Quality()
{
    json choices = JsonArray();
    int tier;
    for (tier = 1; tier <= 5; ++tier) choices = ZKS_Add(choices, "+" + IntToString(tier), tier);
    return choices;
}

json ZKS_Alignments()
{
    json align = JsonArray();
    align = ZKS_Add(align, "Zákonné dobro", 0);
    align = ZKS_Add(align, "Zákonná neutralita", 1);
    align = ZKS_Add(align, "Zákonné zlo", 2);
    align = ZKS_Add(align, "Neutrální dobro", 3);
    align = ZKS_Add(align, "Pravá neutralita", 4);
    align = ZKS_Add(align, "Neutrální zlo", 5);
    align = ZKS_Add(align, "Chaotické dobro", 6);
    align = ZKS_Add(align, "Chaotická neutralita", 7);
    return ZKS_Add(align, "Chaotické zlo", 8);
}

json ZKS_CharacterUI()
{
    json levels = ZKS_Add(JsonArray(), "0 XP · návrat na 1. úroveň", 0);
    int level;
    for (level = 1; level <= 40; ++level)
        levels = ZKS_Add(levels, "Úroveň " + IntToString(level) + " · " + IntToString(ZKS_LevelXP(level)) + " XP", level);
    json rows = JsonArrayInsert(JsonArray(), ZKS_Status("pc_state"));
    rows = JsonArrayInsert(rows, ZKS_Line(NuiWidth(ZKS_Options(levels, "target_level"), 278.0),
        NuiTooltip(ZKS_Button("Nastavit XP", "set_level", 140.0), JsonString("Při snížení hra odebere poslední získané úrovně.")),
        ZKS_Button("O úroveň níž", "down", 135.0)));
    rows = JsonArrayInsert(rows, NuiHeight(ZKS_Label("Po přidání XP dokonči zvýšení úrovně v okně postavy."), 25.0));
    rows = JsonArrayInsert(rows, ZKS_Line(NuiWidth(ZKS_Options(ZKS_Alignments(), "alignment"), 278.0),
        ZKS_Button("Změnit přesvědčení", "set_alignment", 193.0)));
    rows = JsonArrayInsert(rows, ZKS_Status("pc_alignment"));
    rows = JsonArrayInsert(rows, ZKS_Line(ZKS_Button("Obnovit přehled", "refresh"), ZKS_Button("Odpočinout", "rest"),
        ZKS_Button("Exportovat postavu", "export")));
    return NuiCol(rows);
}

json ZKS_GearUI()
{
    json groups = ZKS_Add(JsonArray(), "Zbraně na blízko", 1);
    groups = ZKS_Add(groups, "Střelba a střelivo", 2);
    groups = ZKS_Add(groups, "Zbroje a štíty", 3);
    groups = ZKS_Add(groups, "Oděv a doplňky", 4);
    json rows = JsonArray();
    rows = JsonArrayInsert(rows, ZKS_Line(NuiWidth(ZKS_Label("Skupina"), 88.0), NuiWidth(ZKS_Options(groups, "gear_group"), 489.0)));
    rows = JsonArrayInsert(rows, ZKS_Line(NuiWidth(ZKS_Label("Předmět"), 88.0),
        NuiWidth(ZKS_Options(NuiBind("gear_options"), "gear_item"), 489.0)));
    rows = JsonArrayInsert(rows, ZKS_Line(NuiWidth(ZKS_Label("Kvalita"), 88.0),
        NuiWidth(ZKS_Options(ZKS_Quality(), "quality"), 120.0), NuiWidth(ZKS_Label("Efekt"), 51.0),
        NuiWidth(ZKS_Options(NuiBind("effect_options"), "effect"), 298.0)));
    rows = JsonArrayInsert(rows, ZKS_Status("gear_hint"));
    rows = JsonArrayInsert(rows, ZKS_Line(ZKS_Button("Vydat předmět", "issue"), ZKS_Button("Šperky a pomůcky", "jewels")));
    rows = JsonArrayInsert(rows, ZKS_Status("result"));
    return NuiCol(rows);
}

json ZKS_JewelUI()
{
    json abilities = JsonArray();
    int n;
    for (n = 0; n <= 6; ++n) abilities = ZKS_Add(abilities, ZKS_Ability(n), n);
    json types = ZKS_Add(ZKS_Add(JsonArray(), "Prsten", 0), "Amulet", 1);
    json bonuses = ZKS_Add(ZKS_Add(JsonArray(), "+5", 5), "+12", 12);
    json casters = ZKS_Add(JsonArray(), "Bard", 1);
    casters = ZKS_Add(casters, "Klerik", 2);
    casters = ZKS_Add(casters, "Druid", 3);
    casters = ZKS_Add(casters, "Paladin", 6);
    casters = ZKS_Add(casters, "Hraničář", 7);
    casters = ZKS_Add(casters, "Zaklínač", 9);
    casters = ZKS_Add(casters, "Kouzelník", 10);
    json circles = JsonArray();
    for (n = 1; n <= 5; ++n) circles = ZKS_Add(circles, "Kruh " + IntToString(n), n);
    json rows = JsonArrayInsert(JsonArray(), NuiHeight(ZKS_Label("Bonus ke zvoleným atributům"), 24.0));
    rows = JsonArrayInsert(rows, ZKS_Line(NuiWidth(ZKS_Options(types, "jewel_type"), 115.0),
        NuiWidth(ZKS_Options(abilities, "ability"), 205.0), NuiWidth(ZKS_Options(bonuses, "bonus"), 86.0),
        ZKS_Button("Vydat šperk", "jewel", 130.0)));
    rows = JsonArrayInsert(rows, NuiHeight(ZKS_Label("Ohnisko přidá jednu pozici na kouzlo vybraného kruhu."), 24.0));
    rows = JsonArrayInsert(rows, ZKS_Line(ZKS_Options(casters, "caster"),
        NuiWidth(ZKS_Options(circles, "circle"), 135.0), ZKS_Button("Vydat ohnisko", "focus", 145.0)));
    rows = JsonArrayInsert(rows, ZKS_Line(ZKS_Button("Boty trvalého spěchu", "haste"),
        ZKS_Button("5 lektvarů uzdravení", "heal")));
    rows = JsonArrayInsert(rows, ZKS_Line(ZKS_Button("Paklíče", "lock"), ZKS_Button("Léčitelské sady", "med"),
        ZKS_Button("Zkušební pasti", "trap")));
    rows = JsonArrayInsert(rows, ZKS_Status("result"));
    rows = JsonArrayInsert(rows, ZKS_Line(ZKS_Button("Zpět k výstroji", "gear"), NuiSpacer()));
    return NuiCol(rows);
}

json ZKS_BestiaryUI()
{
    json tiers = ZKS_Add(JsonArray(), "Všechny obtížnosti", 0);
    tiers = ZKS_Add(tiers, "Začátečníci · CR do 2", 1);
    tiers = ZKS_Add(tiers, "Lehcí · CR 3 až 6", 2);
    tiers = ZKS_Add(tiers, "Zkušení · CR 7 až 12", 3);
    tiers = ZKS_Add(tiers, "Silní · CR 13 až 19", 4);
    tiers = ZKS_Add(tiers, "Epičtí · CR 20 až 29", 5);
    tiers = ZKS_Add(tiers, "Legendární · CR 30+", 6);
    json counts = JsonArray();
    int n;
    for (n = 1; n <= 8; ++n) counts = ZKS_Add(counts, IntToString(n), n);
    json cells = JsonArrayInsert(JsonArray(), NuiListTemplateCell(
        NuiLabel(NuiBind("beast_names"), JsonInt(NUI_HALIGN_LEFT), JsonInt(NUI_VALIGN_MIDDLE)), 330.0, TRUE));
    cells = JsonArrayInsert(cells, NuiListTemplateCell(NuiLabel(NuiBind("beast_cr"), JsonInt(NUI_HALIGN_LEFT),
        JsonInt(NUI_VALIGN_MIDDLE)), 70.0, FALSE));
    cells = JsonArrayInsert(cells, NuiListTemplateCell(ZKS_Button("Vybrat", "choose"), 83.0, FALSE));
    json rows = JsonArrayInsert(JsonArray(), ZKS_Line(NuiWidth(ZKS_Options(tiers, "beast_filter"), 270.0),
        NuiWidth(NuiTextEdit(JsonString("Hledat stvůru"), NuiBind("beast_search"), 50, FALSE), 299.0)));
    rows = JsonArrayInsert(rows, NuiWidth(NuiHeight(NuiList(cells, NuiBind("beast_names"), 26.0, TRUE), 290.0), 621.0));
    rows = JsonArrayInsert(rows, ZKS_Status("picked"));
    rows = JsonArrayInsert(rows, ZKS_Line(NuiWidth(ZKS_Label("Počet"), 49.0),
        NuiWidth(ZKS_Options(counts, "quantity"), 77.0), ZKS_Button("Přidat do střetu", "spawn"),
        ZKS_Button("Vyčistit kolbiště", "clear")));
    rows = JsonArrayInsert(rows, ZKS_Status("result"));
    rows = JsonArrayInsert(rows, ZKS_Line(ZKS_Button("Na kolbiště", "enter_ring"),
        ZKS_Button("Ustoupit do předsíně", "leave_ring")));
    return NuiCol(rows);
}

int ZKS_Get(object player, int token, string bind)
{
    return JsonGetInt(NuiGetBind(player, token, bind));
}

void ZKS_Text(object player, int token, string bind, string value)
{
    NuiSetBind(player, token, bind, JsonString(value));
}

void ZKS_Number(object player, int token, string bind, int value)
{
    NuiSetBind(player, token, bind, JsonInt(value));
}

void ZKS_CharacterState(object player, int token)
{
    ZKS_Text(player, token, "pc_state", "Úroveň " + IntToString(GetHitDice(player)) +
        "   ·   " + IntToString(GetXP(player)) + " XP   ·   Životy " + IntToString(GetCurrentHitPoints(player)) +
        "/" + IntToString(GetMaxHitPoints(player)));
    ZKS_Text(player, token, "pc_alignment", "Dobro/zlo " + IntToString(GetGoodEvilValue(player)) +
        "/100   ·   Zákon/chaos " + IntToString(GetLawChaosValue(player)) + "/100");
}

void ZKS_Effects(object player, int token)
{
    int index = ZKS_Get(player, token, "gear_item");
    json row = JsonArrayGet(ZKS_GearCatalog(), index);
    int kind = JsonGetInt(JsonArrayGet(row, 2));
    json choices = ZKS_Add(JsonArray(), ZKS_EffectName(0), 0);
    if (kind != 2)
    {
        int extra;
        for (extra = 1; extra <= 5; ++extra) choices = ZKS_Add(choices, ZKS_EffectName(extra), extra);
    }
    string help = "Kvalita zvyšuje útok a zranění. Živel přidává kostku poškození.";
    if (kind == 2)
    {
        int base = JsonGetInt(JsonArrayGet(row, 5));
        if (base == BASE_ITEM_LONGBOW || base == BASE_ITEM_SHORTBOW || base == BASE_ITEM_SLING)
            choices = ZKS_Add(choices, "Síla střelby (Mighty)", 9);
        help = "Kvalita zvyšuje útok. Živlové poškození přidáš na střelivu.";
    }
    if (kind == 3)
    {
        int extra;
        for (extra = 6; extra <= 8; ++extra) choices = ZKS_Add(choices, ZKS_EffectName(extra), extra);
        help = "Kvalita zvyšuje obranu. Živel přidává odolnost proti poškození.";
    }
    if (kind == 5) help = "Kvalita přidá fyzické poškození. Živel přidá druhý druh poškození.";
    NuiSetBind(player, token, "effect_options", choices);
    ZKS_Number(player, token, "effect", 0);
    ZKS_Text(player, token, "gear_hint", help);
}

void ZKS_FillGear(object player, int token)
{
    int group = ZKS_Get(player, token, "gear_group");
    json catalog = ZKS_GearCatalog();
    json choices = JsonArray();
    int first = -1;
    int index;
    for (index = 0; index < JsonGetLength(catalog); ++index)
    {
        json row = JsonArrayGet(catalog, index);
        if (JsonGetInt(JsonArrayGet(row, 1)) != group) continue;
        if (first < 0) first = index;
        choices = ZKS_Add(choices, JsonGetString(JsonArrayGet(row, 3)), index);
    }
    NuiSetBind(player, token, "gear_options", choices);
    ZKS_Number(player, token, "gear_item", first);
    ZKS_Effects(player, token);
}

int ZKS_Tier(float cr)
{
    if (cr < 3.0) return 1;
    if (cr < 7.0) return 2;
    if (cr < 13.0) return 3;
    if (cr < 20.0) return 4;
    if (cr < 30.0) return 5;
    return 6;
}

string ZKS_CR(float cr)
{
    if (cr >= 1.0) return IntToString(FloatToInt(cr));
    return FloatToString(cr, 1, 2);
}

void ZKS_Filter(object player, int token)
{
    json catalog = ZKS_Bestiary();
    int filter = ZKS_Get(player, token, "beast_filter");
    string search = GetStringLowerCase(JsonGetString(NuiGetBind(player, token, "beast_search")));
    json names = JsonArray();
    json crs = JsonArray();
    json indices = JsonArray();
    int index;
    for (index = 0; index < JsonGetLength(catalog); ++index)
    {
        json row = JsonArrayGet(catalog, index);
        string name = JsonGetString(JsonArrayGet(row, 1));
        float cr = JsonGetFloat(JsonArrayGet(row, 2));
        if (filter && filter != ZKS_Tier(cr)) continue;
        if (search != "" && FindSubString(GetStringLowerCase(name), search) < 0) continue;
        names = JsonArrayInsert(names, JsonString(name));
        crs = JsonArrayInsert(crs, JsonString("CR " + ZKS_CR(cr)));
        indices = JsonArrayInsert(indices, JsonInt(index));
    }
    NuiSetBind(player, token, "beast_names", names);
    NuiSetBind(player, token, "beast_cr", crs);
    NuiSetBind(player, token, "beast_indices", indices);
}

void ZKS_Pick(object player, int token, int index)
{
    json row = JsonArrayGet(ZKS_Bestiary(), index);
    ZKS_Number(player, token, "beast", index);
    ZKS_Text(player, token, "picked", JsonGetString(JsonArrayGet(row, 1)) + " · CR " +
        ZKS_CR(JsonGetFloat(JsonArrayGet(row, 2))));
}

void ZKS_Open(object player, int page, int group = 1)
{
    if (!ZKS_Player(player) || GetIsDead(player)) return;
    json body;
    string title = "Kronika postavy";
    float height = 276.0;
    if (page == 1) body = ZKS_CharacterUI();
    if (page == 2) { body = ZKS_GearUI(); title = "Zbrojnice"; height = 283.0; }
    if (page == 3) { body = ZKS_BestiaryUI(); title = "Kniha bestiáře"; height = 535.0; }
    if (page == 4) { body = ZKS_JewelUI(); title = "Klenotnice a pomůcky"; height = 333.0; }
    int old = NuiFindWindow(player, "zksPanel");
    if (old) NuiDestroy(player, old);
    json window = NuiWindow(body, JsonString(title), NuiRect(120.0, 55.0, 663.0, height),
        JSON_FALSE, JSON_FALSE, JSON_TRUE, JSON_FALSE, JSON_TRUE);
    int token = NuiCreate(player, window, "zksPanel", "zks_panel");
    if (!token) return;
    NuiSetUserData(player, token, JsonInt(page));
    ZKS_Text(player, token, "result", "");
    if (page == 1)
    {
        ZKS_Number(player, token, "target_level", GetHitDice(player));
        int order = 1;
        int moral = 1;
        if (GetLawChaosValue(player) > 69) order = 0;
        if (GetLawChaosValue(player) < 31) order = 2;
        if (GetGoodEvilValue(player) > 69) moral = 0;
        if (GetGoodEvilValue(player) < 31) moral = 2;
        ZKS_Number(player, token, "alignment", order * 3 + moral);
        ZKS_CharacterState(player, token);
    }
    if (page == 2)
    {
        ZKS_Number(player, token, "gear_group", group);
        ZKS_Number(player, token, "quality", 1);
        ZKS_FillGear(player, token);
        NuiSetBindWatch(player, token, "gear_group", TRUE);
        NuiSetBindWatch(player, token, "gear_item", TRUE);
    }
    if (page == 3)
    {
        ZKS_Number(player, token, "beast_filter", 0);
        ZKS_Text(player, token, "beast_search", "");
        ZKS_Number(player, token, "quantity", 1);
        ZKS_Filter(player, token);
        ZKS_Pick(player, token, 0);
        ZKS_Text(player, token, "result", "Na kolbišti čeká " + IntToString(ZKS_Count(GetArea(player))) + "/12 protivníků.");
        NuiSetBindWatch(player, token, "beast_filter", TRUE);
        NuiSetBindWatch(player, token, "beast_search", TRUE);
    }
    if (page == 4)
    {
        ZKS_Number(player, token, "jewel_type", 0);
        ZKS_Number(player, token, "ability", 6);
        ZKS_Number(player, token, "bonus", 5);
        ZKS_Number(player, token, "caster", 10);
        ZKS_Number(player, token, "circle", 1);
    }
}
