#include "zks_ui"

void CharacterClick(object player, int token, string button)
{
    if (button == "set_level") ZKS_SetLevel(player, ZKS_Get(player, token, "target_level"));
    if (button == "down")
    {
        int target = GetHitDice(player) - 1;
        ZKS_SetLevel(player, target);
        ZKS_Number(player, token, "target_level", GetHitDice(player));
    }
    if (button == "set_alignment") ZKS_Alignment(player, ZKS_Get(player, token, "alignment"));
    if (button == "rest") ZKS_Rest(player);
    if (button == "export")
    {
        ExportSingleCharacter(player);
        SendMessageToPC(player, "Postava byla exportována do místního seznamu postav.");
    }
    ZKS_CharacterState(player, token);
}

void GearClick(object player, int token, int page, string button)
{
    if (button == "jewels") { ZKS_Open(player, 4); return; }
    if (button == "gear") { ZKS_Open(player, 2); return; }
    object item = OBJECT_INVALID;
    if (page == 2 && button == "issue")
        item = ZKS_Equipment(player, ZKS_Get(player, token, "gear_item"), ZKS_Get(player, token, "quality"),
                            ZKS_Get(player, token, "effect"));
    if (page == 4)
    {
        if (button == "jewel") item = ZKS_Jewel(player, ZKS_Get(player, token, "jewel_type"),
            ZKS_Get(player, token, "ability"), ZKS_Get(player, token, "bonus"));
        if (button == "focus")
        {
            int caster = ZKS_Get(player, token, "caster");
            int circle = ZKS_Get(player, token, "circle");
            if ((caster == 6 || caster == 7) && circle == 5)
            {
                ZKS_Text(player, token, "result", "Paladin a hraničář mají kouzla do čtvrtého kruhu.");
                return;
            }
            item = ZKS_Focus(player, caster, circle);
        }
        if (button == "haste") item = ZKS_Receive(player, "zks_haste");
        if (button == "heal") item = ZKS_Receive(player, "zks_heal", 5);
        if (button == "lock") item = ZKS_Receive(player, "zks_lock", 5);
        if (button == "med") item = ZKS_Receive(player, "zks_med", 5);
        if (button == "trap") item = ZKS_Receive(player, "zks_trap", 5);
    }
    if (GetIsObjectValid(item)) ZKS_Text(player, token, "result", "V inventáři máš: " + GetName(item) + ".");
}

void ArenaClick(object player, int token, string button)
{
    object area = GetArea(player);
    if (button == "choose")
    {
        json indices = NuiGetBind(player, token, "beast_indices");
        int row = NuiGetEventArrayIndex();
        if (row >= 0 && row < JsonGetLength(indices)) ZKS_Pick(player, token, JsonGetInt(JsonArrayGet(indices, row)));
    }
    if (button == "spawn")
    {
        int made = ZKS_Spawn(player, ZKS_Get(player, token, "beast"), ZKS_Get(player, token, "quantity"));
        ZKS_Text(player, token, "result", "Přivoláno " + IntToString(made) + ". Živí protivníci " +
            IntToString(ZKS_Count(area)) + "/12.");
    }
    if (button == "clear")
    {
        ZKS_Clear(area);
        ZKS_Text(player, token, "result", "Kolbiště je volné.");
    }
    if (button == "enter_ring") ZKS_Jump(player, "zks_into_ring");
    if (button == "leave_ring") ZKS_Jump(player, "zks_arena_in");
}

void main()
{
    object player = NuiGetEventPlayer();
    int token = NuiGetEventWindow();
    int page = JsonGetInt(NuiGetUserData(player, token));
    string eventType = NuiGetEventType();
    string element = NuiGetEventElement();
    if (!ZKS_Player(player) || GetIsDead(player)) return;
    string area = GetTag(GetArea(player));
    if (eventType == "watch")
    {
        if (page == 2 && area == "zks_armory" && element == "gear_group") ZKS_FillGear(player, token);
        if (page == 2 && area == "zks_armory" && element == "gear_item") ZKS_Effects(player, token);
        if (page == 3 && area == "zks_arena" && (element == "beast_filter" || element == "beast_search")) ZKS_Filter(player, token);
        return;
    }
    if (eventType != "click") return;
    if (page == 1 && area == "zks_hall") CharacterClick(player, token, element);
    if ((page == 2 || page == 4) && area == "zks_armory") GearClick(player, token, page, element);
    if (page == 3 && area == "zks_arena") ArenaClick(player, token, element);
}
