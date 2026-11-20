"""Walkmesh footprints and use points for the original placeables."""

from math import cos, sin, tau


def rectangle(x, y, width, depth):
    return tuple((x + dx * width / 2, y + dy * depth / 2)
                 for dx, dy in ((-1,-1),(1,-1),(1,1),(-1,1)))


def ring(radius):
    return tuple((radius * cos(i * tau / 12), radius * sin(i * tau / 12)) for i in range(12))


def arch_feet(offset, width, depth, y=0):
    return tuple(rectangle(x, y, width, depth) for x in (-offset, offset))


def shelter(offset):
    return (rectangle(0, 1.83, offset * 2.1, .41), *arch_feet(offset,.83,.78,-1.75))


FOOTPRINTS = {
    "hvd_octagon": (*arch_feet(3.43,.79,1.04,-6), *arch_feet(3.43,.79,1.04,6),
                    *arch_feet(3.60,.70,8.4), *arch_feet(5.78,.56,5.65,.1)),
    "hvd_plinth": (ring(1.99),),
    "hvd_dial": (ring(.71),),
    "hvd_console": (ring(.71),),
    "hvd_columnade": arch_feet(3.17,.68,1.04),
    "hvd_gatearch": arch_feet(2.88,.98,1.21),
    "hvd_sealstand": (ring(.62),),
    "hvd_beacon": (ring(.64),),
    "hvd_rail": (rectangle(0,0,4.88,.36),),
    "hvd_tallpier": (rectangle(0,0,1.76,1.76),),
    "hvd_brokpier": (rectangle(0,0,1.5,1.5),),
    "hvd_wallpanel": (rectangle(0,0,4.96,.63),),
    "hvd_wallfoot": (rectangle(0,0,4.96,.63),),
    "hvd_window": (rectangle(0,0,2.65,.55),),
    "hvd_cloister": arch_feet(2.42,.90,1.02),
    "hvd_shutwin": (rectangle(0,-.25,2.87,.60),),
    "hvd_facade": (rectangle(0,-.04,5.80,.64),),
    "hvd_campshell": shelter(3.74),
    "hvd_shoproof": shelter(3.38),
    "hvd_crag": (rectangle(0,0,7.8,6.8),),
    "hvd_secretrock": (rectangle(0,0,6.3,2.42),),
    "hvd_snowbank": (rectangle(0,0,3.15,2.0),),
    "hvd_crate": (rectangle(0,0,1.13,.75),),
    "hvd_shelf": (rectangle(0,0,2.13,.75),),
    "hvd_lectern": (rectangle(0,0,.80,.72),),
    "hvd_armillary": (rectangle(0,0,.85,.85),),
    "hvd_cupolarib": (rectangle(0,0,1.57,1.57),),
    "hvd_bluepost": (ring(.29),),
    "hvd_amberpost": (ring(.29),),
    "hvd_sentrybay": (rectangle(0,1.65,3.68,.35), *arch_feet(1.79,.77,.77)),
    "hvd_hoist": arch_feet(1.47,.65,.74),
    "hvd_grille": (rectangle(0,0,4.15,.48),),
    "hvd_pavilion": (*arch_feet(5,1.29,1.29), *arch_feet(5,1.29,1.29,3.3)),
    "hvd_bookpanel": (rectangle(0,0,4.9,.46),),
    "hvd_stonepanel": (rectangle(0,0,4.9,.46),),
    "hvd_lining": (rectangle(0,.31,5.03,.59),),
    "hvd_apsewall": (rectangle(0,.24,5.03,.71),),
    "hvd_wallring": (rectangle(0,.14,.61,.29),),
    "hvd_lensrack": (rectangle(0,-.037,2.94,.67),),
    "hvd_skyport": arch_feet(2.79,1.28,1.0),
    "hvd_skyrail": (rectangle(0,0,4.92,.60),),
    "hvd_skybay": (rectangle(0,1.78,6.9,.48),*arch_feet(3.18,1.08,1.11,-.70),
                   *arch_feet(3.18,.44,1.15,1.32)),
    "hvd_orrery": (ring(2.4),),
    "hvd_eavearch": arch_feet(3.13,2.44,3.87),
    "hvd_beactower": (ring(2.07),),
    "hvd_gate_pod": (ring(.91),),
    "hvd_clamp_pod": (ring(.91),),
    "hvd_gatepull": (ring(.73),),
    "hvd_arc_cabinet": (rectangle(0,-.03,5.94,.55),),
    "hvd_lab_source": (ring(.78),),
    "hvd_gong": (rectangle(0,.14,2.24,.79),),
    "hvd_workroof": (rectangle(0,1.78,6.9,.48), *arch_feet(3.18,1.03,1.08,-.70),
                     *arch_feet(3.18,.44,1.15,1.32)),
    "hvd_grinder": (rectangle(0,0,2.60,1.21),),
    "hvd_smithbench": (rectangle(0,0,2.76,1.16),),
    "hvd_capstan": (rectangle(0,0,2.04,1.46),),
    "hvd_writedesk": (rectangle(0,0,2.68,1.16),),
    "hvd_logstand": (rectangle(0,.075,2.66,1.02),),
    "hvd_register": (rectangle(0,.04,3.31,1.77),),
    "hvd_spearrack": (rectangle(0,.12,2.55,.68),),
    "hvd_wicktable": (rectangle(0,0,2.36,1.18),),
    "hvd_raybaffle": (rectangle(0,0,1.60,.89),),
    "hvd_headhouse": (*arch_feet(2.64,.69,2.78,.65),),
    "hvd_optcover": (rectangle(0,.06,5.85,.33),),
    "hvd_signallamp": (ring(.88),),
    "hvd_flankwalls": arch_feet(5.12,3.13,3.60,.29),
    "hvd_bridgeedge": arch_feet(1.78,.24,18.10),
}

