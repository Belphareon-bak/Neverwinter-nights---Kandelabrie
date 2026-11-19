# Hvězdárna druhého nebe

Samostatný modul pro **Neverwinter Nights: Enhanced Edition** a postavy na **35.–40. úrovni**. Cesta vede od noclehu pod zasněženou kopulí přes dílny až na nebeské předbraní, kde hlídka stále odpovídá na odraz návratové lucerny. [Návrh a příběh](../README.md)

Aktuální sestava má 1 741 umístěných objektů v osmi oblastech. Přibyly nosné oblouky, dílenské přístřešky, pracovní kouty, prstencové modely oblohy a dva skyboxy pro horskou římsu a horní terasy. [Záběry z NWN:EE](../podklady/nahledy.jpg)

## Spuštění

1. Modul [Hvezdarna druheho nebe.mod](<Hvezdarna druheho nebe.mod>) patří do herní složky `modules` a [hvd_observatory.hak](hvd_observatory.hak) do `hak`. HAK obsahuje originální modely a materiály hvězdárny.
2. V klientu vyber **New → Local → Hvezdarna druheho nebe → Play**. Použij vlastní postavu nebo [Radana Hvězdáře na 38. úrovni](<Radan Hvezdar.bic>). Soubor `.bic` patří do `localvault`.
3. V noclehu si přečti **Rozpis nebeské hlídky**. Do hvězdárny vstoupíš přes značku na zemi v prahu kopule. Otevřené běžné přechody mají značku v dlažbě a fungují jako přechody základní kampaně. Do zjeveného světelného oblouku se vstupuje chůzí.

## Cesta hvězdárnou

| Oblast | Co na místě hledat |
| --- | --- |
| Výstupová římsa | Nocleh ve skalním závětří, rozpis hlídky a cesta značená ve sněhu k měděné kopuli |
| Chodby clon | Tři výbojová pole pod klenbami, vodicí koleje, servisní výklenky a náhradní filtry |
| Dílny a servisní lávka | Pracovní stoly s nástroji, naviják, zkouška zrcadla, návratový zápis a Pečeť kotvy |
| Kopule | Refraktor na mosazné mapě, žebra kopule, rukopisy a dva ruční ovladače clon |
| Schody do nebe | Dvě schodiště, rozpis u prvního schodu a větrný vír u stanoviště Křídla |
| Visuté ochozy | Modře a zlatě značené mosty, strážnice Kopí a Lucerny |
| Předbraní | Tři patice pečetí, odpočívárna a schodiště k bráně s reliéfem dvou obloh |
| Poslední stupeň | Tři výseče, patice zkušebního zrcadla a návratová lucerna v otevřeném pavilonu |

V kopuli se otáčí refraktor spolu s oběma ovladači. V předbraní přepínáš jednotlivé patice mezi donesenými pečetěmi a sestavu potvrdíš u ovladače pod schody. Správná kombinace zjeví světelnou bránu. Kniha nové výpravy v noclehu po druhém použití vylosuje další pořadí a výpravu obnoví.

## Úpravy a sestavení

Půdorysy, přechody a interaktivní objekty jsou v [layout.py](../zdroje/layout.py). Výzdobu jednotlivých lokací určuje [dressing.py](../zdroje/dressing.py). Vlastní modely, textury a oblohu sestavují [art.py](../zdroje/art.py), [architecture.py](../zdroje/architecture.py) a [skies.py](../zdroje/skies.py). Předměty a stvůry jsou v [content.py](../zdroje/content.py). [NWScriptové zdroje](../skripty/) jsou také uvnitř modulu. Čeština používá `cp1250`.

```bash
python3 ../zdroje/build.py --game "/cesta/k/Neverwinter Nights/game" \
  --compiler /cesta/k/nwn_script_comp --scripts ../skripty --output ./build
```

Sestavení čte dlaždice, přechody a statické herní zdroje ze základní instalace. Součástí vlastního HAKu jsou původní materiály určené pro zámecké dlaždice horních oblastí. Při integraci do světa zkontroluj sloučení tabulky `placeables.2da` a názvy textur. [Kompilátor NWScriptu](https://github.com/niv/neverwinter.nim/releases/tag/2.3.2)


## Ověření ve hře

V linuxovém NWN:EE 89.8193.37-17 prošly pohybové zkoušky přes pozemní přechody, servisní lávku, obě ramena ochozů a schodiště. Ovladače seřídily refraktor, chybné pečetě nechaly bránu zavřenou a správné pečetě ji zjevily. Ve zkušebním stavu závěru prošlo sklopení clony a obnovení výpravy s novým pořadím. Záběry zachycují všech osm oblastí. Při focení jsem v klientu skryl rozhraní a nastavil kameru. [Záběry z klienta](../podklady/nahledy.jpg)
