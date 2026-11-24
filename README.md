# Kandelábrie

Repozitář pro tvorbu dungeonů a dalších rozšíření světa Kandelábrie pro **Neverwinter Nights: Enhanced Edition**.

[Pravidla worldbuildingu pro Kandelábrii](AGENTS.md)

## Dungeony

| Dungeon | Doporučené úrovně | Stav |
| --- | --- | --- |
| [Hvězdárna druhého nebe](dungeony/hvezdarna-druheho-nebe/README.md) | 34–38 a 37–40 | Samostatný modul NWN:EE |

## Struktura repozitáře

- Každý dungeon má vlastní složku v `dungeony/`. Její `README.md` popisuje příběh, lokace a herní mechanismy.
- Do složky `moduly/` u dungeonu patří exporty `.mod` a informace k jejich spuštění nebo importu. [Moduly Hvězdárny](dungeony/hvezdarna-druheho-nebe/moduly/README.md)
- Skripty NWScript (`.nss`) patří do `skripty/` příslušného dungeonu, mapy a poznámky z testů do jeho `podklady/`. Tyto složky přidej s prvním obsahem.
- Podklady používané ve více dungeonech mají místo ve [společné složce](spolecne/README.md).

Nový námět stačí založit jako `dungeony/nazev-dungeonu/README.md` a přidat ho do přehledu výše.

## Nástroje

[Zkušebna dobrodruhů](nastroje/xp-maker/README.md) obsahuje XP maker, zbrojnici, bestiář a deset postav na 40. úrovni.
