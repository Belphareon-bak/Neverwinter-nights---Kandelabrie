#!/usr/bin/env python3
"""Build the standalone Hvězdárna module and its optional local character."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import uuid

from architecture import MODELS as ARCHITECTURE, SKY_MODELS, architecture_textures
from art import assets
from aurora import GameResources, Record, VOID, bite, dword, erf_encode, gff_encode, integer, loc, lst, ref, string, word
from collision import FOOTPRINTS, walkmesh
from content import creatures, factions, hero, items
from dressing import NAMES, dress_areas
from flights import tile_assets
from gateart import gate_models, seal_assets
from interiors import tileset as interior_tiles
from layout import areas
from skies import sky_assets
from workart import SCENERY as WORKSHOP_SCENERY, VISUALS as WORKSHOP_VISUALS
from workart import portable_mirror_assets
from world import Tileset, object_fields, variables


HERE = Path(__file__).resolve().parent
MODULE_NAME = "Hvezdarna druheho nebe.mod"
CHARACTER_NAME = "Radan Hvezdar.bic"
HAK_NAME = "hvd_observatory"
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
        Mod_Creator_ID=integer(0), Mod_Version=dword(9), Expansion_Pack=word(3),
        Mod_Name=loc("Hvězdárna druhého nebe"),
        Mod_Tag=string("HVEZDARNA"), Mod_Hak=string(""),
        Mod_HakList=lst([Record(8, Mod_Hak=string(HAK_NAME))]), Mod_CustomTlk=string(""),
        Mod_Description=loc("Horská výprava pro úrovně 35–40. Větrní elementálové, Schody do nebe, "
                            "proměnlivá soustava čtyř pečetí a poslední služba solara Ithrena. "
                            "Pro samostatnou zkoušku se hodí Radan Hvězdář (38)."),
        Mod_IsSaveGame=bite(0), Mod_Entry_Area=ref("hvd_rim"),
        Mod_Entry_X=start.fields["XPosition"], Mod_Entry_Y=start.fields["YPosition"],
        Mod_Entry_Z=start.fields["ZPosition"], Mod_Entry_Dir_X=start.fields["XOrientation"],
        Mod_Entry_Dir_Y=start.fields["YOrientation"],
        Mod_Expan_List=lst([]), Mod_DawnHour=bite(6), Mod_DuskHour=bite(18), Mod_MinPerHour=bite(2),
        Mod_StartMonth=bite(10), Mod_StartDay=bite(18), Mod_StartHour=bite(7), Mod_StartYear=dword(1372),
        Mod_XPScale=bite(0), Mod_StartMovie=ref(""), Mod_CutSceneList=lst([]), Mod_GVar_List=lst([]),
        Mod_Area_list=lst([Record(6, Area_Name=ref(zone.key)) for zone in zones]),
        **{event: ref(script) for event, script in scripts.items()},
    )
    if test_guide:
        info.fields["VarTable"] = variables(hvd_test_guide=1)
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
            if "void main()" in text:
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
    return Record(PaletteID=bite(0), **fields)


def build(game_path, compiler, directory, scripts, *, test_guide=False):
    game = GameResources(game_path)
    resources = {}
    prototypes = items(test_guide=test_guide)
    gate_scenery, gate_visuals = gate_models()
    additions = {name: (NAMES[name], mesh) for name, mesh in SKY_MODELS.items()}
    additions.update(gate_scenery | gate_visuals | WORKSHOP_SCENERY | WORKSHOP_VISUALS)
    appearances, art = assets(game, {name: (NAMES[name], mesh) for name, mesh in ARCHITECTURE.items()},
                              additions)
    art.update(seal_assets())
    art.update(portable_mirror_assets())
    art.update({f"{name}.pwk": walkmesh(name) for name in FOOTPRINTS})
    art.update(architecture_textures())
    sky_ids, skies = sky_assets(game)
    art.update(skies)
    flight, paving, stairs = tile_assets(game)
    art.update(stairs)
    art.update(interior_tiles(game))
    zones = areas(appearances, flight, test_guide=test_guide)
    dress_areas(zones)
    for zone in zones:
        if zone.lighting["SkyBox"][1]:
            zone.lighting["SkyBox"] = bite(sky_ids["rim" if zone.key in ("hvd_rim", "hvd_works") else "upper"])
    tiles = {key: Tileset(game, key, art.get(f"{key}.set"), paving if key == "tcm02" else None)
             for key in {area.tileset for area in zones}}
    for name, creature in creatures().items():
        resources[f"{name}.utc"] = gff_encode("UTC", creature, TEXT_ENCODING)
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
    visual_labels = (
        ("hvd_gateway","Světlo druhého nebe"), ("hvd_needle","Mosazný ukazatel"),
        ("hvd_tube","Objektiv druhého nebe"),
        ("hvd_mirror_set","Zrcadlo zasazené v patici"),
        ("hvd_bookpanel","Zadní police archivu"),
        ("hvd_stonepanel","Kamenný kryt"),
    ) + tuple((key, label) for key, (label, _) in (gate_visuals | WORKSHOP_VISUALS).items())
    for key, label in visual_labels:
        appearance = appearances["hvd_refractor" if key == "hvd_tube" else key]
        resources[f"{key}.utp"] = gff_encode("UTP",visual_blueprint(key,label,appearance),TEXT_ENCODING)
    compile_scripts(resources, game_path, compiler, scripts)
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
    parser.add_argument("--scripts", type=Path, default=HERE / "scripts", help="Directory containing the NWScript sources")
    parser.add_argument("--output", type=Path, default=HERE, help="Directory for the module and character")
    parser.add_argument("--test-guide", action="store_true",
                        help="Add a book with the current gate solution to the test chest")
    args = parser.parse_args()
    build(args.game.resolve(), args.compiler.resolve(), args.output.resolve(), args.scripts.resolve(),
          test_guide=args.test_guide)


if __name__ == "__main__":
    main()
