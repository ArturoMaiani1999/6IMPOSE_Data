import bpy
import numpy as np
import simpose
import numpy as np
from pathlib import Path
from mathutils import Vector
import logging
from scipy.spatial.transform import Rotation as R
from .placeable import Placeable
from typing import List, Tuple

class Randomizer:
    def __init__(self) -> None:
        self._subjects = []

    def add(self, object):
        self._subjects.append(object)


class ObjectRandomizer(Randomizer):
    def __init__(self, r_range, yp_limit=(0.9, 0.9),) -> None:
        super().__init__()
        self._r_range = r_range
        self._yp_limit = yp_limit

    def randomize_in_camera_frustum(self,cam: simpose.Camera):
        render = bpy.context.scene.render

        aspect_ratio = render.resolution_x / render.resolution_y

        hfov = cam._bl_object.data.angle_x / 2.0
        vfov = cam._bl_object.data.angle_x / 2.0 / aspect_ratio
        # min_fov = min(hfov, vfov)

        r_range = self._r_range
        yp_limit = self._yp_limit

        for subject in self._subjects:
            r = np.random.uniform(r_range[0], r_range[1])
            yaw = yp_limit[0] * np.random.uniform(-hfov, hfov)
            pitch = yp_limit[1] * np.random.uniform(-vfov, vfov)

            x = np.cos(pitch) * np.sin(yaw) * r
            y = np.sin(pitch) * r
            z = np.cos(pitch) * np.cos(yaw) * r

            cam_origin = cam.location
            cam_rot = cam.rotation

            pos = np.array([x, y, z]) @ cam_rot.as_matrix() + np.array(cam_origin)

            subject.set_location(pos)
            logging.info(
                f"randomize_in_camera_frustum: {subject} randomzied to {pos}"
            )
    
    def randomize_orientation(self):
        for subject in self._subjects:
            subject.set_rotation(R.random())


class LightRandomizer(Randomizer):    
    def __init__(self, 
                 scene: simpose.Scene,
                 no_of_lights_range: Tuple[int, int],
                 energy_range: Tuple[int, int],
                 color_range: Tuple[float, float],
                 distance_range: Tuple[float, float]
                 ):
        super().__init__()
        self._scene = scene
        self._no_of_lights_range = no_of_lights_range
        self._energy_range = energy_range
        self._color_range = color_range
        self._distance_range = distance_range


    def randomize_lighting_around_cam(self, cam: simpose.Camera):
        for key in bpy.data.lights:
            bpy.data.lights.remove(key, do_unlink=True)
                
        n_lights  = np.random.randint(*self._no_of_lights_range)
        for i in range(n_lights):
            energy = np.random.uniform(*self._energy_range)
            light = self._scene.create_light(f"Light_{i}", type="POINT", energy=energy)

            pos = self._get_random_position_rel_to_camera(cam)
            light.set_location(pos)
            light.color = np.random.uniform(*self._color_range, size=(3,))


    def _get_random_position_rel_to_camera(self, cam: simpose.Camera):
        dist = np.random.uniform(*self._distance_range)
        dir = R.random().as_matrix() @ np.array([0,0,1])
        offset = dist * dir
        cam_pos = cam.location
        pos = offset + cam_pos
        return pos


class SceneRandomizer(Randomizer):
    def __init__(self, scene: simpose.Scene, backgrounds_dir: Path= Path("backgrounds")) -> None:
        super().__init__()
        self._scene: simpose.Scene = scene
        self._backgrounds_dir: Path = backgrounds_dir
        self._backgrounds: List = list(self._backgrounds_dir.glob("*.jpg"))

    def randomize_background(self):
        bg = "//" + str(np.random.choice(self._backgrounds))
        self._scene.set_background(bg)
    
