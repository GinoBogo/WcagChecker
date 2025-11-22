#!/usr/bin/env python
"""
WCAG Checker Application

This application provides a graphical user interface (GUI) for checking Web
Content Accessibility Guidelines (WCAG) 2.2 AA compliance for color contrast
ratios. Users can select foreground and background colors, validate their
compliance, and automatically correct non-compliant colors.

Author: Gino Bogo
"""

import configparser as cfg
import copy
import json
import os
import random
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from typing import Tuple, cast

from PIL import Image, ImageDraw, ImageTk

CONFIG_FILE = "wcag_checker.cfg"

FRAME_PADDING = 10  # Padding used in main_frame and controls_frame


def calculate_luminance(color: Tuple[int, int, int]) -> float:
    """Calculates the relative luminance of an RGB color."""
    r, g, b = [c / 255.0 for c in color]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def calculate_contrast_ratio(
    foreground: Tuple[int, int, int], background: Tuple[int, int, int]
) -> float:
    """Calculates the contrast ratio between two RGB colors."""
    l1 = calculate_luminance(foreground)
    l2 = calculate_luminance(background)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def get_contrast_ratio(
    foreground: Tuple[int, int, int], background: Tuple[int, int, int]
) -> float:
    """Gets the contrast ratio between a foreground and background color."""
    return calculate_contrast_ratio(foreground, background)


def is_compliant(
    foreground: Tuple[int, int, int],
    background: Tuple[int, int, int],
    level: str = "AA",
    size: str = "normal",
) -> bool:
    """Checks if a color combination meets a WCAG compliance level."""
    contrast_ratio = get_contrast_ratio(foreground, background)

    if level == "AA":
        if size == "normal":
            return contrast_ratio >= 4.5
        else:
            return contrast_ratio >= 3.0
    else:
        if size == "normal":
            return contrast_ratio >= 7.0
        else:
            return contrast_ratio >= 4.5


