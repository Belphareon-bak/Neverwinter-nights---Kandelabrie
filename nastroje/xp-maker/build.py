#!/usr/bin/env python3
"""Package Zkušebna dobrodruhů as a standalone NWN:EE module."""

import argparse
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import uuid


HERE = Path(__file__).resolve().parent
from common import add_observatory_sources

add_observatory_sources()

from aurora import GameResources, Record, VOID, bite, dword, erf_encode, flt, gff_encode, integer, loc, lst, ref, string, word
from content import factions
from world import Tileset
from catalog import beasts, equipment, nwscript_data, styled_item
from layout import arena, area_records, armory, hall, mentor


ENCODING = "cp1250"
MODULE_FILE = "Zkusebna dobrodruhu.mod"


def metadata(areas):
    return Record(
        Mod_ID=(VOID, uuid.uuid5(uuid.NAMESPACE_URL, "local:nwn/zkusebna-dobrodruhu").bytes),
        Mod_Creator_ID=integer(0), Mod_Version=dword(3), Expansion_Pack=word(3),
        Mod_Name=loc("Zkušebna dobrodruhů"), Mod_Tag=string("ZKUSEBNA"),
        Mod_Description=loc("Síň postav, zbrojnice a výcvikové kolbiště. XP a přesvědčení, "
                            "výstroj +1 až +5, šperky +5/+12 a bestiář pro vlastní střety."),
        Mod_Hak=string(""), Mod_HakList=lst([]), Mod_CustomTlk=string(""), Mod_IsSaveGame=bite(0),
        Mod_Entry_Area=ref("zks_hall"), Mod_Entry_X=flt(49.0), Mod_Entry_Y=flt(18.0), Mod_Entry_Z=flt(0.0),
        Mod_Entry_Dir_X=flt(0.0), Mod_Entry_Dir_Y=flt(1.0), Mod_StartHour=bite(10), Mod_MinPerHour=bite(2),
        Mod_StartMonth=bite(1), Mod_StartDay=bite(1), Mod_StartYear=dword(1372),
        Mod_DawnHour=bite(6), Mod_DuskHour=bite(20), Mod_XPScale=bite(0), Mod_StartMovie=ref(""),
        Mod_Area_list=lst([Record(6, Area_Name=ref(area.key)) for area in areas]),
        Mod_Expan_List=lst([]), Mod_CutSceneList=lst([]), Mod_GVar_List=lst([]),
        Mod_OnModLoad=ref("zks_load"), Mod_OnClientEntr=ref("zks_enter"),
        Mod_OnPlrDeath=ref("zks_death"), Mod_OnSpawnBtnDn=ref(""),
    )


def compile_scripts(resources, game, compiler, data):
    with TemporaryDirectory(prefix="zks-build-") as temp:
        work = Path(temp)
        source, output = work / "source", work / "bytecode"
        source.mkdir()
        output.mkdir()
        files = {script.name: script.read_text(encoding="utf-8") for script in (HERE / "scripts").glob("*.nss")}
        files["zks_data.nss"] = data
        mains = []
        for name, text in sorted(files.items()):
            encoded = text.encode(ENCODING)
            (source / name).write_bytes(encoded)
            resources[name] = encoded
            if "void main()" in text:
                mains.append(source / name)
        subprocess.run([str(compiler), "--root", str(game), "--userdirectory", str(work), "--dirs", str(source),
                        "--nwn-encoding", "windows-1250", "-j", "2", "-c", "-d", str(output), *map(str, mains)],
                       check=True, cwd=source, timeout=55)
        for main in mains:
            bytecode = (output / main.name).with_suffix(".ncs")
            data = bytecode.read_bytes()
            if not data.startswith(b"NCS V1.0"):
                raise ValueError(f"Invalid NWScript bytecode for {main.name}")
            resources[bytecode.name] = data


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--game", type=Path, required=True)
    cli.add_argument("--compiler", type=Path, required=True)
    cli.add_argument("--output", type=Path, default=HERE)
    args = cli.parse_args()
    game_path = args.game.resolve()
    game = GameResources(game_path)
    resources = {}

    def pack(key, extension, record):
        resources[f"{key}.{extension}"] = gff_encode(extension, record, ENCODING)

    items, gear = equipment(game)
    monsters, bestiary = beasts(game)
    items["zks_mentor_robe"] = styled_item(game, "zks_mentor_robe", "Oděv kronikářky", 16, "nw_cloth001")
    for key, record in items.items():
        pack(key, "uti", record)
    for key, record in monsters.items():
        pack(key, "utc", record)
    pack("zks_mentor", "utc", mentor())
    tiles = Tileset(game, "tni02")
    areas = (hall(), armory(), arena())
    for index, area in enumerate(areas):
        for number, placeable in enumerate(area.places):
            key = f"zks_p{index}{number:02d}"
            placeable.fields["TemplateResRef"] = ref(key)
            if placeable.value("Useable"):
                placeable.fields["OnUsed"] = ref("zks_use")
            template = {field: data for field, data in placeable.fields.items()
                        if field not in ("X", "Y", "Z", "Bearing")}
            pack(key, "utp", Record(PaletteID=bite(0), Comment=string(area.title), **template))
        for extension, record in area_records(area, tiles).items():
            pack(area.key, extension, record)
    pack("module", "ifo", metadata(areas))
    pack("repute", "fac", factions())
    compile_scripts(resources, game_path, args.compiler.resolve(), nwscript_data(gear, bestiary))
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / MODULE_FILE
    target.write_bytes(erf_encode(resources))
    print(f"{target}: {len(areas)} areas, {len(gear)} equipment models, {len(bestiary)} bestiary entries, {len(resources)} resources")


if __name__ == "__main__":
    main()
