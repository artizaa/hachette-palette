from PIL import Image, ImageFont, ImageDraw

from models.CAM02UCSColorMatcher import CAM02UCSColorMatcher
from models.CIEDE2000ColorMatcher import CIEDE2000ColorMatcher
from models.CLIPColorMatcher import CLIPColorMatcher

class PaletteVisualizer:
    def __init__(self, cell_w=120, cell_h=80, font_size=24):
        #self.matcher = LPIPSColorMatcher(net="alex")
        self.matcher = CIEDE2000ColorMatcher()
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.font_size = font_size

    @staticmethod
    def get_text_color(rgb):
        """Белый текст на темных фонах, черный на светлых"""
        r, g, b = rgb
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        return "white" if brightness < 128 else "black"

    def create_lpips_image_for_page(self, rows_colors, color_dict, top_n=3):
        """
        Возвращает PIL.Image с исходными цветами и top-N ближайших по LPIPS.
        """
        n_colors = len(rows_colors)
        img_h = (top_n + 1) * self.cell_h
        img_w = n_colors * self.cell_w

        img = Image.new("RGB", (img_w, img_h), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", self.font_size)
        except:
            font = ImageFont.load_default()

        print("Моделька работает", self.matcher)
        for i, color in enumerate(rows_colors):
            top_colors = self.matcher.find_top_n_closest(
                color, color_dict, top_n=top_n
            )

            # исходный цвет
            x0, y0 = i * self.cell_w, 0
            x1, y1 = x0 + self.cell_w, self.cell_h
            draw.rectangle([x0, y0, x1, y1], fill=tuple(map(int, color)))

            # top-N
            for j, (dist, key, closest_color) in enumerate(top_colors):
                y0 = (j + 1) * self.cell_h
                y1 = y0 + self.cell_h
                draw.rectangle([x0, y0, x1, y1], fill=tuple(map(int, closest_color)))

                text = str(key)
                text_color = self.get_text_color(closest_color)

                bbox = draw.textbbox((0, 0), text, font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

                draw.text(
                    (x0 + (self.cell_w - tw) / 2, y0 + (self.cell_h - th) / 2),
                    text,
                    fill=text_color,
                    font=font,
                )

        print("Моделька закончила")
        return img
