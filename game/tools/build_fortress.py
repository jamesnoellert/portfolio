# Builds the two game files for the Fortress level from the render set export:
#   models/Fortress_v5.glb      what players see: cleaned up, heavy plants simplified, objects merged by material,
#                                textures shrunk to JPEG, geometry Draco-compressed
#   models/Fortress_v5_col.glb  what the game collides with (and shoots, sees and walks on): simplified terrain and fort,
#                                props as boxes, no plants, plus the closed front gate as a box named Front_Gate
# Run (from the game folder):
#   "/Applications/Blender 5.2.app/Contents/MacOS/Blender" -b --python tools/build_fortress.py -- <render set .glb> models
import bpy, sys, os, tempfile
from mathutils import Vector

SRC, OUT = sys.argv[-2], sys.argv[-1]
TMP = tempfile.mkdtemp()  # shrunk textures, only needed while exporting

# Not part of the level: characters and their props, the render-only cannon, and render helpers
DROP_ROOTS = {'RIG-Cloud_Human', 'RIG-Cloud_Apprentice', 'Prop Rig', 'Prop Rig Apprentice', 'Roof Cannon'}
DROP_NAMES = {'Temp Land', 'Hill for shadow', 'Plane.002', 'Where the Master is plugging something in.001', 'Cable Socket'}
KEEP_APART = {'Water', 'Important Computer'}  # the game looks these up by name
# Display: simplify the heaviest meshes (name prefix -> target triangles)
DISPLAY_TRIS = {'Terrain': 90000, 'Flame': 4000, 'Computer_room_v04': 6000, 'Palm leaf 2': 3000, 'Morel': 2500, 'Bush': 2500, 'Pear': 2500}
# Display: largest texture size per image (name prefix -> pixels); everything else gets DEFAULT_TEX
TEX_SIZE = {'Terrain_Base': 2048, 'Fort_': 2048, 'Ground': 1024, 'ephemera': 1024, 'Screen_Map': 1024, 'theshining': 1024, 'Midas_Battery': 1024}
DEFAULT_TEX = 512
# Collision: structure kept as (simplified) meshes; everything else becomes a box or is left out
COL_TRIS = {'Terrain': 20000, 'fort_sculpt_2': 20000}  # the tower and its stairs stay exact: simplifying narrows the landings
COL_MESHES = {'Terrain', 'fort_sculpt_2', 'fort_sculpt_2.001', 'Fort Tower', 'Stairs', 'Stairs.001', 'Door Old Wood', 'Water'}
COL_SKIP = ('Flame', 'Morel', 'Bush', 'Pear', 'Palm', 'Cypress', 'Mball', 'Ball trees', 'Big tree', 'Courtyard tree', 'ball flower',
            'Trunks', 'Red LED', 'Yellow LED', 'Catenary', 'Window', 'Mill work', 'Sign', 'theshining', 'Gauge', 'Dails', 'Botton Box',
            'Keyboard', 'Rack spacing', 'A', 'B', 'B.001')
# The closed gate in the passage under the wall walk, in game coordinates (x, y up, z toward the attackers)
GATE = ((-3.55, 33.45, 2.95), (-0.25, 36.5, 3.55))


def load():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC)
    shown = set(bpy.context.view_layer.objects.keys())
    drop = []
    for o in bpy.data.objects:  # decide everything first: removing a parent would hide where its children came from
        root = o
        while root.parent: root = root.parent
        no_mat = o.type == 'MESH' and not any(o.data.materials) and o.name != 'Scrap Truck'
        cannon = o.type == 'MESH' and any(m and m.name == 'MAT Cannon' for m in o.data.materials)
        if o.name not in shown or root.name in DROP_ROOTS or o.name in DROP_NAMES or no_mat or cannon: drop.append(o)
    for o in drop: bpy.data.objects.remove(o, do_unlink=True)
    for o in bpy.data.objects:  # free children of anything removed, keeping their place
        if o.parent:
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    for o in [o for o in bpy.data.objects if o.type != 'MESH']: bpy.data.objects.remove(o, do_unlink=True)
    for o in bpy.data.objects:  # single users without shape keys, so modifiers can be applied
        o.data = o.data.copy()
        if o.data.shape_keys: o.shape_key_clear()


