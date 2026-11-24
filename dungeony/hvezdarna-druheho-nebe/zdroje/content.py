"""Original creatures, items, factions, and a ready-to-play local character."""

from aurora import SHORT, Record, bite, dword, flt, integer, loc, lst, ref, string, word
from furnishings import BOOK_MODELS
from gateart import SEAL_MODELS
from world import variables
from workart import MIRROR_MODEL


def prop(kind, sub=0, table=0, value=0):
    return Record(0, PropertyName=word(kind), Subtype=word(sub), CostTable=bite(table),
                  CostValue=word(value), Param1=bite(255), Param1Value=bite(255),
                  ChanceAppear=bite(100))


def item(key, base, name, description, *, properties=(), plot=0, model=1, stack=1, **style):
    fields = dict(
        TemplateResRef=ref(key), Tag=string(key), BaseItem=integer(base), LocalizedName=loc(name),
        Description=loc(description), DescIdentified=loc(description),
        Identified=bite(1), Cursed=bite(0), Stolen=bite(0), Charges=bite(0),
        Plot=bite(plot), StackSize=word(stack), Cost=dword(0), AddCost=dword(0),
        ModelPart1=bite(model), ModelPart2=bite(1), ModelPart3=bite(1),
        PropertiesList=lst(list(properties)), PaletteID=bite(0), Comment=string("Hvězdárna druhého nebe"),
    )
    fields.update({name: bite(value) for name, value in style.items()})
    return Record(**fields)


ARMOR = {
    "ArmorPart_Torso": 33, "ArmorPart_Pelvis": 6, "ArmorPart_Belt": 8, "ArmorPart_Neck": 4,
    "ArmorPart_LShoul": 6, "ArmorPart_RShoul": 6,
    "ArmorPart_LBicep": 7, "ArmorPart_RBicep": 7, "ArmorPart_LFArm": 1, "ArmorPart_RFArm": 1,
    "ArmorPart_LHand": 4, "ArmorPart_RHand": 4, "ArmorPart_LThigh": 9, "ArmorPart_RThigh": 9,
    "ArmorPart_LShin": 8, "ArmorPart_RShin": 8, "ArmorPart_LFoot": 5, "ArmorPart_RFoot": 5,
}

