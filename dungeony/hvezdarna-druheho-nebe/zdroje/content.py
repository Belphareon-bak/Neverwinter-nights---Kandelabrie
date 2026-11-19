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
        "čtvrtá zvedne závoru u spouště. Každá směna používá vlastní rozpis, aby se vedením nedalo projít naslepo."),
    "hvd_book_steps": ("Zápis seřizovače na schodech", 7,
        "Na spodním stolku zůstala poznámka z poslední zkoušky. Při měření se díváme od nástupu "
        "k bráně. Po levé ruce máme západní sloup, po pravé východní. Písmenům na starých štítcích "
        "už nevěřím, ale znaky na okružích jsou pořád dobře čitelné."),
    "hvd_book_gate": ("Protokol o seřízení sloupů", 5,
        "Povolili jsme všechny tři páčky. V každém okruží má svítit jiný znak, Srpek, Hvězda nebo Slunce. "
        "Závora propouští převod i se čtvrtou raznicí a vlastní clonu nemá. Spoušť táhneme až po "
        "seřízení, když všichni stojí za mosazným značením. Zkoušku vadného vedení jsem si od minule odřel do kamene."),
    "hvd_book_halls": ("Předpis obsluhy clon", 2,
        "Při zkoušce filtru se od stěny ke stěně rozbíhá světlý pruh. Jakmile je na kameni vidět, "
        "ustup za mosaznou rysku a počkej na doznění výboje. Pojistka visí u vstupu do paprskové chodby "
        "v dolní příjmové síni. Poškozenou západku pomůže uvolnit návod uložený v dolní dílně.\n\n"
        "Z kalibračních tabulek se v archivu zvedá prach i ve dnech bez větru. Správkyně v posledním hlášení "
        "prosila, aby hlídka nepodkládala mosaznou zarážku pod jejich rámem."),
    "hvd_book_study": ("Zápis z kalibrační komory", 9,
        "Zkusila jsem na severní stěně srovnat obě štěrbiny. Mezi komorou a kopulí jsou dvě clony "
        "na jediném převodu. Mosazný uzávěr u skříně je stáhne zároveň. Do kopule se pak vracím "
        "úzkým průlezem v pravém rohu. Po zalomení průlezu narazím na zadní stěnu kopule.\n\n"
        "Při kontrole prvního schodu jsem se vyhnula hlídce po spodním můstku. Za západní opěrou "
        "visí protizávaží krytu. Před přechodem lávky vždy zajisti malou větrnou klapku. "
        "Pod obloukem se proud stáčí do prostoru, kde člověk nemá kam uhnout."),
    "hvd_book_return": ("Návratový zápis správkyně", 10,
        "Sestoupila jsem servisní lávkou a vrátila se do dolní dílny. V ohlašovně mě při výměně "
        "směn minuli. Doufám, že Ithren zahlédne můj zápis dřív, než začne hledat příčinu opakovaných záblesků. "
        "Lucernu jsem při odchodu nechala na posledním stupni.\n\n"
        "Klíč jsem uložila do schránky u pracovního stolu v dolní dílně. Otevírá moje zamčené pouzdro "
        "pod toutéž stříškou, při západním okraji podesty. Ruční pojistka v Chodbách clon se při zaseknutí "
        "odlehčí stlačením ramene. Pak zavře všechny tři vysílače."),
    "hvd_book_optic": ("Sešit o clonách a zrcadle", 8,
        "Objektiv po opravě stále táhne na východ. Při příštím měření nastav na západním podstavci "
        "rysku II a na východním rysku III. Pak zkontroluj obraz v refraktoru uprostřed kopule.\n\n"
        "Spoušť u stolu tyhle hodnoty ukáže na skle za pevným zrcadlem. Přenosné zrcadlo z pouzdra ve zkušebně je záloha pro hlídku. Stejnou patici najdeš na Posledním "
        "stupni vpravo od příchodu, ještě pod prvním schodištěm. Zrcadlo tam umí jednou zachytit druhý "
        "z Ithrenových závěrečných výbojů a přidá čas na sklopení clony."),
    "hvd_book_dome": ("Deník hvězdárny", 4,
        "Po Čase potíží jsme nad horskou římsou dokončili průchod pro návrat služební hlídky. "
        "Ze zdejší kopule lze vidět dvě oblohy. Čistá část skla ukazuje naši horu a prasklina vrací "
        "světlo poslední lucerny z předbraní.\n\n"
        "Má-li se průchod ukázat celý, musejí se obrazy spojit. Dílenské nastavení je vyznačené u "
        "obou podstavců. Až se světlo srovná, vystoupej severním obloukem za objektivem."),
    "hvd_book_top": ("Plán poslední hlídky", 6,
        "Hlídka vystupuje k lucerně ve třech výsečích. Před výbojem se na podlaze vyznačí dráha. "
        "Z té ustup za kamennou clonu nebo do sousední výseče. Zkušební zrcadlo pasuje do "
        "mosazné patice vpravo pod schody. Až Ithren odstoupí, je potřeba sklopit clonu u samotné lucerny."),
}


