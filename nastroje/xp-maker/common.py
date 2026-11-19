"""Locate the shared NWN resource generators in the local project or Git checkout."""

from pathlib import Path
import sys


def add_observatory_sources():
    here = Path(__file__).resolve().parent
    candidates = (
        here.parent / "hvezdarna",
        here.parents[1] / "Hvezdarna druheho nebe" / "hvezdarna",
        here.parents[1] / "dungeony" / "hvezdarna-druheho-nebe" / "zdroje",
    )
    for candidate in candidates:
        if all((candidate / name).is_file() for name in ("aurora.py", "content.py", "world.py")):
            sys.path.append(str(candidate))
            return
    raise RuntimeError("The shared Aurora sources are missing. Keep the observatory and XP maker in the same project.")
