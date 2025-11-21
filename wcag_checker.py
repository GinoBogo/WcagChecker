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
import os
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
from typing import Tuple, cast
from PIL import Image, ImageTk, ImageDraw

CONFIG_FILE = "wcag_checker.cfg"

# Constants for UI layout
FRAME_PADDING = 10  # Padding used in main_frame and controls_frame


def calculate_luminance(color: Tuple[int, int, int]) -> float:
    """Calculates the relative luminance of an RGB color."""
    r, g, b = [c / 255.0 for c in color]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def calculate_contrast_ratio(
    color1: Tuple[int, int, int], color2: Tuple[int, int, int]
) -> float:
    """Calculates the contrast ratio between two RGB colors."""
    l1 = calculate_luminance(color1)
    l2 = calculate_luminance(color2)
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
        self.root.minsize(400, 800)

        self.app_background_color = "#F0F0F0"

        self.button_state_definitions = [
            ("default", "Button Default"),
            ("hover", "Button Hover"),
            ("focused", "Button Focused"),
            ("active", "Button Active"),
            ("disabled", "Button Disabled"),
        ]
        self.state_descriptions = dict(self.button_state_definitions)

        self.state_color_settings = {
            "default": {
                "background": "#4682B4",
                "foreground": "#FFFFFF",
            },
            "hover": {
                "background": "#326496",
                "foreground": "#FFFFFF",
            },
            "focused": {
                "background": "#5A96C8",
                "foreground": "#FFFFFF",
            },
            "active": {
                "background": "#1E466E",
                "foreground": "#FFFFFF",
            },
            "disabled": {
                "background": "#BED2E6",
                "foreground": "#696969",
            },
        }

        self.state_ui_elements = {}
        self._resizing = False

        self.SWATCHES_PER_ROW = 36
        self.SWATCH_WIDTH = 16

        self.web_safe_colors = [
            "#000000",
            "#330000",
            "#660000",
            "#990000",
            "#CC0000",
            "#FF0000",
            "#003300",
            "#333300",
            "#663300",
            "#993300",
            "#CC3300",
            "#FF3300",
            "#006600",
            "#336600",
            "#666600",
            "#996600",
            "#CC6600",
            "#FF6600",
            "#009900",
            "#339900",
            "#669900",
            "#999900",
            "#CC9900",
            "#FF9900",
            "#00CC00",
            "#33CC00",
            "#66CC00",
            "#99CC00",
            "#CCCC00",
            "#FFCC00",
            "#00FF00",
            "#33FF00",
            "#66FF00",
            "#99FF00",
            "#CCFF00",
            "#FFFF00",
            "#000033",
            "#330033",
            "#660033",
            "#990033",
            "#CC0033",
            "#FF0033",
            "#003333",
            "#333333",
            "#663333",
            "#993333",
            "#CC3333",
            "#FF3333",
            "#006633",
            "#336633",
            "#666633",
            "#996633",
            "#CC6633",
            "#FF6633",
            "#009933",
            "#339933",
            "#669933",
            "#999933",
            "#CC9933",
            "#FF9933",
            "#00CC33",
            "#33CC33",
            "#66CC33",
            "#99CC33",
            "#CCCC33",
            "#FFCC33",
            "#00FF33",
            "#33FF33",
            "#66FF33",
            "#99FF33",
            "#CCFF33",
            "#FFFF33",
            "#000066",
            "#330066",
            "#660066",
            "#990066",
            "#CC0066",
            "#FF0066",
            "#003366",
            "#333366",
            "#663366",
            "#993366",
            "#CC3366",
            "#FF3366",
            "#006666",
            "#336666",
            "#666666",
            "#996666",
            "#CC6666",
            "#FF6666",
            "#009966",
            "#339966",
            "#669966",
            "#999966",
            "#CC9966",
            "#FF9966",
            "#00CC66",
            "#33CC66",
            "#66CC66",
            "#99CC66",
            "#CCCC66",
            "#FFCC66",
            "#00FF66",
            "#33FF66",
            "#66FF66",
            "#99FF66",
            "#CCFF66",
            "#FFFF66",
            "#000099",
            "#330099",
            "#660099",
            "#990099",
            "#CC0099",
            "#FF0099",
            "#003399",
            "#333399",
            "#663399",
            "#993399",
            "#CC3399",
            "#FF3399",
            "#006699",
            "#336699",
            "#666699",
            "#996699",
            "#CC6699",
            "#FF6699",
            "#009999",
            "#339999",
            "#669999",
            "#999999",
            "#CC9999",
            "#FF9999",
            "#00CC99",
            "#33CC99",
            "#66CC99",
            "#99CC99",
            "#CCCC99",
            "#FFCC99",
            "#00FF99",
            "#33FF99",
            "#66FF99",
            "#99FF99",
            "#CCFF99",
            "#FFFF99",
            "#0000CC",
            "#3300CC",
            "#6600CC",
            "#9900CC",
            "#CC00CC",
            "#FF00CC",
            "#0033CC",
            "#3333CC",
            "#6633CC",
            "#9933CC",
            "#CC33CC",
            "#FF33CC",
            "#0066CC",
            "#3366CC",
            "#6666CC",
            "#9966CC",
            "#CC66CC",
            "#FF66CC",
            "#0099CC",
            "#3399CC",
            "#6699CC",
            "#9999CC",
            "#CC99CC",
            "#FF99CC",
            "#00CCCC",
            "#33CCCC",
            "#66CCCC",
            "#99CCCC",
            "#CCCCCC",
            "#FFCCCC",
            "#00FFCC",
            "#33FFCC",
            "#66FFCC",
            "#99FFCC",
            "#CCFFCC",
            "#FFFFCC",
            "#0000FF",
            "#3300FF",
            "#6600FF",
            "#9900FF",
            "#CC00FF",
            "#FF00FF",
            "#0033FF",
            "#3333FF",
            "#6633FF",
            "#9933FF",
            "#CC33FF",
            "#FF33FF",
            "#0066FF",
            "#3366FF",
            "#6666FF",
            "#9966FF",
            "#CC66FF",
            "#FF66FF",
            "#0099FF",
            "#3399FF",
            "#6699FF",
            "#9999FF",
            "#CC99FF",
            "#FF99FF",
            "#00CCFF",
            "#33CCFF",
            "#66CCFF",
            "#99CCFF",
            "#CCCCFF",
            "#FFCCFF",
            "#00FFFF",
            "#33FFFF",
            "#66FFFF",
            "#99FFFF",
            "#CCFFFF",
            "#FFFFFF",
        ]

        self.load_window_geometry()
        self.initialize_ui()
        self.refresh_all_displays()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handles the window closing event."""
        self.save_window_geometry()
        self.root.destroy()

    def save_window_geometry(self):
        """Saves the current window geometry to a config file."""
        config = cfg.ConfigParser()
        config["WINDOW"] = {
            "geometry": self.root.geometry(),
        }
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)

    def load_window_geometry(self):
        """Loads the window geometry from a config file if it exists."""
        config = cfg.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            if "WINDOW" in config and "geometry" in config["WINDOW"]:
                self.root.geometry(config["WINDOW"]["geometry"])

    def set_default_button_color(self, hex_color: str):
        """Sets the default button background color and refreshes the display."""
        self.state_color_settings["default"]["background"] = hex_color
        self.refresh_all_displays()

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

    def _generate_web_safe_colors_palette_image(self) -> Image.Image:
        """Generates a PIL Image containing the web safe colors palette."""
        num_colors = len(self.web_safe_colors)
        rows = (num_colors + self.SWATCHES_PER_ROW - 1) // self.SWATCHES_PER_ROW

        # Calculate image dimensions
        image_width = self.SWATCHES_PER_ROW * self.SWATCH_WIDTH
        image_height = rows * self.SWATCH_WIDTH

        image = Image.new("RGB", (image_width, image_height), "#FFFFFF")
        draw = ImageDraw.Draw(image)

        for i, color_hex in enumerate(self.web_safe_colors):
            row = i // self.SWATCHES_PER_ROW
            col = i % self.SWATCHES_PER_ROW
            x1 = col * self.SWATCH_WIDTH
            y1 = row * self.SWATCH_WIDTH
            x2 = x1 + self.SWATCH_WIDTH
            y2 = y1 + self.SWATCH_WIDTH
            draw.rectangle([x1, y1, x2, y2], fill=color_hex)

        return image

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

    def _resize_palette_image(self, event=None):
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

        color_index = row * self.SWATCHES_PER_ROW + col

        if 0 <= color_index < len(self.web_safe_colors):
            hex_color = self.web_safe_colors[color_index]

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

    def _create_color_palette_widgets(self, parent):
        """Creates the widgets for the color palette selection."""
        ttk.Label(parent, text="Color Palette", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Generate and display the web safe colors palette image
        self.palette_image_pil = self._generate_web_safe_colors_palette_image()
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
        bg_compliance.grid(row=row, column=4, sticky=tk.W, padx=5)
        fg_compliance = ttk.Label(
            parent, text="", font=("Courier", 10, "bold"), anchor="center"
        )
        fg_compliance.grid(row=row, column=5, sticky=tk.W, padx=5)

        self.state_ui_elements[state_key] = {
            "background_hex_var": bg_hex_var,
            "foreground_hex_var": fg_hex_var,
            "background_hex_entry": bg_hex_entry,
            "foreground_hex_entry": fg_hex_entry,
            "background_compliance_label": bg_compliance,
            "foreground_compliance_label": fg_compliance,
        }

    def _create_control_buttons(self, parent):
        """Creates the Validate, Restore, and Correct action buttons."""
        buttons_inner_frame = ttk.Frame(parent)
        buttons_inner_frame.pack(expand=True, anchor="center")

        ttk.Button(
            buttons_inner_frame,
            text="Validate",
            cursor="hand2",
            width=15,
            command=self.validate_compliance,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buttons_inner_frame,
            text="Restore",
            cursor="hand2",
            width=15,
            command=self.restore_defaults,
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            buttons_inner_frame,
            text="Correct",
            cursor="hand2",
            width=15,
            command=self.correct_issues,
        ).pack(side=tk.LEFT, padx=5)

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

    def update_app_background_from_hex_entry(self, _event):
        """Updates the app background color from the hex entry field."""
        new_hex_color = self.app_background_hex_var.get()
        print(f"Updating app background with value {new_hex_color}")
        try:
            # Validate hex color
            self.hex_to_rgb(new_hex_color)
            self.app_background_color = new_hex_color
            self.refresh_all_displays()
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

    @staticmethod
    def _cast_color_list(color_list: list[int]) -> Tuple[int, int, int]:
        """Casts a list of 3 integers to a fixed-size tuple for type checking."""
        return cast(Tuple[int, int, int], tuple(color_list))

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

    def fix_colors_for_state(self, state_key: str) -> int:
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

    def validate_compliance(self):
        """Checks all color combinations and displays a compliance summary."""
        self.app_background_compliance_label.config(text="", foreground="black")
        for state_key, _ in self.button_state_definitions:
            self.state_ui_elements[state_key]["background_compliance_label"].config(
                text="", foreground="black"
            )
            self.state_ui_elements[state_key]["foreground_compliance_label"].config(
                text="", foreground="black"
            )

        all_combinations_compliant = True

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
                all_combinations_compliant = False

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
                all_combinations_compliant = False

        if all_combinations_compliant:
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
            total_fixes_applied += self.fix_colors_for_state(state_key)

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
        """Restores all color settings to their default values."""
        self.app_background_color = "#F0F0F0"
        self.state_color_settings = {
            "default": {
                "background": "#4682B4",
                "foreground": "#FFFFFF",
            },
            "hover": {
                "background": "#326496",
                "foreground": "#FFFFFF",
            },
            "focused": {
                "background": "#5A96C8",
                "foreground": "#FFFFFF",
            },
            "active": {
                "background": "#1E466E",
                "foreground": "#FFFFFF",
            },
            "disabled": {
                "background": "#BED2E6",
                "foreground": "#696969",
            },
        }
        self.refresh_all_displays()

        self.app_background_compliance_label.config(text="", foreground="black")
        for state_key, _ in self.button_state_definitions:
            self.state_ui_elements[state_key]["background_compliance_label"].config(
                text="", foreground="black"
            )
            self.state_ui_elements[state_key]["foreground_compliance_label"].config(
                text="", foreground="black"
            )

        messagebox.showinfo(
            "Reset Complete", "All colors have been restored to defaults."
        )
        self.validate_compliance()


def main() -> None:
    """Main function to run the WCAG Checker application."""
    root = tk.Tk()
    WCAGCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
