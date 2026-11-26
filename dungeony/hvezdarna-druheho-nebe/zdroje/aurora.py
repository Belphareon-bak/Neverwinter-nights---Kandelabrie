"""The Aurora V3.2 GFF and V1.0 ERF records used by the module builder."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path


BYTE, CHAR, WORD, SHORT, DWORD, INT, QWORD, INT64, FLOAT, DOUBLE = range(10)
STRING, RESREF, LOC, VOID, STRUCT, LIST = range(10, 16)
TYPE = {
    "tga": 3, "plt": 6, "mdl": 2002, "nss": 2009, "ncs": 2010, "are": 2012, "set": 2013, "ifo": 2014,
    "bic": 2015, "wok": 2016, "2da": 2017, "git": 2023, "uti": 2025,
    "utc": 2027, "itp": 2030, "utt": 2032, "dds": 2033, "gic": 2046, "utp": 2044,
    "utd": 2042, "dlg": 2029, "fac": 2038, "pwk": 2053, "jrl": 2056,
    "uts": 2035,
}
EXT = {number: name for name, number in TYPE.items()}


@dataclass
class Record:
    ident: int
    fields: dict

    def __init__(self, ident=0xFFFFFFFF, **fields):
        self.ident = ident
        self.fields = fields

    def value(self, label, default=None):
        field = self.fields.get(label)
        return field[1] if field is not None else default


def bite(value): return (BYTE, value)
def word(value): return (WORD, value)
def dword(value): return (DWORD, value)
def integer(value): return (INT, value)
def flt(value): return (FLOAT, value)
def string(value): return (STRING, value)
def ref(value): return (RESREF, value)
def loc(value): return (LOC, (0xFFFFFFFF, {0: value}))
def lst(value): return (LIST, value)


def gff_encode(kind: str, root: Record, encoding: str = "cp1250") -> bytes:
    labels, records, fields = {}, [], []
    field_data, field_indices, list_indices = bytearray(), bytearray(), bytearray()

    def data(raw):
        offset = len(field_data)
        field_data.extend(raw)
        return offset

    def value_of(field_type, value):
        if field_type < 6:
            return value & 0xFFFFFFFF
        if field_type == FLOAT:
            return struct.unpack("<I", struct.pack("<f", value))[0]
        if field_type in (QWORD, INT64, DOUBLE):
            return data(struct.pack({QWORD: "<Q", INT64: "<q", DOUBLE: "<d"}[field_type], value))
        if field_type in (STRING, RESREF, VOID):
            raw = value if field_type == VOID else value.encode("ascii" if field_type == RESREF else encoding)
            if field_type == RESREF:
                assert len(raw) <= 16, value
                return data(struct.pack("<B", len(raw)) + raw)
            return data(struct.pack("<I", len(raw)) + raw)
        if field_type == LOC:
            strref, versions = value
            body = bytearray(struct.pack("<II", strref, len(versions)))
            for language, text in versions.items():
                raw = text.encode(encoding) if isinstance(text, str) else text
                body.extend(struct.pack("<II", language, len(raw)) + raw)
            return data(struct.pack("<I", len(body)) + body)
        if field_type == STRUCT:
            return add_record(value)
        if field_type == LIST:
            children = [add_record(child) for child in value]
            offset = len(list_indices)
            list_indices.extend(struct.pack("<" + "I" * (1 + len(children)), len(children), *children))
            return offset
        raise ValueError(f"Unsupported GFF field type {field_type}")

    def add_record(record):
        index = len(records)
        records.append(None)
        own_fields = []
        for label, (field_type, value) in record.fields.items():
            raw_label = label.encode("ascii")
            assert len(raw_label) <= 16, label
            label_index = labels.setdefault(raw_label, len(labels))
            encoded_value = value_of(field_type, value)
            own_fields.append(len(fields))
            fields.append((field_type, label_index, encoded_value))
        count = len(own_fields)
        offset = 0
        if count == 1:
            offset = own_fields[0]
        elif count > 1:
            offset = len(field_indices)
            field_indices.extend(struct.pack("<" + "I" * count, *own_fields))
        records[index] = record.ident, offset, count
        return index

    add_record(root)
    blocks = [
        (b"".join(struct.pack("<III", *entry) for entry in records), len(records)),
        (b"".join(struct.pack("<III", *entry) for entry in fields), len(fields)),
        (b"".join(label.ljust(16, b"\0") for label in labels), len(labels)),
        (field_data, len(field_data)), (field_indices, len(field_indices)),
        (list_indices, len(list_indices)),
    ]
    header = bytearray(kind.upper().encode("ascii").ljust(4, b" ") + b"V3.2")
    offset = 56
    for block, count in blocks:
        header.extend(struct.pack("<II", offset, count))
        offset += len(block)
    return bytes(header) + b"".join(block for block, _ in blocks)


def gff_decode(raw: bytes, encoding: str = "cp1252") -> Record:
    assert raw[4:8] == b"V3.2", raw[:8]
    structure, _, fields, _, labels, _, data, _, indices, _, lists, _ = struct.unpack_from("<12I", raw, 8)

    def uint(offset):
        return struct.unpack_from("<I", raw, offset)[0]

    def value_of(field_type, value):
        offset = data + value
        if field_type in (BYTE, CHAR, WORD, SHORT, DWORD, INT, FLOAT):
            return struct.unpack({BYTE: "<B", CHAR: "<b", WORD: "<H", SHORT: "<h",
                                  DWORD: "<I", INT: "<i", FLOAT: "<f"}[field_type],
                                 struct.pack("<I", value)[:{BYTE: 1, CHAR: 1, WORD: 2, SHORT: 2}.get(field_type, 4)])[0]
        if field_type in (QWORD, INT64, DOUBLE):
            return struct.unpack_from({QWORD: "<Q", INT64: "<q", DOUBLE: "<d"}[field_type], raw, offset)[0]
        if field_type in (STRING, RESREF, VOID):
            length_size = 1 if field_type == RESREF else 4
            length = raw[offset] if length_size == 1 else uint(offset)
            value = raw[offset + length_size:offset + length_size + length]
            return value if field_type == VOID else value.decode(encoding, errors="replace")
        if field_type == LOC:
            _, strref, count = struct.unpack_from("<III", raw, offset)
            offset += 12
            values = {}
            for _ in range(count):
                language, length = struct.unpack_from("<II", raw, offset)
                offset += 8
                values[language] = raw[offset:offset + length]
                offset += length
            return strref, values
        if field_type == STRUCT:
            return record_at(value)
        if field_type == LIST:
            offset = lists + value
            return [record_at(uint(offset + 4 + index * 4)) for index in range(uint(offset))]
        raise ValueError(f"Unsupported GFF field type {field_type}")

    def record_at(index):
        ident, source, count = struct.unpack_from("<III", raw, structure + index * 12)
        result = Record(ident)
        field_ids = [source] if count == 1 else [uint(indices + source + step * 4) for step in range(count)]
        for field in field_ids:
            kind, label_index, value = struct.unpack_from("<III", raw, fields + field * 12)
            start = labels + label_index * 16
            label = raw[start:start + 16].rstrip(b"\0").decode("ascii")
            result.fields[label] = kind, value_of(kind, value)
        return result

    return record_at(0)


def erf_encode(resources: dict[str, bytes], kind: str = "MOD") -> bytes:
    key_entries, resource_entries, data = bytearray(), bytearray(), bytearray()
    offset = 160 + len(resources) * 32
    for index, (file, content) in enumerate(sorted(resources.items())):
        name, extension = file.rsplit(".", 1)
        name = name.lower().encode("ascii")
        assert 0 < len(name) <= 16, file
        key_entries.extend(struct.pack("<16sIHH", name, index, TYPE[extension], 0))
        resource_entries.extend(struct.pack("<II", offset + len(data), len(content)))
        data.extend(content)
    header = struct.pack("<4s4s9I116x", kind.encode("ascii").ljust(4, b" "), b"V1.0",
                         0, 0, len(resources), 160, 160, 160 + len(resources) * 24,
                         126, 321, 0xFFFFFFFF)
    return header + key_entries + resource_entries + data


def erf_index(path: Path):
    raw = path.read_bytes()
    count, _, keys, resources = struct.unpack_from("<4I", raw, 16)
    result = {}
    for key in range(count):
        name, ident, kind, _ = struct.unpack_from("<16sIHH", raw, keys + key * 24)
        start, length = struct.unpack_from("<II", raw, resources + ident * 8)
        result[name.rstrip(b"\0").decode("ascii"), kind] = raw[start:start + length]
    return result


class GameResources:
    def __init__(self, game: Path):
        self.game = game
        self.index = {}
        self.bif_offsets = {}
        for database in sorted((game / "data").glob("*.key")):
            raw = database.read_bytes()
            bif_count, key_count, files, keys = struct.unpack_from("<4I", raw, 8)
            archive_names = []
            for index in range(bif_count):
                _, name_at, length, _ = struct.unpack_from("<IIHH", raw, files + index * 12)
                name = raw[name_at:name_at + length].rstrip(b"\0").decode("ascii").replace("\\", "/").lower()
                archive_names.append(game / name)
            for index in range(key_count):
                name, kind, ident = struct.unpack_from("<16sHI", raw, keys + index * 22)
                self.index[name.rstrip(b"\0").decode("ascii").lower(), kind] = (
                    archive_names[ident >> 20], ident & 0xFFFFF,
                )

    def read(self, name, kind):
        archive, ident = self.index[name, TYPE.get(kind, kind)]
        with archive.open("rb") as file:
            if archive not in self.bif_offsets:
                magic, version, _, _, offset = struct.unpack("<4s4sIII", file.read(20))
                assert (magic, version) == (b"BIFF", b"V1  "), (archive, magic, version)
                self.bif_offsets[archive] = offset
            file.seek(self.bif_offsets[archive] + ident * 16)
            _, offset, length, resource_type = struct.unpack("<4I", file.read(16))
            assert resource_type == TYPE.get(kind, kind), (name, kind, resource_type)
            file.seek(offset)
            return file.read(length)

    def tlk(self, index):
        with (self.game / "lang/en/data/dialog.tlk").open("rb") as file:
            magic, _, _, count, strings = struct.unpack("<4s4sIII", file.read(20))
            if magic != b"TLK " or not 0 <= index < count:
                return ""
            file.seek(20 + index * 40 + 28)
            offset, length = struct.unpack("<II", file.read(8))
            file.seek(strings + offset)
            return file.read(length).decode("cp1252", errors="replace")
