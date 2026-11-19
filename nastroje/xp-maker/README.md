# Zkušebna dobrodruhů pro NWN:EE

Samostatný modul pro stavbu postav, výdej vybavení a bojové zkoušky. Používá herní systémy a modely základní instalace NWN:EE. České texty jsou v `cp1250`.

## Jak začít

1. Spusť **New → Local → Zkusebna dobrodruhu → Play**. Vyber vlastní postavu nebo ji vytvoř přímo v nabídce hry.
2. Oslov **mistryni Neriu** nebo otevři **Kroniku postavy**. Zvol cílovou úroveň 1–40 a potvrď **Nastavit XP**. Pro růst potom vyber povolání a ostatní volby v běžném level-upu. Snížení se provede okamžitě odebráním posledních úrovní. Volba **0 XP** vrací postavu na 1. úroveň.
3. Západní dveře vedou do **zbrojnice**, východní do **předsíně bestiáře**. Mezi oběma je i přímá spojka.

V nabídce **Select Premade Character** je k dispozici [deset komunitních buildů na 40. úrovni](premade/README.md).

Kronika umí všech devět přesvědčení, úplný odpočinek a export postavy do místního seznamu. Při změně přesvědčení platí požadavky jednotlivých povolání.

## Výstroj

Čtyři výdejní pulty pokrývají 62 typů výstroje s kvalitou **+1 až +5**. Jsou tu zbraně zblízka, střelné a vrhací zbraně, střelivo, mnišské rukavice, všech devět tříd základní zbroje včetně oděvu, tři druhy štítů i doplňky. Efekt se volí podle předmětu. Zbraně a střelivo mohou přidat živel, zbroje mají na výběr odolnosti, regeneraci, záchranné hody a bonusy k zámkům a pastem. U luku a praku lze přidat **Mighty**.

Klenotnice vydává **prsteny a amulety +5 nebo +12** k jednomu z šesti atributů nebo ke všem zároveň. Najdeš tu také **Boty trvalého spěchu**, lektvary, pomůcky pro zloděje a ohniska s jednou pozicí na kouzlo pro zvolené sesílající povolání. Běžná pravidla hry určují, co může která postava nosit.

## Bestiář

Kniha obsahuje **69 protivníků** s filtrem podle obtížnosti a vyhledáváním podle názvu. Vyber stvůru, nastav počet **1–8** a přidej ji do střetu. Rozličné skupiny lze poskládat až do **12 živých soupeřů**. Ve výběru jsou stvůry od krysy a kobolda přes elementály, upíra a balora až po demiliche, prizmatického draka a drakoliche. Kolbiště má samostatný vstup z předsíně.

Před vstupem můžeš v předsíni odpočinout. Po porážce tě modul oživí a přenese zpět do předsíně. Kniha u ústupu i kniha v předsíni mají tlačítko **Vyčistit kolbiště**. Zkušenosti se nastavují v Kronice.

## Instalace a zdroje

[Zkusebna dobrodruhu.mod](<Zkusebna dobrodruhu.mod>) patří do složky `modules` v uživatelských datech NWN:EE. Pro úpravy jsou k dispozici [rozmístění oblastí](layout.py), [katalog předmětů a stvůr](catalog.py) a [skripty](scripts/).

Příkaz pro sestavení modulu z těchto zdrojů je uveden níže.

```bash
python3 build.py --game "/cesta/k/Neverwinter Nights/game" \
  --compiler /cesta/k/nwn_script_comp --output ./build
```

`--game` míří na složku s `data/` a `ovr/`. Sestavení používá společné zpracování formátů Aurora ze zdrojů Hvězdárny. Výstupní `.mod` obsahuje i zdroje NWScript. [Kompilátor nwn_script_comp](https://github.com/niv/neverwinter.nim/releases/tag/2.3.2)

## Ověření v NWN:EE

V klientu prošlo nastavení 780 000 XP pro úroveň 40, snížení až na 1. úroveň, všech devět přesvědčení a export postavy. Herní zkouška vydala všech 62 typů výstroje, nasadila šperk s bonusem +12 ke všem atributům a porovnala pohyb s botami spěchu. Všech 69 protivníků se podařilo přivolat jako nepřátele. Přes knihu prošel výběr drakolicha, přivolání a vyčištění kolbiště. Ověřený je i návrat po porážce při zachování XP. Stejný `.mod` načetl dedikovaný server.
