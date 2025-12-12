import torch
import clip
from PIL import Image
import numpy as np

class CLIPColorMatcher:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

    @staticmethod
    def rgb_to_image(rgb, size=64):
        arr = np.ones((size, size, 3), dtype=np.uint8)
        arr[:, :, :] = rgb
        return Image.fromarray(arr)

    def find_top_n_closest(self, color_rgb, color_dict, top_n=3):
        img = self.rgb_to_image(color_rgb)
        img_tensor = self.preprocess(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            color_emb = self.model.encode_image(img_tensor)
            color_emb /= color_emb.norm(dim=-1, keepdim=True)

        distances = []
        for key, rgb in color_dict.items():
            im = self.rgb_to_image(rgb)
            im_tensor = self.preprocess(im).unsqueeze(0).to(self.device)
            with torch.no_grad():
                emb = self.model.encode_image(im_tensor)
                emb /= emb.norm(dim=-1, keepdim=True)
            dist = 1 - torch.cosine_similarity(color_emb, emb).item()
            distances.append((dist, key, rgb))
        distances.sort(key=lambda x: x[0])
        return distances[:top_n]
