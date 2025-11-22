# WcagChecker
GUI application for checking WCAG 2.2 AA compliance

This application provides a graphical user interface (GUI) for checking Web
Content Accessibility Guidelines (WCAG) 2.2 AA compliance, specifically focusing
on color contrast ratios. Users can select foreground and background colors,
validate their compliance against WCAG 2.2 AA standards, and automatically
correct non-compliant colors to meet accessibility requirements.

## Features
-   **Color Contrast Checking:** Evaluate the contrast ratio between foreground and background colors.
-   **WCAG 2.2 AA Compliance:** Verify compliance against WCAG 2.2 Level AA guidelines for normal and large text.
-   **Automatic Correction:** Automatically adjust non-compliant colors to meet minimum contrast requirements.
-   **Interactive UI:** Select colors using a color picker or by entering hex values, and see live previews.
-   **Web Safe Color Palette:** Provides a palette of web-safe colors for easy selection.
-   **Customizable Button States:** Check and adjust colors for different button states (default, hover, focused, active, disabled).

![GUI Screenshot](docs/images/figure_01.png)

## Requirements

To run this application, you need Python 3.x and the dependencies listed in `requirements.txt`.

1.  **Python 3.x**: Ensure you have Python installed. You can download it from [python.org](https://www.python.org/).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the `wcag_checker.py` script from your terminal:

```bash
python wcag_checker.py
```

The main window will appear, allowing you to begin checking color contrast ratios.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! If you would like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with a clear message.
4.  Submit a pull request.

## Roadmap

Future enhancements may include:

-   Support for WCAG 2.2 AAA compliance checking.
-   Ability to analyze local HTML files for accessibility issues.
-   Integration with browser extensions for live web page analysis.

## Project Status

This project is in active development. New features and improvements are ongoing.

## Acknowledgments

This tool was developed with the help of the open-source community and relies on the following key libraries:

-   [Pillow](https://python-pillow.org/)
-   [Tkinter](https://docs.python.org/3/library/tkinter.html)

## Contact

Created by [Gino Bogo](https://github.com/ginobogo). Please feel free to reach out with any questions or feedback.
