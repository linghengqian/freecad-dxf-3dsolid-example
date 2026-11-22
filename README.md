# FreeCAD DXF 3DSOLID example (ezdxf stand-in)

Two minimal DXF files, each with one 3DSOLID entity: a 10 × 10 × 10 box with six planar faces. They are a stand-in for the minimal example described in https://github.com/FreeCAD/FreeCAD/discussions/34011.

- `standin-box-r2000-sat.dxf`: DXF R2000 (AC1015). The ACIS data is stored as SAT text in the entity.
- `standin-box-r2018-sab.dxf`: DXF R2018 (AC1032). The ACIS data is stored as SAB binary in the ACDSDATA section.

## How they were made

`make_standin.py` (ezdxf 1.4.5) builds the box as a polyhedron mesh, converts it to an ACIS body with `ezdxf.acis.api.body_from_mesh`, and writes it to a 3DSOLID entity. Run it with an output directory:

    python make_standin.py out/

Both files were reloaded with ezdxf afterwards: one 3DSOLID entity, six faces, bounding box 10 × 10 × 10, no audit errors.

## What these files are not

- They were not produced by AutoCAD. AutoCAD's own ACIS output may differ.
- There is no DWG file. ezdxf cannot write DWG, and no DWG converter was available.
- They have not been opened in FreeCAD. The behaviour described in the discussion (the solid is dropped on import) has not yet been reproduced with these files.
