# Hvězdárna druhého nebe

Samostatný modul pro **Neverwinter Nights: Enhanced Edition** a postavy na **35.–40. úrovni**. Verze 12 staví dva výstupové okruhy kolem pozorovací Kopule. Nová výprava začíná v Horském táboře. Jediná stezka vede na Výstupovou římsu, kde se cesta rozdělí k hlavnímu vstupu do Zkušebny a k vedlejšímu vchodu do Chodeb clon. Nad Kopulí je cesta rozdělená mezi zalomená schodiště a dvojici visutých mostů. Obě horní ramena se setkají u dvora pečetí. [Původní návrh a příběh](../README.md)

## Spuštění

1. [Modul](<Hvezdarna druheho nebe.mod>) patří do složky `modules` a [hvd_obs_v12.hak](hvd_obs_v12.hak) do složky `hak` v profilu Neverwinter Nights.
2. Založ novou výpravu přes **New → Local → Hvezdarna druheho nebe → Play**. Použij vlastní postavu nebo [Radana Hvězdáře na 38. úrovni](<Radan Hvezdar.bic>). Soubor `.bic` patří do `localvault`.
3. V noclehu seber ze stolu **Rozpis nebeské hlídky**. V inventáři ho otevři přes **Prohlédnout** (**Examine**).

## Mapa průchodů

Všechny oblasti jsou na jednom půdorysu se společným směrem na sever. Jeden čtvereček je **1 × 1 v Toolsetu**, tedy **10 × 10 m**. Čísla 00–09 označují prahy na společných hranách. Vedle každého půdorysu jsou jeho rozměry. [Hráčská mapa](../podklady/mapa-hvezdarny.png) · [Úplný půdorys včetně tajných cest](../podklady/mapa-hvezdarny-vsechny-lokace.png) · [Tiskové PDF](../podklady/mapa-hvezdarny.pdf)

## Cesta hvězdárnou

- **Dolní okruh · 35–37.** Z rozcestí na Výstupové římse vede hlavní vstup do Zkušebny. Od optiky vystoupej po servisní lávce na horní dvůr dílen. Z něj se můžeš přes archiv a Chodby clon vrátit na rozcestí. Z horní dílny vede zároveň samostatný severní vstup do Kopule. Na horní podestě vyzvedni **Pečeť kotvy**.
- **Kopule.** Seřiď dva podstavce a zkontroluj obraz v refraktoru. Modrý paprsek od objektivu rozsvítí severní průchod ke Schodům do nebe.
- **Horní okruh · 38–40.** Od paty schodů stoupá západní trasa po třech střídavě položených schodištích přes bouřnou podestu s **Pečetí křídla**. Východní trasa vede na dva Visuté ochozy. Tam hlídka drží **Pečeť kopí** a **Pečeť lucerny**. Obě ramena vystoupají o 15 metrů ke svému vstupu do Předbraní a spojí se u optického dvora.
- **Předbraní a Poslední stupeň.** Přesuň čtyři pečetě do inventářů sloupů a závory. Páčkami nastav v každém sloupu jiný znak. Rozpis v táboře, zápis na schodech a protokol u písaře určují sestavu. Po otevření brány pokračuj na Poslední stupeň. Po sklopení clony u Ithrenovy lucerny si vyber odměnu a sestup přes Předbraní.

V dolní dílně je u zkušebního stolu příruční schránka s klíčem. Otevře správkynino pouzdro pod stejným přístřeškem. Přenosné zrcadlo ze zkušebny pomůže při závěrečném výboji. Na Posledním stupni je patice vpravo od nástupu, pod úrovní horní podesty.

### Služební průchody pro úrovně 38 a vyšší

Tuto část si rozbal při zkoušení tajných cest.

<details>
<summary>Hledání Pracovny a výstupu na Visuté ochozy</summary>

- Na římse obejdi zasněžené výčnělky na východním konci. V závětří u slepé skalní stěny použij režim **Hledání**. Druhý vstup odhalí Hledání u registrů ve východním křídle Chodeb clon.
- V Pracovně je u stolu archivní stejnopis Pečeti kotvy. Pouzdro vydá stejnou raznici jako Dílny a pro celou výpravu platí jedna Kotva. Ze stolu lze sebrat zápis správkyně.
- Odjisti páku na severním konci služební chodby a dojdi pěšky na Visuté ochozy. Křídlo získáš přes západní návrat na Schody do nebe. Kopí a Lucerna jsou u horních mostních podest. Pro bránu stále potřebuješ všechny čtyři pečetě a stopy v zápisech.

