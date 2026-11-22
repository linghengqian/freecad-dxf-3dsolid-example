"""Write DXF files with one 3DSOLID box, using ezdxf's ACIS support.

Usage: python make_standin.py OUTPUT_DIR

Writes standin-box-r2000-sat.dxf (SAT text) and standin-box-r2018-sab.dxf (SAB in ACDSDATA),
then reloads each file and prints what it found. Requires ezdxf 1.4.5.
"""

import pathlib
import sys

import ezdxf
from ezdxf.acis import api as acis
from ezdxf.math import BoundingBox, Vec3
from ezdxf.render import MeshBuilder

CORNERS = [
    (0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0),
    (0, 0, 10), (10, 0, 10), (10, 10, 10), (0, 10, 10),
]
# Quads wound counter-clockwise when seen from outside the box.
QUADS = [
    (0, 3, 2, 1),  # bottom, z = 0
    (4, 5, 6, 7),  # top, z = 10
    (0, 1, 5, 4),  # front, y = 0
    (1, 2, 6, 5),  # right, x = 10
    (2, 3, 7, 6),  # back, y = 10
    (3, 0, 4, 7),  # left, x = 0
]


def make_box_mesh() -> MeshBuilder:
    mesh = MeshBuilder()
    mesh.vertices = [Vec3(c) for c in CORNERS]
    mesh.faces = [list(q) for q in QUADS]
    return mesh


def write_standin(path: pathlib.Path, dxfversion: str) -> None:
    doc = ezdxf.new(dxfversion)
    body = acis.body_from_mesh(make_box_mesh())
    solid = doc.modelspace().add_3dsolid()
    if doc.dxfversion >= "AC1027":  # R2013 and later: SAB stored in the ACDSDATA section
        solid.sab = acis.export_sab([body])
    else:  # R2000 to R2010: SAT text stored in the entity
        solid.sat = acis.export_sat([body])
    doc.saveas(str(path))


def verify(path: pathlib.Path) -> dict:
    doc = ezdxf.readfile(str(path))
    audit = doc.audit()
    result = {
        "file": path.name,
        "dxf_version": doc.dxfversion,
        "audit_errors": len(audit.errors),
        "3DSOLID_entities": 0,
        "faces": [],
        "bbox_size": None,
    }
    all_vertices = []
    for entity in doc.modelspace().query("3DSOLID"):
        result["3DSOLID_entities"] += 1
        for body in acis.load(entity.acis_data):
            for mesh in acis.mesh_from_body(body):
                result["faces"].append(len(mesh.faces))
                all_vertices.extend(mesh.vertices)
    if all_vertices:
        bbox = BoundingBox(all_vertices)
        result["bbox_size"] = tuple(round(v, 3) for v in bbox.size)
    text = path.read_text(encoding="utf-8", errors="replace")
    result["text_has_3DSOLID"] = "3DSOLID" in text
    result["text_has_ACDSDATA"] = "ACDSDATA" in text
    return result


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, version in [
        ("standin-box-r2000-sat.dxf", "R2000"),
        ("standin-box-r2018-sab.dxf", "R2018"),
    ]:
        target = out / name
        write_standin(target, version)
        print(verify(target))