class WCAGCheckerApp:
    def __init__(self, root: tk.Tk):
        """Initializes the WCAG Checker GUI application."""
        self.root = root
        self.root.title("WCAG Checker")
        self.root.geometry("600x900")
        self.root.minsize(600, 800)

        self.button_state_definitions = [
            ("default", "Button Default"),
            ("hover", "Button Hover"),
            ("focused", "Button Focused"),
            ("active", "Button Active"),
            ("disabled", "Button Disabled"),
        ]
        self.state_descriptions = dict(self.button_state_definitions)

        self.default_app_background_color = "#F0F0F0"
        self.default_state_color_settings = {
            "default": {"background": "#4682B4", "foreground": "#FFFFFF"},
            "hover": {"background": "#326496", "foreground": "#FFFFFF"},
            "focused": {"background": "#5A96C8", "foreground": "#FFFFFF"},
            "active": {"background": "#1E466E", "foreground": "#FFFFFF"},
            "disabled": {"background": "#BED2E6", "foreground": "#696969"},
        }

        self.app_background_color = self.default_app_background_color
        self.state_color_settings = copy.deepcopy(self.default_state_color_settings)

        self.restore_app_background_color = self.default_app_background_color
        self.restore_state_color_settings = copy.deepcopy(
            self.default_state_color_settings
        )

        self.state_ui_elements = {}
        self._resizing = False
        self._file_loaded = False

        self.SWATCH_COLUMNS = 32
        self.SWATCH_WIDTH = 16

        # fmt: off
        self.balanced_colors = [
            # Row 0
            "#000000", "#080808", "#101010", "#181818", "#202020", "#282828", "#303030", "#383838",
            "#404040", "#484848", "#505050", "#585858", "#606060", "#686868", "#707070", "#787878",
            "#808080", "#888888", "#909090", "#989898", "#A0A0A0", "#A8A8A8", "#B0B0B0", "#B8B8B8",
            "#C0C0C0", "#C8C8C8", "#D0D0D0", "#D8D8D8", "#E0E0E0", "#E8E8E8", "#F0F0F0", "#FFFFFF",
            # Row 1
            "#1A237E", "#1F2884", "#242E8A", "#293490", "#2E3A96", "#33409C", "#3846A2", "#3D4CA8",
            "#4252AE", "#4758B4", "#4C5EBA", "#5164C0", "#566AC6", "#5B70CC", "#6076D2", "#657CD8",
            "#6A82DE", "#6F88E4", "#748EEA", "#7994F0", "#7E9AF6", "#83A0FC", "#88A6FF", "#8DACFF",
            "#92B2FF", "#97B8FF", "#9CBEFF", "#A1C4FF", "#A6CAFF", "#ABD0FF", "#B0D6FF", "#DBEFFF",
            # Row 2
            "#004D40", "#005446", "#005C4C", "#006452", "#006C58", "#00745E", "#007C64", "#00846A",
            "#008C70", "#009476", "#009C7C", "#00A482", "#00AC88", "#00B48E", "#00BC94", "#00C49A",
            "#00CCA0", "#00D4A6", "#00DCAC", "#00E4B2", "#00ECB8", "#00F4BE", "#00FCC4", "#1AFFCA",
            "#34FFD0", "#4EFFD6", "#68FFDC", "#82FFE2", "#9CFFE8", "#B6FFEE", "#D0FFF4", "#EAFFEE",
            # Row 3
            "#991818", "#A01D1D", "#A72222", "#AE2727", "#B52C2C", "#BC3131", "#C33636", "#CA3B3B",
            "#D14040", "#D84545", "#DF4A4A", "#E64F4F", "#ED5454", "#F45959", "#FB5E5E", "#FF6363",
            "#FF6E6E", "#FF7979", "#FF8484", "#FF8F8F", "#FF9A9A", "#FFA5A5", "#FFB0B0", "#FFBBBB",
            "#FFC6C6", "#FFD1D1", "#FFDCDC", "#FFE7E7", "#FFEDED", "#FFF0F0", "#FFF3F3", "#FFF5F5",  
            # Row 4
            "#935114", "#9A581C", "#A15F24", "#A8662C", "#AF6D34", "#B6743C", "#BD7B44", "#C4824C",
            "#CB8954", "#D2905C", "#D99764", "#E09E6C", "#E7A574", "#EEAC7C", "#F5B384", "#FCBA8C",
            "#FFC194", "#FFC89C", "#FFCFA4", "#FFD6AC", "#FFDDB4", "#FFE4BC", "#FFEBC4", "#FFF0C7",
            "#FFF2C9", "#FFF2CC", "#FFF4D1", "#FFF6D6", "#FFF8DB", "#FFFADF", "#FFFCE4", "#FFFEE9",
            # Row 5
            "#3E0A91", "#461398", "#4E1C9F", "#5625A6", "#5E2EAD", "#6637B4", "#6E40BB", "#7649C2",
            "#7E52C9", "#865BD0", "#8E64D7", "#966DDE", "#9E76E5", "#A67FEC", "#AE88F3", "#B691FA",
            "#BE9AFF", "#C6A3FF", "#CEACFF", "#D6B5FF", "#DEBEFF", "#E6C7FF", "#E2CEFF", "#EED0FF",
            "#E9D6FF", "#F6D9FF", "#F0DEFF", "#FEE2FF", "#F8E6FF", "#FFEBFF", "#FFF4FF", "#FFFDFF",
            # Row 6
            "#005A5A", "#006161", "#006868", "#006F6F", "#007676", "#007D7D", "#008484", "#008B8B",
            "#009292", "#009999", "#00A0A0", "#00A7A7", "#00AEAE", "#00B5B5", "#00BCBC", "#00C3C3",
            "#00CACA", "#00D1D1", "#00D8D8", "#00DFDF", "#00E6E6", "#00EDED", "#00F4F4", "#00FBFB",
            "#47FFFF", "#77FFFF", "#A7FFFF", "#C7FFFF", "#D7FFFF", "#DFFFFF", "#E7FFFF", "#E0F7FA",
            # Row 7
            "#FF0000", "#FF3300", "#FF6600", "#FF9900", "#FFCC00", "#CCFF00", "#99FF00", "#66FF00",
            "#33FF00", "#00FF00", "#00FF33", "#00FF66", "#00FF99", "#00FFCC", "#00FFFF", "#00CCFF",
            "#0099FF", "#0066FF", "#0033FF", "#0000FF", "#3300FF", "#6600FF", "#9900FF", "#CC00FF",
            "#FF00FF", "#FF00CC", "#FF0099", "#FF0066", "#FF0033", "#FF3366", "#FF6699", "#FF99CC"
        ]
        # fmt: on

        self.load_window_geometry()
        self.initialize_ui()
        self.refresh_all_displays()
        self._update_compliance_indicators()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handles the window closing event."""
        self.save_window_geometry()
        self.root.destroy()

    def load_window_geometry(self):
        """Loads the window geometry from a config file if it exists."""
        config = cfg.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            if "WINDOW" in config and "geometry" in config["WINDOW"]:
                self.root.geometry(config["WINDOW"]["geometry"])

    def save_window_geometry(self):
        """Saves the current window geometry to a config file."""
        config = cfg.ConfigParser()
        config["WINDOW"] = {
            "geometry": self.root.geometry(),
        }
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)

    def load_settings(self):
        """Loads color settings from a file."""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Color Settings",
        )

        if not filepath:
            return

        try:
            with open(filepath, "r") as f:
                settings = json.load(f)

            # Robust validation
            if not isinstance(settings, dict):
                raise ValueError("Settings file is not a valid JSON object.")

            if (
                "app_background_color" not in settings
                or "state_color_settings" not in settings
            ):
                raise ValueError("Missing required keys in settings file.")

            if not isinstance(settings["state_color_settings"], dict):
                raise ValueError("'state_color_settings' should be a dictionary.")

            for state_key, _ in self.button_state_definitions:
                if state_key not in settings["state_color_settings"]:
                    raise ValueError(f"Missing settings for state: {state_key}")
                if (
                    "background" not in settings["state_color_settings"][state_key]
                    or "foreground" not in settings["state_color_settings"][state_key]
                ):
                    raise ValueError(
                        f"Missing 'background' or 'foreground' for state: {state_key}"
                    )

            self.app_background_color = settings["app_background_color"]
            self.state_color_settings = settings["state_color_settings"]

            self.restore_app_background_color = settings["app_background_color"]
            self.restore_state_color_settings = copy.deepcopy(
                settings["state_color_settings"]
            )

            self._file_loaded = True
            self.refresh_all_displays()
            self._update_compliance_indicators()
            messagebox.showinfo("Load Complete", "Settings loaded successfully.")

        except (ValueError, json.JSONDecodeError) as e:
            messagebox.showerror(
                "Invalid File",
                f"The selected file is not a valid settings file.\n\n{e}",
            )
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load settings: {e}")

    def save_settings(self):
        """Saves the current color settings to a file."""
        settings = {
            "app_background_color": self.app_background_color,
            "state_color_settings": self.state_color_settings,
        }

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Color Settings",
        )

        if not filepath:
            return

        try:
            with open(filepath, "w") as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Save Complete", f"Settings saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings: {e}")

    def random_colors(self):
        """Sets all editable colors to random values from the palette, ensuring WCAG compliance."""

        # 1. Select a light app_background_color from self.balanced_colors
        # Calculate luminance for each color and filter for light ones (Luminance > 0.5)
        light_colors = [hex_color for hex_color in self.balanced_colors if calculate_luminance(self.hex_to_rgb(hex_color)) > 0.5]

        if light_colors:
            self.app_background_color = random.choice(light_colors)
        else:
            # Fallback if no sufficiently light colors are found (should not happen with balanced_colors)
            self.app_background_color = random.choice(["#F0F0F0", "#FFFFFF"]) # Robust default light colors

        app_bg_rgb = self.hex_to_rgb(self.app_background_color)

        for state_key in self.state_color_settings:
            # 2. Determine a compliant darker button background based on app_background_color
            button_bg_rgb = app_bg_rgb # Start with app background color
            min_contrast_button_vs_app_bg = 3.0 # WCAG AA for large text (buttons often have large text)
            MAX_DARK_ATTEMPTS = 50

            # Try to find a compliant darker background by iteratively darkening
            for _ in range(MAX_DARK_ATTEMPTS):
                current_contrast = get_contrast_ratio(button_bg_rgb, app_bg_rgb)
                lum_app_bg = calculate_luminance(app_bg_rgb)
                lum_button_bg = calculate_luminance(button_bg_rgb)

                # Check if compliant and actually darker than app background
                if (current_contrast >= min_contrast_button_vs_app_bg) and (lum_button_bg < lum_app_bg):
                    break
                
                # Darken the color components by 10
                darkened_rgb = tuple(max(0, c - 10) for c in button_bg_rgb)
                if darkened_rgb == button_bg_rgb: # If no component changed, can't darken further
                    break
                button_bg_rgb = darkened_rgb
            else:
                # Fallback if a compliant darker color couldn't be found
                button_bg_rgb = self.hex_to_rgb("#4682B4") # Steel Blue as a robust default compliant darker color

            self.state_color_settings[state_key]["background"] = self.rgb_to_hex(button_bg_rgb)

            # 3. Find a compliant foreground color for the button (text on button)
            # Starting with white as preferred, then black, then adjust
            new_fg_rgb, _ = self.find_suitable_foreground_color(button_bg_rgb, self.hex_to_rgb("#FFFFFF"))
            self.state_color_settings[state_key]["foreground"] = self.rgb_to_hex(new_fg_rgb)

        self.refresh_all_displays()
        self._update_compliance_indicators()

    def initialize_ui(self):
        """Sets up the main UI components by calling helper methods."""
        main_frame = self._create_main_frames()
        controls_frame = self._create_controls_frame(main_frame)
        self._create_color_palette_widgets(controls_frame)
        preview_frame = self._create_preview_frame(main_frame)
        self._create_preview_area(preview_frame)

        button_controls_frame_main = ttk.Frame(main_frame, padding="10")
        button_controls_frame_main.grid(row=2, column=0, sticky=tk.E + tk.W)
        self._create_control_buttons(button_controls_frame_main)

    def _create_main_frames(self):
        """Creates and configures the main application frames."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=0)
        return main_frame

    def _create_controls_frame(self, parent):
        """Creates the frame for color selection and action buttons."""
        controls_frame = ttk.Frame(parent, padding="10")
        controls_frame.grid(row=0, column=0, sticky=tk.N + tk.E + tk.W)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        return controls_frame

    def _create_preview_frame(self, parent):
        """Creates the frame for the application preview."""
        preview_frame = ttk.Frame(parent, padding="10")
        preview_frame.grid(row=1, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        return preview_frame

    def _create_color_palette_widgets(self, parent):
        """Creates the widgets for the color palette selection."""
        ttk.Label(parent, text="Color Palette", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Generate and display the web safe colors palette image
        self.palette_image_pil = self._generate_colors_palette_image()
        self.palette_image_tk = ImageTk.PhotoImage(self.palette_image_pil)

        self.palette_image_label = ttk.Label(parent, image=self.palette_image_tk)
        self.palette_image_label.grid(row=1, column=0, sticky=tk.W + tk.E, pady=(0, 5))
        self.palette_image_label.bind("<Configure>", self._resize_palette_image)
        self.palette_image_label.bind("<Button-1>", self._on_palette_click)

        ttk.Label(parent, text="Color Selection", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        color_selection_frame = ttk.LabelFrame(parent, padding="10")
        color_selection_frame.grid(
            row=3, column=0, columnspan=4, sticky=tk.W + tk.E, pady=(0, 10)
        )
        # Configure columns for alignment
        for i in range(7):
            color_selection_frame.columnconfigure(i, weight=1 if i > 4 else 0)

        # Headers
        headers = ["", "Background", "Foreground", "BG Compliance", "FG Compliance"]
        ttk.Label(color_selection_frame, text=headers[0]).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(color_selection_frame, text=headers[1]).grid(
            row=0, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(0, 20)
        )
        ttk.Label(color_selection_frame, text=headers[2]).grid(
            row=0, column=3, columnspan=2, sticky=tk.W, pady=5
        )
        ttk.Label(color_selection_frame, text=headers[3]).grid(
            row=0, column=5, sticky=tk.W, pady=5
        )
        ttk.Label(color_selection_frame, text=headers[4]).grid(
            row=0, column=6, sticky=tk.W, pady=5
        )

        # App Background
        ttk.Label(color_selection_frame, text="Application:").grid(
            row=1, column=0, sticky=tk.E, pady=5, padx=(0, 10)
        )
        self.app_background_hex_var = tk.StringVar()
        self.app_background_hex_entry = ttk.Entry(
            color_selection_frame,
            textvariable=self.app_background_hex_var,
            font=("Courier", 10),
            width=10,
        )
        self.app_background_hex_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.app_background_hex_entry.bind(
            "<Return>", self.update_app_background_from_hex_entry
        )
        self.app_background_hex_entry.bind(
            "<FocusOut>", self.update_app_background_from_hex_entry
        )
        self.app_background_compliance_label = ttk.Label(
            color_selection_frame,
            text="",
            font=("Courier", 10, "bold"),
            anchor="center",
        )
        self.app_background_compliance_label.grid(row=1, column=5, sticky=tk.W, padx=5)

        # Button State Colors
        for i, (state_key, desc) in enumerate(self.button_state_definitions, start=2):
            ttk.Label(color_selection_frame, text=f"{desc}:").grid(
                row=i, column=0, sticky=tk.E, pady=5, padx=(0, 10)
            )
            self._create_color_row(color_selection_frame, state_key, i)

    def _create_color_row(self, parent, state_key, row):
        """Creates a single row of color selection widgets for a button state."""
        bg_hex_var = tk.StringVar()
        bg_hex_entry = ttk.Entry(
            parent, textvariable=bg_hex_var, font=("Courier", 10), width=10
        )
        bg_hex_entry.grid(row=row, column=1, sticky=tk.W, padx=5)
        bg_hex_entry.bind(
            "<Return>",
            lambda _, s=state_key, t="background": self.update_color_from_hex_entry(
                s, t
            ),
        )
        bg_hex_entry.bind(
            "<FocusOut>",
            lambda _, s=state_key, t="background": self.update_color_from_hex_entry(
                s, t
            ),
        )

        fg_hex_var = tk.StringVar()
        fg_hex_entry = ttk.Entry(
            parent, textvariable=fg_hex_var, font=("Courier", 10), width=10
        )
        fg_hex_entry.grid(row=row, column=3, sticky=tk.W, padx=5)
        fg_hex_entry.bind(
            "<Return>",
            lambda _, s=state_key, t="foreground": self.update_color_from_hex_entry(
                s, t
            ),
        )
        fg_hex_entry.bind(
            "<FocusOut>",
            lambda _, s=state_key, t="foreground": self.update_color_from_hex_entry(
                s, t
            ),
        )

        bg_compliance = ttk.Label(
            parent, text="", font=("Courier", 10, "bold"), anchor="center"
        )
        bg_compliance.grid(row=row, column=5, sticky=tk.W, padx=5)
        fg_compliance = ttk.Label(
            parent, text="", font=("Courier", 10, "bold"), anchor="center"
        )
        fg_compliance.grid(row=row, column=6, sticky=tk.W, padx=5)

        self.state_ui_elements[state_key] = {
            "background_hex_var": bg_hex_var,
            "foreground_hex_var": fg_hex_var,
            "background_hex_entry": bg_hex_entry,
            "foreground_hex_entry": fg_hex_entry,
            "background_compliance_label": bg_compliance,
            "foreground_compliance_label": fg_compliance,
        }

    def _create_preview_area(self, parent):
        """Creates the application preview area with placeholder buttons."""
        ttk.Label(parent, text="Application Preview", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W
        )
        preview_container = tk.Frame(parent)
        preview_container.grid(
            row=1, column=0, sticky=tk.N + tk.S + tk.E + tk.W, pady=10
        )
        preview_container.columnconfigure(0, weight=1)
        preview_container.rowconfigure(0, weight=1)
        preview_container.config(height=300)
        preview_container.grid_propagate(False)

        self.preview_display_frame = tk.Frame(preview_container, relief="sunken", bd=2)
        self.preview_display_frame.grid(
            row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.preview_display_frame.columnconfigure(0, weight=1)
        self.preview_display_frame.rowconfigure(0, weight=1)

        self.preview_buttons_container = tk.Frame(self.preview_display_frame)
        self.preview_buttons_container.pack(fill="both", expand=True)
        self.preview_buttons_container.columnconfigure(0, weight=1)

        self.preview_button_elements = {}
        for i, (state_key, desc) in enumerate(self.button_state_definitions):
            button = tk.Button(
                self.preview_buttons_container,
                text=desc,
                cursor="hand2",
                width=24,
                height=3,
            )
            button.grid(row=i, column=0, pady=8, sticky="n")
            self.preview_buttons_container.grid_rowconfigure(i, weight=1)
            self.preview_button_elements[state_key] = button

    def _create_control_buttons(self, parent):
        """Creates the Open, Save, Random, Validate, Correct, and Restore action buttons."""
        buttons_inner_frame = ttk.Frame(parent)
        buttons_inner_frame.pack(expand=True, anchor="center")

        ttk.Button(
            buttons_inner_frame,
            text="Open",
            cursor="hand2",
            width=10,
            command=self.load_settings,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buttons_inner_frame,
            text="Save",
            cursor="hand2",
            width=10,
            command=self.save_settings,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buttons_inner_frame,
            text="Random",
            cursor="hand2",
            width=10,
            command=self.random_colors,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buttons_inner_frame,
            text="Validate",
            cursor="hand2",
            width=10,
            command=self.validate_compliance,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buttons_inner_frame,
            text="Correct",
            cursor="hand2",
            width=10,
            command=self.correct_issues,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buttons_inner_frame,
            text="Restore",
            cursor="hand2",
            width=10,
            command=self.restore_defaults,
        ).pack(side=tk.LEFT, padx=5)

    def _generate_colors_palette_image(self) -> Image.Image:
        """Generates a PIL Image containing the web safe colors palette."""
        num_colors = len(self.balanced_colors)
        rows = (num_colors + self.SWATCH_COLUMNS - 1) // self.SWATCH_COLUMNS

        # Calculate image dimensions
        image_width = self.SWATCH_COLUMNS * self.SWATCH_WIDTH
        image_height = rows * self.SWATCH_WIDTH

        image = Image.new("RGB", (image_width, image_height), "#FFFFFF")
        draw = ImageDraw.Draw(image)

        for i, color_hex in enumerate(self.balanced_colors):
            row = i // self.SWATCH_COLUMNS
            col = i % self.SWATCH_COLUMNS
            x1 = col * self.SWATCH_WIDTH
            y1 = row * self.SWATCH_WIDTH
            x2 = x1 + self.SWATCH_WIDTH
            y2 = y1 + self.SWATCH_WIDTH
            draw.rectangle([x1, y1, x2, y2], fill=color_hex)

        return image

    def _resize_palette_image(self, _event=None):
        """Resizes the palette image to fit the label width while maintaining aspect ratio."""
        if self._resizing:
            return
        self._resizing = True
        try:
            if not hasattr(self, "palette_image_pil") or not self.palette_image_pil:
                return

            new_width = self.palette_image_label.winfo_width()

            if new_width <= 1:
                return

            original_width, original_height = self.palette_image_pil.size

            if original_width == 0:
                return

            aspect_ratio = original_height / original_width
            new_height = int(new_width * aspect_ratio)

            if new_height <= 0:
                return

            resized_image = self.palette_image_pil.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            self.palette_image_tk = ImageTk.PhotoImage(resized_image)
            self.palette_image_label.config(image=self.palette_image_tk)
        finally:
            self._resizing = False

    def _on_palette_click(self, event):
        """Handles clicks on the color palette to select a color."""
        focused_widget = self.root.focus_get()

        # Check if the focused widget is one of our color entries
        is_color_entry = False
        if focused_widget == self.app_background_hex_entry:
            is_color_entry = True
        else:
            for state_key in self.state_ui_elements:
                if focused_widget in (
                    self.state_ui_elements[state_key]["background_hex_entry"],
                    self.state_ui_elements[state_key]["foreground_hex_entry"],
                ):
                    is_color_entry = True
                    break

        if not is_color_entry:
            return  # Do nothing if a color entry is not focused

        # Calculate clicked color
        label_width = self.palette_image_label.winfo_width()
        original_width, original_height = self.palette_image_pil.size

        if original_width == 0:
            return

        aspect_ratio = original_height / original_width
        label_height = int(label_width * aspect_ratio)

        # Click coordinates relative to the resized image
        x, y = event.x, event.y

        # Ignore clicks outside the image area
        if not (0 <= x < label_width and 0 <= y < label_height):
            return

        scale_x = label_width / original_width
        scale_y = label_height / original_height

        orig_x = x / scale_x
        orig_y = y / scale_y

        col = int(orig_x // self.SWATCH_WIDTH)
        row = int(orig_y // self.SWATCH_WIDTH)  # SWATCH_WIDTH is used for height too

        color_index = row * self.SWATCH_COLUMNS + col

        if 0 <= color_index < len(self.balanced_colors):
            hex_color = self.balanced_colors[color_index]

            # Now update the focused entry
            if focused_widget == self.app_background_hex_entry:
                self.app_background_hex_var.set(hex_color)
                self.update_app_background_from_hex_entry(None)
            else:
                for state_key, ui_elements in self.state_ui_elements.items():
                    if focused_widget == ui_elements["background_hex_entry"]:
                        ui_elements["background_hex_var"].set(hex_color)
                        self.update_color_from_hex_entry(state_key, "background")
                        break
                    elif focused_widget == ui_elements["foreground_hex_entry"]:
                        ui_elements["foreground_hex_var"].set(hex_color)
                        self.update_color_from_hex_entry(state_key, "foreground")
                        break

    def update_app_background_from_hex_entry(self, _event):
        """Updates the app background color from the hex entry field."""
        new_hex_color = self.app_background_hex_var.get()
        try:
            # Validate hex color
            self.hex_to_rgb(new_hex_color)
            self.app_background_color = new_hex_color
            self.refresh_all_displays()
            self._update_compliance_indicators()
        except ValueError:
            # Restore original color if invalid
            self.app_background_hex_var.set(self.app_background_color)
            messagebox.showerror(
                "Invalid Color", f"'{new_hex_color}' is not a valid hex color."
            )

    def update_color_from_hex_entry(self, state_key: str, color_type: str):
        """Updates the color from a hex entry field."""
        ui_elements = self.state_ui_elements[state_key]
        hex_var = ui_elements[f"{color_type}_hex_var"]
        new_hex_color = hex_var.get()
        try:
            # Validate hex color
            self.hex_to_rgb(new_hex_color)
            self.state_color_settings[state_key][color_type] = new_hex_color
            self.refresh_all_displays()
            self._update_compliance_indicators()
        except ValueError:
            # Restore original color if invalid
            original_color = self.state_color_settings[state_key][color_type]
            hex_var.set(original_color)
            messagebox.showerror(
                "Invalid Color", f"'{new_hex_color}' is not a valid hex color."
            )

    def select_app_background(self):
        """Opens a color chooser to select the application background color."""
        color = colorchooser.askcolor(
            initialcolor=self.app_background_color,
            title="Choose Application Background Color",
        )
        if color[1]:
            self.app_background_color = color[1]
            self.refresh_all_displays()

    def select_button_color(self, state_key: str, color_type: str):
        """Opens a color chooser for a button's background or foreground color."""
        current_color = self.state_color_settings[state_key][color_type]
        color = colorchooser.askcolor(
            initialcolor=current_color,
            title=f"Choose {state_key} Button {color_type.title()}",
        )
        if color[1]:
            self.state_color_settings[state_key][color_type] = color[1]
            self.refresh_all_displays()

    def check_contrast_compliance(
        self,
        foreground_color: Tuple[int, int, int],
        background_color: Tuple[int, int, int],
        element_name: str,
    ) -> Tuple[bool, float]:
        """Checks the contrast ratio and compliance for a color pair."""
        contrast_ratio = get_contrast_ratio(foreground_color, background_color)
        is_aa_compliant = is_compliant(
            foreground_color, background_color, level="AA", size="normal"
        )
        return is_aa_compliant, contrast_ratio

    def adjust_color_for_contrast(
        self,
        target_color: Tuple[int, int, int],
        reference_color: Tuple[int, int, int],
        minimum_ratio: float = 4.5,
        max_iterations: int = 20,
    ) -> Tuple[Tuple[int, int, int], float]:
        """Adjusts a color to meet a minimum contrast ratio against another color."""
        adjusted_color = list(target_color)
        reference_luminance = calculate_luminance(reference_color)
        target_luminance = calculate_luminance(self._cast_color_list(adjusted_color))

        needs_darker = target_luminance > reference_luminance
        adjustment = -10 if needs_darker else 10

        for iteration in range(max_iterations):
            current_contrast = calculate_contrast_ratio(
                self._cast_color_list(adjusted_color), reference_color
            )

            if current_contrast >= minimum_ratio:
                return (
                    self._cast_color_list(adjusted_color),
                    current_contrast,
                )

            for i in range(3):
                new_value = adjusted_color[i] + adjustment
                adjusted_color[i] = max(0, min(255, new_value))

            if all(c == 0 for c in adjusted_color) or all(
                c == 255 for c in adjusted_color
            ):
                break

        return (
            self._cast_color_list(adjusted_color),
            calculate_contrast_ratio(
                self._cast_color_list(adjusted_color), reference_color
            ),
        )

    def find_suitable_foreground_color(
        self,
        background_color: Tuple[int, int, int],
        current_foreground_color: Tuple[int, int, int],
        minimum_ratio: float = 4.5,
    ) -> Tuple[Tuple[int, int, int], float]:
        """Finds a compliant foreground color for a given background."""
        high_contrast_colors = [
            "#FFFFFF",
            "#000000",
        ]

        for test_color_hex in high_contrast_colors:
            test_color_rgb = self.hex_to_rgb(test_color_hex)
            contrast = get_contrast_ratio(test_color_rgb, background_color)
            if contrast >= minimum_ratio:
                return test_color_rgb, contrast

        return self.adjust_color_for_contrast(
            current_foreground_color, background_color, minimum_ratio
        )

    def _fix_colors_for_state(self, state_key: str) -> int:
        """Corrects the colors for a given state to meet compliance."""
        fixes_applied = 0
        background_color = self.state_color_settings[state_key]["background"]
        foreground_color = self.state_color_settings[state_key]["foreground"]

        fg_bg_compliant, _ = self.check_contrast_compliance(
            self.hex_to_rgb(foreground_color), self.hex_to_rgb(background_color), ""
        )
        if not fg_bg_compliant:
            new_foreground_rgb, _ = self.find_suitable_foreground_color(
                self.hex_to_rgb(background_color), self.hex_to_rgb(foreground_color)
            )
            self.state_color_settings[state_key]["foreground"] = self.rgb_to_hex(
                new_foreground_rgb
            )
            foreground_color = self.rgb_to_hex(new_foreground_rgb)
            fixes_applied += 1

        app_bg_compliant, _ = self.check_contrast_compliance(
            self.hex_to_rgb(self.app_background_color),
            self.hex_to_rgb(background_color),
            "",
        )
        if not app_bg_compliant:
            new_background_rgb, _ = self.adjust_color_for_contrast(
                self.hex_to_rgb(background_color),
                self.hex_to_rgb(self.app_background_color),
            )
            self.state_color_settings[state_key]["background"] = self.rgb_to_hex(
                new_background_rgb
            )
            background_color = self.rgb_to_hex(new_background_rgb)
            fixes_applied += 1

            fg_bg_compliant_after_fix, _ = self.check_contrast_compliance(
                self.hex_to_rgb(foreground_color), self.hex_to_rgb(background_color), ""
            )
            if not fg_bg_compliant_after_fix:
                new_foreground_after_fix_rgb, _ = self.find_suitable_foreground_color(
                    self.hex_to_rgb(background_color),
                    self.hex_to_rgb(foreground_color),
                )
                self.state_color_settings[state_key]["foreground"] = self.rgb_to_hex(
                    new_foreground_after_fix_rgb
                )
                fixes_applied += 1
        return fixes_applied

    def refresh_all_displays(self):
        """Refreshes all UI elements with the current color settings."""
        self.app_background_hex_var.set(self.app_background_color)

        preview_hex = self.app_background_color
        self.preview_display_frame.configure(bg=preview_hex)
        self.preview_buttons_container.configure(bg=preview_hex)
        self.preview_buttons_container.grid_columnconfigure(0, weight=1)

        for state_key, ui_elements in self.state_ui_elements.items():
            background_color = self.state_color_settings[state_key]["background"]
            foreground_color = self.state_color_settings[state_key]["foreground"]

            ui_elements["background_hex_var"].set(background_color)
            ui_elements["foreground_hex_var"].set(foreground_color)

            preview_button = self.preview_button_elements[state_key]
            preview_button.configure(
                bg=background_color,
                fg=foreground_color,
                activebackground=background_color,
                activeforeground=foreground_color,
                relief="raised",
                font=("Arial", 11),
                text=self.state_descriptions[state_key],
            )

    def update_compliance_display(
        self, label: ttk.Label, is_compliant: bool, ratio: float
    ):
        """Updates a label to display compliance status and contrast ratio."""
        if is_compliant:
            label.config(
                text=f"{ratio:7.2f}:1",
                foreground="green",
                anchor="center",
                font=("Courier", 10, "bold"),
            )
        else:
            label.config(
                text=f"{ratio:7.2f}:1",
                foreground="red",
                anchor="center",
                font=("Courier", 10, "bold"),
            )

    def _update_compliance_indicators(self) -> bool:
        """Checks all color combinations and updates the compliance indicators."""
        all_compliant = True
        # Check foreground-background contrast for each button state
        for state_key, description in self.button_state_definitions:
            background_color = self.state_color_settings[state_key]["background"]
            foreground_color = self.state_color_settings[state_key]["foreground"]
            is_compliant, ratio = self.check_contrast_compliance(
                self.hex_to_rgb(foreground_color),
                self.hex_to_rgb(background_color),
                f"{description} Button",
            )
            self.update_compliance_display(
                self.state_ui_elements[state_key]["foreground_compliance_label"],
                is_compliant,
                ratio,
            )
            if not is_compliant:
                all_compliant = False

        # Check button background against application background contrast
        for state_key, description in self.button_state_definitions:
            button_background = self.state_color_settings[state_key]["background"]
            is_compliant, ratio = self.check_contrast_compliance(
                self.hex_to_rgb(self.app_background_color),
                self.hex_to_rgb(button_background),
                f"App BG vs {description} Button BG",
            )
            self.update_compliance_display(
                self.state_ui_elements[state_key]["background_compliance_label"],
                is_compliant,
                ratio,
            )
            if not is_compliant:
                all_compliant = False
        return all_compliant

    def validate_compliance(self):
        """Checks all color combinations and displays a compliance summary."""
        if self._update_compliance_indicators():
            messagebox.showinfo(
                "Compliance Check", "All color combinations are WCAG 2.2 AA compliant!"
            )
        else:
            messagebox.showwarning(
                "Compliance Issues",
                "Some color combinations need improvement. See details above.",
            )

    def correct_issues(self):
        """Automatically corrects all non-compliant color combinations."""
        total_fixes_applied = 0

        for state_key, _ in self.button_state_definitions:
            total_fixes_applied += self._fix_colors_for_state(state_key)

        self.refresh_all_displays()

        if total_fixes_applied > 0:
            messagebox.showinfo(
                "Auto-Correction Complete",
                f"Applied {total_fixes_applied} color adjustments to improve contrast.",
            )
            self.validate_compliance()
        else:
            messagebox.showinfo(
                "No Corrections Needed", "All color combinations are already compliant!"
            )

    def restore_defaults(self):
        """Restores color settings to the last loaded or default values."""
        self.app_background_color = self.restore_app_background_color
        self.state_color_settings = copy.deepcopy(self.restore_state_color_settings)
        self.refresh_all_displays()

        self.app_background_compliance_label.config(text="", foreground="black")
        for state_key, _ in self.button_state_definitions:
            self.state_ui_elements[state_key]["background_compliance_label"].config(
                text="", foreground="black"
            )
            self.state_ui_elements[state_key]["foreground_compliance_label"].config(
                text="", foreground="black"
            )

        if self._file_loaded:
            messagebox.showinfo(
                "Reset Complete", "Colors have been restored from the last loaded file."
            )
        else:
            messagebox.showinfo(
                "Reset Complete", "The default color set has been restored."
            )
        self.validate_compliance()

    def rgb_to_hex(self, color: Tuple[int, int, int]) -> str:
        """Converts an RGB color tuple to a hex string."""
        return "#{:02X}{:02X}{:02X}".format(*color)

    def hex_to_rgb(self, hex_string: str) -> Tuple[int, int, int]:
        """Converts a hex color string to an RGB tuple."""
        color_string = hex_string.strip().lstrip("#")

        if len(color_string) != 6:
            raise ValueError(f"Invalid hex color length: {hex_string}")

        try:
            return (
                int(color_string[0:2], 16),
                int(color_string[2:4], 16),
                int(color_string[4:6], 16),
            )
        except ValueError:
            raise ValueError(f"Invalid hex color value: {hex_string}")

    @staticmethod
    def _cast_color_list(color_list: list[int]) -> Tuple[int, int, int]:
        """Casts a list of 3 integers to a fixed-size tuple for type checking."""
        return cast(Tuple[int, int, int], tuple(color_list))


def main() -> None:
    """Main function to run the WCAG Checker application."""
    root = tk.Tk()
    WCAGCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
