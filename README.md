# Teapot

A RenderMan render project for the Utah teapot, rendered with
[gman](https://github.com/jac18281828/gman). The RIB files under `assets/` are the masters.

## Render

Run every command from this directory.

```sh
make shot=full                            # next renders/full/full_vNNN.png
make shot=museum                          # the teapot in its museum case; builds build/tex first
make all                                  # every shot
RENDERER=gmanraytracer make shot=full     # gmanpathtracer by default
GMAN=/path/to/gman make shot=full         # gman on PATH by default
FORMAT=tiff make shot=full                # png by default; needs that driver in gman
```

A render never overwrites an earlier version. `tools/render.sh` writes a frame RIB under
`build/frames/` that names the output and reads the shot, and stops before rendering when gman is
older than 1.3.1 or lacks the format's driver. Versions count across formats.

## Layout

| Path | Holds |
|---|---|
| `assets/teapot/teapot.rib` | The asset's entry: every part with its look, two-sided |
| `assets/teapot/lookdev/<part>.rib` | One part's material, bound to its geometry |
| `assets/teapot/geo/<part>.rib` | One `PointsPolygons` of triangles with `"P"`, vertex `"N"` and `"st"` |
| `assets/teapot/teapot_tall.rib` | The teapot at the physical teapot's height, 4/3 of Blinn's |
| `assets/museum/museum.rib` | The museum display: cherry frame and plinth, marble border, glass lightbox, acrylic case |
| `assets/museum/tex/` | Master TIFFs: `<map>_diff` colour, `<map>_nrm` normal (DirectX convention) |
| `lights/studio.rib` | The light rig |
| `shots/<shot>/shot.rib` | Camera, format, samples and what the shot reads |
| `tools/` | `render.sh` |
| `tests/` | `unittest` suites: `python3 -I -m unittest discover -s tests -v` |
| `AGENTS.md` | The project's facts, workflow and completion gates |
| `build/`, `renders/` | Generated; not tracked |

Parts, by 1-based patch index in the source's file order: `body` 1-12 (rim and body), `handle` 13-16,
`spout` 17-20, `lid` 21-28, `bottom` 29-32. A shot that wants a subset reads `lookdev/<part>.rib`
files directly.

## Conventions

- Axes are RenderMan camera space: x right, y up, z away from the camera. The bottom sits at y 0
  and the lid's knob tops out at y 3.15; the spout points to +x and the handle to -x. The source is
  z-up, and the import maps a data point `(x, y, z)` to `(x, z, y)`.
- `geo/` is the master: each patch is tessellated at 32 x 32 quads per patch, each split into two
  triangles, with exact normals. `make` never generates it.
- `"N"` is the exact surface normal, unit length and finite everywhere, including the lid's
  and the bottom's collapsed edges. Every patch's normals face away from the teapot's interior.
  `"st"` is each patch's own (u, v) in [0, 1].
- A new shot is a directory under `shots/` with a `shot.rib` that has no `Display`.

## Credit

The data is the Utah teapot, from `teapotCGA.bpt`: the 32 bicubic Bezier patches Frank Crow
published in IEEE Computer Graphics and Applications in January 1987, as digitized by
holmes3d.net.

- URL: `http://www.holmes3d.net/graphics/teapot/teapotCGA.bpt`
- sha256: `83c3cf09ff33cff17b8de714836c4c6758fccfc4288cef8671bacf0b7c294953`

The museum textures are CC0 scans from [ambientCG](https://ambientcg.com): `Marble020` for the
border and `Wood067` for the frame, each its 2K colour and DirectX normal map converted to TIFF.

## Known gman defects

- gman 1.3.1 emits light only from `Sphere` and `Disk`. The museum's lightbox is one polygon area
  light, which needs gman `main` at `86ef3c1` or later until the next release. 1.3.1 skips the
  panel with a warning, `area-light primitive(s) are ineligible or unsupported`, and renders the
  floor unlit; `tools/render.sh` passes either build, since its floor is 1.3.1.

- gman 1.3.1 builds nothing for `Patch`: `GMANRayObjectManager::getRSPatch` returns an empty
  primitive. The import tessellates the patches into `PointsPolygons` instead.
- The path tracer skips `ambientlight`, so `lights/studio.rib`'s ambient light adds nothing there.
