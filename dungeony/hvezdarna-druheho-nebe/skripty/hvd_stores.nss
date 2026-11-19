void HVD_Stock(object chest, string resource, int quantity = 1)
{
    if (!GetIsObjectValid(chest)) return;
    int count;
    for (count = 0; count < quantity; ++count)
    {
        object item = CreateItemOnObject(resource, chest);
        if (GetItemPossessor(item) == chest)
        {
            SetLocalString(item, "hvd_stock_from", GetTag(chest));
            SetLocalInt(item, "hvd_run", HVD_Run());
        }
    }
}

void HVD_ClearStock(string tag, int locked = FALSE)
{
    object chest = GetObjectByTag(tag);
    if (!GetIsObjectValid(chest)) return;
    object item = GetFirstItemInInventory(chest);
    while (GetIsObjectValid(item))
    {
        object next = GetNextItemInInventory(chest);
        if (GetLocalString(item, "hvd_stock_from") == tag) DestroyObject(item);
        item = next;
    }
    SetLocked(chest, locked);
}

void HVD_FillStores(int run)
{
    if (run != HVD_Run()) return;
    object supply = GetObjectByTag("hvd_supply");
    HVD_Stock(supply, "hvd_sword");
    HVD_Stock(supply, "hvd_armor");
    HVD_Stock(supply, "hvd_shield");
    HVD_Stock(supply, "hvd_heal", 5);

    HVD_Stock(GetObjectByTag("hvd_keycase"), "hvd_workkey");
    HVD_Stock(GetObjectByTag("hvd_mirror_case"), "hvd_mirror");

    object workshop = GetObjectByTag("hvd_work_cache");
    HVD_Stock(workshop, "hvd_brooch");
    HVD_Stock(workshop, "hvd_heal", 2);

    object guard = GetObjectByTag("hvd_guard_cache");
    HVD_Stock(guard, "hvd_glass");
    HVD_Stock(guard, "hvd_heal", 3);

    object study = GetObjectByTag("hvd_study_cache");
    HVD_Stock(study,"hvd_resist");
    HVD_Stock(study,"hvd_glass");
    HVD_Stock(study,"hvd_book_study");
    HVD_Stock(GetObjectByTag("hvd_eave_cache"),"hvd_glass");
    HVD_Stock(GetObjectByTag("hvd_eave_cache"),"hvd_heal");
    HVD_Stock(GetObjectByTag("hvd_walk_cache"),"hvd_glass");
    HVD_Stock(GetObjectByTag("hvd_walk_cache"),"hvd_heal",2);
}

void HVD_ResetStores()
{
    HVD_ClearStock("hvd_supply");
    HVD_ClearStock("hvd_keycase");
    HVD_ClearStock("hvd_mirror_case");
    HVD_ClearStock("hvd_work_cache", TRUE);
    HVD_ClearStock("hvd_guard_cache");
    HVD_ClearStock("hvd_cloak_reward", TRUE);
    HVD_ClearStock("hvd_badge_reward", TRUE);
    HVD_ClearStock("hvd_study_cache");
    HVD_ClearStock("hvd_eave_cache");
    HVD_ClearStock("hvd_walk_cache");
    DelayCommand(0.15, HVD_FillStores(HVD_Run()));
}

void HVD_FillReward(object chest, string resource, int wanted)
{
    object item = GetFirstItemInInventory(chest);
    while (GetIsObjectValid(item))
    {
        if (GetResRef(item) == resource && GetLocalString(item, "hvd_stock_from") == GetTag(chest))
            --wanted;
        item = GetNextItemInInventory(chest);
    }
    if (wanted > 0) HVD_Stock(chest, resource, wanted);
}

int HVD_RewardCount()
{
    int pending = 0;
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_IsPlayer(player) && GetLocalInt(player, "hvd_final_reward") != HVD_Run()) ++pending;
        player = GetNextPC();
    }
    return pending;
}

void HVD_OpenRewardStores()
{
    object cloaks = GetObjectByTag("hvd_cloak_reward");
    object badges = GetObjectByTag("hvd_badge_reward");
    int pending = HVD_RewardCount();
    HVD_FillReward(cloaks, "hvd_cloak", pending);
    HVD_FillReward(badges, "hvd_badge", pending);
    HVD_Stock(cloaks, "hvd_glass", pending);
    SetLocked(cloaks, FALSE);
    SetLocked(badges, FALSE);
}