BOOKS = {
    "hvd_book_camp": ("Rozpis nebeské hlídky", 3,
        "Rozpis údržby. Kotva je v horní dílně, Křídlo na bouřné podestě a Kopí s Lucernou "
        "na visutých ochozech. Doneseme všechny čtyři raznice do předbraní. Tři pustí světlo do optických sloupů, "
        "čtvrtá zvedne závoru u spouště. Každá směna používá vlastní rozpis, aby se vedením nedalo projít naslepo.\n\n"
        "Od tábora nás cesta přivede k jediné bráně. Za ní se čeká na rozdělení služby. "
        "Dílna a lávka jsou vlevo, obsluha clon má průchod vpravo. Správkyně připomíná horní hlídce, "
        "že při pátrání po ztracené výstroji má prohlédnout i slepá závětří ve sněhu."),
    "hvd_book_study": ("Zápis správkyně o horní službě", 9,
        "Dnes vyjde hlídka k mostům služební štolou. Stejnopis Kotvy jsem nechala v pouzdře vedle stolu. "
        "Převod uzná jedinou Kotvu za celou směnu, ať je z dílny nebo odtud. Na mostech převezmou "
        "Kopí a Lucernu. Pro Křídlo se od paty mostů vrátí západním průchodem na Schody do nebe.\n\n"
        "Rozpis leží v táboře, zápis seřizovače u paty schodů a protokol u písaře v Předbraní. "
        "Severní závoru štoly po službě vždy vrať do kamene."),
    "hvd_book_steps": ("Zápis seřizovače na schodech", 7,
        "Na spodním stolku zůstala poznámka z poslední zkoušky. Při měření se díváme od nástupu "
        "k bráně. Po levé ruce máme západní sloup, po pravé východní. Písmenům na starých štítcích "
        "už nevěřím, ale znaky na okružích jsou pořád dobře čitelné."),
    "hvd_book_gate": ("Protokol o seřízení sloupů", 5,
        "Povolili jsme všechny tři páčky. V každém okruží má svítit jiný znak, Srpek, Hvězda nebo Slunce. "
        "Závora propouští převod i se čtvrtou raznicí a vlastní clonu nemá. Spoušť táhneme až po "
        "seřízení, když všichni stojí za mosazným značením. Zkoušku vadného vedení jsem si od minule odřel do kamene."),
    "hvd_book_halls": ("Předpis obsluhy clon", 2,
        "Vzkaz noční směně. Kamenný záchyt pojme světlo z jediné větve. Kdo tahá sklo v paprskové chodbě, "
        "nechá svítit levou kontrolku. Pro práci za ohybem zvol prostřední. K archivu patří pravá. "
        "Ověř si víčka na čočkách po cestě a pamatuj na družinu v ostatních pruzích. "
        "Při varovném záblesku ustup za příčnou rysku.\n\n"
        "Klíč od světelného servisu za ohybem nosí Ithren u Poslední lucerny. V přerušeném vedení je stále plno suti."),
    "hvd_book_return": ("Návratový zápis správkyně", 10,
        "Sestoupila jsem servisní lávkou a vrátila se do dolní dílny. V ohlašovně mě při výměně "
        "směn minuli. Doufám, že Ithren zahlédne můj zápis dřív, než začne hledat příčinu opakovaných záblesků. "
        "Lucernu jsem při odchodu nechala na posledním stupni.\n\n"
        "Klíč jsem uložila do schránky vedle zápisového pultu na straně k brusírně. Otevírá "
        "moje zamčené pouzdro v sousedním rohu brusírny. Směně v Chodbách clon jsem přepsala postup "
        "odstávky do sešitu na pultu ohlašovny. Značky odpovídají jednotlivým větvím na mosazném schématu."),
    "hvd_book_optic": ("Sešit o clonách a zrcadle", 8,
        "Objektiv po opravě stále mění odchylku. Před každou směnou odečti rysky na měřicí stupnici "
        "a zanes je do deníku v Kopuli. Po nastavení obou clon zkontroluj obraz v refraktoru.\n\n"
        "Pod severní stříškou vyšle spoušť paprsek přes pevné zrcadlo na stupnici. Přenosné zrcadlo z pouzdra "
        "u zápisového pultu je záloha pro hlídku. Stejnou patici najdeš na Posledním "
        "stupni vpravo od příchodu, ještě pod schodištěm. Přepne vedení do záchytu a odstaví "
        "sluneční výboje Poslední lucerny už z dolní podesty."),
    "hvd_book_dome": ("Deník hvězdárny", 4,
        "Po Čase potíží jsme k pozorovacímu sálu připojili obě křídla výstupové cesty. "
        "Ze zdejší kopule lze vidět dvě oblohy. Čistá část skla ukazuje naši horu a prasklina vrací "
        "světlo poslední lucerny z předbraní.\n\n"
        "Má-li se průchod ukázat celý, musejí se obrazy spojit. Nastav obě clony podle posledního měření. "
        "Až se světlo srovná, vystoupej severním obloukem za objektivem. U prvních schodů se cesta dělí. "
        "Po schodech najdeš Křídlo. Na východních římsách se drž vyšlapané stopy a hledej Kopí a Lucernu "
        "pod přístřešky hlídky. Obě výstupové cesty vedou do předbraní."),
    "hvd_book_top": ("Plán poslední hlídky", 6,
        "Za čárou ústupu začíná Ithrenova hlídka. Poutník bez nebeského znamení smí odejít k hoře "
        "nebo požádat o zkoušku. Pro případ poplachu jsme vedle lucerny upevnili páku odklonu. "
        "Paprsek musí dopadnout do kamenného záchytu. Stejný odklon lze zavést zkušebním zrcadlem "
        "v patici pod schody. Když lucerna žhne, její sluneční paprsek znovu udeří každé kolo."),
}


