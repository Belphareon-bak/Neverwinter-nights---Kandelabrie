# Hvězdárna druhého nebe

Samostatný modul pro **Neverwinter Nights: Enhanced Edition** a postavy na **35.–40. úrovni**. Cesta vede od noclehu pod zasněženou kopulí přes dílny až na nebeské předbraní, kde hlídka stále odpovídá na odraz návratové lucerny. [Návrh a příběh](../README.md)

Ve verzi 8 rozsvěcí bránu soustava tří optických sloupů a závora se čtvrtou pečetí. Každá výprava má vlastní sestavu pečetí a clon. [Brána tří paprsků v klientu](../podklady/brana-tri-paprsku.jpg)

Schody do nebe stoupají po třech širokých ramenech s převýšením 15 metrů. Klenuté dílny, servisní kupole, měřicí podesty, visuté ochozy se signální věží a dvůr před branou patří k jednomu provozu. V chodbách a kopuli jsou čočky, mapy a lampy zasazené do stěn. Při průzkumu lze najít dvě vedlejší trasy, vlastní klapky a menší zásoby. [Prohlídka oblastí z v7](../podklady/nahledy.jpg)

## Spuštění

Při přechodu z dřívější verze vyměň `.mod` i `.hak` a založ novou výpravu z nabídky **New → Local**.

1. Modul [Hvezdarna druheho nebe.mod](<Hvezdarna druheho nebe.mod>) patří do herní složky `modules` a [hvd_observatory.hak](hvd_observatory.hak) do `hak`. HAK obsahuje originální modely a materiály hvězdárny.
2. V klientu vyber **New → Local → Hvezdarna druheho nebe → Play**. Použij vlastní postavu nebo [Radana Hvězdáře na 38. úrovni](<Radan Hvezdar.bic>). Soubor `.bic` patří do `localvault`.
3. V noclehu seber ze stolu **Rozpis nebeské hlídky** a otevři ho v inventáři přes **Prohlédnout** (**Examine**). Do hvězdárny vystoupej po cestě k prahu mezi zdmi průčelí. Do zjeveného světelného oblouku se vstupuje chůzí.

## Cesta hvězdárnou

| Oblast | Co na místě hledat |
| --- | --- |
| Výstupová římsa | Nocleh ve skalním závětří, stůl s rozpisem hlídky a vyhrnutá cesta na předpolí |
| Chodby clon | Příjmová síň, odbočka k dílnám a samostatná zděná chodba se třemi výbojovými poli |
| Dílny a servisní lávka | Optická zkušebna, kovárna a most k údržbářské kupoli s Pečetí kotvy |
| Kopule | Refraktor uprostřed, pracovní kouty při obvodu a dva pevné podstavce s pohyblivými ukazateli |
| Schody do nebe | Tři ramena schodů, rozpis u paty, orloj na měřicí podestě a stanoviště Křídla ve větrných vírech |
| Visuté ochozy | Dvě mostní ramena, strážnice Kopí a signální věž Lucerny |
| Předbraní | Tři optické sloupy, závora převodu a široké schodiště k Bráně tří paprsků |
| Poslední stupeň | Tři výseče, patice zkušebního zrcadla a návratová lucerna mezi klenutými stanovišti |

V kopuli se po seřízení otáčí objektiv a mosazné ukazatele na pevných stupnicích. Do předbraní dones všechny čtyři pečetě. Otevři inventář každého sloupu i závory a přesuň do něj jednu raznici. Páčkami na bocích sloupů nastav Srpek, Hvězdu a Slunce. Rozpis u noclehu, zápis na schodech a protokol na stole v předbraní určují sestavu. Nakonec zatáhni za spoušť u paty schodiště. Pult nové výpravy obnoví zápisy, obsah kontejnerů a stav mechanismů.

V dolní dílně hledej příruční schránku s klíčem u pracovního stolu. Klíč otevře správkynino pouzdro pod stejným přístřeškem při západním okraji. Přenosné zrcadlo má své pouzdro v téže zkušebně. Pasuje do patice vpravo pod schody na Posledním stupni a pomůže při závěrečném výboji. Kořist ber z inventářů truhlic. Běžné zásoby a poklady jsou společné pro družinu.

## Úpravy a sestavení

Půdorysy, přechody a interaktivní objekty jsou v [layout.py](../zdroje/layout.py). Výzdobu jednotlivých lokací určuje [dressing.py](../zdroje/dressing.py). Vlastní modely, textury a oblohu sestavují [art.py](../zdroje/art.py), [architecture.py](../zdroje/architecture.py) a [skies.py](../zdroje/skies.py). Schodiště, pochozí povrch a jejich kolize sestavuje [flights.py](../zdroje/flights.py). Tvary kolizí a body použití pro vlastní architekturu jsou v [collision.py](../zdroje/collision.py). Pečetě, jejich ikony, clony a paprsky sestavuje [gateart.py](../zdroje/gateart.py). Texty knih, předměty a stvůry jsou v [content.py](../zdroje/content.py). [NWScriptové zdroje](../skripty/) jsou také uvnitř modulu. Čeština používá `cp1250`.

```bash
python3 ../zdroje/build.py --game "/cesta/k/Neverwinter Nights/game" \
  --compiler /cesta/k/nwn_script_comp --scripts ../skripty --output ./build
```

Sestavení čte dlaždice, přechody a statické herní zdroje ze základní instalace. HAK doplňuje dvě dlaždice do `tcm02.set`. Při importu do Kandelábrie je třeba zachovat návaznost vlastních položek na `placeables.2da` a sloučit obě nové dlaždice s cílovou sadou. [Kompilátor NWScriptu](https://github.com/niv/neverwinter.nim/releases/tag/2.3.2)


## Zkušební list

Přepínač `--test-guide` při sestavení přidá schránku **TEST · Pouzdro s řešením brány**. Stojí vlevo po příchodu do předbraní, kousek před pultem pro výměnu pečetí. Zkušební list se bere do inventáře a čte přes **Prohlédnout** (**Examine**). Obsahuje přesnou sestavu právě rozehrané výpravy. Každá nová výprava doplní nový list. Běžné sestavení vzniká bez tohoto přepínače a navazuje na stejný HAK.

## Ověření ve hře

Přepočet všech 144 sestav prokázal jediné řešení pro každou trojici zápisů. V NWN:EE 89.8193.37-17 prošlo přetažení raznice do patice i její vyjmutí, přestavení clony, odmítnutí nesprávných pečetí a clon, zjevení brány a chůze na Poslední stupeň. Ověřil jsem i vydání náhradní pečeti a obnovu zkušebního listu při nové výpravě. [Záběr z otevření brány](../podklady/brana-tri-paprsku.jpg)
