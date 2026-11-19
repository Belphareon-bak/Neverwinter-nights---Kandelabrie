# Hvězdárna druhého nebe

Samostatný modul pro **Neverwinter Nights: Enhanced Edition** a postavy na **35.–40. úrovni**. Cesta vede od noclehu pod zasněženou kopulí přes dílny až na nebeské předbraní, kde hlídka stále odpovídá na odraz návratové lucerny. [Návrh a příběh](../README.md)

## Spuštění

1. Modul [Hvezdarna druheho nebe.mod](<Hvezdarna druheho nebe.mod>) patří do herní složky `modules` a [hvd_observatory.hak](hvd_observatory.hak) do `hak`. HAK obsahuje originální modely a materiály hvězdárny.
2. V klientu vyber **New → Local → Hvezdarna druheho nebe → Play**. Použij vlastní postavu nebo [Radana Hvězdáře na 38. úrovni](<Radan Hvezdar.bic>). Soubor `.bic` patří do `localvault`.
3. V noclehu si přečti **Rozpis nebeské hlídky**. Do hvězdárny vstoupíš přes značku na zemi v prahu kopule. Otevřené běžné přechody mají značku v dlažbě a fungují jako přechody základní kampaně. Do zjeveného světelného oblouku se vstupuje chůzí.

## Cesta hvězdárnou

| Oblast | Co na místě hledat |
| --- | --- |
| Výstupová římsa | Plátěný nocleh, rozpis hlídky, praporky v poryvu a vstup pod měděnou kopulí |
| Chodby clon | Tři pole výboje pod kamennými oblouky, výklenek obsluhy a odbočka na lávku |
| Dílny a servisní lávka | Zkouška zrcadla, návratový zápis, Kotva a zkratka do noclehu |
| Kopule | Mosazná mapa oblohy, refraktor a dva ruční ovladače clon |
| Schody do nebe | Dvě stoupání, rozpis u prvního schodu a bouřná podesta s Pečetí křídla |
| Visuté ochozy | Dvě kamenné lávky ke stanovištím Kopí a Lucerny |
| Předbraní | Tři patice pečetí, odpočívárna a schodiště k bráně |
| Poslední stupeň | Tři výseče, patice zkušebního zrcadla a clona návratové lucerny |

V kopuli se otáčí refraktor spolu s oběma ovladači. V předbraní přepínáš jednotlivé patice mezi donesenými pečetěmi a sestavu potvrdíš u ovladače pod schody. Správná kombinace zjeví světelnou bránu. Kniha nové výpravy v noclehu po druhém použití vylosuje další pořadí a výpravu obnoví.

## Úpravy a sestavení

Rozestavení a přechody jsou v [layout.py](../zdroje/layout.py), vlastní modely a textury v [art.py](../zdroje/art.py), předměty a stvůry v [content.py](../zdroje/content.py). [NWScriptové zdroje](../skripty/) jsou také uvnitř modulu. Čeština používá `cp1250`.

```bash
python3 ../zdroje/build.py --game "/cesta/k/Neverwinter Nights/game" \
  --compiler /cesta/k/nwn_script_comp --scripts ../skripty --output ./build
```

Sestavení čte dlaždice, přechody a statické herní zdroje ze základní instalace. Součástí vlastního HAKu jsou původní materiály určené pro zámecké dlaždice horních oblastí. Při integraci do světa zkontroluj sloučení tabulky `placeables.2da` a názvy textur. [Kompilátor NWScriptu](https://github.com/niv/neverwinter.nim/releases/tag/2.3.2)


## Ověření ve hře

V linuxovém NWN:EE 89.8193.37-17 jsem načetl všech osm oblastí. Kliknutí na zem otevřelo vchod do Chodeb clon a postava přešla přes dílnu až do kopule. Pohybové zkoušky prošly přes servisní lávku, obě ramena ochozů a všechna schodiště. Ovladače seřídily refraktor, chybné pečetě nechaly bránu zavřenou a správné pečetě ji zjevily. Ve zkušebním stavu závěru prošlo sklopení clony a obnovení výpravy s novým pořadím. Zkoušky se soustředily na trasu a mechanismy. Obtížnost střetů a napojení na K1 se tímto ověřením neposuzovaly. [Záběry z klienta](../podklady/nahledy.jpg)
