# Hvězdárna druhého nebe

Samostatný modul pro **Neverwinter Nights: Enhanced Edition** a postavy na **35.–40. úrovni**. Cesta vede od noclehu pod zasněženou kopulí přes dílny až na nebeské předbraní, kde hlídka stále odpovídá na odraz návratové lucerny. [Návrh a příběh](../README.md)

Ve verzi 7 stoupají Schody do nebe po třech širokých ramenech s převýšením 15 metrů. Klenuté dílny, servisní kupole, měřicí podesty, visuté ochozy se signální věží a dvůr před branou patří k jednomu provozu. V chodbách a kopuli jsou čočky, mapy a lampy zasazené do stěn. Při průzkumu lze najít dvě vedlejší trasy, vlastní klapky a menší zásoby. [Záběry z NWN:EE](../podklady/nahledy.jpg)

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
| Předbraní | Dvůr tří patic, zázemí hlídky a široké schodiště k bráně |
| Poslední stupeň | Tři výseče, patice zkušebního zrcadla a návratová lucerna mezi klenutými stanovišti |

V kopuli se po seřízení otáčí objektiv a mosazné ukazatele na pevných stupnicích. V předbraní přepínáš jednotlivé patice mezi donesenými pečetěmi a sestavu potvrdíš u ovladače pod schody. Správná kombinace zjeví světelnou bránu. Pult nové výpravy v noclehu po druhém použití vylosuje další pořadí, obnoví zápisy, doplní obsah kontejnerů a uzavře servisní clony.

V dolní dílně hledej příruční schránku s klíčem u pracovního stolu. Klíč otevře správkynino pouzdro pod stejným přístřeškem při západním okraji. Přenosné zrcadlo má své pouzdro v téže zkušebně. Pasuje do patice vpravo pod schody na Posledním stupni a pomůže při závěrečném výboji. Kořist ber z inventářů truhlic. Běžné zásoby a poklady jsou společné pro družinu.

## Úpravy a sestavení

Půdorysy, přechody a interaktivní objekty jsou v [layout.py](../zdroje/layout.py). Výzdobu jednotlivých lokací určuje [dressing.py](../zdroje/dressing.py). Vlastní modely, textury a oblohu sestavují [art.py](../zdroje/art.py), [architecture.py](../zdroje/architecture.py) a [skies.py](../zdroje/skies.py). Schodiště, pochozí povrch a jejich kolize sestavuje [flights.py](../zdroje/flights.py). Tvary kolizí a body použití pro vlastní architekturu jsou v [collision.py](../zdroje/collision.py). Texty knih, předměty a stvůry jsou v [content.py](../zdroje/content.py). [NWScriptové zdroje](../skripty/) jsou také uvnitř modulu. Čeština používá `cp1250`.

```bash
python3 ../zdroje/build.py --game "/cesta/k/Neverwinter Nights/game" \
  --compiler /cesta/k/nwn_script_comp --scripts ../skripty --output ./build
```

Sestavení čte dlaždice, přechody a statické herní zdroje ze základní instalace. HAK doplňuje dvě dlaždice do `tcm02.set`. Při importu do Kandelábrie je třeba zachovat návaznost vlastních položek na `placeables.2da` a sloučit obě nové dlaždice s cílovou sadou. [Kompilátor NWScriptu](https://github.com/niv/neverwinter.nim/releases/tag/2.3.2)


## Ověření ve hře

V linuxovém NWN:EE 89.8193.37-17 jsem ověřil chůzi přes původní přechody, všechna tři ramena hlavního schodiště, obě ramena ochozů a průchod oběma směry přes nové odbočky. Zkoušky zahrnuly odemknutí skrytých vstupů, aktivní poryv a jeho odstavení, truhlice, čtení nalezeného záznamu, optiku, správné i chybné pořadí pečetí a obnovu výpravy. Záběry ukazují lokace v herním klientu se skrytým rozhraním. [Pohledy z lokací](../podklady/nahledy.jpg)
