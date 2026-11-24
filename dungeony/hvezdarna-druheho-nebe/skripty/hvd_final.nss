#include "hvd_dungeon"

object HVD_Guardian()
{
    return GetLocalObject(HVD_Module(), "hvd_boss");
}

object HVD_EnsureGuardian()
{
    object module = HVD_Module();
    object boss = HVD_Guardian();
    int state = HVD_GuardState();
    if (!GetIsObjectValid(boss) && GetLocalInt(module, "hvd_gate_open") &&
        (state == HVD_GUARD_IDLE || state == HVD_GUARD_OFFER || state == HVD_GUARD_REPAIR))
    {
        boss = HVD_MobAt("hvd_ithren", GetWaypointByTag("hvd_boss_home"), 0, TRUE);
        if (GetIsObjectValid(boss)) SetLocalObject(module, "hvd_boss", boss);
    }
    return boss;
}

int HVD_GuardCanTalk(object player)
{
    object boss = HVD_Guardian();
    int state = HVD_GuardState();
    return state != HVD_GUARD_DUEL && state != HVD_GUARD_COMBAT &&
        GetIsObjectValid(boss) && HVD_PlayerIn(player, GetArea(boss)) &&
        !GetIsInCombat(player) && !GetIsInCombat(boss) && GetDistanceBetween(boss, player) <= 14.0;
}

string HVD_GuardDialogue()
{
    int players = 0;
    object member = GetFirstPC();
    while (GetIsObjectValid(member))
    {
        if (!GetIsDM(member) && ++players >= 2) return "hvd_ithren_grp";
        member = GetNextPC();
    }
    return "hvd_ithren";
}

void HVD_GuardTalk(object player)
{
    object boss = HVD_Guardian();
    if (!HVD_GuardCanTalk(player) || IsInConversation(boss) || IsInConversation(player)) return;
    AssignCommand(boss, ClearAllActions());
    AssignCommand(boss, ActionStartConversation(player, HVD_GuardDialogue(), TRUE, FALSE));
}

void HVD_GuardGreet(object player)
{
    object boss = HVD_EnsureGuardian();
    if (HVD_GuardState() != HVD_GUARD_IDLE || !HVD_GuardCanTalk(player) ||
        GetLocalInt(player, "hvd_guard_seen") == HVD_Run() ||
        IsInConversation(boss) || IsInConversation(player) ||
        GetDistanceBetween(boss, player) > 11.5 || !LineOfSightObject(boss, player)) return;
    SetLocalInt(player, "hvd_guard_seen", HVD_Run());
    HVD_GuardTalk(player);
}

void HVD_LanternPulse(object source)
{
    if (!HVD_LanternCharged() || source != GetLocalObject(HVD_Module(), "hvd_sun_caster")) return;
    object target = HVD_NearPlayer(source, 34.0);
    if (GetIsObjectValid(target) && GetPosition(target).y >= 29.8)
        AssignCommand(source, ActionCastSpellAtLocation(SPELL_SUNBEAM, GetLocation(target),
            METAMAGIC_ANY, TRUE, PROJECTILE_PATH_TYPE_DEFAULT, TRUE));
}

void HVD_StartLantern()
{
    HVD_UpdateLastLight();
    object module = HVD_Module();
    if (!HVD_LanternCharged() || GetIsObjectValid(GetLocalObject(module, "hvd_sun_caster"))) return;
    object source = CreateObject(OBJECT_TYPE_CREATURE, "hvd_suncaster",
                                  GetLocation(GetWaypointByTag("hvd_sun_home")));
    if (GetIsObjectValid(source)) SetLocalObject(module, "hvd_sun_caster", source);
}

void HVD_DivertLamp(object player)
{
    object module = HVD_Module();
    if (GetLocalInt(module, "hvd_repair_done"))
    {
        SendMessageToPC(player, "Pojistka drží purpurový paprsek na lucerně.");
        return;
    }
    if (GetLocalInt(module, "hvd_lamp_diverted")) return;
    SetLocalInt(module, "hvd_lamp_diverted", TRUE);
    HVD_UpdateLastLight();
    HVD_AreaMessage(GetArea(player), "Zrcadlo přesměrovalo paprsek do záchytu. Poslední lucerna zhasla.");
}

