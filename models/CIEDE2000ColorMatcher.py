import numpy as np
import torch
from skimage import color

class CIEDE2000ColorMatcher:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    @staticmethod
    def rgb_to_lab(rgb):
        rgb = np.array(rgb).astype(np.float32)[None, None, :] / 255.0
        lab = color.rgb2lab(rgb)
        return lab[0, 0, :]

    @staticmethod
    def delta_e_ciede2000(lab1, lab2):
        return color.deltaE_ciede2000(lab1[None, :], lab2[None, :])[0]

    def find_top_n_closest(self, color_rgb, color_dict, top_n=3):
        color_lab = self.rgb_to_lab(color_rgb)
        distances = []
        for key, rgb in color_dict.items():
            lab = self.rgb_to_lab(rgb)
            dist = self.delta_e_ciede2000(color_lab, lab)
            distances.append((dist, key, rgb))
        distances.sort(key=lambda x: x[0])
        return distances[:top_n]