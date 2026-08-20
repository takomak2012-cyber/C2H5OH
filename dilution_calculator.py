# -*- coding: utf-8 -*-
"""Калькулятор разбавления с водой, версия 3.4. Автор: Вячеслав Долар."""

from __future__ import annotations

import os
import sys
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

try:
    from PIL import Image
    import pystray
    PYSTRAY_AVAILABLE = True
except Exception:  # pragma: no cover - optional runtime dependency
    PYSTRAY_AVAILABLE = False
    Image = None
    pystray = None


def resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


APP_NAME = "AlcoKa"
APP_VERSION = "3.4"
APP_AUTHOR = "Вячеслав Долар"
GITHUB_URL = "https://github.com/takomak2012-cyber/C2H5OH"
MAX_HISTORY = 30


def app_data_path() -> str:
    root = os.getenv("APPDATA") or os.path.expanduser("~")
    path = os.path.join(root, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def state_file_path() -> str:
    return os.path.join(app_data_path(), "state.json")

BG = "#F3F3F3"
TEXT = "#1A1A1A"
MUTED = "#5C5C5C"
OK_BG = "#E8F5E9"

TEXTS = {
    'ru': {
        'app_name': 'Калькулятор разбавления',
        'window_title': 'Калькулятор разбавления {version}',
        'subtitle': 'Смешивание спирта с водой.',
        'alcohol': 'Спирт:',
        'volume': 'Объём:',
        'unit_hint': 'Единицы спирта в полях должны совпадать.',
        'tab_water': 'Вода',
        'tab_total': 'Объём',
        'tab_result': 'Итог спирта',
        'water_tab_desc': 'Сколько воды добавить к известному объёму спирта.',
        'total_tab_desc': 'Сколько спирта и воды взять на заданный готовый объём.',
        'result_tab_desc': 'Какой спирт получится после смешивания с водой.',
        'field_initial': 'Крепость начального спирта',
        'field_volume': 'Объём спирта',
        'field_target': 'Желаемая крепость',
        'field_total_initial': 'Крепость начального спирта',
        'field_total_target': 'Желаемая крепость',
        'field_total_volume': 'Готовый объём',
        'field_final_alcohol': 'Крепость спирта',
        'field_final_volume': 'Объём спирта',
        'field_final_water': 'Объём воды',
        'btn_calc': 'Рассчитать',
        'btn_clear': 'Очистить',
        'btn_about': 'О программе',
        'btn_copy': 'Копировать',
        'btn_export': 'Экспорт',
        'menu_tools': 'Инструменты',
        'menu_history': 'История расчётов',
        'menu_copy': 'Копировать результат',
        'menu_export': 'Экспорт результата',
        'history_title': 'История расчётов',
        'history_empty': 'История пока пуста.',
        'history_clear': 'Очистить историю',
        'copy_empty': 'Сначала выполните расчёт.',
        'copy_done': 'Результат скопирован в буфер обмена.',
        'export_title': 'Сохранить результат',
        'export_done': 'Результат сохранён.',
        'export_error': 'Не удалось сохранить файл.',
        'no_result': 'Нет результата для этой вкладки.',
        'strength_range': 'Крепость в процентах должна быть от 0 до 100.',
        'history_item': '{date} — {text}',
        'footer': 'Версия {version}  ·  {author}',
        'errors': {
            'fill_field': 'Заполните поле «{field}».',
            'invalid_number': 'В поле «{field}» введите число.',
            'negative': '«{field}» не может быть отрицательным.',
            'initial_zero': 'Начальный спирт должен быть больше нуля.',
            'target_zero': 'Желаемая крепость должна быть больше нуля.',
            'target_greater': 'Желаемая крепость больше начальной: водой её можно только снизить.',
            'target_equal': 'Начальная крепость уже равна желаемой — воду добавлять не нужно.',
            'total_zero': 'Суммарный объём равен нулю.',
        },
        'about_title': 'О программе',
        'about_text': '{name}\nВерсия: {version}\nАвтор: {author}\n\nИсточник: {url}\n\nНачальный спирт × объём спирта =\nнужный спирт × итоговый объём.\n\nРезультаты округляются до сотых.\nОбъёмы складываются (вода + спирт).',
        'error_title': 'Ошибка ввода',
        'menu_lang': 'Язык',
        'lang_ru': 'Русский',
        'lang_en': 'English',
        'lang_de': 'Deutsch',
        'results': {
            'water_add': 'Добавить воды: {value} {unit}',
            'final_volume': 'Итоговый объём: {value} {unit}',
            'factor': 'Кратность: {value}×',
            'ratio': 'Соотношение: 1 : {value}',
            'check': 'Проверка: {left} {left_unit} × {right} {right_unit}',
            'check_equal': '= {target} {target_unit} × {final} {final_unit}',
            'alcohol_volume': 'Объём спирта: {value} {unit}',
            'ready_solution': 'Готовый раствор: {value} {unit}',
            'share_percent': 'Доля спирта: {value} %',
            'final_strength': 'Итоговый спирт: {value} {unit}',
            'dilution': 'Разбавление: {value}×',
            'water_amount': 'Вода: {value} {unit}',
        },
    },
    'en': {
        'app_name': 'Dilution Calculator',
        'window_title': 'Dilution Calculator {version}',
        'subtitle': 'Mixing alcohol with water.',
        'alcohol': 'Alcohol:',
        'volume': 'Volume:',
        'unit_hint': 'Alcohol units in fields must match.',
        'tab_water': 'Water',
        'tab_total': 'Volume',
        'tab_result': 'Final alcohol',
        'water_tab_desc': 'How much water to add to a known volume of alcohol.',
        'total_tab_desc': 'How much alcohol and water for a given final volume.',
        'result_tab_desc': 'Final alcohol strength after mixing with water.',
        'field_initial': 'Initial alcohol strength',
        'field_volume': 'Alcohol volume',
        'field_target': 'Desired strength',
        'field_total_initial': 'Initial alcohol strength',
        'field_total_target': 'Desired strength',
        'field_total_volume': 'Final volume',
        'field_final_alcohol': 'Final alcohol strength',
        'field_final_volume': 'Alcohol volume',
        'field_final_water': 'Water volume',
        'btn_calc': 'Calculate',
        'btn_clear': 'Clear',
        'btn_about': 'About',
        'btn_copy': 'Copy',
        'btn_export': 'Export',
        'menu_tools': 'Tools',
        'menu_history': 'Calculation history',
        'menu_copy': 'Copy result',
        'menu_export': 'Export result',
        'history_title': 'Calculation history',
        'history_empty': 'History is empty.',
        'history_clear': 'Clear history',
        'copy_empty': 'Run a calculation first.',
        'copy_done': 'Result copied to clipboard.',
        'export_title': 'Save result',
        'export_done': 'Result saved.',
        'export_error': 'Could not save the file.',
        'no_result': 'There is no result for this tab.',
        'strength_range': 'Percentage strength must be between 0 and 100.',
        'history_item': '{date} — {text}',
        'footer': 'Version {version}  ·  {author}',
        'errors': {
            'fill_field': 'Fill in the "{field}" field.',
            'invalid_number': 'Enter a number in the "{field}" field.',
            'negative': '"{field}" cannot be negative.',
            'initial_zero': 'Initial strength must be greater than zero.',
            'target_zero': 'Desired strength must be greater than zero.',
            'target_greater': 'Desired strength is greater than initial: water can only lower it.',
            'target_equal': 'Initial strength already equals desired — no water needed.',
            'total_zero': 'Total volume is zero.',
        },
        'about_title': 'About',
        'about_text': '{name}\nVersion: {version}\nAuthor: {author}\n\nSource: {url}\n\nInitial strength × alcohol volume =\ntarget strength × final volume.\n\nResults are rounded to hundredths.\nVolumes are additive (water + alcohol).',
        'error_title': 'Input error',
        'menu_lang': 'Language',
        'lang_ru': 'Russian',
        'lang_en': 'English',
        'lang_de': 'German',
        'results': {
            'water_add': 'Add water: {value} {unit}',
            'final_volume': 'Final volume: {value} {unit}',
            'factor': 'Factor: {value}×',
            'ratio': 'Ratio: 1 : {value}',
            'check': 'Check: {left} {left_unit} × {right} {right_unit}',
            'check_equal': '= {target} {target_unit} × {final} {final_unit}',
            'alcohol_volume': 'Alcohol volume: {value} {unit}',
            'ready_solution': 'Prepared solution: {value} {unit}',
            'share_percent': 'Alcohol share: {value} %',
            'final_strength': 'Final alcohol: {value} {unit}',
            'dilution': 'Dilution: {value}×',
            'water_amount': 'Water: {value} {unit}',
        },
    },
    'de': {
        'app_name': 'Verdünnungsrechner',
        'window_title': 'Verdünnungsrechner {version}',
        'subtitle': 'Alkohol mit Wasser mischen.',
        'alcohol': 'Alkohol:',
        'volume': 'Volumen:',
        'unit_hint': 'Die Alkoholeinheiten in den Feldern müssen übereinstimmen.',
        'tab_water': 'Wasser',
        'tab_total': 'Volumen',
        'tab_result': 'Endalkohol',
        'water_tab_desc': 'Wie viel Wasser zu einem bekannten Alkoholvolumen hinzufügen.',
        'total_tab_desc': 'Wie viel Alkohol und Wasser für ein gegebenes Endvolumen.',
        'result_tab_desc': 'Endalkoholgehalt nach dem Mischen mit Wasser.',
        'field_initial': 'Alkohol-Anfangsstärke',
        'field_volume': 'Alkoholvolumen',
        'field_target': 'Gewünschte Stärke',
        'field_total_initial': 'Alkohol-Anfangsstärke',
        'field_total_target': 'Gewünschte Stärke',
        'field_total_volume': 'Endvolumen',
        'field_final_alcohol': 'End-Alkoholstärke',
        'field_final_volume': 'Alkoholvolumen',
        'field_final_water': 'Wasservolumen',
        'btn_calc': 'Berechnen',
        'btn_clear': 'Löschen',
        'btn_about': 'Über',
        'btn_copy': 'Kopieren',
        'btn_export': 'Export',
        'menu_tools': 'Werkzeuge',
        'menu_history': 'Berechnungsverlauf',
        'menu_copy': 'Ergebnis kopieren',
        'menu_export': 'Ergebnis exportieren',
        'history_title': 'Berechnungsverlauf',
        'history_empty': 'Der Verlauf ist leer.',
        'history_clear': 'Verlauf löschen',
        'copy_empty': 'Führen Sie zuerst eine Berechnung aus.',
        'copy_done': 'Ergebnis in die Zwischenablage kopiert.',
        'export_title': 'Ergebnis speichern',
        'export_done': 'Ergebnis gespeichert.',
        'export_error': 'Datei konnte nicht gespeichert werden.',
        'no_result': 'Für diesen Tab gibt es kein Ergebnis.',
        'strength_range': 'Die Prozentstärke muss zwischen 0 und 100 liegen.',
        'history_item': '{date} — {text}',
        'footer': 'Version {version}  ·  {author}',
        'errors': {
            'fill_field': 'Füllen Sie das Feld "{field}".',
            'invalid_number': 'Geben Sie eine Zahl im Feld "{field}" ein.',
            'negative': '"{field}" darf nicht negativ sein.',
            'initial_zero': 'Die Anfangsstärke muss größer als null sein.',
            'target_zero': 'Die Zielstärke muss größer als null sein.',
            'target_greater': 'Die Zielstärke ist höher als die Anfangsstärke: Wasser kann sie nur senken.',
            'target_equal': 'Die Anfangsstärke entspricht bereits der Zielstärke — kein Wasser nötig.',
            'total_zero': 'Das Gesamtvolumen ist null.',
        },
        'about_title': 'Über das Programm',
        'about_text': '{name}\nVersion: {version}\nAutor: {author}\n\nQuelle: {url}\n\nAnfangsstärke × Alkoholvolumen =\nZielstärke × Endvolumen.\n\nErgebnisse werden auf Hundertstel gerundet.\nVolumina sind additiv (Wasser + Alkohol).',
        'error_title': 'Eingabefehler',
        'menu_lang': 'Sprache',
        'lang_ru': 'Russisch',
        'lang_en': 'Englisch',
        'lang_de': 'Deutsch',
        'results': {
            'water_add': 'Wasser hinzufügen: {value} {unit}',
            'final_volume': 'Endvolumen: {value} {unit}',
            'factor': 'Faktor: {value}×',
            'ratio': 'Verhältnis: 1 : {value}',
            'check': 'Prüfung: {left} {left_unit} × {right} {right_unit}',
            'check_equal': '= {target} {target_unit} × {final} {final_unit}',
            'alcohol_volume': 'Alkoholvolumen: {value} {unit}',
            'ready_solution': 'Gerechte Lösung: {value} {unit}',
            'share_percent': 'Alkoholanteil: {value} %',
            'final_strength': 'Endalkohol: {value} {unit}',
            'dilution': 'Verdünnung: {value}×',
            'water_amount': 'Wasser: {value} {unit}',
        },
    }
}


def parse_number(raw: str, field: str, lang: str = 'ru') -> float:
    text = (raw or "").strip().replace(",", ".").replace(" ", "")
    if not text:
        raise ValueError(TEXTS[lang]['errors']['fill_field'].format(field=field))
    try:
        value = Decimal(text)
        if not value.is_finite():
            raise InvalidOperation
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(TEXTS[lang]['errors']['invalid_number'].format(field=field)) from exc
    if value < 0:
        raise ValueError(TEXTS[lang]['errors']['negative'].format(field=field))
    return float(value)


def fmt(value: float) -> str:
    return f"{Decimal(str(value)).quantize(Decimal('0.01')):.2f}"


def precise(value: float) -> Decimal:
    return Decimal(str(value))


def rounded(value: Decimal) -> float:
    return float(value.quantize(Decimal('0.01')))


def result_line(lang: str, key: str, **kwargs) -> str:
    template = TEXTS[lang].get('results', {}).get(key, '{value}')
    return template.format(**kwargs)


def calculate_water_needed(initial_strength: float, alcohol_volume: float, target_strength: float) -> dict:
    if initial_strength <= 0:
        raise ValueError("Initial strength must be greater than zero.")
    if target_strength <= 0:
        raise ValueError("Target strength must be greater than zero.")
    if target_strength >= initial_strength:
        raise ValueError("Target strength cannot be greater than or equal to the initial strength.")

    initial = precise(initial_strength)
    volume = precise(alcohol_volume)
    target = precise(target_strength)
    final_volume = volume * initial / target
    water_to_add = final_volume - volume
    factor = initial / target
    ratio = factor - 1
    return {
        "final_volume": rounded(final_volume),
        "water_to_add": rounded(water_to_add),
        "factor": rounded(factor),
        "ratio": rounded(ratio),
    }


def calculate_total_mix(initial_strength: float, target_strength: float, final_volume: float) -> dict:
    if initial_strength <= 0:
        raise ValueError("Initial strength must be greater than zero.")
    if target_strength < 0:
        raise ValueError("Target strength cannot be negative.")
    if final_volume < 0:
        raise ValueError("Final volume cannot be negative.")
    if target_strength > initial_strength:
        raise ValueError("Target strength cannot be greater than initial strength.")

    if target_strength == 0:
        alcohol_volume = Decimal("0")
        water_to_add = precise(final_volume)
    else:
        alcohol_volume = precise(final_volume) * precise(target_strength) / precise(initial_strength)
        water_to_add = precise(final_volume) - alcohol_volume

    share_percent = (alcohol_volume / precise(final_volume) * 100) if final_volume else Decimal("0")
    return {
        "alcohol_volume": rounded(alcohol_volume),
        "water_to_add": rounded(water_to_add),
        "final_volume": rounded(precise(final_volume)),
        "share_percent": rounded(share_percent),
    }


def calculate_final_strength(initial_strength: float, alcohol_volume: float, water_volume: float) -> dict:
    if initial_strength <= 0:
        raise ValueError("Initial strength must be greater than zero.")
    if alcohol_volume < 0:
        raise ValueError("Alcohol volume cannot be negative.")
    if water_volume < 0:
        raise ValueError("Water volume cannot be negative.")

    alcohol = precise(alcohol_volume)
    water = precise(water_volume)
    total_volume = alcohol + water
    if total_volume == 0:
        raise ValueError("Total volume is zero.")

    final_strength = precise(initial_strength) * alcohol / total_volume
    dilution = (total_volume / alcohol) if alcohol else Decimal("0")
    return {
        "final_strength": rounded(final_strength),
        "total_volume": rounded(total_volume),
        "dilution": rounded(dilution),
    }


class DilutionApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self._state = self._load_state()
        self.current_lang = self._state.get('lang', 'ru') if self._state.get('lang') in TEXTS else 'ru'
        self._tray = None
        self._last_result = ''
        self.title(self._tr('window_title').format(version=APP_VERSION))
        self.configure(bg=BG)
        self.minsize(480, 620)
        self.geometry(self._state.get('geometry', "500x660"))
        self.resizable(True, True)
        self._set_window_icon()
        self._wrap_labels: list[ttk.Label] = []
        self._setup_style()
        self._build_menu()
        self._build_tray_icon()
        self._build()
        self._restore_state()
        self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)
        self.bind("<Configure>", self._on_resize)
        self.bind("<Return>", self._run_active_tab)

    def _tr(self, key: str) -> str:
        return TEXTS[self.current_lang].get(key, key)

    def _load_state(self) -> dict:
        try:
            with open(state_file_path(), 'r', encoding='utf-8') as file:
                state = json.load(file)
                return state if isinstance(state, dict) else {}
        except (OSError, ValueError, TypeError):
            return {}

    def _restore_state(self) -> None:
        self.unit_var.set(self._state.get('alcohol_unit', '%'))
        self.vol_unit_var.set(self._state.get('volume_unit', 'мл'))
        fields = self._state.get('fields', {})
        for name, entry in (
            ('w_c1', self.w_c1), ('w_v1', self.w_v1), ('w_c2', self.w_c2),
            ('t_c1', self.t_c1), ('t_c2', self.t_c2), ('t_v2', self.t_v2),
            ('f_c1', self.f_c1), ('f_v1', self.f_v1), ('f_water', self.f_water),
        ):
            if name in fields:
                entry.delete(0, 'end')
                entry.insert(0, str(fields[name]))
        self.w_c1.focus_set()

    def _save_state(self) -> None:
        fields = {
            name: entry.get() for name, entry in (
                ('w_c1', self.w_c1), ('w_v1', self.w_v1), ('w_c2', self.w_c2),
                ('t_c1', self.t_c1), ('t_c2', self.t_c2), ('t_v2', self.t_v2),
                ('f_c1', self.f_c1), ('f_v1', self.f_v1), ('f_water', self.f_water),
            )
        }
        state = {
            'lang': self.current_lang,
            'alcohol_unit': self.unit_var.get(),
            'volume_unit': self.vol_unit_var.get(),
            'geometry': self.geometry(),
            'fields': fields,
            'history': self._state.get('history', [])[-MAX_HISTORY:],
        }
        try:
            with open(state_file_path(), 'w', encoding='utf-8') as file:
                json.dump(state, file, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def _run_active_tab(self, _event=None) -> None:
        index = self.notebook.index(self.notebook.select())
        if index == 0:
            self.calc_water()
        elif index == 1:
            self.calc_total()
        elif index == 2:
            self.calc_final()

    def _set_window_icon(self) -> None:
        ico = resource_path("dollar.ico")
        try:
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except tk.TclError:
            pass

    def _build_tray_icon(self) -> None:
        if not PYSTRAY_AVAILABLE:
            return
        try:
            tray_image = Image.open(resource_path("whiskey.ico"))
            self._tray = pystray.Icon(
                "AlcoKa",
                tray_image,
                APP_NAME,
                menu=pystray.Menu(
                    pystray.MenuItem("Показать / скрыть", self._toggle_window),
                    pystray.MenuItem("О программе", self._about),
                    pystray.MenuItem("Выход", self._quit_app),
                ),
            )
            self._tray.run_detached()
        except Exception:
            self._tray = None

    def _toggle_window(self) -> None:
        if self.state() == "withdrawn":
            self.deiconify()
            self.focus_force()
        else:
            self.withdraw()

    def _hide_to_tray(self) -> None:
        self._save_state()
        self.withdraw()

    def _quit_app(self) -> None:
        self._save_state()
        if self._tray is not None:
            self._tray.stop()
        self.destroy()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            style.theme_use("clam")

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 9))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 8))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 14))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 8))
        style.configure("TButton", font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 9))
        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", font=("Segoe UI", 8), padding=(8, 4))
        style.configure("TCombobox", font=("Segoe UI", 9))

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self._tr('menu_lang'), menu=lang_menu)
        lang_menu.add_command(label=self._tr('lang_ru'), command=lambda: self.change_lang('ru'))
        lang_menu.add_command(label=self._tr('lang_en'), command=lambda: self.change_lang('en'))
        lang_menu.add_command(label=self._tr('lang_de'), command=lambda: self.change_lang('de'))

        menubar.add_command(label=self._tr('btn_about'), command=self._about)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self._tr('menu_tools'), menu=tools_menu)
        tools_menu.add_command(label=self._tr('menu_history'), command=self._show_history)
        tools_menu.add_command(label=self._tr('menu_copy'), command=self._copy_result)
        tools_menu.add_command(label=self._tr('menu_export'), command=self._export_result)

    def change_lang(self, lang_code: str) -> None:
        self.current_lang = lang_code
        self.title(self._tr('window_title').format(version=APP_VERSION))
        self._update_ui()

    def _update_ui(self) -> None:
        self._rebuild_menu()
        self.notebook.tab(0, text=self._tr('tab_water'))
        self.notebook.tab(1, text=self._tr('tab_total'))
        self.notebook.tab(2, text=self._tr('tab_result'))
        self._update_labels()
        self._update_tab_texts()
        self.footer_label.config(text=self._tr('footer').format(version=APP_VERSION, author=APP_AUTHOR))

    def _rebuild_menu(self) -> None:
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self._tr('menu_lang'), menu=lang_menu)
        lang_menu.add_command(label=self._tr('lang_ru'), command=lambda: self.change_lang('ru'))
        lang_menu.add_command(label=self._tr('lang_en'), command=lambda: self.change_lang('en'))
        lang_menu.add_command(label=self._tr('lang_de'), command=lambda: self.change_lang('de'))

        menubar.add_command(label=self._tr('btn_about'), command=self._about)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self._tr('menu_tools'), menu=tools_menu)
        tools_menu.add_command(label=self._tr('menu_history'), command=self._show_history)
        tools_menu.add_command(label=self._tr('menu_copy'), command=self._copy_result)
        tools_menu.add_command(label=self._tr('menu_export'), command=self._export_result)

    def _update_labels(self) -> None:
        self.alcohol_label.config(text=self._tr('alcohol'))
        self.volume_label.config(text=self._tr('volume'))
        self.unit_hint_label.config(text=self._tr('unit_hint'))
        self._update_field_labels()
        for btn in self.calc_buttons:
            btn.config(text=self._tr('btn_calc'))
        for btn in self.clear_buttons:
            btn.config(text=self._tr('btn_clear'))

    def _update_field_labels(self) -> None:
        self.water_labels[0].config(text=self._tr('field_initial'))
        self.water_labels[1].config(text=self._tr('field_volume'))
        self.water_labels[2].config(text=self._tr('field_target'))

        self.total_labels[0].config(text=self._tr('field_total_initial'))
        self.total_labels[1].config(text=self._tr('field_total_target'))
        self.total_labels[2].config(text=self._tr('field_total_volume'))

        self.final_labels[0].config(text=self._tr('field_final_alcohol'))
        self.final_labels[1].config(text=self._tr('field_final_volume'))
        self.final_labels[2].config(text=self._tr('field_final_water'))

    def _update_tab_texts(self) -> None:
        self.water_desc.config(text=self._tr('water_tab_desc'))
        self.total_desc.config(text=self._tr('total_tab_desc'))
        self.final_desc.config(text=self._tr('result_tab_desc'))

    def _add_wrap(self, parent: ttk.Frame, text: str, style: str = "TLabel") -> ttk.Label:
        lbl = ttk.Label(parent, text=text, style=style, justify="left", wraplength=420)
        lbl.pack(anchor="w", fill="x")
        self._wrap_labels.append(lbl)
        return lbl

    def _on_resize(self, event: tk.Event) -> None:
        if event.widget is not self:
            return
        wrap = max(event.width - 48, 200)
        for lbl in self._wrap_labels:
            lbl.configure(wraplength=wrap)

    def _build(self) -> None:
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True, padx=12, pady=8)

        self.title_label = self._add_wrap(outer, APP_NAME, "Title.TLabel")
        self.subtitle_label = self._add_wrap(outer, self._tr('subtitle'), "Sub.TLabel")

        units = ttk.Frame(outer)
        units.pack(fill="x", pady=(8, 4))
        units.columnconfigure(1, weight=1)

        self.alcohol_label = ttk.Label(units, text=self._tr('alcohol'))
        self.alcohol_label.grid(row=0, column=0, sticky="w", pady=2)
        self.unit_var = tk.StringVar(value="%")
        ttk.Combobox(
            units,
            textvariable=self.unit_var,
            values=("%", "г/л", "мг/л", "ppm", "усл. ед."),
            state="readonly",
            width=10,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)

        self.volume_label = ttk.Label(units, text=self._tr('volume'))
        self.volume_label.grid(row=1, column=0, sticky="w", pady=2)
        self.vol_unit_var = tk.StringVar(value="мл")
        ttk.Combobox(
            units,
            textvariable=self.vol_unit_var,
            values=("мл", "л", "мкл", "капли"),
            state="readonly",
            width=10,
        ).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)

        self.unit_hint_label = self._add_wrap(outer, self._tr('unit_hint'), "Muted.TLabel")

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill="both", expand=True, pady=8)

        self.tab_water = ttk.Frame(self.notebook, padding=8)
        self.tab_total = ttk.Frame(self.notebook, padding=8)
        self.tab_result = ttk.Frame(self.notebook, padding=8)

        self.notebook.add(self.tab_water, text=self._tr('tab_water'))
        self.notebook.add(self.tab_total, text=self._tr('tab_total'))
        self.notebook.add(self.tab_result, text=self._tr('tab_result'))

        self._build_water_tab()
        self._build_total_tab()
        self._build_result_tab()

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(4, 0))
        footer.columnconfigure(0, weight=1)
        self.footer_label = ttk.Label(
            footer,
            text=self._tr('footer').format(version=APP_VERSION, author=APP_AUTHOR),
            style="Muted.TLabel",
            wraplength=280,
            justify="left",
        )
        self.footer_label.grid(row=0, column=0, sticky="ew")
        self._wrap_labels.append(self.footer_label)

    def _field(self, parent: ttk.Frame, label: str, default: str = "") -> tuple[ttk.Label, ttk.Entry]:
        lbl = self._add_wrap(parent, label)
        entry = ttk.Entry(parent, font=("Segoe UI", 11))
        entry.insert(0, default)
        entry.pack(fill="x", ipady=2, pady=(2, 6))
        return lbl, entry

    def _actions(self, parent: ttk.Frame, calc, clear) -> tuple[ttk.Button, ttk.Button]:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(4, 6))
        calc_btn = ttk.Button(row, text=self._tr('btn_calc'), style="Accent.TButton", command=calc)
        calc_btn.pack(side="left")
        clear_btn = ttk.Button(row, text=self._tr('btn_clear'), command=clear)
        clear_btn.pack(side="left", padx=6)

        if not hasattr(self, 'calc_buttons'):
            self.calc_buttons = []
            self.clear_buttons = []
        self.calc_buttons.append(calc_btn)
        self.clear_buttons.append(clear_btn)
        return calc_btn, clear_btn

    def _result_box(self, parent: ttk.Frame) -> tk.Text:
        box = tk.Text(
            parent,
            height=7,
            wrap="word",
            font=("Segoe UI", 10),
            bg=OK_BG,
            fg="#1B5E20",
            relief="flat",
            padx=8,
            pady=8,
            state="disabled",
        )
        box.pack(fill="both", expand=True)
        return box

    def _show(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")
        if text.strip():
            self._last_result = text
            history = self._state.setdefault('history', [])
            history.append({
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'text': text,
            })
            self._state['history'] = history[-MAX_HISTORY:]

    def _copy_result(self) -> None:
        if not self._last_result:
            messagebox.showwarning(self._tr('error_title'), self._tr('copy_empty'), parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(self._last_result)
        self.update()
        messagebox.showinfo(self._tr('btn_copy'), self._tr('copy_done'), parent=self)

    def _export_result(self) -> None:
        if not self._last_result:
            messagebox.showwarning(self._tr('error_title'), self._tr('copy_empty'), parent=self)
            return
        path = filedialog.asksaveasfilename(
            parent=self,
            title=self._tr('export_title'),
            defaultextension='.txt',
            filetypes=[('Text files', '*.txt'), ('All files', '*.*')],
        )
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(self._last_result + '\n')
            messagebox.showinfo(self._tr('btn_export'), self._tr('export_done'), parent=self)
        except OSError:
            messagebox.showerror(self._tr('error_title'), self._tr('export_error'), parent=self)

    def _show_history(self) -> None:
        window = tk.Toplevel(self)
        window.title(self._tr('history_title'))
        window.geometry('560x360')
        window.transient(self)
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        items = tk.Listbox(window, width=80, height=18)
        items.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        scrollbar = ttk.Scrollbar(window, orient='vertical', command=items.yview)
        scrollbar.grid(row=0, column=1, pady=10, sticky='ns')
        items.configure(yscrollcommand=scrollbar.set)
        history = self._state.get('history', [])
        if history:
            for item in reversed(history):
                items.insert('end', f"{item.get('date', '')} — {item.get('text', '')}")
        else:
            items.insert('end', self._tr('history_empty'))

        def clear_history() -> None:
            self._state['history'] = []
            self._save_state()
            window.destroy()

        ttk.Button(window, text=self._tr('history_clear'), command=clear_history).grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky='w'
        )

    def _units(self) -> tuple[str, str]:
        return self.unit_var.get(), self.vol_unit_var.get()

    def _validate_strength(self, value: float) -> None:
        if self.unit_var.get() == '%' and value > 100:
            raise ValueError(self._tr('strength_range'))

    def _build_water_tab(self) -> None:
        p = self.tab_water
        self.water_desc = self._add_wrap(p, self._tr('water_tab_desc'))
        self.water_labels = []
        self.w_c1_lbl, self.w_c1 = self._field(p, self._tr('field_initial'), "10")
        self.water_labels.append(self.w_c1_lbl)
        self.w_v1_lbl, self.w_v1 = self._field(p, self._tr('field_volume'), "100")
        self.water_labels.append(self.w_v1_lbl)
        self.w_c2_lbl, self.w_c2 = self._field(p, self._tr('field_target'), "2")
        self.water_labels.append(self.w_c2_lbl)
        self._actions(p, self.calc_water, self.clear_water)
        self.w_out = self._result_box(p)

    def _build_total_tab(self) -> None:
        p = self.tab_total
        self.total_desc = self._add_wrap(p, self._tr('total_tab_desc'))
        self.total_labels = []
        self.t_c1_lbl, self.t_c1 = self._field(p, self._tr('field_total_initial'), "36")
        self.total_labels.append(self.t_c1_lbl)
        self.t_c2_lbl, self.t_c2 = self._field(p, self._tr('field_total_target'), "3")
        self.total_labels.append(self.t_c2_lbl)
        self.t_v2_lbl, self.t_v2 = self._field(p, self._tr('field_total_volume'), "1000")
        self.total_labels.append(self.t_v2_lbl)
        self._actions(p, self.calc_total, self.clear_total)
        self.t_out = self._result_box(p)

    def _build_result_tab(self) -> None:
        p = self.tab_result
        self.final_desc = self._add_wrap(p, self._tr('result_tab_desc'))
        self.final_labels = []
        self.f_c1_lbl, self.f_c1 = self._field(p, self._tr('field_final_alcohol'), "5")
        self.final_labels.append(self.f_c1_lbl)
        self.f_v1_lbl, self.f_v1 = self._field(p, self._tr('field_final_volume'), "20")
        self.final_labels.append(self.f_v1_lbl)
        self.f_water_lbl, self.f_water = self._field(p, self._tr('field_final_water'), "80")
        self.final_labels.append(self.f_water_lbl)
        self._actions(p, self.calc_final, self.clear_final)
        self.f_out = self._result_box(p)

    def _get_error_text(self, key: str, **kwargs) -> str:
        template = TEXTS[self.current_lang]['errors'].get(key, key)
        return template.format(**kwargs)

    def calc_water(self) -> None:
        cu, vu = self._units()
        lang = self.current_lang
        try:
            c1 = parse_number(self.w_c1.get(), self._tr('field_initial'), lang)
            v1 = parse_number(self.w_v1.get(), self._tr('field_volume'), lang)
            c2 = parse_number(self.w_c2.get(), self._tr('field_target'), lang)
            self._validate_strength(c1)
            self._validate_strength(c2)
            if c1 == 0:
                raise ValueError(self._get_error_text('initial_zero'))
            if c2 == 0:
                raise ValueError(self._get_error_text('target_zero'))
            if c2 > c1:
                raise ValueError(self._get_error_text('target_greater'))
            if c2 == c1:
                raise ValueError(self._get_error_text('target_equal'))
            result = calculate_water_needed(c1, v1, c2)
            self._show(
                self.w_out,
                "\n".join(
                    [
                        result_line(lang, 'water_add', value=fmt(result['water_to_add']), unit=vu),
                        result_line(lang, 'final_volume', value=fmt(result['final_volume']), unit=vu),
                        result_line(lang, 'factor', value=fmt(result['factor'])),
                        result_line(lang, 'ratio', value=fmt(result['ratio'])),
                        result_line(lang, 'check', left=fmt(c1), left_unit=cu, right=fmt(v1), right_unit=vu),
                        result_line(lang, 'check_equal', target=fmt(c2), target_unit=cu, final=fmt(result['final_volume']), final_unit=vu),
                    ]
                ),
            )
        except ValueError as err:
            messagebox.showerror(self._tr('error_title'), str(err), parent=self)

    def calc_total(self) -> None:
        cu, vu = self._units()
        lang = self.current_lang
        try:
            c1 = parse_number(self.t_c1.get(), self._tr('field_total_initial'), lang)
            c2 = parse_number(self.t_c2.get(), self._tr('field_total_target'), lang)
            v2 = parse_number(self.t_v2.get(), self._tr('field_total_volume'), lang)
            self._validate_strength(c1)
            self._validate_strength(c2)
            if v2 == 0:
                raise ValueError(self._get_error_text('total_zero'))
            if c1 == 0:
                raise ValueError(self._get_error_text('initial_zero'))
            if c2 > c1:
                raise ValueError(self._get_error_text('target_greater'))
            if c2 == 0:
                v1 = 0.0
                water = v2
            else:
                v1 = v2 * c2 / c1
                water = v2 - v1
            result = calculate_total_mix(c1, c2, v2)
            self._show(
                self.t_out,
                "\n".join(
                    [
                        result_line(lang, 'alcohol_volume', value=fmt(result['alcohol_volume']), unit=vu),
                        result_line(lang, 'water_add', value=fmt(result['water_to_add']), unit=vu),
                        result_line(lang, 'ready_solution', value=fmt(result['final_volume']), unit=vu),
                        result_line(lang, 'final_strength', value=fmt(c2), unit=cu),
                        result_line(lang, 'share_percent', value=fmt(result['share_percent'])),
                    ]
                ),
            )
        except ValueError as err:
            messagebox.showerror(self._tr('error_title'), str(err), parent=self)

    def calc_final(self) -> None:
        cu, vu = self._units()
        lang = self.current_lang
        try:
            c1 = parse_number(self.f_c1.get(), self._tr('field_final_alcohol'), lang)
            v1 = parse_number(self.f_v1.get(), self._tr('field_final_volume'), lang)
            water = parse_number(self.f_water.get(), self._tr('field_final_water'), lang)
            self._validate_strength(c1)
            if c1 <= 0:
                raise ValueError(self._get_error_text('initial_zero'))
            if v1 < 0:
                raise ValueError(self._get_error_text('negative', field=self._tr('field_final_volume')))
            if water < 0:
                raise ValueError(self._get_error_text('negative', field=self._tr('field_final_water')))
            result = calculate_final_strength(c1, v1, water)
            self._show(
                self.f_out,
                "\n".join(
                    [
                        result_line(lang, 'final_strength', value=fmt(result['final_strength']), unit=cu),
                        result_line(lang, 'final_volume', value=fmt(result['total_volume']), unit=vu),
                        result_line(lang, 'dilution', value=fmt(result['dilution'])),
                        result_line(lang, 'alcohol_volume', value=fmt(v1), unit=vu),
                        result_line(lang, 'water_amount', value=fmt(water), unit=vu),
                    ]
                ),
            )
        except ValueError as err:
            messagebox.showerror(self._tr('error_title'), str(err), parent=self)

    def clear_water(self) -> None:
        for e in (self.w_c1, self.w_v1, self.w_c2):
            e.delete(0, "end")
        self._show(self.w_out, "")

    def clear_total(self) -> None:
        for e in (self.t_c1, self.t_c2, self.t_v2):
            e.delete(0, "end")
        self._show(self.t_out, "")

    def clear_final(self) -> None:
        for e in (self.f_c1, self.f_v1, self.f_water):
            e.delete(0, "end")
        self._show(self.f_out, "")

    def _about(self) -> None:
        about_window = tk.Toplevel(self)
        about_window.title(self._tr('about_title'))
        about_window.geometry("420x320")
        about_window.resizable(False, False)
        about_window.configure(bg=BG)

        text = self._tr('about_text').format(
            name=APP_NAME,
            version=APP_VERSION,
            author=APP_AUTHOR,
            url=GITHUB_URL,
        )
        label = ttk.Label(
            about_window,
            text=text,
            justify="left",
            font=("Segoe UI", 9),
            background=BG,
        )
        label.pack(padx=20, pady=(20, 10), fill="both", expand=True)

        def open_github() -> None:
            webbrowser.open_new(GITHUB_URL)

        github_btn = ttk.Button(about_window, text="🔗 GitHub", command=open_github)
        github_btn.pack(pady=5)

        close_btn = ttk.Button(about_window, text="Закрыть", command=about_window.destroy)
        close_btn.pack(pady=5)

        about_window.transient(self)
        about_window.grab_set()
        self.wait_window(about_window)


def main() -> None:
    app = DilutionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
