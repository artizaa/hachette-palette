# markers.py
import json
from typing import Optional

import os

class Markers:
    def __init__(self):
        # маркеры: название -> {dict_file, type}
        self.markers = {
            "Guangna 120": {"dict_file": r"markers_palettes\dict_guangna_120.json", "type": "brush"},
            "Guangna 168": {"dict_file": r"markers_palettes\dict_guangna_168.json", "type": "brush"},
            "Guangna 240": {"dict_file": r"markers_palettes\dict_guangna_240.json", "type": "brush"},
            "Languo Series": {"dict_file": r"markers_palettes\dict_languo_series.json", "type": "brush"},
            "Grasp 120": {"dict_file": r"markers_palettes\dict_grasp.json", "type": "brush"},
        }

        # отдельные серии Languo
        self.languo_series_options = [
            "Colour of skin series",
            "Color of skin 2.0 series",
            "Maillard series",
            "Blue series",
            "Green series",
            "Dopamine Series",
            "Dopamine Series 2.0",
            "Sweet Pink Series",
            "Gray Brown Series",
            "Purple Series",
            "Red Yellow Series",
            "Colorful Black Series",
            "Lip Gross Red Series",
            "Warm Yellow Series",
            "Advanced Gray Series",
            "Dark Skin Series",
            "Sage Green Series",
            "Dusty Blue Series",
            "Light Color Series"
        ]

        self.series_ranges = [
            ("CS", 141, 149, "Colour of skin series"),
            ("CS", 501, 509, "Color of skin 2.0 series"),
            ("HC", 131, 139, "Dopamine Series"),
            ("HC", 601, 609, "Dopamine Series 2.0"),
            ("BL", 201, 209, "Blue series"),
            ("GR", 101, 109, "Green series"),
            ("RY", 1, 9, "Red Yellow Series"),
            ("DB", 161, 169, "Dusty Blue Series"),
            ("LC", 111, 119, "Lip Gross Red Series"),
            ("LC", 191, 199, "Light Color Series"),
            ("CB", 901, 909, "Colorful Black Series"),
            ("AG", 171, 179, "Advanced Gray Series"),
            ("SG", 151, 159, "Sage Green Series"),
            ("PC", 801, 809, "Sweet Pink Series"),
            ("DS", 181, 189, "Dark Skin Series"),
            ("YE", 121, 129, "Warm Yellow Series"),
            ("BR", 701, 709, "Gray Brown Series"),
            ("GB", 401, 409, "Gray Brown Series"),
            ("PU", 301, 309, "Purple Series"),
        ]


    def get_options(self):
        """Вернёт список доступных наборов"""
        return list(self.markers.keys())

    def get_marker_type(self, marker_name):
        """Возвращает тип маркера по имени"""
        return self.markers.get(marker_name, {}).get("type", "brush")

    def get_dict_file(self, marker_name):
        """Возвращает путь к JSON файлу словаря для выбранного набора"""
        return self.markers.get(marker_name, {}).get("dict_file")

    def load_dictionary(self, marker_name):
        """Загружает JSON-словарь для выбранного маркерного набора"""
        import os
        dict_file = self.get_dict_file(marker_name)
        if not dict_file:
            print(f"Нет dict_file для {marker_name}")
            return {}

        # Сделать путь абсолютным относительно текущего файла
        dict_file_path = os.path.join(os.path.dirname(__file__), dict_file)

        try:
            with open(dict_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Ошибка возникла, нет json-файла: {dict_file_path}")
            return {}

    def load_selected_markers(self, user_markers: dict, user_languo_series: dict) -> dict:
        """
        Возвращает один словарь всех выбранных пользователем маркеров:
        обычные + выбранные серии Languo
        """
        combined_dict = {}

        # --- обычные маркеры ---
        for marker_name, selected in user_markers.items():
            if selected:
                marker_data = self.load_dictionary(marker_name)
                combined_dict.update(marker_data)

        # --- Languo Series ---
        info = self.markers.get("Languo Series")
        if info and user_languo_series:
            dict_file = info["dict_file"]
            if os.path.exists(dict_file):
                with open(dict_file, "r", encoding="utf-8") as f:
                    all_colors = json.load(f)
                # оставляем только выбранные серии
                selected_series_names = [name for name, sel in user_languo_series.items() if sel]
                filtered_colors = {
                    code: rgb
                    for code, rgb in all_colors.items()
                    if self.get_series_name_from_code(code) in selected_series_names
                }
                combined_dict.update(filtered_colors)

        return combined_dict

    def load_languo_series(self, selected_series):
        info = self.markers.get("Languo Series")
        if not info:
            return {}

        dict_file = info["dict_file"]
        if not os.path.exists(dict_file):
            return {}

        with open(dict_file, "r", encoding="utf-8") as f:
            all_colors = json.load(f)

        active_series = {
            name for name, selected in selected_series.items() if selected
        }

        filtered = {}

        for code, rgb in all_colors.items():
            series = self.get_series_name_from_code(code)
            if series and series in active_series:
                filtered[code] = rgb

        return filtered

    def get_series_name_from_code(self, marker_code: str) -> Optional[str]:
        """
        Возвращает название серии по коду маркера, например:
        'CS-505' -> 'Color of skin 2.0 series'
        """
        try:
            prefix, num_str = marker_code.split('-')
            num = int(num_str)
        except (ValueError, AttributeError):
            return None

        for pref, start, end, series_name in self.series_ranges:
            if pref == prefix and start <= num <= end:
                return series_name
        return None