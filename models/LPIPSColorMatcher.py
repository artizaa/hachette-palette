import torch
import lpips
import numpy as np

class LPIPSColorMatcher:
    def __init__(self, net="alex", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.loss_fn = lpips.LPIPS(net=net).to(self.device)
        self.loss_fn.eval()

    @staticmethod
    def rgb_to_tensor_patch(rgb, size=64):
        """Преобразуем RGB цвет в тензор для LPIPS"""
        rgb = np.array(rgb).astype(np.float32) / 255.0
        rgb = rgb * 2 - 1
        patch = np.ones((size, size, 3), dtype=np.float32)
        patch[:, :, 0] *= rgb[0]
        patch[:, :, 1] *= rgb[1]
        patch[:, :, 2] *= rgb[2]
        patch_tensor = torch.tensor(patch).permute(2, 0, 1)  # [3,H,W]
        return patch_tensor

    def find_top_n_closest(self, color_rgb, color_dict, top_n=3):
        """
        Находит top-N ближайших цветов с LPIPS для одного цвета.
        """
        # целевой цвет
        color_tensor = self.rgb_to_tensor_patch(color_rgb).unsqueeze(0).to(self.device)

        # все кандидаты
        keys, values = zip(*color_dict.items())
        val_tensors = torch.stack(
            [self.rgb_to_tensor_patch(v) for v in values], dim=0
        ).to(self.device)  # [N,3,H,W]

        # LPIPS считает попарно
        color_batch = color_tensor.expand(val_tensors.size(0), -1, -1, -1)

        with torch.no_grad():
            dists = self.loss_fn(color_batch, val_tensors).squeeze().cpu().numpy()

        distances = list(zip(dists, keys, values))
        distances.sort(key=lambda x: x[0])
        return distances[:top_n]
