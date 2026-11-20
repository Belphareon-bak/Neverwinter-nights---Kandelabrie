"""Furnishings specific to the trades and stations of the observatory."""

from math import cos, pi, sin
from struct import pack

from architecture import BASALT, ICE, LIMESTONE, MASONRY, OLDWOOD, PALE, PARCHMENT, WOOD
from art import BRASS, DARK, GILT, TRIM, Material, Mesh, arch


IRON = Material((.34, .38, .40), 'hvd_rough')
LEATHER = Material((.29, .35, .20), 'hvd_oak')
OXIDE = Material((.40, .47, .40), 'hvd_copper')
INK = Material((.30, .23, .18), 'hvd_rough')


def bench(mesh, width, depth, top=WOOD):
    for x in (-(width / 2 - .17), width / 2 - .17):
        for y in (-(depth / 2 - .13), depth / 2 - .13):
            mesh.box(WOOD, x, y, 0, .17, .18, .81)
        mesh.box(WOOD, x, 0, .21, .14, depth - .12, .14)
    mesh.box(top, 0, 0, .76, width, depth, .12)


def service_roof():
    m = Mesh()
    m.box(MASONRY, 0, 1.78, 0, 6.9, .48, 2.91)
    for x in (-3.18, 3.18):
        m.box(BASALT, x, -.70, 0, 1.03, 1.08, .32)
        m.box(WOOD, x, -.70, .30, .35, .38, 2.65)
        m.box(MASONRY, x, 1.32, 0, .44, 1.15, 2.94)
        m.tube(WOOD, (x, -.71, 2.35), (x * .81, -.71, 3.06), .11, sides=8)
    for y, z in ((-1.07, 2.91), (1.77, 3.70)):
        m.box(WOOD, 0, y, z, 7.24, .34, .21)
    for i in range(8):
        a, b = -3.64 + .91*i, -3.64 + .91*(i+1)
        sheet = ((a, -1.47, 3.15), (b, -1.47, 3.15), (b, 2.20, 4.03), (a, 2.20, 4.03))
        m.polygon(OXIDE if i % 3 else IRON, sheet, ((0, 0), (1, 0), (1, 4), (0, 4)))
        m.polygon(WOOD, tuple(reversed(sheet)))
        m.tube(BRASS, sheet[0], sheet[-1], .026, sides=5)
    return m


def grinding_bench():
    m = Mesh()
    bench(m, 2.60, 1.21)
    m.box(BASALT, 0, .14, .89, 1.32, .71, .19)
    m.box(DARK, 0, .13, 1.06, 1.12, .55, .054)
    for x in (-.46, .46):
        m.box(BRASS, x, .16, 1.07, .14, .24, .47)
    m.tube(IRON, (-.61, .16, 1.48), (.73, .16, 1.48), .072, sides=10)
    m.disc(LIMESTONE, (-.14, .16, 1.48), (.16, .16, 1.48), .49, sides=20)
    m.disc(BRASS, (.16, .16, 1.48), (.22, .16, 1.48), .18, sides=12)
    m.tube(BRASS, (.72, .16, 1.48), (.72, -.14, 1.30), .049, sides=8)
    m.tube(WOOD, (.70, -.14, 1.30), (.96, -.14, 1.30), .059, sides=8)
    return m


def smith_bench():
    m = Mesh()
    bench(m, 2.76, 1.16)
    m.box(IRON, -.91, -.17, .87, .52, .42, .14)
    for y in (-.31, .035):
        m.box(IRON, -.94, y, .99, .37, .10, .18)
    for x, y in ((-.18, .31), (.32, -.19), (.69, .20)):
        m.tube(WOOD, (x, y-.35, .96), (x, y+.08, .96), .034, sides=6)
        m.box(IRON, x, y+.09, .91, .28, .16, .11)
    m.box(WOOD, .57, .43, .87, 1.25, .16, .63)
    for x in (.20, .55, .92):
        m.disc(BRASS, (x, .37, 1.07), (x, .31, 1.07), .084, sides=12)
    return m