def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)


def decimate(o, target):
    t = tris(o)
    if t <= target: return
    m = o.modifiers.new('dec', 'DECIMATE'); m.ratio = target / t
    with bpy.context.temp_override(object=o, active_object=o): bpy.ops.object.modifier_apply(modifier=m.name)


def prefix(name, table):
    for k, v in table.items():
        if name.startswith(k): return v
    return None


def export(path, **kw):
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=False, export_apply=True, export_cameras=False,
                              export_lights=False, export_animations=False, export_skins=False, export_morph=False, export_extras=False, **kw)


def report(label, path):
    print(f'BUILT {label}: {os.path.getsize(path) / 1e6:.1f} MB, {len(bpy.data.objects)} objects, {sum(tris(o) for o in bpy.data.objects)} triangles')


# ---------- Display version ----------
load()
truck = bpy.data.objects.get('Scrap Truck')
if truck and not any(truck.data.materials): truck.data.materials.append(bpy.data.materials.get('MAT METAL DARK'))
for o in bpy.data.objects:
    t = prefix(o.name, DISPLAY_TRIS)
    if t: decimate(o, t)
# Merge everything that shares a material into one object, so each material is drawn once
group = [o for o in bpy.data.objects if o.name not in KEEP_APART]
bpy.ops.object.select_all(action='DESELECT')
for o in group: o.select_set(True)
bpy.context.view_layer.objects.active = group[0]
bpy.ops.object.join()
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='MATERIAL'); bpy.ops.object.mode_set(mode='OBJECT')
for o in bpy.data.objects:
    if o.name not in KEEP_APART and o.data.materials: o.name = 'M ' + o.data.materials[0].name
# Textures: shrink, and store as JPEG unless the material needs transparency
for img in list(bpy.data.images):
    if not img.users or img.size[0] == 0: continue
    size = prefix(img.name, TEX_SIZE) or DEFAULT_TEX
    if img.size[0] > size: img.scale(size, size)
    alpha = img.name.startswith('theshining')
    path = os.path.join(TMP, img.name.replace('/', '_') + ('.png' if alpha else '.jpg'))
    img.file_format = 'PNG' if alpha else 'JPEG'
    img.save(filepath=path, quality=85)
    new = bpy.data.images.load(path); new.colorspace_settings.name = img.colorspace_settings.name; new.name = img.name + ' small'
    img.user_remap(new)
disp = os.path.join(OUT, 'Fortress_v5.glb')
export(disp, export_image_format='AUTO', export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
       export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12)
report('display', disp)

# ---------- Collision version ----------
load()
for o in list(bpy.data.objects):
    if o.name in COL_MESHES:
        t = COL_TRIS.get(o.name)
        if t: decimate(o, t)
        continue
    skip = any(o.name == s or o.name.startswith(s + ' ') or o.name.startswith(s + '.') or (len(s) > 2 and o.name.startswith(s)) for s in COL_SKIP)
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector([min(v[i] for v in bb) for i in range(3)]); hi = Vector([max(v[i] for v in bb) for i in range(3)])
    size = hi - lo
    bpy.data.objects.remove(o, do_unlink=True)
    if skip or size.z < 0.4 or max(size.x, size.y) < 0.3: continue
    bpy.ops.mesh.primitive_cube_add(location=(lo + hi) / 2); box = bpy.context.object; box.scale = size / 2
    bpy.ops.object.transform_apply(scale=True)
# The gate (game x, y, z -> Blender x, -z, y)
(gx0, gy0, gz0), (gx1, gy1, gz1) = GATE
bpy.ops.mesh.primitive_cube_add(location=((gx0 + gx1) / 2, -(gz0 + gz1) / 2, (gy0 + gy1) / 2)); gate = bpy.context.object
gate.scale = ((gx1 - gx0) / 2, (gz1 - gz0) / 2, (gy1 - gy0) / 2); bpy.ops.object.transform_apply(scale=True); gate.name = 'Front_Gate'
col = os.path.join(OUT, 'Fortress_v5_col.glb')
export(col, export_materials='PLACEHOLDER', export_texcoords=False, export_normals=False)
report('collision', col)
