# Convert a photogrammetry USDZ (from tools/photogrammetry) into a web GLB:
#   Blender -b --factory-startup -P blender/usdz_to_glb.py -- in.usdz out.glb [scale]
# `scale` multiplies the model (Object Capture output is in metres already;
# pass e.g. 0.001 if the scan came out in millimetres).
import sys
import bpy

argv = sys.argv[sys.argv.index('--') + 1:]
src, dst = argv[0], argv[1]
scale = float(argv[2]) if len(argv) > 2 else 1.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.usd_import(filepath=src)
for ob in bpy.context.scene.objects:
    if ob.parent is None:
        ob.scale = (scale, scale, scale)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_yup=True, export_apply=True,
                          export_draco_mesh_compression_enable=True)
print('wrote', dst)