def capstan():
    m = Mesh()
    m.box(BASALT, 0, 0, 0, 2.04, 1.46, .25)
    for x in (-.67, .67):
        m.box(WOOD, x, 0, .24, .29, .40, 1.42)
        m.disc(BRASS, (x, 0, 1.18), (x+.055, 0, 1.18), .23, sides=12)
    m.tube(IRON, (-.88, 0, 1.18), (.87, 0, 1.18), .115, sides=12)
    for x in (-.44, .44):
        m.disc(WOOD, (x-.065, 0, 1.18), (x+.065, 0, 1.18), .58, sides=16)
    for i in range(12):
        x = -.37 + .067 * i
        m.disc(TRIM, (x, 0, 1.18), (x+.056, 0, 1.18), .391 + .018*sin(i), sides=16)
    m.tube(IRON, (.82, 0, 1.18), (.82, -.37, 1.58), .056, sides=8)
    m.tube(WOOD, (.82, -.37, 1.58), (1.09, -.37, 1.58), .072, sides=8)
    return m


def writing_desk():
    m = Mesh()
    bench(m, 2.68, 1.16)
    for x in (-.76, .76):
        m.box(LEATHER, x, .15, .90, .47, .54, .12)
        m.box(PARCHMENT, x+.013, .15, .928, .46, .51, .066)
        m.box(GILT, x-.18, -.129, .945, .031, .018, .06)
    m.box(LEATHER, .13, -.21, .886, .68, .51, .015)
    m.disc(INK, (1.02, -.23, .88), (1.02, -.23, 1.03), .087, sides=8)
    m.tube(IRON, (.88, -.30, .90), (1.18, -.20, .91), .015, sides=6)
    m.polygon(PARCHMENT, ((.99, -.27, .926), (1.24, -.19, .951), (1.10, -.16, .959)))
    return m


def plan_drawers():
    m = Mesh()
    m.box(OLDWOOD,0,.04,0,3.12,.82,.22,tile_uv=.37)
    m.box(WOOD,0,.04,.22,3.02,.77,1.18,tile_uv=.45)
    m.box(OLDWOOD,0,.022,1.40,3.19,.91,.10)
    for x in (-.76,.76):
        for z in (.28,.58,.88,1.17):
            m.box(OLDWOOD,x,-.366,z,1.36,.15,.24,tile_uv=.65)
            m.box(BRASS,x,-.459,z+.106,.27,.071,.064)
            m.box(PARCHMENT,x-.38,-.452,z+.081,.192,.032,.12)
        m.tube(PARCHMENT,(x-.32,.11,1.56),(x+.45,.05,1.56),.065,sides=14)
    return m


def filter_grid():
    m = Mesh()
    m.box(BASALT,0,0,0,4.45,.80,.25,tile_uv=.34)
    m.box(MASONRY,0,.1,.25,4.27,.49,2.71,tile_uv=.41)
    m.box(LIMESTONE,0,0,2.91,4.51,.79,.18)
    for i in range(5):
        x = (i-2)*.812
        m.box(BRASS,x,-.224,.42,.69,.18,2.16)
        m.box(DARK,x,-.33,.50,.51,.06,1.99)
        for j in range(2):
            z=1.02+j*.89
            m.disc(TRIM,(x,-.357,z),(x,-.41,z),.263,sides=12)
            m.disc(PALE if (i+j)%2 else ICE,(x,-.410,z),(x,-.474,z),.212,sides=16)
    return m


def plans():
    m = Mesh()
    m.box(WOOD, 0, 0, 1.20, 3.82, .27, 1.63)
    ink_y = -.170
    for x in (-.89, .89):
        m.box(PARCHMENT, x, -.151, 1.34, 1.54, .028, 1.32)
        for z in (1.58, 1.80, 2.29, 2.49):
            m.tube(INK, (x-.54, ink_y, z), (x+.54, ink_y, z), .009, sides=5)
        m.tube(INK, (x-.49, ink_y, 1.81), (x-.49, ink_y, 2.28), .012, sides=5)
        m.tube(INK, (x+.48, ink_y, 1.81), (x+.48, ink_y, 2.28), .012, sides=5)
        m.tube(IRON, (x-.42, ink_y, 1.91), (x+.41, ink_y, 2.19 if x < 0 else 1.93), .021, sides=5)
        for z in (1.38, 2.61):
            m.disc(BRASS, (x, -.173, z), (x, -.197, z), .034, sides=8)
    return m


