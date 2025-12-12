import numpy as np
from colorspacious import cspace_convert
from numpy.linalg import norm

class CAM02UCSColorMatcher:
    def __init__(self):
        pass

    @staticmethod
    def rgb_to_cam02ucs(rgb):
        rgb = np.array(rgb, dtype=np.float32) / 255.0
        cam = cspace_convert(rgb[None, :], start="sRGB1", end="CAM02-UCS")
        return cam[0]

    def find_top_n_closest(self, color_rgb, color_dict, top_n=3):
        color_cam = self.rgb_to_cam02ucs(color_rgb)
        distances = []
        for key, rgb in color_dict.items():
            cam = self.rgb_to_cam02ucs(rgb)
            dist = norm(color_cam - cam)
            distances.append((dist, key, rgb))
        distances.sort(key=lambda x: x[0])
        return distances[:top_n]
