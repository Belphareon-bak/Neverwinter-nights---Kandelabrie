"""Area construction from an original floor plan and the installed tilesets."""

from collections import defaultdict
from dataclasses import dataclass, field
import math
import random
import re

from aurora import STRUCT, Record, bite, dword, flt, integer, loc, lst, ref, string, word
from plan import height_at


CORNERS = ("BottomLeft", "BottomRight", "TopRight", "TopLeft")
OFFSETS = ((0, 0), (1, 0), (1, 1), (0, 1))
SURFACES = {
    "tts02": ("snow", "trees", (120, 123, 124, 126, 116)),
    "tni02": ("stone", "wall", (90,)),
    "hvd_interior": ("stone", "wall", (0,)),
    "tcm02": ("cobble", "chasm", (34, 35, 36)),
}


def variables(**values):
    types = {str: (3,string), float: (2,flt)}
    records = []
    for name,value in values.items():
        kind,field = types.get(type(value),(1,integer))
        records.append(Record(0,Name=string(name),Type=dword(kind),Value=field(value)))
    return lst(records)


def color(red, green, blue):
    return dword(red | green << 8 | blue << 16)


class Tileset:
    def __init__(self, resource, name, custom=None, paving=None):
        self.name = name
        self.floor, self.border, self.plain = SURFACES[name]
        if paving is not None:
            self.plain = (paving,)
        self.choices = defaultdict(list)
        self.rows = {}
        raw = (custom if custom is not None else resource.read(name, "set")).decode("latin-1")
        for match in re.finditer(r"\[TILE(\d+)\]\s*([^\[]+)", raw):
            ident = int(match[1])
            row = dict(line.strip().split("=", 1) for line in match[2].splitlines() if "=" in line)
            self.rows[ident] = row
            if row.get("Doors") != "0" or any(row.get(edge) for edge in ("Top", "Right", "Bottom", "Left")):
                continue
            pattern = self.pattern(row)
            if any(surface not in (self.floor, self.border) for surface, _ in pattern):
                continue
            for rotation in range(4):
                rotated = pattern[-rotation:] + pattern[:-rotation] if rotation else pattern
                self.choices[rotated].append((ident, rotation))

    @staticmethod
    def pattern(row):
        return tuple((row[corner].lower(), int(row[corner + "Height"])) for corner in CORNERS)

    def make_tiles(self, area):
        rng = random.Random(area.key)
        tiles = []
        for y in range(area.height):
            for x in range(area.width):
                vertices = [(x + dx, y + dy) for dx, dy in OFFSETS]
                heights = [area.vertex_height(vy) for _, vy in vertices]
                floor_height = min(heights)
                pattern = tuple((self.floor if area.on_floor(vx, vy) else self.border, h - floor_height)
                                for (vx, vy), h in zip(vertices, heights))
                options = self.choices[pattern]
                if pattern == ((self.floor, 0),) * 4:
                    options = [(ident, angle) for ident in self.plain for angle in range(4)]
                if len(set(heights)) > 1 and self.name == "tcm02":
                    stairs = [(ident, angle) for ident, angle in options if ident in (27, 1040, 1041)]
                    if stairs:
                        if y in area.stair_columns:
                            # Keep the rest of a raised terrace as a continuous
                            # retaining wall with one authored flight.
                            tile = 27 if x in area.stair_columns[y] else 0
                            options = [entry for entry in options if entry[0] == tile]
                        else:
                            options = stairs
                if (x, y) in area.special_tiles:
                    ident, rotation = area.special_tiles[x, y]
                    tile_pattern = self.pattern(self.rows[ident])
                    if rotation:
                        tile_pattern = tile_pattern[-rotation:] + tile_pattern[:-rotation]
                    if not area.fixed_tiles:
                        assert tile_pattern == pattern, (area.key, x, y, ident, tile_pattern, pattern)
                else:
                    assert options, (area.key, x, y, pattern)
                    if pattern == ((self.border, 0),) * 4:
                        options = options[:4]
                    ident, rotation = rng.choice(options)
                main1, main2, source1, source2 = area.tile_lights.get((x, y), (0, 0, 0, 0))
                tiles.append(Record(
                    1, Tile_ID=integer(ident), Tile_Orientation=integer(rotation),
                    Tile_Height=integer(floor_height),
                    Tile_MainLight1=bite(main1), Tile_MainLight2=bite(main2),
                    Tile_SrcLight1=bite(source1), Tile_SrcLight2=bite(source2),
                    Tile_AnimLoop1=bite(1), Tile_AnimLoop2=bite(1), Tile_AnimLoop3=bite(1),
                ))
        return tiles