def items(*, test_guide=False, cloak_model=15):
    result = {}
    for key, (name, model, description) in BOOKS.items():
        result[key] = item(key, 74, name, description, model=BOOK_MODELS[model], plot=1)
    for ident, (name, model) in enumerate(zip(("Kotvy", "Křídla", "Kopí", "Lucerny"), SEAL_MODELS), 1):
        key = f"hvd_seal{ident}"
        result[key] = item(key, 24, f"Pečeť {name}", "Osmiboká mosazná raznice se znakem nebeské hlídky. "
                           "V předbraní otevři patici sloupu nebo závoru a přesuň do ní pečeť z inventáře.",
                           model=model)
    if test_guide:
        result["hvd_book_test"] = item("hvd_book_test", 74, "Zkušební list · řešení brány",
                                      "Pracovní list se sestavou pro aktuální výpravu.", model=6, plot=1)
    descriptors = [
        ("hvd_mirror", 24, "Přenosné zkušební zrcadlo",
         "Na Posledním stupni ho usaď do mosazné patice vpravo pod schody, dřív než se postavíš Ithrenovi. "
         "Odkloní světlo do kamenného záchytu a odstaví Poslední lucernu.", 1, MIRROR_MODEL, ()),
        ("hvd_workkey", 65, "Klíč správkyně clon",
         "Otevírá zamčené pouzdro pod stříškou v dolní dílně, u západního okraje podesty. "
         "Za jižní vstupní bránou se dej vlevo. Stříška stojí u pracovního stolu na konci podesty.", 1, 1, ()),
        ("hvd_ithrenkey", 65, "Ithrenův klíč ke světlovodu",
         "Kamenné dveře ve východní části Chodeb clon odemkne klíč, který ti svěřil Ithren po čestné zkoušce. "
         "Na hlavici je znak Poslední lucerny.", 1, 1, ()),
        ("hvd_glass", 77, "Broušené nebeské sklo", "Neporušený kus čočky z nebeského předbraní.", 0, 11, ()),
        ("hvd_brooch", 19, "Brož hvězdáře", "Chrání před mrazem a kouzlem slepoty a hluchoty.", 0, 2, (prop(23, 7, 7, 2), prop(53, 6))),
        ("hvd_badge", 19, "Spona strážce", "Připomínka hlídky, která čekala na poslední návrat.", 0, 3,
            (prop(1, 0, 2, 3), prop(40, 0, 2, 3))),
        ("hvd_sword", 1, "Adamantiový meč ozvěny +5", "Samostatná výstroj pro zkoušku větrných elementálů. "
         "Při zásahu nese také zvukové poškození.", 0, 1, (prop(6, 0, 2, 5), prop(16, 13, 4, 7), prop(85, 0, 28, 1))),
        ("hvd_shield", 14, "Štít horské výpravy +5", "Štít s vyrytým světlem noclehu.", 0, 3, (prop(1, 0, 2, 5),)),
        ("hvd_windskin", 73, "Složení z větru", "Zvuk rozkmitá vír.", 1, 0, (prop(24, 13, 22, 3),)),
        ("hvd_windhit", 71, "Náraz větru", "", 1, 0, (prop(16, 0, 4, 6),)),
        ("hvd_windhit2", 71, "Zesílený náraz větru", "", 1, 0, (prop(16, 0, 4, 12),)),
        ("hvd_winddart", 31, "Osten zvířeného kovu", "Úlomek vrhaný rukavicí prázdné zbroje.",
         1, 1, (prop(16, 1, 4, 6),)),
        ("hvd_spear", 10, "Kopí nebeské hlídky", "", 1, 1, (prop(6, 0, 2, 3),)),
        ("hvd_guardtorch", 15, "Svítilna nebeské hlídky", "", 1, 0, ()),
        ("hvd_resist", 52, "Prsten odolání větru", "Zásoba pro dlouhý výstup.", 0, 3, (prop(1, 0, 2, 3),)),
    ]
    for key, base, name, description, plot, model, properties in descriptors:
        result[key] = item(key, base, name, description, plot=plot, model=model, properties=properties)
    result["hvd_solarblade"] = item(
        "hvd_solarblade", 1, "Meč posledního stupně", "", plot=1,
        model=0, ModelPart2=0, ModelPart3=0,
        properties=(prop(6, 0, 2, 5), prop(16, 8, 4, 7)),
    )
    result["hvd_cloak"] = item(
        "hvd_cloak", 80, "Plášť dvojí oblohy",
        "Na temně modré látce je vyšita hvězdná obloha. Pomáhá přečkat výboje a vítr nad mraky.",
        model=cloak_model, Cloth1Color=135, Cloth2Color=139, Metal1Color=148, Metal2Color=165,
        Leather1Color=171, Leather2Color=132,
        properties=(prop(1, 0, 2, 3), prop(23, 13, 7, 2)),
    )
    result["hvd_armor"] = item(
        "hvd_armor", 16, "Zbroj horské výpravy +5", "Výstroj pro dlouhý výstup.",
        properties=(prop(1, 0, 2, 5),), Metal1Color=29, Metal2Color=22,
        Leather1Color=21, Cloth1Color=29, Cloth2Color=35, **ARMOR,
    )
    result["hvd_guardarmor"] = item(
        "hvd_guardarmor", 16, "Zbroj odrazu hlídky", "", plot=1,
        Metal1Color=26, Metal2Color=21, Leather1Color=18, Cloth1Color=4, Cloth2Color=8, **ARMOR,
    )
    result["hvd_solararmor"] = item(
        "hvd_solararmor", 16, "Zbroj posledního strážce", "", plot=1,
        Metal1Color=15, Metal2Color=14, Leather1Color=9, Cloth1Color=49, Cloth2Color=10, **ARMOR,
    )
    result["hvd_valkarmor"] = item(
        "hvd_valkarmor", 16, "Zbroj Jízdy Valkýr", "", plot=1,
        Metal1Color=148, Metal2Color=165, Leather1Color=171, Cloth1Color=139, Cloth2Color=82, **ARMOR,
    )
    # Use the stock potion property and bottle model. The prepared dose has its own name and resref.
    potion = item("hvd_heal", 49, "Nápoj zotavení", "Úplné uzdravení pro další výstup.",
                  properties=(prop(15, 139, 3, 1),), model=41)
    potion.fields.update(ModelPart2=bite(13), ModelPart3=bite(33))
    result["hvd_heal"] = potion
    return result