void HVD_LanternStatus(object player)
{
    if (GetLocalInt(HVD_Module(), "hvd_repair_done"))
        SendMessageToPC(player, "Purpurové světlo chrání stezku. Vítr utichl a hlídky se rozešly.");
    else if (HVD_LanternCharged())
        SendMessageToPC(player, "Nabitá lucerna sesílá Sluneční paprsek každé kolo. U odkláněcího zrcadla vlevo je mosazná páka.");
    else
        SendMessageToPC(player, "Sklo lucerny je tmavé. Sluneční výboje ustaly.");
}

void HVD_StartGuardFight(object player, int combat)
{
    object boss = HVD_Guardian();
    object module = HVD_Module();
    if (HVD_GuardState() != HVD_GUARD_IDLE || !GetIsObjectValid(boss) ||
        !HVD_PlayerIn(player, GetArea(boss))) return;
    SetLocalInt(module, "hvd_guard_state", combat ? HVD_GUARD_COMBAT : HVD_GUARD_DUEL);
    DeleteLocalInt(module, "hvd_valks_complete");
    HVD_SetBattleTrack(GetArea(boss), combat ? HVD_MUSIC_CHALLENGE : HVD_MUSIC_DUEL);
    SetPlotFlag(boss, FALSE);
    SetImmortal(boss, TRUE);
    ChangeToStandardFaction(boss, STANDARD_FACTION_HOSTILE);
    if (combat)
    {
        effect blessing = EffectLinkEffects(EffectAttackIncrease(5), EffectACIncrease(6));
        blessing = EffectLinkEffects(blessing, EffectSavingThrowIncrease(SAVING_THROW_ALL, 6));
        blessing = EffectLinkEffects(blessing, EffectDamageIncrease(DAMAGE_BONUS_2d6, DAMAGE_TYPE_DIVINE));
        ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(blessing), boss);
        HVD_StartLantern();
        if (HVD_LanternCharged())
            HVD_AreaMessage(GetArea(boss), "Paprsek naplnil sklo Poslední lucerny. Ta bude sesílat sluneční výboje, dokud neodkloníte světlo.");
    }
    else HVD_UpdateLastLight();
    AssignCommand(boss, ClearAllActions());
    AssignCommand(boss, ActionAttack(player));
    MusicBattlePlay(GetArea(boss));
}

void HVD_OfferWhenQuiet(object boss, int remaining = 15)
{
    if (HVD_GuardState() != HVD_GUARD_OFFER || HVD_Guardian() != boss) return;
    object near = HVD_NearPlayer(boss, 12.0);
    if (!GetIsObjectValid(near)) return;
    if (HVD_GuardCanTalk(near))
    {
        HVD_PlayPledge(GetArea(boss));
        HVD_GuardTalk(near);
    }
    else if (remaining > 0)
        DelayCommand(1.0, HVD_OfferWhenQuiet(boss, remaining - 1));
}

void HVD_GuardYield(object boss)
{
    SetLocalInt(HVD_Module(), "hvd_guard_state", HVD_GUARD_OFFER);
    AssignCommand(boss, ClearAllActions());
    ChangeToStandardFaction(boss, STANDARD_FACTION_COMMONER);
    SetPlotFlag(boss, TRUE);
    SetCurrentHitPoints(boss, GetMaxHitPoints(boss));
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        if (HVD_PlayerIn(player, GetArea(boss)))
        {
            if (GetAttackTarget(player) == boss) AssignCommand(player, ClearAllActions());
            ClearPersonalReputation(boss, player);
            ClearPersonalReputation(player, boss);
        }
        player = GetNextPC();
    }
    HVD_EndGuardMusic(GetArea(boss));
    HVD_AreaMessage(GetArea(boss), "Ithren sklonil čepel. Zkouška skončila a solar vás chce oslovit.");
    DelayCommand(2.0, HVD_OfferWhenQuiet(boss));
}

