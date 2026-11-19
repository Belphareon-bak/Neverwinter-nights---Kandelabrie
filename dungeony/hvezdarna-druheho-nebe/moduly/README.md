# Hvězdárna druhého nebe

Samostatný modul pro **Neverwinter Nights: Enhanced Edition** a postavy na **35.–40. úrovni**. Cesta vede od noclehu pod zasněženou kopulí přes dílny až na nebeské předbraní, kde hlídka stále odpovídá na odraz návratové lucerny. [Návrh a příběh](../README.md)

Od noclehu vede vyhrnutá cesta na kamenné předpolí pod kopulí. Zděné chodby spojují příjmovou síň, servisní odbočku a výstup do kopule. Dílenské přístřešky mají vlastní pracovní kouty po stranách přímého nástupu na most. [Záběry z NWN:EE](../podklady/nahledy.jpg)

## Spuštění

1. Modul [Hvezdarna druheho nebe.mod](<Hvezdarna druheho nebe.mod>) patří do herní složky `modules` a [hvd_observatory.hak](hvd_observatory.hak) do `hak`. HAK obsahuje originální modely a materiály hvězdárny.
2. V klientu vyber **New → Local → Hvezdarna druheho nebe → Play**. Použij vlastní postavu nebo [Radana Hvězdáře na 38. úrovni](<Radan Hvezdar.bic>). Soubor `.bic` patří do `localvault`.
3. V noclehu seber ze stolu **Rozpis nebeské hlídky** a otevři ho v inventáři přes **Prohlédnout** (**Examine**). Do hvězdárny vystoupej po cestě k prahu mezi zdmi průčelí. Do zjeveného světelného oblouku se vstupuje chůzí.

## Cesta hvězdárnou

| Oblast | Co na místě hledat |
| --- | --- |
| Výstupová římsa | Nocleh ve skalním závětří, stůl s rozpisem hlídky a vyhrnutá cesta na předpolí |
| Chodby clon | Příjmová síň, odbočka k dílnám a samostatná zděná chodba se třemi výbojovými poli |
| Dílny a servisní lávka | Zkušebna vlevo od příchodu, kovárna vpravo a most k údržbářské podestě s Pečetí kotvy |
| Kopule | Refraktor uprostřed, pracovní kouty při obvodu a dva pevné podstavce s pohyblivými ukazateli |
| Schody do nebe | Dvě schodiště, rozpis u prvního schodu a větrný vír u stanoviště Křídla |
| Visuté ochozy | Modře a zlatě značené mosty, strážnice Kopí a Lucerny |
| Předbraní | Tři patice pečetí, odpočívárna a schodiště k bráně s reliéfem dvou obloh |
| Poslední stupeň | Tři výseče, patice zkušebního zrcadla a návratová lucerna v otevřeném pavilonu |

V kopuli se po seřízení otáčí objektiv a mosazné ukazatele na pevných stupnicích. V předbraní přepínáš jednotlivé patice mezi donesenými pečetěmi a sestavu potvrdíš u ovladače pod schody. Správná kombinace zjeví světelnou bránu. Pult nové výpravy v noclehu po druhém použití vylosuje další pořadí, obnoví zápisy a doplní obsah kontejnerů.

V dolní dílně hledej příruční schránku s klíčem u pracovního stolu. Klíč otevře správkynino pouzdro pod stejným přístřeškem při západním okraji. Přenosné zrcadlo má své pouzdro v téže zkušebně. Pasuje do patice vpravo pod schody na Posledním stupni a pomůže při závěrečném výboji. Kořist ber z inventářů truhlic. Běžné zásoby a poklady jsou společné pro družinu.

## Úpravy a sestavení

Půdorysy, přechody a interaktivní objekty jsou v [layout.py](../zdroje/layout.py). Výzdobu jednotlivých lokací určuje [dressing.py](../zdroje/dressing.py). Vlastní modely, textury a oblohu sestavují [art.py](../zdroje/art.py), [architecture.py](../zdroje/architecture.py) a [skies.py](../zdroje/skies.py). Tvary kolizí a body použití pro vlastní architekturu jsou v [collision.py](../zdroje/collision.py). Texty knih, předměty a stvůry jsou v [content.py](../zdroje/content.py). [NWScriptové zdroje](../skripty/) jsou také uvnitř modulu. Čeština používá `cp1250`.

```bash
python3 ../zdroje/build.py --game "/cesta/k/Neverwinter Nights/game" \
  --compiler /cesta/k/nwn_script_comp --scripts ../skripty --output ./build
```

Sestavení čte dlaždice, přechody a statické herní zdroje ze základní instalace. Součástí vlastního HAKu jsou původní materiály určené pro zámecké dlaždice horních oblastí. Při integraci do světa zkontroluj sloučení tabulky `placeables.2da` a názvy textur. [Kompilátor NWScriptu](https://github.com/niv/neverwinter.nim/releases/tag/2.3.2)


## Ověření ve hře

V linuxovém NWN:EE 89.8193.37-17 prošly zkoušky chůzí přes všech 21 mezilokačních přechodů. U těch podmíněných byl při kontrole průchodnosti připravený odemčený stav. Samostatné zkoušky ověřily optiku, bránu, obnovení výpravy, klíč a inventář truhly, sebrání a otevření deníku a zasazení zrcadla. Záběry lokací zachycují všech osm oblastí se skrytým rozhraním. [Pohledy z lokací](../podklady/nahledy.jpg) · [Truhla, deník a zrcadlo v klientu](../podklady/inventar.jpg)