CREATURES = (
    ("hvd_strhavac", "Strhávač", "Zhuštěný vzduch se stáčí do prudkého víru.", 1, 52, 34, 35, 340, 24, 30, 18),
    ("hvd_vrhac", "Vrhač vírů", "Vítr drží pohromadě prázdnou zbroj staré hlídky. Z rukavic srší jiskry.",
     2, 100, 34, 34, 230, 19, 22, 20),
    ("hvd_spradac", "Spřádač proudů", "Proud se natahuje po nejbližším spojenci.", 3, 64, 35, 35, 270, 21, 20, 19),
    ("hvd_elit_strh", "Elitní Strhávač", "Nad podestou roste zhuštěný větrný vír.",
     1, 53, 38, 38, 460, 26, 34, 22),
    ("hvd_elit_vrhac", "Elitní Vrhač vírů", "Zbroj důstojníka staré hlídky nese větrný vír. Ocelové rukavice dopadají zprudka.",
     2, 100, 37, 37, 310, 22, 26, 22),
    ("hvd_elit_sprad", "Elitní Spřádač proudů", "Spřádá ochranné proudy nebeské hlídky.",
     3, 64, 38, 38, 350, 25, 22, 21),
    ("hvd_vir", "Bouřný vír", "Jádro drží tvar díky proudění mezi dvěma oblohami.",
     4, 53, 40, 40, 730, 26, 30, 22),
    ("hvd_kopi", "Kopiník z předbraní", "Odraz hlídky zapírá kopí o dlažbu.", 5, 6, 40, 40, 640, 27, 24, 18),
    ("hvd_svetlonos", "Světlonoš z předbraní", "Okřídlený příslušník hlídky vede družinu světlem lucerny.",
     6, 6, 40, 41, 560, 25, 21, 22),
    ("hvd_ithren", "Ithren, strážce posledního stupně", "Solar čeká na poslední návrat.",
     7, 6, 40, 44, 1050, 26, 30, 22),
    ("hvd_valkyra", "Valkýra nebeské jízdy", "Okřídlená elitní strážkyně odpovídá na rozkaz solara.",
     8, 6, 39, 39, 280, 23, 32, 26),
)