USE_POINTS = {
    "hvd_plinth": ((0,-2.68), (0,2.68)),
    "hvd_dial": ((0,-1.25), (0,1.25)),
    "hvd_console": ((0,-1.25), (0,1.25)),
    "hvd_sealstand": ((0,-1.18), (0,1.18)),
    "hvd_beacon": ((0,-1.24), (0,1.24)),
    "hvd_wallring": ((0,-.89),),
    "hvd_gate_pod": ((0,-1.45),(1.34,.04)),
    "hvd_clamp_pod": ((0,-1.43),(1.40,.05)),
    "hvd_gatepull": ((0,-1.22),),
    "hvd_lab_source": ((0,-1.24),(1.20,0)),
    "hvd_gong": ((0,-1.12),(0,1.08)),
    "hvd_signallamp": ((.48,-1.10),(1.11,-.48),(-.08,-1.23)),
}


def walkmesh(name):
    vertices, faces = [], []
    for polygon in FOOTPRINTS[name]:
        offset = len(vertices)
        vertices.extend(polygon)
        faces.extend((offset,offset+i,offset+i+1) for i in range(1,len(polygon)-1))
    parent = f"{name}_pwk"
    lines = [
        "#MAXDOOR ASCII", f"# model: {parent}",
        f"node trimesh {name}_wg", f"  parent {parent}", "  position 0 0 0",
        "  orientation 0 0 0 0", "  bitmap NULL", f"  verts {len(vertices)}",
    ]
    lines.extend(f"    {x:.4f} {y:.4f} 0" for x,y in vertices)
    lines.append(f"  faces {len(faces)}")
    lines.extend(f"    {a} {b} {c} 0 0 0 0 7" for a,b,c in faces)
    lines.append("endnode")
    for i,(x,y) in enumerate(USE_POINTS.get(name,()),1):
        lines.extend((f"node dummy hvd_pwk_use0{i}", f"  parent {parent}",
                      f"  position {x} {y} 0", "  orientation 0 0 0 0", "endnode"))
    return ("\n".join(lines) + "\n").encode("ascii")
