const int HVD_MUSIC_WIND = 71;
const int HVD_MUSIC_STORM = 44;
const int HVD_MUSIC_TEMPLE = 98;
const int HVD_MUSIC_DUEL = 47;
const int HVD_MUSIC_PLEDGE = 51;
const int HVD_MUSIC_CHALLENGE = 75;
const int HVD_MUSIC_VALKYRIES = 72;

void HVD_SetBattleTrack(object area, int track, int restart = FALSE)
{
    if (MusicBackgroundGetBattleTrack(area) == track) return;
    if (restart) MusicBattleStop(area);
    MusicBattleChange(area, track);
    if (restart) MusicBattlePlay(area);
}

void HVD_RefreshStormMusic(object area)
{
    if (GetTag(area) != "hvd_steps" || !HVD_EncounterActive(area, "bourna")) return;
    object mob = GetFirstObjectInArea(area, OBJECT_TYPE_CREATURE);
    while (GetIsObjectValid(mob))
    {
        if (GetLocalString(mob, "hvd_group") == "bourna" && !GetIsDead(mob) &&
            GetIsObjectValid(HVD_NearPlayer(mob, 28.0, FALSE, GetLocalFloat(mob, "hvd_leash"))))
        {
            HVD_SetBattleTrack(area, HVD_MUSIC_STORM);
            return;
        }
        mob = GetNextObjectInArea(area, OBJECT_TYPE_CREATURE);
    }
    HVD_SetBattleTrack(area, HVD_MUSIC_WIND);
}

void HVD_SetTempleTrack(object area, int track, int play = FALSE)
{
    if (MusicBackgroundGetNightTrack(area) != track || MusicBackgroundGetDayTrack(area) != track)
    {
        if (play) MusicBackgroundStop(area);
        MusicBackgroundChangeDay(area, track);
        MusicBackgroundChangeNight(area, track);
    }
    if (play) MusicBackgroundPlay(area);
}

void HVD_EndGuardMusic(object area)
{
    MusicBattleStop(area);
    HVD_SetBattleTrack(area, HVD_MUSIC_DUEL);
    HVD_SetTempleTrack(area, HVD_MUSIC_TEMPLE);
}

void HVD_EndPledge(object area, int run)
{
    if (HVD_Run() == run && MusicBackgroundGetNightTrack(area) == HVD_MUSIC_PLEDGE)
        HVD_SetTempleTrack(area, HVD_MUSIC_TEMPLE, HVD_AreaCount(area) > 0);
}

void HVD_PlayPledge(object area)
{
    HVD_SetTempleTrack(area, HVD_MUSIC_PLEDGE, TRUE);
    // The installed Aribeth Theme 1 runs for just over 38 seconds.
    AssignCommand(area, DelayCommand(39.0, HVD_EndPledge(area, HVD_Run())));
}