WHIRLWINDS = {
    "hvd_strhavac": (25, 12),
    "hvd_elit_strh": (30, 15),
    "hvd_vir": (45, 30),
}

CREATURE_FOLDER_ID = 180


def creature_palette():
    entries = [
        Record(0, NAME=string(name), RESREF=ref(key), CR=flt(cr),
               FACTION=string("Commoner" if role == 7 else "Hostile"))
        for key, name, description, role, appearance, level, cr, hp, armor, strength, dexterity in CREATURES
    ]
    folder = Record(0, NAME=string("Hvězdárna druhého nebe"), ID=bite(CREATURE_FOLDER_ID), LIST=lst(entries))
    return Record(MAIN=lst([folder]))


def creatures():
    result = {}
    for key, name, description, role, appearance, level, cr, hp, armor, strength, dexterity in CREATURES:
        elemental = role <= 4
        humanoid = appearance == 6
        equip = {
            1 << 16: "hvd_windhit2" if role in (1, 2) else "hvd_windhit",
            **({1 << 17: "hvd_windskin"} if elemental else {}),
        }
        if humanoid:
            armor_item = {7: "hvd_solararmor", 8: "hvd_valkarmor"}.get(role, "hvd_guardarmor")
            weapon = "hvd_solarblade" if role >= 6 else "hvd_spear"
            equip = {2: armor_item, 16: weapon}
            if role == 6:
                equip[32] = "hvd_guardtorch"
        feats = (2, 3, 4, 32, 45) if humanoid else (46,) if role == 2 else ()
        traits = {"role": role, "elite": int(key.startswith("hvd_elit_"))}
        if key in WHIRLWINDS:
            traits["whirlwind_dc"], traits["whirlwind_dice"] = WHIRLWINDS[key]
        if role == 3:
            traits["nature_caster_level"] = 40
        spells = (114, 169) if role == 3 else ()
        save_bonus = 5 if role in (1, 2, 3) else 0
        if key == "hvd_vir":
            save_bonus = 8
        result[key] = Record(
            TemplateResRef=ref(key), Tag=string(key), FirstName=loc(name), LastName=loc(""),
            Description=loc(description), Race=bite(16 if elemental else 20),
            Appearance_Type=word(appearance), Gender=bite(role == 8), Phenotype=integer(0),
            PortraitId=word(0), Conversation=ref(key if role == 7 else ""), IsPC=bite(0),
            FactionID=word(2 if role == 7 else 1),
            Disarmable=bite(0), Subrace=string(""), Deity=string("Helm" if role == 7 else ""),
            Wings=bite(2 if humanoid else 0), Tail=bite(0), SoundSetFile=word(0),
            Plot=bite(role == 7), Interruptable=bite(1), NoPermDeath=bite(0), BodyBag=bite(0),
            Appearance_Head=bite(16 if role == 7 else 5), Color_Skin=bite(3), Color_Hair=bite(17),
            Color_Tattoo1=bite(0), Color_Tattoo2=bite(0),
            Str=bite(strength), Dex=bite(dexterity), Con=bite(16), Int=bite(13), Wis=bite(14), Cha=bite(14),
            WalkRate=integer(0), NaturalAC=bite(armor),
            HitPoints=(SHORT, hp - level * 3), CurrentHitPoints=(SHORT, hp), MaxHitPoints=(SHORT, hp),
            refbonus=(SHORT, 4 + save_bonus), willbonus=(SHORT, 5 + save_bonus), fortbonus=(SHORT, 4 + save_bonus),
            GoodEvil=bite(100 if role >= 5 else 50), LawfulChaotic=bite(100 if role >= 5 else 50),
            ChallengeRating=flt(cr), CRAdjust=integer(0), PerceptionRange=bite(11),
            SkillList=lst([Record(0, Rank=bite(0)) for _ in range(28)]),
            FeatList=lst([Record(1, Feat=word(feat)) for feat in feats]),
            ClassList=lst([Record(2, Class=integer(4 if humanoid else 16 if elemental else 24),
                                        ClassLevel=(SHORT, level))]),
            Equip_ItemList=lst([Record(slot, EquippedRes=ref(name)) for slot, name in equip.items()]),
            ItemList=lst([]), TemplateList=lst([]),
            SpecAbilityList=lst([Record(4, Spell=word(spell), SpellFlags=bite(1), SpellCasterLevel=bite(15))
                                 for spell in spells]),
            ScriptSpawn=ref("hvd_cre_spawn"), ScriptHeartbeat=ref("hvd_cre_tick"),
            ScriptOnNotice=ref("hvd_cre_tick"), ScriptAttacked=ref("hvd_cre_tick"),
            ScriptDamaged=ref("hvd_cre_tick"), ScriptDeath=ref("hvd_cre_dead"),
            ScriptSpellAt=ref(""), ScriptDisturbed=ref(""), ScriptEndRound=ref(""),
            ScriptDialogue=ref("hvd_guard_talk" if role == 7 else ""), ScriptRested=ref(""),
            ScriptUserDefine=ref(""), ScriptOnBlocked=ref(""),
            VarTable=variables(**traits), PaletteID=bite(CREATURE_FOLDER_ID), Comment=string("Hvězdárna druhého nebe"),
        )
    result["hvd_suncaster"] = Record(
        TemplateResRef=ref("hvd_suncaster"), Tag=string("hvd_suncaster"),
        FirstName=loc("Poslední lucerna"), LastName=loc(""), Appearance_Type=word(569),
        Race=bite(9), Gender=bite(0), Phenotype=integer(0), FactionID=word(1), Plot=bite(1),
        IsPC=bite(0), Str=bite(10), Dex=bite(10), Con=bite(16), Int=bite(16), Wis=bite(30), Cha=bite(10),
        HitPoints=(SHORT, 125), CurrentHitPoints=(SHORT, 125), MaxHitPoints=(SHORT, 125),
        ClassList=lst([Record(2, Class=integer(2), ClassLevel=(SHORT, 26))]),
        ScriptHeartbeat=ref("hvd_lamp_pulse"), ItemList=lst([]), Equip_ItemList=lst([]),
    )
    return result