def items(*, test_guide=False):
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
         "Zachytí jeden výboj a dá družině víc času doběhnout ke cloně návratové lucerny.", 1, MIRROR_MODEL, ()),
        ("hvd_workkey", 65, "Klíč správkyně clon",
         "Otevírá zamčené pouzdro pod stříškou v dolní dílně, u západního okraje podesty. "
         "Po příchodu z Chodeb clon tu stříšku uvidíš vlevo.", 1, 1, ()),
        ("hvd_glass", 77, "Broušené nebeské sklo", "Neporušený kus čočky z nebeského předbraní.", 0, 11, ()),
        ("hvd_brooch", 19, "Brož hvězdáře", "Chrání před mrazem a kouzlem slepoty a hluchoty.", 0, 2, (prop(23, 7, 7, 2), prop(53, 6))),
        ("hvd_cloak", 80, "Plášť dvojí oblohy", "Pomáhá přečkat výboje a vítr nad mraky.", 0, 1, (prop(1, 0, 2, 3), prop(23, 13, 7, 2))),
        ("hvd_badge", 19, "Spona strážce", "Připomínka hlídky, která čekala na poslední návrat.", 0, 3,
         (prop(1, 0, 2, 3), prop(40, 0, 2, 3))),
        ("hvd_sword", 1, "Adamantiový meč ozvěny +5", "Samostatná výstroj pro zkoušku větrných elementálů. "
         "Při zásahu nese také zvukové poškození.", 0, 1, (prop(6, 0, 2, 5), prop(16, 13, 4, 7), prop(85, 0, 28, 1))),
        ("hvd_shield", 14, "Štít horské výpravy +5", "Štít s vyrytým světlem noclehu.", 0, 3, (prop(1, 0, 2, 5),)),
        ("hvd_windskin", 73, "Složení z větru", "Zvuk rozkmitá vír.", 1, 0, (prop(24, 13, 22, 3),)),
        ("hvd_windhit", 71, "Náraz větru", "", 1, 0, (prop(16, 0, 4, 6),)),
        ("hvd_spear", 10, "Kopí nebeské hlídky", "", 1, 1, (prop(6, 0, 2, 3),)),
        ("hvd_solarblade", 1, "Meč posledního stupně", "", 1, 1, (prop(6, 0, 2, 5), prop(16, 8, 4, 7))),
        ("hvd_resist", 52, "Prsten odolání větru", "Zásoba pro dlouhý výstup.", 0, 3, (prop(1, 0, 2, 3),)),
    ]
    for key, base, name, description, plot, model, properties in descriptors:
        result[key] = item(key, base, name, description, plot=plot, model=model, properties=properties)
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
    # Use the stock potion property and bottle model. The prepared dose has its own name and resref.
    potion = item("hvd_heal", 49, "Nápoj zotavení", "Úplné uzdravení pro další výstup.",
                  properties=(prop(15, 139, 3, 1),), model=41)
    potion.fields.update(ModelPart2=bite(13), ModelPart3=bite(33))
    result["hvd_heal"] = potion
    return result


