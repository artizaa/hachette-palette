# markers.py
import json
from typing import Optional


class Markers:
    def __init__(self):
        # маркеры: название -> {dict_file, type}
        self.markers = {
            "Guangna 120": {"dict_file": "markers_palettes\dict_guangna_120.json", "type": "brush"},
            "Guangna 168": {"dict_file": "markers_palettes\dict_guangna_168.json", "type": "brush"},
            "Guangna 240": {"dict_file": "markers_palettes\dict_guangna_240.json", "type": "brush"},
            "Languo Series": {"dict_file": "markers_palettes\dict_languo_series.json", "type": "brush"},
            #"Languo 240": {"dict_file": "markers_palettes\languo_240.json", "type": "brush"},
            "Grasp 120": {"dict_file": "markers_palettes\dict_grasp.json", "type": "brush"},
        }


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

    def load_selected_markers(self, user_marker_state):
        """
        Объединяет словари всех выбранных пользователем маркеров
        user_marker_state: {marker_name: True/False}
        Возвращает один большой словарь
        """
        combined_dict = {}
        for marker_name, selected in user_marker_state.items():
            if selected:
                marker_data = self.load_dictionary(marker_name)
                combined_dict.update(marker_data)
        return combined_dict

    # def load_selected_markers(self, user_markers, marker_name="Languo Series"):
    #     """
    #     Загружает только выбранные пользователем цвета для набора marker_name.
    #     Для Languo Series фильтрует по выбранным сериям.
    #     """
    #     info = self.markers.get(marker_name)
    #     if not info:
    #         return {}
    #
    #     dict_file = info["dict_file"]
    #     if not os.path.exists(dict_file):
    #         return {}
    #
    #     # --- подгружаем JSON с цветами ---
    #     with open(dict_file, "r", encoding="utf-8") as f:
    #         all_colors = json.load(f)
    #
    #     # --- выбираем только серии, которые активны у пользователя ---
    #     selected_series_names = [
    #         name for name, selected in user_markers.items() if selected
    #     ]
    #
    #     filtered_colors = {
    #         code: rgb for code, rgb in all_colors.items()
    #         if self.get_series_name_from_code(code) in selected_series_names
    #     }
    #
    #     return filtered_colors

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