def factions():
    names = ["PC", "Hostile", "Commoner", "Merchant", "Defender"]
    factions = [Record(0, FactionParentID=dword(0xFFFFFFFF), FactionName=string(name), FactionGlobal=word(0))
                for name in names]
    relations = []
    for source in range(len(names)):
        for target in range(len(names)):
            relation = 100 if source == target else 50
            if source != target and 1 in (source, target):
                relation = 0
            relations.append(Record(0, FactionID1=dword(source), FactionID2=dword(target),
                                    FactionRep=dword(relation)))
    return Record(FactionList=lst(factions), RepList=lst(relations))


def hero(prototypes):
    """An original level 38 fighter with normal attacks and the module's expedition gear."""
    level = 38
    feats = [2, 3, 4, 10, 23, 26, 32, 42, 43, 45, 106, 144, 490, 636, 676, 754, 755, 756]
    fields = dict(
        FirstName=loc("Radan"), LastName=loc("Hvězdář"), IsPC=bite(1), IsDM=bite(0),
        Description=loc("Radan se vrací po stezce, po níž kdysi sestoupila poslední správkyně clon."),
        Tag=string(""), Conversation=ref(""), Gender=bite(0), Race=bite(6), Subrace=string(""),
        Age=integer(39), StartingPackage=bite(4), Deity=string("Helm"),
        Str=bite(26), Dex=bite(14), Con=bite(14), Int=bite(13), Wis=bite(10), Cha=bite(8),
        GoodEvil=bite(70), LawfulChaotic=bite(75), Gold=dword(1000), Experience=dword(703000),
        HitPoints=(SHORT, 306), CurrentHitPoints=(SHORT, 412), MaxHitPoints=(SHORT, 412),
        PregameCurrent=(SHORT, 412), BaseAttackBonus=bite(29), OverrideBAB=bite(0), ArmorClass=(SHORT, 46),
        RefSaveThrow=(1, 17), WillSaveThrow=(1, 15), FortSaveThrow=(1, 23),
        fortbonus=(SHORT, 0), refbonus=(SHORT, 0), willbonus=(SHORT, 0), NaturalAC=bite(0),
        Appearance_Type=word(6), Appearance_Head=bite(13), Phenotype=integer(0), Portrait=ref("po_hu_m_13_"),
        Color_Skin=bite(2), Color_Hair=bite(11), Color_Tattoo1=bite(0), Color_Tattoo2=bite(0),
        Wings=bite(0), Tail=bite(0), SoundSetFile=word(218), MovementRate=bite(0), FactionID=word(0),
        ChallengeRating=flt(38), Plot=bite(0), IsImmortal=bite(0), NoPermDeath=bite(0),
        IsDestroyable=bite(1), IsRaiseable=bite(1), IsCommandable=bite(1),
        Disarmable=bite(1), Interruptable=bite(1), CorpseDecayTime=dword(5000),
        TemplateResRef=ref(""), ClassList=lst([Record(2, Class=integer(4), ClassLevel=(SHORT, level))]),
        FeatList=lst([Record(1, Feat=word(feat)) for feat in feats]), SkillPoints=word(0),
    )
    ranks = {2: 28, 3: 13, 5: 41, 6: 20, 10: 20, 16: 20, 17: 20, 20: 20, 21: 20}
    fields["SkillList"] = lst([Record(0, Rank=bite(ranks.get(index, 0))) for index in range(30)])
    fields["LvlStatList"] = lst([
        Record(0, LvlStatClass=bite(4), LvlStatHitDie=bite(10 if index == 1 else 8),
               EpicLevel=bite(index > 20), SkillPoints=word(0),
               SkillList=lst([Record(0, Rank=bite(0)) for _ in range(30)]), FeatList=lst([]))
        for index in range(1, level + 1)
    ])
    for name in ("Neck", "Torso", "Pelvis", "LBicep", "LFArm", "LHand", "LThigh", "LShin", "LFoot",
                 "RBicep", "RFArm", "RHand", "RThigh", "RShin", "RFoot"):
        fields[f"BodyPart_{name}"] = bite(1)

    def owned(key, slot, position=None, quantity=1):
        data = dict(prototypes[key].fields, ObjectId=dword(230 + slot), StackSize=word(quantity),
                    Dropable=bite(1), Pickpocketable=bite(0), XPosition=flt(0), YPosition=flt(0), ZPosition=flt(0),
                    XOrientation=flt(1), YOrientation=flt(0), ZOrientation=flt(0))
        if position:
            data.update(Repos_PosX=word(position[0]), Repos_Posy=word(position[1]))
        return Record(slot, **data)

    fields["Equip_ItemList"] = lst([owned("hvd_armor", 2), owned("hvd_sword", 16),
                                  owned("hvd_shield", 32), owned("hvd_resist", 128)])
    fields["ItemList"] = lst([owned("hvd_heal", 0, (0, 0), 8)])
    fields["QBList"] = lst([])
    return Record(**fields)