int HVD_ValkyriesAlive(object area)
{
    object guard = GetFirstObjectInArea(area, OBJECT_TYPE_CREATURE);
    while (GetIsObjectValid(guard))
    {
        if (GetLocalString(guard, "hvd_group") == "valkyries" && !GetIsDead(guard)) return TRUE;
        guard = GetNextObjectInArea(area, OBJECT_TYPE_CREATURE);
    }
    return FALSE;
}

void HVD_CallValkyries(object boss)
{
    object area = GetArea(boss);
    if (HVD_ValkyriesAlive(area)) return;
    int born = GetLocalInt(boss, "hvd_valks_born");
    if (born >= 6)
    {
        SetLocalInt(HVD_Module(), "hvd_valks_complete", TRUE);
        int lastStand = GetMaxHitPoints(boss) / 4;
        if (GetCurrentHitPoints(boss) < lastStand) SetCurrentHitPoints(boss, lastStand);
        SetImmortal(boss, FALSE);
        HVD_AreaMessage(area, "Poslední dvojice padla. Ithren zůstal u lucerny sám.");
        return;
    }
    if (!GetLocalInt(boss, "hvd_called"))
    {
        SetLocalInt(boss, "hvd_called", TRUE);
        HVD_SetBattleTrack(area, HVD_MUSIC_VALKYRIES, TRUE);
        AssignCommand(boss, SpeakString("Jménem Helma povolávám nebeskou gardu! " +
                                       "Valkýry, sestupte z výšin a držte se mnou poslední práh!",
                                       TALKVOLUME_TALK));
    }
    int last = born + 2;
    if (last > 6) last = 6;
    int index;
    for (index = born + 1; index <= last; ++index)
    {
        object origin = GetWaypointByTag("hvd_valk_" + IntToString(index));
        object guard = HVD_MobAt("hvd_valkyra", origin, 0, TRUE, "valkyries", 23);
        if (!GetIsObjectValid(guard)) return;
        SetLocalInt(boss, "hvd_valks_born", index);
        ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_FNF_SUMMON_CELESTIAL),
                              GetLocation(origin));
    }
}

void HVD_GuardVictory(object area)
{
    if (HVD_GuardState() != HVD_GUARD_COMBAT || !GetLocalInt(HVD_Module(), "hvd_valks_complete")) return;
    object boss = HVD_Guardian();
    if (GetIsObjectValid(boss) && !GetIsDead(boss)) return;
    if (HVD_ValkyriesAlive(area)) return;
    SetLocalInt(HVD_Module(), "hvd_guard_state", HVD_GUARD_VICTORY);
    HVD_EndGuardMusic(area);
    MusicBackgroundPlay(area);
    HVD_UpdateLastLight();
    HVD_AreaMessage(area, "Ithren i jeho Jízda byli poraženi. Cesta k hoře je volná. Práh předměstí zůstává uzavřený.");
}

int HVD_Lane(vector position)
{
    if (position.x < 27.5) return 1;
    if (position.x > 42.5) return 3;
    return 2;
}

void HVD_MarkLane(object area, int lane)
{
    float middle = 20.0 + IntToFloat(lane - 1) * 15.0;
    HVD_MarkLine(area, Vector(middle - 6.0, 31.0, 10.0), Vector(middle - 6.0, 51.5, 10.0), VFX_IMP_SONIC);
    HVD_MarkLine(area, Vector(middle + 6.0, 31.0, 10.0), Vector(middle + 6.0, 51.5, 10.0), VFX_IMP_SONIC);
}

