#!/usr/bin/env python3
"""Build the standalone Hvězdárna module and its optional local character."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import uuid

from architecture import MODELS as ARCHITECTURE, SKY_MODELS, architecture_textures
from art import assets
from aurora import (GameResources, Record, TYPE, VOID, bite, dword, erf_encode, erf_index, gff_encode,
                    integer, loc, lst, ref, string, word)
from collision import FOOTPRINTS, walkmesh
from content import creature_palette, creatures, factions, hero, items
from dressing import NAMES, dress_areas
from flights import tile_assets
from gateart import gate_models, seal_assets
from furnishings import SCENERY as FURNISHINGS, book_assets, star_cloak_assets
from lightart import SCENERY as LINK_SCENERY, VISUALS as LINK_VISUALS
from plan import SECRET_LEVEL, VERSION
from routes import SECRET_SILLS, route_assets
from interiors import tileset as interior_tiles, workshop_tiles, yard_wall_assets
from ithren import conversation, journal
from layout import REWARD_CATEGORIES, areas
from skies import sky_assets
from shrines import SCENERY as SHRINE_SCENERY
from sunrepair import SCENERY as REPAIR_SCENERY, VISUALS as REPAIR_VISUALS
from temple import SCENERY as TEMPLE_SCENERY
from workart import SCENERY as WORKSHOP_SCENERY, VISUALS as WORKSHOP_VISUALS
from workart import portable_mirror_assets
from world import Tileset, object_fields, variables


MODULE_DIR = Path(__file__).resolve().parent.parent
MODULE_NAME = "Hvezdarna druheho nebe.mod"
CHARACTER_NAME = "Radan Hvezdar.bic"
HAK_NAME = "hvd_obs_v24"  # Last version with changes to the art assets.
TEXT_ENCODING = "cp1250"


def metadata(zones, test_guide):
    scripts = {
        "Mod_OnModLoad": "hvd_load",
        "Mod_OnClientEntr": "hvd_client",
        "Mod_OnPlrDeath": "hvd_death",
        "Mod_OnSpawnBtnDn": "hvd_respawn",
        "Mod_OnAcquirItem": "hvd_pickup",
    }
    for event in ("Mod_OnHeartbeat", "Mod_OnModStart", "Mod_OnClientLeav", "Mod_OnUnAqreItem",
                  "Mod_OnUsrDefined", "Mod_OnPlrDying", "Mod_OnPlrLvlUp", "Mod_OnPlrRest", "Mod_OnActvtItem"):
        scripts[event] = ""
    start = next(marker for marker in zones[0].waypoints if marker.value("Tag") == "hvd_start")
    info = Record(
        Mod_ID=(VOID, uuid.uuid5(uuid.NAMESPACE_URL, "local:nwn/hvezdarna-druheho-nebe").bytes),
        Mod_Creator_ID=integer(0), Mod_Version=dword(VERSION), Expansion_Pack=word(3),
        Mod_Name=loc("Hvězdárna druhého nebe"),
        Mod_Tag=string("HVEZDARNA"), Mod_Hak=string(""),
        Mod_HakList=lst([Record(8, Mod_Hak=string(HAK_NAME))]), Mod_CustomTlk=string(""),
        Mod_Description=loc("Horská výprava pro úrovně 34–40. Větrní elementálové, Schody do nebe, "
                            "proměnlivá soustava čtyř pečetí a poslední služba solara Ithrena. "
                            "Pro samostatnou zkoušku se hodí Radan Hvězdář (38)."),
        Mod_IsSaveGame=bite(0), Mod_Entry_Area=ref(zones[0].key),
        Mod_Entry_X=start.fields["XPosition"], Mod_Entry_Y=start.fields["YPosition"],
        Mod_Entry_Z=start.fields["ZPosition"], Mod_Entry_Dir_X=start.fields["XOrientation"],
        Mod_Entry_Dir_Y=start.fields["YOrientation"],
        Mod_Expan_List=lst([]), Mod_DawnHour=bite(6), Mod_DuskHour=bite(18), Mod_MinPerHour=bite(2),
        Mod_StartMonth=bite(10), Mod_StartDay=bite(18), Mod_StartHour=bite(7), Mod_StartYear=dword(1372),
        Mod_XPScale=bite(0), Mod_StartMovie=ref(""), Mod_CutSceneList=lst([]), Mod_GVar_List=lst([]),
        Mod_Area_list=lst([Record(6, Area_Name=ref(zone.key)) for zone in zones]),
        **{event: ref(script) for event, script in scripts.items()},
    )
    settings = {"hvd_secret_level": SECRET_LEVEL}
    if test_guide:
        settings["hvd_test_guide"] = 1
    info.fields["VarTable"] = variables(**settings)
    return info


def compile_scripts(resources, game, compiler, scripts):
    with TemporaryDirectory(prefix="hvd-build-") as temp:
        work = Path(temp)
        source = work / "source"
        output = work / "compiled"
        source.mkdir()
        output.mkdir()
        mains = []
        for script in sorted(scripts.glob("*.nss")):
            text = script.read_text(encoding="utf-8")
            encoded = text.encode(TEXT_ENCODING)
            (source / script.name).write_bytes(encoded)
            resources[script.name] = encoded
            if "void main()" in text or "int StartingConditional()" in text:
                mains.append(source / script.name)
        subprocess.run([str(compiler), "--root", str(game), "--userdirectory", str(work),
                        "--dirs", str(source), "--nwn-encoding", "windows-1250",
                        "-j", "2", "-c", "-d", str(output), *map(str, mains)],
                       check=True, cwd=source, timeout=55)
        for script in mains:
            compiled = (output / script.name).with_suffix(".ncs")
            binary = compiled.read_bytes()
            if binary[:8] != b"NCS V1.0":
                raise ValueError(f"Invalid NWScript bytecode for {script.name}")
            resources[compiled.name] = binary


def visual_blueprint(key, label, appearance):
    fields = object_fields(key, label, "")
    fields.update(Appearance=dword(appearance), Static=bite(0), Useable=bite(0),
                  Type=bite(0), HasInventory=bite(0), TemplateResRef=ref(key))
    if key in SECRET_SILLS:
        fields.update(Useable=bite(1), OnUsed=ref("hvd_use"))
    return Record(PaletteID=bite(0), **fields)


def load_reward_items(folder, prototypes, resources):
    if not folder.is_dir():
        raise ValueError(f'Složka s vlastními odměnami neexistuje: {folder}')
    catalog = {}
    for category,_,_ in REWARD_CATEGORIES:
        names = []
        for path in sorted((folder/category).glob('*.uti')):
            name = path.stem.lower()
            if not re.fullmatch(r'[a-z0-9_]{1,16}',name):
                raise ValueError(f'Neplatný resref odměny: {path}')
            if name in prototypes or f'{name}.uti' in resources:
                raise ValueError(f'Resref odměny se opakuje: {path}')
            data = path.read_bytes()
            if not data.startswith(b'UTI V3.2'):
                raise ValueError(f'Očekáván předmět exportovaný jako UTI: {path}')
            resources[f'{name}.uti'] = data
            names.append(name)
        catalog[category] = names
    return catalog


def build(game_path, compiler, directory, scripts, *, test_guide=False, reward_folder=None, xp_module=None):
    game = GameResources(game_path)
    resources = {}
    cloak_model, cloak_art = star_cloak_assets(game)
    prototypes = items(test_guide=test_guide, cloak_model=cloak_model)
    rewards = load_reward_items(reward_folder,prototypes,resources) if reward_folder else {}
    gate_scenery, gate_visuals = gate_models()
    sills, inscriptions = route_assets()
    additions = {name: (NAMES[name], mesh) for name, mesh in SKY_MODELS.items()}
    additions.update(gate_scenery | gate_visuals | WORKSHOP_SCENERY | WORKSHOP_VISUALS | sills | FURNISHINGS)
    additions.update(LINK_SCENERY | LINK_VISUALS | yard_wall_assets())
    additions.update(TEMPLE_SCENERY | SHRINE_SCENERY | REPAIR_SCENERY | REPAIR_VISUALS)
    appearances, art = assets(game, {name: (NAMES[name], mesh) for name, mesh in ARCHITECTURE.items()},
                              additions)
    art.update(seal_assets())
    art.update(portable_mirror_assets())
    art.update(book_assets())
    art.update(cloak_art)
    art.update(inscriptions)
    art.update({f"{name}.pwk": walkmesh(name) for name in FOOTPRINTS})
    art.update(architecture_textures())
    sky_ids, skies = sky_assets(game)
    art.update(skies)
    terrace_tiles, work_tiles, castle_tiles = tile_assets(game, workshop_tiles())
    art.update(castle_tiles)
    art.update(interior_tiles(game))
    zones = areas(appearances, terrace_tiles, work_tiles, test_guide=test_guide,reward_items=rewards)
    dress_areas(zones)
    for zone in zones:
        if zone.lighting["SkyBox"][1]:
            zone.lighting["SkyBox"] = bite(sky_ids["rim" if zone.key in ("hvd_camp", "hvd_rim", "hvd_works") else "upper"])
    tiles = {key: Tileset(game, key, art.get(f"{key}.set"), terrace_tiles.paving if key == "tcm02" else None)
             for key in {area.tileset for area in zones}}
    for name, creature in creatures().items():
        resources[f"{name}.utc"] = gff_encode("UTC", creature, TEXT_ENCODING)
    resources["creaturepalcus.itp"] = gff_encode("ITP", creature_palette(), TEXT_ENCODING)
    for name, item in prototypes.items():
        resources[f"{name}.uti"] = gff_encode("UTI", item, TEXT_ENCODING)

    for index, zone in enumerate(zones):
        for type_name, placed, position in [
            ("utp", zone.places, ("X", "Y", "Z", "Bearing")),
            ("utd", zone.doors, ("X", "Y", "Z", "Bearing")),
            ("utt", zone.triggers, ("XPosition", "YPosition", "ZPosition", "XOrientation", "YOrientation", "ZOrientation")),
        ]:
            for number, obj in enumerate(placed):
                key = f"hvd_{type_name}{index}{number:02d}"
                obj.fields["TemplateResRef"] = ref(key)
                fields = {name: data for name, data in obj.fields.items() if name not in position}
                resources[f"{key}.{type_name}"] = gff_encode(
                    type_name, Record(PaletteID=bite(0), Comment=string(zone.title), **fields), TEXT_ENCODING,
                )
        for extension, record in zone.records(tiles[zone.tileset]).items():
            resources[f"{zone.key}.{extension}"] = gff_encode(extension, record, TEXT_ENCODING)

    resources["module.ifo"] = gff_encode("IFO", metadata(zones, test_guide), TEXT_ENCODING)
    resources["repute.fac"] = gff_encode("FAC", factions(), TEXT_ENCODING)
    resources["hvd_ithren.dlg"] = gff_encode("DLG", conversation(), TEXT_ENCODING)
    resources["hvd_ithren_grp.dlg"] = gff_encode("DLG", conversation(group=True), TEXT_ENCODING)
    resources["module.jrl"] = gff_encode("JRL", journal(), TEXT_ENCODING)
    visual_labels = (
        ("hvd_gateway","Světlo druhého nebe"), ("hvd_needle","Mosazný ukazatel"),
        ("hvd_tube","Objektiv druhého nebe"),
        ("hvd_mirror_set","Zrcadlo zasazené v patici"),
        ("hvd_bookpanel","Zadní police archivu"),
        ("hvd_stonepanel","Kamenný kryt"),
    ) + tuple((key, label) for key, (label, _) in
              (gate_visuals | WORKSHOP_VISUALS | sills | LINK_VISUALS | REPAIR_VISUALS).items())
    for key, label in visual_labels:
        appearance = appearances["hvd_refractor" if key == "hvd_tube" else key]
        resources[f"{key}.utp"] = gff_encode("UTP",visual_blueprint(key,label,appearance),TEXT_ENCODING)
    compile_scripts(resources, game_path, compiler, scripts)
    if xp_module is not None:
        pwfxp = erf_index(xp_module).get(("pwfxp", TYPE["ncs"]))
        if not pwfxp or pwfxp[:8] != b"NCS V1.0":
            raise ValueError(f"Chybí platný pwfxp.ncs v {xp_module}")
        resources["pwfxp.ncs"] = pwfxp
    directory.mkdir(parents=True, exist_ok=True)
    module_file = directory / MODULE_NAME
    character_file = directory / CHARACTER_NAME
    module_file.write_bytes(erf_encode(resources))
    hak_file = directory / f"{HAK_NAME}.hak"
    hak_file.write_bytes(erf_encode(art, "HAK"))
    character_file.write_bytes(gff_encode("BIC", hero(prototypes), TEXT_ENCODING))
    print(f"{len(zones)} areas, {sum(len(zone.places) for zone in zones)} placeables, {len(resources)} resources")
    print(module_file)
    print(hak_file)
    print(character_file)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True, type=Path, help="NWN:EE game directory with data and ovr")
    parser.add_argument("--compiler", required=True, type=Path, help="Linux nwn_script_comp compiler")
    parser.add_argument("--scripts", type=Path, default=MODULE_DIR / "skripty", help="Directory containing the NWScript sources")
    parser.add_argument("--output", type=Path, default=MODULE_DIR / "build", help="Directory for the module, character and HAK")
    parser.add_argument("--test-guide", action="store_true",
                        help="Add a book with the current gate solution to the test chest")
    parser.add_argument("--reward-items", type=Path, help="Složka s vlastními UTI ve složkách kategorií")
    parser.add_argument("--xp-module", type=Path, help="Lokální modul Kandelábrie pro přibalení jeho pwfxp.ncs")
    args = parser.parse_args()
    build(args.game.resolve(), args.compiler.resolve(), args.output.resolve(), args.scripts.resolve(),
          test_guide=args.test_guide, reward_folder=args.reward_items, xp_module=args.xp_module)


if __name__ == "__main__":
    main()
