import simpose as sp
from pathlib import Path
import logging
from tqdm import tqdm, trange

logging.basicConfig(level=logging.WARN)

scene = sp.Scene()


# use context manager to explicitly specify the blender scene, where the objects are created
with scene:
    duck = sp.Object.from_obj(
        str(Path(__file__).parent / Path("meshes/cpsduck/cpsduck.obj").resolve()),
        object_id=1,
    )
    cam = sp.Camera("Camera")
    sp.Object.add_material(duck)

    light = sp.Light("Light", type="POINT", energy=100.0)
    light.set_location((1.0, 1.0, -0.2))


for i in trange(10):
    sp.random.randomize_rotation(duck)
    sp.random.randomize_in_camera_frustum(duck, cam, (0.3, 1.0), (0.9, 0.9))
    # Render the scene

    scene.render(
        f"render/render_{i}.png"
    )  # Save the rendered image to the specified file path

# export Scene as .blend file, so we can open it in Blender and check results
scene.export_blend(str(Path("scene.blend").resolve()))