def log_stand():
    m = Mesh()
    m.box(BASALT, 0, .20, 0, 2.62, .92, .22)
    m.box(MASONRY, 0, .20, .19, 2.43, .74, .59)
    m.box(WOOD, 0, -.03, .75, 2.79, 1.20, .13)
    m.box(TRIM, 0, .48, .88, 2.79, .21, .14)
    m.box(BRASS, -.90, .15, .88, .48, .51, .035)
    for x in (-.98, -.78):
        m.tube(BRASS, (x, .05, .92), (x+.24, .28, .92), .018, sides=6)
    for x in (-1.20, 1.20):
        m.box(GILT, x, -.535, .79, .28, .046, .07)
    return m


def scribe_station():
    m = Mesh()
    m.box(BASALT, 0, .56, 0, 3.25, .62, .28)
    m.box(MASONRY, 0, .57, .27, 3.17, .51, 1.76)
    m.box(LIMESTONE, 0, .58, 2.01, 3.31, .66, .19)
    for x in (-1.34, 1.34):
        m.box(MASONRY, x, -.03, 0, .33, .93, .77)
    m.box(WOOD, 0, -.13, .76, 3.10, 1.14, .12)
    m.box(DARK, 0, .267, 1.18, 2.27, .15, .65)
    for x in (-.69, 0, .69):
        m.disc(BRASS, (x, .18, 1.51), (x, .128, 1.51), .227, sides=8)
        m.box(IRON, x, .118, 1.41, .14, .036, .19)
    m.disc(DARK, (.91, -.23, .88), (.91, -.23, 1.01), .098, sides=10)
    return m


def arms_rack():
    m = Mesh()
    m.box(WOOD, 0, .12, 0, 2.55, .68, .18)
    for x in (-1.09, 1.09):
        m.box(WOOD, x, .21, .17, .16, .19, 1.64)
    m.box(WOOD, 0, .18, 1.46, 2.33, .20, .14)
    for i in range(5):
        x = -.86 + .43 * i
        m.tube(WOOD, (x, -.17, .18), (x+.08, .14, 2.20), .041, sides=7)
        m.tube(IRON, (x+.08, .14, 2.16), (x+.11, .16, 2.53), .081, .009, sides=6)
    return m


def wick_table():
    m = Mesh()
    bench(m, 2.36, 1.18)
    for x, y, r in ((-.59, .12, .22), (-.13, .21, .16)):
        m.tube(OXIDE, (x,y,.88), (x,y,1.29), r, r*.65, sides=12)
        m.disc(BRASS, (x,y,1.26), (x,y,1.34), r*.65, sides=10)
        m.tube(BRASS, (x,y,1.27), (x,y,1.43), r*.29, sides=8)
    m.disc(BRASS, (.63,.13,.89), (.63,.13,1.025), .30, sides=12)
    for i in range(5):
        m.tube(PARCHMENT, (.36,-.41+i*.065,.92), (.90,-.38+i*.066,.92), .019, sides=6)
    return m


def ray_baffle():
    m = Mesh()
    m.box(BASALT, 0, 0, 0, 1.60, .89, .24)
    m.box(MASONRY, 0, .07, .23, 1.31, .67, 1.03)
    m.box(LIMESTONE, 0, .07, 1.23, 1.46, .73, .14)
    m.box(BRASS, 0, -.31, .43, .91, .105, .61)
    for x in (-.31, 0, .31):
        m.box(IRON, x, -.38, .47, .13, .09, .52)
    return m