CREATURES = (
    ("hvd_strhavac", "Strhávač", "Zhuštěný vzduch stahuje prach do úzké dráhy.", 1, 52, 31, 150, 15, 24, 18),
    ("hvd_vrhac", "Vrhač vírů", "Uvnitř víru se zableskne, než vyšle další proud.", 2, 106, 28, 112, 13, 20, 20),
    ("hvd_spradac", "Spřádač proudů", "Proud se natahuje po nejbližším spojenci.", 3, 64, 29, 125, 13, 20, 19),
    ("hvd_vir", "Bouřný vír", "Jádro drží tvar díky proudění mezi dvěma oblohami.", 4, 53, 38, 355, 20, 28, 22),
    ("hvd_kopi", "Kopiník z předbraní", "Odraz hlídky zapírá kopí o dlažbu.", 5, 6, 36, 240, 16, 24, 18),
    ("hvd_svetlonos", "Světlonoš z předbraní", "Odraz nebeské hlídky nese světlo na ochoz.", 6, 103, 36, 205, 16, 21, 22),
    ("hvd_ithren", "Ithren, strážce posledního stupně", "Solar čeká na poslední návrat.", 7, 6, 40, 610, 19, 30, 22),
)


def creatures():
    result = {}
    for key, name, description, role, appearance, level, hp, armor, strength, dexterity in CREATURES:
        elemental = role <= 4
        humanoid = appearance == 6
        equip = {
            1 << 16: "hvd_windhit",
            **({1 << 17: "hvd_windskin"} if elemental else {}),
        }
        if humanoid:
            equip = {2: "hvd_solararmor" if role == 7 else "hvd_guardarmor",
                     16: "hvd_solarblade" if role == 7 else "hvd_spear"}
        feats = (2, 3, 4, 32, 45) if humanoid else ()
        result[key] = Record(
            TemplateResRef=ref(key), Tag=string(key), FirstName=loc(name), LastName=loc(""),
            Description=loc(description), Race=bite(16 if elemental else 20),
            Appearance_Type=word(appearance), Gender=bite(0), Phenotype=integer(0),
            PortraitId=word(0), Conversation=ref(""), IsPC=bite(0), FactionID=word(1),
            Disarmable=bite(0), Subrace=string(""), Deity=string("Helm" if role == 7 else ""),
            Wings=bite(2 if humanoid else 0), Tail=bite(0), SoundSetFile=word(0),
            Plot=bite(0), Interruptable=bite(1), NoPermDeath=bite(0), BodyBag=bite(0),
            Appearance_Head=bite(16 if role == 7 else 5), Color_Skin=bite(3), Color_Hair=bite(17),
            Color_Tattoo1=bite(0), Color_Tattoo2=bite(0),
            Str=bite(strength), Dex=bite(dexterity), Con=bite(16), Int=bite(13), Wis=bite(14), Cha=bite(14),
            WalkRate=integer(0), NaturalAC=bite(armor),
            HitPoints=(SHORT, hp - level * 3), CurrentHitPoints=(SHORT, hp), MaxHitPoints=(SHORT, hp),
            refbonus=(SHORT, 4), willbonus=(SHORT, 5), fortbonus=(SHORT, 4),
            GoodEvil=bite(100 if role >= 5 else 50), LawfulChaotic=bite(100 if role >= 5 else 50),
            ChallengeRating=flt(level - (4 if role <= 3 else 0)), CRAdjust=integer(0), PerceptionRange=bite(11),
            SkillList=lst([Record(0, Rank=bite(0)) for _ in range(28)]),
            FeatList=lst([Record(1, Feat=word(feat)) for feat in feats]),
            ClassList=lst([Record(2, Class=integer(4 if humanoid else 16 if elemental else 24),
                                        ClassLevel=(SHORT, level))]),
            Equip_ItemList=lst([Record(slot, EquippedRes=ref(name)) for slot, name in equip.items()]),
            ItemList=lst([]), TemplateList=lst([]), SpecAbilityList=lst([]),
            ScriptSpawn=ref("hvd_cre_spawn"), ScriptHeartbeat=ref("hvd_cre_tick"),
            ScriptOnNotice=ref("hvd_cre_tick"), ScriptAttacked=ref("hvd_cre_tick"),
            ScriptDamaged=ref("hvd_cre_tick"), ScriptDeath=ref("hvd_cre_dead"),
            ScriptSpellAt=ref(""), ScriptDisturbed=ref(""), ScriptEndRound=ref(""),
            ScriptDialogue=ref(""), ScriptRested=ref(""), ScriptUserDefine=ref(""), ScriptOnBlocked=ref(""),
            VarTable=variables(role=role), PaletteID=bite(0), Comment=string("Hvězdárna druhého nebe"),
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