void HVD_BossLane(object boss, int lane, int state)
{
    if (!GetIsObjectValid(boss) || GetIsDead(boss) || state != HVD_GuardState()) return;
    object area = GetArea(boss);
    vector origin = GetPosition(boss);
    float middle = 20.0 + IntToFloat(lane - 1) * 15.0;
    HVD_MarkLine(area, Vector(middle, 31.5, 10.0), Vector(middle, 51.5, 10.0), VFX_IMP_PULSE_HOLY);
    object player = GetFirstPC();
    while (GetIsObjectValid(player))
    {
        vector position = GetPosition(player);
        if (HVD_PlayerIn(player, area) && HVD_Lane(position) == lane && position.y >= 30.0 &&
            position.y < 55.0 && !HVD_Covered(area, origin, position))
            HVD_Strike(player, boss, state == HVD_GUARD_COMBAT ? 72 : 31,
                       DAMAGE_TYPE_DIVINE, state == HVD_GUARD_COMBAT ? 38 : 29);
        player = GetNextPC();
    }
}

void HVD_BossThink(object boss)
{
    int state = HVD_GuardState();
    if (!GetIsObjectValid(boss) || GetIsDead(boss) ||
        (state != HVD_GUARD_DUEL && state != HVD_GUARD_COMBAT)) return;
    int hp = GetCurrentHitPoints(boss);
    int full = GetMaxHitPoints(boss);
    if (state == HVD_GUARD_DUEL && 100 * hp <= 23 * full)
    {
        HVD_GuardYield(boss);
        return;
    }
    if (state == HVD_GUARD_COMBAT && 2 * hp <= full && !GetLocalInt(HVD_Module(), "hvd_valks_complete"))
        HVD_CallValkyries(boss);

    object target = HVD_NearPlayer(boss, 40.0);
    if (!GetIsObjectValid(target)) return;
    if (GetLocalInt(boss, "hvd_cast"))
    {
        if (!GetLocalInt(boss, "hvd_aim")) HVD_NormalAttack(boss, target);
        return;
    }
    if (GetPosition(target).y < 30.0)
    {
        AssignCommand(boss, ClearAllActions());
        AssignCommand(boss, ActionMoveToLocation(GetLocalLocation(boss, "hvd_home"), TRUE));
        return;
    }
    AssignCommand(boss, ClearAllActions());
    int lane = HVD_Lane(GetPosition(target));
    int hard = state == HVD_GUARD_COMBAT;
    HVD_Cooldown(boss, hard ? 9.5 : 13.0, 3.1);
    HVD_MarkLane(GetArea(boss), lane);
    HVD_AreaMessage(GetArea(boss), "Ithrenova čepel rozsvítila výseč " + IntToString(lane) + ". Ustup za sloup nebo mimo značku.");
    DelayCommand(3.0, HVD_BossLane(boss, lane, state));
}

void HVD_AcceptRepair(object player)
{
    int state = HVD_GuardState();
    if ((state != HVD_GUARD_OFFER && state != HVD_GUARD_REPAIR) ||
        !HVD_PlayerIn(player, GetArea(HVD_Guardian()))) return;
    string tag = HVD_RepairKeyTag();
    if (!GetIsObjectValid(GetItemPossessedBy(player, tag)))
    {
        object key = CreateItemOnObject(HVD_ITHREN_KEY, player);
        if (!GetIsObjectValid(key))
        {
            SendMessageToPC(player, "Uvolni v inventáři místo pro Ithrenův klíč a zkus to znovu.");
            return;
        }
        SetTag(key, tag);
        SetLocalInt(key, "hvd_run", HVD_Run());
    }
    if (state == HVD_GUARD_REPAIR) return;
    SetLocalInt(HVD_Module(), "hvd_guard_state", HVD_GUARD_REPAIR);
    HVD_RepairJournals();
    HVD_TraceRepair();
}

void HVD_ReportRepair(object player)
{
    object module = HVD_Module();
    if (HVD_GuardState() != HVD_GUARD_REPAIR || !GetLocalInt(module, "hvd_repair_done") ||
        GetLocalInt(module, "hvd_won") || !HVD_PlayerIn(player, GetArea(HVD_Guardian()))) return;
    HVD_OpenPassage("hvd_won");
    HVD_OpenRewardStores();
    HVD_RepairJournals();
}