def stair_headhouse():
    m = Mesh()
    for x in (-2.64, 2.64):
        m.box(BASALT, x, .62, -1.42, .79, 2.83, 1.65)
        m.box(MASONRY, x, .66, .18, .64, 2.74, 2.08)
        m.box(LIMESTONE, x, -.69, 1.87, .75, .36, .33)
    arch(m, 2.32, 1.91, -.66, .31, .30, LIMESTONE, masonry=True)
    for i in range(5):
        m.box(LIMESTONE if i == 0 else MASONRY, 0, -.79 + .39*i, -.018 + .13*i,
              4.62, .39, .17)
    m.box(MASONRY, 0, 1.43, .48, 4.63, .96, .18)
    arch(m, 2.01, 2.16, 1.74, .29, .22, MASONRY)
    shadow = Material((.055, .061, .077), 'hvd_rough')
    throat = [(2.03*cos(pi*i/18), 1.88, 2.16+2.03*sin(pi*i/18)) for i in range(19)]
    throat.extend(((-2.03, 1.88, .61), (2.03, 1.88, .61)))
    m.polygon(shadow, throat)
    for i in range(12):
        a, b = pi * i / 12, pi * (i+1) / 12
        x0, x1 = 2.64 * cos(a), 2.64 * cos(b)
        z0, z1 = 1.91 + 2.64 * sin(a), 1.91 + 2.64 * sin(b)
        m.polygon(MASONRY, ((x0, -.69, z0), (x0, 2.03, z0), (x1, 2.03, z1), (x1, -.69, z1)))
    return m


SCENERY = {
    'hvd_workroof': ('Měděná střecha servisní dílny', service_roof),
    'hvd_grinder': ('Brus čoček s vodní vanou', grinding_bench),
    'hvd_smithbench': ('Stůl s přípravkem na kování obrub', smith_bench),
    'hvd_capstan': ('Buben lana pro vytažení lávky', capstan),
    'hvd_writedesk': ('Stůl správkyně s folianti', writing_desk),
    'hvd_drawers': ('Přihrádky na hvězdné mapy', plan_drawers),
    'hvd_filtergrid': ('Sušák optických filtrů', filter_grid),
    'hvd_planrail': ('Technické výkresy clon', plans),
    'hvd_logstand': ('Pozorovací stolec s deníkem', log_stand),
    'hvd_register': ('Přijímací místo písaře pečetí', scribe_station),
    'hvd_spearrack': ('Stojan s náhradními kopími', arms_rack),
    'hvd_wicktable': ('Stůl na výměnu knotů a doplnění oleje', wick_table),
    'hvd_raybaffle': ('Stínicí blok optického dvora', ray_baffle),
    'hvd_headhouse': ('Klenutý vstup ke spodnímu schodišti', stair_headhouse),
}

# Preserve the native book type and description handling. Each volume gets a mesh and icon.
BOOK_COLORS = (
    (88, 102, 76), (82, 93, 113), (120, 77, 49), (65, 85, 132), (113, 66, 64),
    (95, 79, 101), (102, 84, 50), (67, 105, 91), (119, 87, 57),
)
BOOK_MODELS = {stock: 244 + stock for stock in range(2, 11)}


def book_assets():
    assets = {}
    for model, color in zip(BOOK_MODELS.values(), BOOK_COLORS, strict=True):
        name = f'it_book_{model:03d}'
        binding = Material(tuple(c / 255 for c in color), 'hvd_oak')
        mesh = Mesh()
        mesh.box(binding, 0, 0, .014, .68, .53, .036)
        mesh.box(PARCHMENT, .027, 0, .043, .60, .495, .092)
        mesh.box(binding, 0, 0, .132, .68, .53, .038)
        mesh.box(binding, -.318, 0, .043, .067, .533, .108)
        for y in (-.201, .201):
            mesh.box(BRASS, -.278, y, .161, .08, .035, .014)
        mesh.box(GILT, .035, -.018, .165, .24, .134, .009)
        assets[f'{name}.mdl'] = mesh.mdl(name).replace(b'classification Other', b'classification Item')
        icon = bytearray()
        for y in range(64):
            for x in range(64):
                if not (9 <= x < 55 and 6 <= y < 58):
                    icon.extend((0, 0, 0, 0))
                    continue
                if x >= 51:
                    shade = (212, 195, 151)
                elif x < 15 or y in (9, 54):
                    shade = (170, 128, 70)
                elif 23 <= x <= 42 and 25 <= y <= 39:
                    shade = (207, 171, 105)
                else:
                    shade = color
                icon.extend((*reversed(shade), 255))
        assets[f'i{name}.tga'] = pack('<BBBHHBHHHHBB',0,0,2,0,0,0,0,0,64,64,32,8) + icon
    return assets