</details>

### Ovládání v dolní části

- **Pojistka paprskové chodby** v příjmové síni zavře tři clony a vypne jejich světelné pasti do konce výpravy. Západku lze uvolnit se Zneškodňováním pastí 15 nebo po sebrání Sešitu o clonách a zrcadle či Návratového zápisu správkyně v dolní dílně.
- **Spoušť zkušební optiky** u pracovního stolu vyšle paprsek přes pevné zrcadlo. Odraz na měřicí stupnici na chvíli rozsvítí polohy západní a východní clony pro seřízení v kopuli.
- **Ozvučnice servisní lávky** stojí na horní podestě u výstupu z mostu. Jednou za vlnu zasáhne nejbližšího viditelného větrného elementála v dosahu 18 metrů za 64 bodů zvukového poškození před úpravou odolností. Úder naprázdno ji nevyčerpá.

## Návrh a sestavení

Společnou síť, rozměry, půdorysy a směry určuje [plan.py](../zdroje/plan.py). Podle něj vznikají dlaždice a přechody v [layout.py](../zdroje/layout.py), [interiors.py](../zdroje/interiors.py) a [routes.py](../zdroje/routes.py). Výzdobu podest a chodeb skládá [dressing.py](../zdroje/dressing.py). [Kreslič mapy](../zdroje/mapa_hvezdarny.py) umí ověřit rozměry, prahy, polohu a natočení příchodů i návaznost výšek v hotovém modulu.

```bash
python3 ../zdroje/build.py --game "/cesta/k/Neverwinter Nights/game" \
  --compiler /cesta/k/nwn_script_comp --scripts ../skripty --output ./build
python3 ../zdroje/mapa_hvezdarny.py --module "./build/Hvezdarna druheho nebe.mod" \
  --output ./build/mapa-hvezdarny.pdf
```

Sestavení čte základní herní prostředky z místní instalace. HAK doplňuje dlaždice do `tcm02.set` a přidává interiérovou sadu `hvd_interior.set`. Kreslič mapy používá ReportLab a písmo DejaVu Sans. Pro PNG potřebuje také Poppler. Přepínač `--player-map` kreslí hráčskou mapu bez tajných cest. [Kompilátor NWScriptu](https://github.com/niv/neverwinter.nim/releases/tag/2.3.2)

## Zkušební list

Přepínač `--test-guide` při sestavení přidá schránku **TEST · Pouzdro s řešením brány**. Stojí na jižním dvoře Předbraní u pultu pro výměnu pečetí. Zkušební list se bere do inventáře a čte přes **Prohlédnout** (**Examine**). Obsahuje přesnou sestavu právě rozehrané výpravy. Každá nová výprava doplní nový list. Běžné sestavení vzniká bez tohoto přepínače a navazuje na stejný HAK.

## Ověření ve hře

V klientu NWN:EE jsem prošel oběma okruhy včetně obou mostů a zkontroloval všech 26 směrů průchodu. Postava na 38. úrovni našla oba skryté vstupy v režimu Hledání, vyzvedla jednu platnou Kotvu a došla služební chodbou na Ochozy. Postava na 37. úrovni zůstala ve výchozí lokaci i po jeho odkrytí. Ověřil jsem chybný a platný stav refraktoru i brány, příchod na Poslední stupeň, sklopení clony a obnovu zakrytí při nové výpravě. Chůzi jsem ověřoval v připraveném stavu výpravy a clonu zkoušel v okamžiku, kdy je po střetu přístupná.

Pásma obtížnosti jsou vodítkem při návrhu okruhů. Jejich herní vyvážení má vlastní zkušební výpravu.

[Rozcestí](../podklady/v12-rozcesti.jpg) · [Horní schodiště](../podklady/v12-schodiste.jpg) · [Kopule](../podklady/v12-kopule.jpg) · [Ithren](../podklady/v12-ithren.jpg)

### Starší verze

[Ithren a paprsek ve verzi 11](../podklady/ithren-lucerna-v11.jpg)

### Ověření brány ve verzi 8

Přepočet všech 144 sestav prokázal jediné řešení pro každou trojici zápisů. V NWN:EE 89.8193.37-17 prošlo přetažení raznice do patice i její vyjmutí, přestavení clony, odmítnutí nesprávných pečetí a clon, zjevení brány a chůze na Poslední stupeň. Ověřil jsem i vydání náhradní pečeti a obnovu zkušebního listu při nové výpravě. [Záběr z otevření brány](../podklady/brana-tri-paprsku.jpg)
