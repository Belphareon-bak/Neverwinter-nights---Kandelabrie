# Hotové postavy na 40. úrovni

V NWN:EE otevři **New → Local → Zkusebna dobrodruhu → Play → Select Premade Character**. Stejné postavy můžeš vybrat i v jiném lokálním modulu.

Každá postava má 780 000 XP, historii level-upů, výstroj +5 pro svůj styl boje, pět lektvarů uzdravení a v batohu boty trvalého spěchu. Sesilatelé mají naučená nebo připravená kouzla. Zkušebna umožňuje pomocí Kroniky postavy odebrat poslední úrovně a pak znovu levelovat.

| Postava | Povolání | Soubor | Původní rozpis |
|---|---|---|---|
| The Shadow Priest | Cleric 26, Monk 9, Shadowdancer 5 | [BIC](characters/zks_shadow.bic) | [ECB Guild](https://www.tapatalk.com/groups/nwnecbguild/the-shadow-priest-cleric-26-monk-9-sd5-t515430.html) |
| Dwarven Slayer | Fighter 10, Rogue 4, Dwarven Defender 26 | [BIC](characters/zks_slayer.bic) | [ECB Guild, příspěvek 8](https://www.tapatalk.com/groups/nwnecbguild/damage-reduction-questions-t2355036.html) |
| The Master | Rogue 7, Fighter 8, Weapon Master 25 | [BIC](characters/zks_master.bic) | [ECB Guild, verze s Devastating Critical](https://www.tapatalk.com/groups/nwnecbguild/the-master-rogue-7-fighter-8-weapon-master-25-t2355235.html) |
| Dwarven Outcast | Ranger 26, Fighter 12, Shadowdancer 2 | [BIC](characters/zks_outcast.bic) | [ECB Guild](https://www.tapatalk.com/groups/nwnecbguild/dwarven-outcast-ranger-26-fighter-12-shadowdancer--t2354434.html) |
| The Divine Howitzer | Wizard 1, Paladin 10, Arcane Archer 29 | [BIC](characters/zks_howitzer.bic) | [World of Greyhawk](https://world-of-greyhawk.github.io/builds/data/build295887.html) |
| Exalted Sorceress | Sorcerer 38, Paladin 1, Monk 1 | [BIC](characters/zks_exalted.bic) | [ECB Guild, verze z roku 2022](https://www.tapatalk.com/groups/nwnecbguild/exalted-sorceress-sorcerer-38-paladin-1-monk-1-t515460.html) |
| Heirophant of the Cabal | Druid 37, Champion of Torm 2, Monk 1 | [BIC](characters/zks_heirophant.bic) | [ECB Guild](https://www.tapatalk.com/groups/nwnecbguild/heirophant-of-the-cabal-druid-37-cot2-monk1-t2355778.html) |
| The Bulwark of Tharizdun | Bard 26, Blackguard 4, Red Dragon Disciple 10 | [BIC](characters/zks_bulwark.bic) | [ECB Guild](https://www.tapatalk.com/groups/nwnecbguild/the-bulwark-of-tharizdun-bard-26-blackguard-4-rdd--t2355544.html) |
| Tiny Reaper | Rogue 13, Assassin 26, Shadowdancer 1 | [BIC](characters/zks_tiny.bic) | [ECB Guild, verze se dvěma dýkami](https://www.tapatalk.com/groups/nwnecbguild/tiny-reaper-rogue-13-shadowdancer-1-assassin-26-t515504.html) |
| Knight of the Quest | Paladin 26, Champion of Torm 10, Rogue 4 | [BIC](characters/zks_quest.bic) | [World of Greyhawk](https://world-of-greyhawk.github.io/builds/data/build222567.html) |

Vzhled, výstroj a sady kouzel jsem zvolil pro Zkušebnu. Dwarven Outcast má sedm oblíbených nepřátel od nemrtvých po skřetí humanoidy. Dvě drobné úpravy dodržují rozpočet dovedností podle herních tabulek. The Divine Howitzer má Search 5. Heirophant má Hide 17 a Move Silently 19.

## Ověření v klientu

Všech deset postav se načetlo z nabídky **Select Premade Character**. Herní kontrola ověřila povolání, atributy, dovednosti, talenty, výstroj, obsah batohu a dostupná kouzla. Snížení úrovně ve zkušební kopii modulu prošlo postupně na 39., 20. a 1. úroveň.

## Soubory a sestavení

`.bic` patří do `localvault` v uživatelských datech NWN:EE. Na tomto počítači je to `~/.local/share/Neverwinter Nights/localvault`.

Rozpisy upravíš v [roster.py](roster.py), [skills.txt](skills.txt) a [spellbook.py](spellbook.py). Sestavení čte pravidla a modely ze základních herních dat.

```bash
python3 build.py --game "/cesta/k/Neverwinter Nights/game" --output characters
```
