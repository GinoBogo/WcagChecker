import unittest
from unittest.mock import MagicMock, patch
import re
import colorsys
import copy
import sys
import os

# Add the project root to the Python path to allow importing wcag_checker
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Mock tkinter and its modules
mock_tk = MagicMock()
mock_ttk = MagicMock()
mock_colorchooser = MagicMock()
mock_filedialog = MagicMock()
mock_messagebox = MagicMock()

# Patch tkinter imports in the module being tested
# This needs to be done before importing wcag_checker
# since tkinter imports happen at the top of the file
with patch.dict(
    "sys.modules",
    {
        "tkinter": mock_tk,
        "tkinter.ttk": mock_ttk,
        "tkinter.colorchooser": mock_colorchooser,
        "tkinter.filedialog": mock_filedialog,
        "tkinter.messagebox": mock_messagebox,
        "PIL.Image": MagicMock(),  # Mock PIL as well
        "PIL.ImageDraw": MagicMock(),
        "PIL.ImageTk": MagicMock(),
    },
):
    # Import the application after mocking tkinter
    from wcag_checker import WCAGCheckerApp, calculate_contrast_ratio


class TestWCAGCheckerApp(unittest.TestCase):
    def setUp(self):
        # Create a dummy root for the app
        self.mock_root = mock_tk.Tk()
        self.app = WCAGCheckerApp(self.mock_root)
        # Ensure the default colors are set as a baseline
        self.app.restore_defaults()

    def _is_hex_color(self, hex_string):
        """Helper to check if a string is a valid hex color."""
        return re.fullmatch(r"^#[0-9a-fA-F]{6}$", hex_string) is not None

    def _rgb_to_hsl(self, rgb: tuple) -> tuple:
        """Converts an RGB color tuple to an HSL tuple (hue, saturation, lightness)."""
        _r, _g, _b = [c / 255.0 for c in rgb]
        _h, _l, _s = colorsys.rgb_to_hls(_r, _g, _b)
        return _h, _s, _l

    def test_random_colors_execution(self):
        """Test that random_colors runs without errors."""
        try:
            self.app.random_colors()
        except Exception as e:
            self.fail(f"random_colors raised an exception: {e}")

    def test_random_colors_validity(self):
        """Test that all generated colors are valid hex codes."""
        self.app.random_colors()
        for state_key, _ in self.app.button_state_definitions:
            bg_color = self.app.state_color_settings[state_key]["background"]
            fg_color = self.app.state_color_settings[state_key]["foreground"]
            self.assertTrue(
                self._is_hex_color(bg_color),
                f"Invalid background color: {bg_color} for state {state_key}",
            )
            self.assertTrue(
                self._is_hex_color(fg_color),
                f"Invalid foreground color: {fg_color} for state {state_key}",
            )

    def test_random_colors_default_button_unchanged(self):
        """Test that the default button's background remains unchanged."""
        initial_default_bg = self.app.state_color_settings["default"]["background"]
        self.app.random_colors()
        final_default_bg = self.app.state_color_settings["default"]["background"]
        self.assertEqual(
            initial_default_bg,
            final_default_bg,
            "Default button background should not change after random_colors.",
        )

    def test_random_colors_compliance(self):
        """Test that generated colors meet WCAG contrast requirements."""
        self.app.random_colors()
        app_bg_rgb = self.app.hex_to_rgb(self.app.app_background_color)
        min_contrast_button_bg_vs_app_bg = 3.0
        # Relaxed test requirement to WCAG AA normal text
        min_contrast_button_bg_vs_button_fg = 4.5

        for state_key, _ in self.app.button_state_definitions:
            bg_hex = self.app.state_color_settings[state_key]["background"]
            fg_hex = self.app.state_color_settings[state_key]["foreground"]

            bg_rgb = self.app.hex_to_rgb(bg_hex)
            fg_rgb = self.app.hex_to_rgb(fg_hex)

            # Test button background against app background
            contrast_bg_vs_app_bg = calculate_contrast_ratio(bg_rgb, app_bg_rgb)
            self.assertGreaterEqual(
                contrast_bg_vs_app_bg,
                min_contrast_button_bg_vs_app_bg,
                f"Background contrast for {state_key} ({bg_hex} vs App BG {self.app.app_background_color}) "
                f"is {contrast_bg_vs_app_bg:.2f}:1, expected >= {min_contrast_button_bg_vs_app_bg}:1",
            )

            # Test foreground against button background, ONLY for non-default states
            if state_key != "default":
                contrast_fg_vs_bg = calculate_contrast_ratio(fg_rgb, bg_rgb)
                self.assertGreaterEqual(
                    contrast_fg_vs_bg,
                    min_contrast_button_bg_vs_button_fg,
                    f"Foreground contrast for {state_key} ({fg_hex} vs BG {bg_hex}) "
                    f"is {contrast_fg_vs_bg:.2f}:1, expected >= {min_contrast_button_bg_vs_button_fg}:1",
                )

    def test_random_colors_distinctness(self):
        """
        Test that colors for non-default states are distinct from the default
        and vary from each other (probabilistically).
        """
        initial_colors = copy.deepcopy(self.app.state_color_settings)
        self.app.random_colors()
        generated_colors = self.app.state_color_settings

        # Default button background should be the same
        self.assertEqual(
            initial_colors["default"]["background"],
            generated_colors["default"]["background"],
        )

        # Other states should ideally change
        changed_count = 0
        for state_key in self.app.state_descriptions:
            if state_key != "default":
                if (
                    initial_colors[state_key]["background"]
                    != generated_colors[state_key]["background"]
                    or initial_colors[state_key]["foreground"]
                    != generated_colors[state_key]["foreground"]
                ):
                    changed_count += 1
        # Expect at least most colors to change, but not necessarily all due to randomness
        # This is a probabilistic test, so it might fail rarely.
        self.assertGreater(
            changed_count,
            len(self.app.button_state_definitions) - 2,
            "Most random colors for non-default states should change.",
        )


if __name__ == "__main__":
    unittest.main()