def coordinates(x, y, z, bearing):
    return dict(X=flt(x), Y=flt(y), Z=flt(z), Bearing=flt(math.radians(bearing)))


@dataclass
class Area:
    key: str
    title: str
    tileset: str
    width: int
    height: int
    rooms: list
    purpose: str
    special_tiles: dict = field(default_factory=dict)
    fixed_tiles: bool = False
    high_row: int = 999
    places: list = field(default_factory=list)
    waypoints: list = field(default_factory=list)
    triggers: list = field(default_factory=list)
    doors: list = field(default_factory=list)
    encounter_positions: dict = field(default_factory=dict)
    rises: tuple = ()
    relief: tuple = ()
    stair_columns: dict = field(default_factory=dict)
    tile_lights: dict = field(default_factory=dict)
    lighting: dict = field(default_factory=dict)
    soundscape: dict = field(default_factory=dict)

    def on_floor(self, x, y):
        return any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in self.rooms)

    def vertex_height(self, y):
        return sum(y >= row for row in (self.rises or (self.high_row,)))

    def z_at(self, y):
        if self.relief:
            return height_at(self.relief,y)
        # Castle Exterior places its cobbled surfaces five metres above the tile origin.
        base = 5.0 if self.tileset == "tcm02" else 0.0
        for row in (self.rises or (self.high_row,)):
            base += max(0.0, min(5.0, (y - (row - 1) * 10) * 0.5))
        return base

    def point(self, tag, x, y, bearing=90, title="", z=None, **settings):
        z = self.z_at(y) if z is None else z
        point = Record(
            5, Appearance=bite(1), LinkedTo=string(""), TemplateResRef=ref(""),
            Tag=string(tag), LocalizedName=loc(title or tag), Description=loc(""),
            HasMapNote=bite(bool(title)), MapNote=loc(title), MapNoteEnabled=bite(bool(title)),
            XPosition=flt(x), YPosition=flt(y), ZPosition=flt(z),
            XOrientation=flt(math.cos(math.radians(bearing))), YOrientation=flt(math.sin(math.radians(bearing))),
        )
        if settings:
            point.fields["VarTable"] = variables(**settings)
        self.waypoints.append(point)
        return self

    def prop(self, appearance, name, x, y, *, tag="", action="", text="", bearing=0, z=None, **settings):
        z = self.z_at(y) if z is None else z
        fields = object_fields(tag, name, text)
        fields.update(Appearance=dword(appearance), Type=bite(0), HasInventory=bite(0),
                      Static=bite(not action and not settings.get("cover")), Useable=bite(bool(action)),
                      OnInvDisturbed=ref(""), OnUsed=ref("hvd_use" if action else ""),
                      BodyBag=bite(0))
        if action or settings:
            fields["VarTable"] = variables(action=action, **settings)
        self.places.append(Record(9, **fields, **coordinates(x, y, z, bearing)))
        return self

    def stash(self, appearance, name, x, y, tag, *, bearing=0, text="", key="", reward=False, z=None):
        self.prop(appearance, name, x, y, tag=tag, bearing=bearing, text=text, z=z)
        self.places[-1].fields.update(
            Static=bite(0), Useable=bite(1), HasInventory=bite(1), ItemList=lst([]),
            Locked=bite(bool(key)), Lockable=bite(bool(key)), KeyRequired=bite(reward),
            KeyName=string(key), OpenLockDC=bite(34 if key else 0),
            OnInvDisturbed=ref("hvd_reward" if reward else ""),
            OnOpen=ref("hvd_reward_open" if reward else ""),
        )
        return self

    def find(self, resource, x, y, *, height=0, bearing=0, clue=0):
        return self.point("hvd_find", x, y, bearing, z=self.z_at(y) + height, find=resource, clue=clue)

    def passage(self, name, x, y, to, bearing=0, appearance=28, **settings):
        return self.prop(appearance, name, x, y, action="pass", target=to, bearing=bearing, **settings)

    def encounter(self, group, name, *approaches):
        for bounds in approaches:
            self.trigger(name, "hvd_encounter", bounds, "hvd_zone", encounter=group)

    def mob(self, group, refname, x, y, *, seal=0, bearing=90, elite=0, leash=20):
        index = self.encounter_positions.get(group, 0) + 1
        self.encounter_positions[group] = index
        return self.point(f"hvs_{group}_{index}", x, y, bearing=bearing, spawn=refname, encounter=group,
                          seal=seal, elite=elite, leash=leash)

    def trap(self, name, tag, bounds, **settings):
        self.trigger(name, tag, bounds, "hvd_zone", **settings)
        return self

    def transition(self, name, tag, bounds, target, *, require="", minimum_level=0, secret=0):
        if require:
            # Closed paths stay unmarked until their reveal. Walking into them
            # invokes the progression check instead of the engine's default jump.
            self.trigger(name, tag, bounds, "hvd_travel", target=target, require=require,
                         minimum_level=minimum_level, hidden_route=secret)
        else:
            trigger = self.trigger(name, tag, bounds, "hvd_travel", target=target)
            trigger.fields.update(Cursor=bite(1), Type=integer(1), LinkedTo=string(target),
                                  LinkedToFlags=bite(2))
        return self

    def trigger(self, name, tag, bounds, on_enter, **settings):
        x0, y0, x1, y1 = bounds
        center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
        z = self.z_at(center_y)
        vertices = [Record(3, PointX=flt(x - center_x), PointY=flt(y - center_y), PointZ=flt(0))
                    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        record = Record(
            1, TemplateResRef=ref(""), Tag=string(tag), LocalizedName=loc(name), Description=loc(""),
            Cursor=bite(0), Faction=dword(0), HighlightHeight=flt(0),
            LinkedTo=string(""), LinkedToFlags=bite(0), TrapFlag=bite(0), Type=integer(0),
            OnClick=ref(""), ScriptOnEnter=ref(on_enter), ScriptOnExit=ref(""),
            ScriptHeartbeat=ref(""), ScriptUserDefine=ref(""),
            XPosition=flt(center_x), YPosition=flt(center_y), ZPosition=flt(z),
            XOrientation=flt(1), YOrientation=flt(0), ZOrientation=flt(0),
            Geometry=lst(vertices), VarTable=variables(x0=float(x0),y0=float(y0),
                                                      x1=float(x1),y1=float(y1),**settings),
        )
        self.triggers.append(record)
        return record

    def door(self, tag, name, x, y, *, key, bearing=0, generic=7):
        fields = object_fields(tag, name, "Na kameni je vyrytý znak hlídky.")
        fields.update(GenericType=bite(generic), Appearance=dword(0), LinkedTo=string(""),
                      LinkedToFlags=bite(0), LoadScreenID=word(0), Locked=bite(1), Lockable=bite(1),
                      KeyRequired=bite(1), KeyName=string(key), OnFailToOpen=ref("hvd_doortxt"),
                      OnClick=ref(""))
        self.doors.append(Record(8, **fields, **coordinates(x, y, self.z_at(y), bearing)))
        return self

    def records(self, tileset):
        indoor = self.tileset in ("tni02", "hvd_interior")
        mountain = self.tileset == "tts02"
        snow = color(180, 199, 219)
        moon = color(45, 61, 91)
        are = Record(
            ID=integer(-1), Creator_ID=integer(0), Version=dword(1), Tag=string(self.key), Name=loc(self.title),
            ResRef=ref(self.key), Comments=string(self.purpose), Expansion_List=lst([]), Flags=dword(int(indoor)),
            ModSpotCheck=integer(0), ModListenCheck=integer(0),
            MoonAmbientColor=moon if not indoor else color(76, 70, 81),
            MoonDiffuseColor=color(151, 163, 221), MoonFogAmount=bite(10 if not indoor else 1),
            MoonFogColor=color(81, 104, 155), MoonShadows=bite(1),
            SunAmbientColor=snow if mountain else color(160, 177, 220),
            SunDiffuseColor=color(223, 230, 250), SunFogAmount=bite(12 if mountain else 1),
            SunFogColor=snow, SunShadows=bite(1), IsNight=bite(not mountain),
            LightingScheme=bite(0), ShadowOpacity=bite(45), DayNightCycle=bite(0),
            ChanceRain=integer(0), ChanceSnow=integer(65 if mountain else 0),
            ChanceLightning=integer(0), WindPower=integer(0 if indoor else 2),
            SkyBox=bite(0 if indoor else 4 if mountain else 5), LoadScreenID=word(0),
            PlayerVsPlayer=bite(0), NoRest=bite(1), Width=integer(self.width), Height=integer(self.height),
            OnEnter=ref("hvd_enter"), OnExit=ref("hvd_exit"), OnHeartbeat=ref("hvd_area_hb"),
            OnUserDefined=ref(""), Tileset=ref(self.tileset), Tile_List=lst(tileset.make_tiles(self)),
        )
        ambient = Record(100, AmbientSndDay=integer(31 if mountain else 67 if indoor else 202),
                         AmbientSndNight=integer(31 if mountain else 67 if indoor else 202),
                         AmbientSndDayVol=integer(57), AmbientSndNitVol=integer(57), EnvAudio=integer(0 if not indoor else 13),
                         MusicBattle=integer(60), MusicDay=integer(59 if mountain else 50 if indoor else 49),
                         MusicNight=integer(59 if mountain else 50 if indoor else 49), MusicDelay=integer(48000))
        are.fields.update(self.lighting)
        ambient.fields.update(self.soundscape)
        lists = {
            "Creature List": [], "Door List": self.doors, "Encounter List": [], "List": [],
            "SoundList": [], "StoreList": [], "TriggerList": self.triggers,
            "WaypointList": self.waypoints, "Placeable List": self.places,
        }
        git = Record(AreaProperties=(STRUCT, ambient), **{k: lst(v) for k, v in lists.items()})
        gic = Record(**{k: lst([Record(item.ident, Comment=string("")) for item in v]) for k, v in lists.items()})
        return {"are": are, "git": git, "gic": gic}


def object_fields(tag, name, description):
    fields = dict(Tag=string(tag), LocName=loc(name), Description=loc(description),
                  TemplateResRef=ref(""), AutoRemoveKey=bite(0), CloseLockDC=bite(0),
                  Conversation=ref(""), Interruptable=bite(1), Faction=dword(1), Plot=bite(1),
                  KeyRequired=bite(0), Lockable=bite(0), Locked=bite(0), OpenLockDC=bite(0), PortraitId=word(0),
                  TrapDetectable=bite(0), TrapDetectDC=bite(0), TrapDisarmable=bite(0), DisarmDC=bite(0),
                  TrapFlag=bite(0), TrapOneShot=bite(0), TrapType=bite(0), KeyName=string(""),
                  AnimationState=bite(0), HP=(3, 40), CurrentHP=(3, 40), Hardness=bite(8),
                  Fort=bite(0), Ref=bite(0), Will=bite(0))
    for event in ("OnClosed", "OnDamaged", "OnDeath", "OnDisarm", "OnHeartbeat", "OnLock",
                  "OnMeleeAttacked", "OnOpen", "OnSpellCastAt", "OnTrapTriggered", "OnUnlock", "OnUserDefined"):
        fields[event] = ref("")
    return fields
