"""
WaterMarker - PyQt6 Implementation
A modern desktop application to apply text watermarks to images.
"""

import sys
import os
import shutil
import configparser
from PIL import Image, ImageFont, ImageDraw
import matplotlib.font_manager as fm

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QListWidget, QSlider, QPushButton, QToolButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QFileDialog,
    QColorDialog, QMessageBox, QDialog
)
from PyQt6.QtGui import QIcon, QPixmap, QImage, QFont, QAction, QColor, QCursor
from PyQt6.QtCore import Qt, QSize

# **** PATHS & CONSTANTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(BASE_DIR, 'watermarker.ini')
PROGRAM_NAME = 'WaterMarker'
PROGRAM_VERSION = '1.0.0'
PROGRAM_DESCRIPTION = 'Set a text watermark\nthe easy way\n\nProgram by @edfasano70'


class AboutDialog(QDialog):
    """Modal dialog displaying application information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(300, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        logo_path = os.path.join(RESOURCES_DIR, 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(15, 15, 15, 15)

        # Splash image
        splash_path = os.path.join(RESOURCES_DIR, 'splash.png')
        if os.path.exists(splash_path):
            splash_label = QLabel()
            pixmap = QPixmap(splash_path)
            splash_label.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(splash_label)

        # Program Name
        name_label = QLabel(PROGRAM_NAME)
        name_font = QFont("Arial", 14, QFont.Weight.Bold)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"v{PROGRAM_VERSION}")
        version_font = QFont("Arial", 10, QFont.Weight.Bold)
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Description
        desc_label = QLabel(PROGRAM_DESCRIPTION)
        desc_font = QFont("Arial", 9)
        desc_label.setFont(desc_font)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        layout.addSpacing(10)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(90)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


class HelpDialog(QDialog):
    """Modal dialog displaying application help and instructions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - WaterMarker")
        self.setFixedSize(390, 340)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        logo_path = os.path.join(RESOURCES_DIR, 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("How to use WaterMarker")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        instructions = (
            "1. Open an image using <b>File &rarr; Open</b>.<br>"
            "2. Enter your watermark text in the <b>Text</b> field.<br>"
            "3. Choose a font from the <b>Font</b> list.<br>"
            "4. Adjust <b>Size</b>, <b>Transparency</b>, and <b>Angle</b> using the sliders or +/- buttons.<br>"
            "5. Click on the <b>Color</b> box to choose a text color.<br>"
            "6. Save your watermarked image using <b>File &rarr; Save</b>.<br><br>"
            "<i>Preferences and recent folders are automatically saved on exit.</i>"
        )
        text_label = QLabel(instructions)
        text_label.setFont(QFont("Arial", 9))
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(90)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


class WatermarkerApp(QMainWindow):
    """Main application window using PyQt6."""

    def __init__(self):
        super().__init__()
        self.root_dir = BASE_DIR
        self.save_dir = BASE_DIR
        self.display_image_path = os.path.join(RESOURCES_DIR, 'checkers.png')
        self.text_color = (0, 0, 0)
        self.color_hex = "#000000"
        self.updating_controls = False

        self.init_fonts()
        self.init_ui()
        self.load_preferences()
        self.refresh()
        self.center_window()

    def init_fonts(self):
        """Discovers system TTF fonts."""
        system_fonts = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        self.fonts = []
        for font_path in system_fonts:
            if '.ttf' in font_path.lower():
                font_name = os.path.splitext(os.path.basename(font_path))[0].capitalize()
                self.fonts.append((font_name, font_path))

        self.fonts.sort(key=lambda x: x[0])
        if not self.fonts:
            self.fonts.append(("Default", ""))
        self.font_selected = self.fonts[0]

    def init_ui(self):
        """Builds the PyQt6 user interface."""
        self.setWindowTitle(PROGRAM_NAME)
        logo_path = os.path.join(RESOURCES_DIR, 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Menu Bar
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help Menu
        help_menu = menu_bar.addMenu("Help")
        help_action = QAction("Help", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Controls Panel (Left)
        controls_widget = QWidget()
        controls_layout = QGridLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setVerticalSpacing(8)
        controls_layout.setHorizontalSpacing(8)

        # 1. Text Entry
        text_lbl = QLabel("Text")
        self.text_entry = QLineEdit("The Lazy Fox")
        self.text_entry.textChanged.connect(self.on_text_changed)
        controls_layout.addWidget(text_lbl, 0, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.text_entry, 0, 1)

        # 2. Font List
        font_lbl = QLabel("Font")
        self.font_list = QListWidget()
        self.font_list.setFixedHeight(110)
        for font_name, _ in self.fonts:
            self.font_list.addItem(font_name)
        self.font_list.setCurrentRow(0)
        self.font_list.currentRowChanged.connect(self.on_font_changed)
        controls_layout.addWidget(font_lbl, 1, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        controls_layout.addWidget(self.font_list, 1, 1)

        # Icons
        minus_icon_path = os.path.join(RESOURCES_DIR, 'icon_minus.png')
        plus_icon_path = os.path.join(RESOURCES_DIR, 'icon_plus.png')
        minus_icon = QIcon(minus_icon_path) if os.path.exists(minus_icon_path) else QIcon()
        plus_icon = QIcon(plus_icon_path) if os.path.exists(plus_icon_path) else QIcon()

        # 3. Size Control (Slider + Buttons)
        size_lbl = QLabel("Size")
        size_container = QWidget()
        size_layout = QHBoxLayout(size_container)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(4)

        self.size_minus_btn = QToolButton()
        self.size_minus_btn.setIcon(minus_icon)
        self.size_minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.size_minus_btn.clicked.connect(self.on_size_minus)
        size_layout.addWidget(self.size_minus_btn)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(2, 150)
        self.size_slider.setValue(24)
        self.size_slider.setFixedWidth(100)
        self.size_slider.valueChanged.connect(self.on_size_slider_changed)
        size_layout.addWidget(self.size_slider)

        self.size_plus_btn = QToolButton()
        self.size_plus_btn.setIcon(plus_icon)
        self.size_plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.size_plus_btn.clicked.connect(self.on_size_plus)
        size_layout.addWidget(self.size_plus_btn)

        self.size_val_lbl = QLabel("24")
        self.size_val_lbl.setFixedWidth(30)
        size_layout.addWidget(self.size_val_lbl)

        controls_layout.addWidget(size_lbl, 2, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(size_container, 2, 1, Qt.AlignmentFlag.AlignLeft)

        # 4. Transparency Control (Slider + Buttons)
        transp_lbl = QLabel("Transparency")
        transp_container = QWidget()
        transp_layout = QHBoxLayout(transp_container)
        transp_layout.setContentsMargins(0, 0, 0, 0)
        transp_layout.setSpacing(4)

        self.transp_minus_btn = QToolButton()
        self.transp_minus_btn.setIcon(minus_icon)
        self.transp_minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.transp_minus_btn.clicked.connect(self.on_transp_minus)
        transp_layout.addWidget(self.transp_minus_btn)

        self.transp_slider = QSlider(Qt.Orientation.Horizontal)
        self.transp_slider.setRange(0, 255)
        self.transp_slider.setValue(125)
        self.transp_slider.setFixedWidth(100)
        self.transp_slider.valueChanged.connect(self.on_transp_slider_changed)
        transp_layout.addWidget(self.transp_slider)

        self.transp_plus_btn = QToolButton()
        self.transp_plus_btn.setIcon(plus_icon)
        self.transp_plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.transp_plus_btn.clicked.connect(self.on_transp_plus)
        transp_layout.addWidget(self.transp_plus_btn)

        self.transp_val_lbl = QLabel("125")
        self.transp_val_lbl.setFixedWidth(30)
        transp_layout.addWidget(self.transp_val_lbl)

        controls_layout.addWidget(transp_lbl, 3, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(transp_container, 3, 1, Qt.AlignmentFlag.AlignLeft)

        # 5. Angle Control (Slider + Buttons)
        angle_lbl = QLabel("Angle")
        angle_container = QWidget()
        angle_layout = QHBoxLayout(angle_container)
        angle_layout.setContentsMargins(0, 0, 0, 0)
        angle_layout.setSpacing(4)

        self.angle_minus_btn = QToolButton()
        self.angle_minus_btn.setIcon(minus_icon)
        self.angle_minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.angle_minus_btn.clicked.connect(self.on_angle_minus)
        angle_layout.addWidget(self.angle_minus_btn)

        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setRange(0, 360)
        self.angle_slider.setValue(45)
        self.angle_slider.setFixedWidth(100)
        self.angle_slider.valueChanged.connect(self.on_angle_slider_changed)
        angle_layout.addWidget(self.angle_slider)

        self.angle_plus_btn = QToolButton()
        self.angle_plus_btn.setIcon(plus_icon)
        self.angle_plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.angle_plus_btn.clicked.connect(self.on_angle_plus)
        angle_layout.addWidget(self.angle_plus_btn)

        self.angle_val_lbl = QLabel("45")
        self.angle_val_lbl.setFixedWidth(30)
        angle_layout.addWidget(self.angle_val_lbl)

        controls_layout.addWidget(angle_lbl, 4, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(angle_container, 4, 1, Qt.AlignmentFlag.AlignLeft)

        # 6. Color Control (Visual Swatch + Hex)
        color_lbl = QLabel("Color")
        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(6)

        self.color_swatch = QPushButton()
        self.color_swatch.setFixedSize(26, 22)
        self.color_swatch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_swatch.clicked.connect(self.choose_color)
        self.update_color_swatch_style()
        color_layout.addWidget(self.color_swatch)

        self.color_hex_btn = QPushButton(self.color_hex)
        self.color_hex_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_hex_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_hex_btn)

        controls_layout.addWidget(color_lbl, 5, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(color_container, 5, 1, Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(controls_widget, 0, Qt.AlignmentFlag.AlignTop)

        # Image Display Area (Right)
        self.image_display_label = QLabel()
        self.image_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display_label.setFrameShape(QFrame.Shape.StyledPanel)
        main_layout.addWidget(self.image_display_label, 1)

    def update_color_swatch_style(self):
        """Updates the color swatch background and border."""
        self.color_swatch.setStyleSheet(
            f"background-color: {self.color_hex}; border: 1px solid #777; border-radius: 3px;"
        )

    def on_text_changed(self, text):
        self.refresh()

    def on_font_changed(self, index):
        if 0 <= index < len(self.fonts):
            self.font_selected = self.fonts[index]
            self.refresh()

    def on_size_slider_changed(self, val):
        self.size_val_lbl.setText(str(val))
        if not self.updating_controls:
            self.refresh()

    def on_size_minus(self):
        val = max(2, self.size_slider.value() - 2)
        self.size_slider.setValue(val)

    def on_size_plus(self):
        val = min(150, self.size_slider.value() + 2)
        self.size_slider.setValue(val)

    def on_transp_slider_changed(self, val):
        self.transp_val_lbl.setText(str(val))
        if not self.updating_controls:
            self.refresh()

    def on_transp_minus(self):
        val = max(0, self.transp_slider.value() - 5)
        self.transp_slider.setValue(val)

    def on_transp_plus(self):
        val = min(255, self.transp_slider.value() + 5)
        self.transp_slider.setValue(val)

    def on_angle_slider_changed(self, val):
        self.angle_val_lbl.setText(str(val))
        if not self.updating_controls:
            self.refresh()

    def on_angle_minus(self):
        val = max(0, self.angle_slider.value() - 5)
        self.angle_slider.setValue(val)

    def on_angle_plus(self):
        val = min(360, self.angle_slider.value() + 5)
        self.angle_slider.setValue(val)

    def choose_color(self):
        """Opens QColorDialog to select watermark color."""
        initial = QColor(self.color_hex)
        chosen = QColorDialog.getColor(initial, self, "Select Color")
        if chosen.isValid():
            self.text_color = (chosen.red(), chosen.green(), chosen.blue())
            self.color_hex = chosen.name()
            self.color_hex_btn.setText(self.color_hex)
            self.update_color_swatch_style()
            self.refresh()

    def open_image(self):
        """Opens an image file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image File",
            self.root_dir,
            "Image Files (*.png *.jpg *.jpeg *.gif);;All Files (*)"
        )
        if file_path:
            self.display_image_path = file_path
            self.root_dir = os.path.dirname(file_path)
            self.refresh()
            self.center_window()

    def save_image(self):
        """Saves the watermarked image to user selected path."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            os.path.join(self.save_dir, "watermarked.png"),
            "PNG Image (*.png);;All Files (*)"
        )
        if file_path:
            temp_out = os.path.join(TMP_DIR, 'out.png')
            if os.path.exists(temp_out):
                shutil.copy(temp_out, file_path)
                self.save_dir = os.path.dirname(file_path)
                QMessageBox.information(self, "Info", "Image saved successfully")
            else:
                QMessageBox.critical(self, "Error", "Watermarked image could not be found.")

    def show_about(self):
        """Displays About modal dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def show_help(self):
        """Displays Help modal dialog."""
        dialog = HelpDialog(self)
        dialog.exec()

    def refresh(self):
        """Renders the watermarked preview."""
        if not os.path.exists(self.display_image_path):
            return

        try:
            base_image = Image.open(self.display_image_path).convert("RGBA")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open image:\n{e}")
            return

        # Keep preview within 600x600 px
        width, height = base_image.size
        if width > 600 or height > 600:
            base_image.thumbnail((600, 600))
            width, height = base_image.size

        text_layer = Image.new('RGBA', base_image.size, (255, 255, 255, 0))

        font_size = self.size_slider.value()
        if self.font_selected and self.font_selected[1] and os.path.exists(self.font_selected[1]):
            try:
                font_obj = ImageFont.truetype(self.font_selected[1], font_size)
            except Exception:
                font_obj = ImageFont.load_default()
        else:
            font_obj = ImageFont.load_default()

        draw = ImageDraw.Draw(text_layer)
        text = self.text_entry.text()

        # Exact text centering with draw.textbbox
        if text:
            bbox = draw.textbbox((0, 0), text, font=font_obj)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) / 2 - bbox[0]
            y = (height - text_height) / 2 - bbox[1]

            fill_color = (
                self.text_color[0],
                self.text_color[1],
                self.text_color[2],
                self.transp_slider.value()
            )
            draw.text((x, y), text, fill=fill_color, font=font_obj)

        rotated_text_layer = text_layer.rotate(self.angle_slider.value())

        # Alpha composite and save out.png
        watermarked = Image.alpha_composite(base_image, rotated_text_layer)
        temp_out = os.path.join(TMP_DIR, 'out.png')
        watermarked.save(temp_out)

        # Convert PIL RGBA to QPixmap for QLabel display
        im_rgba = watermarked.convert("RGBA")
        data = im_rgba.tobytes("raw", "RGBA")
        qimg = QImage(data, im_rgba.width, im_rgba.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
        self.image_display_label.setPixmap(pixmap)

    def center_window(self):
        """Centers window on the primary screen."""
        self.adjustSize()
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            win_geo = self.frameGeometry()
            win_geo.moveCenter(screen_geo.center())
            self.move(win_geo.topLeft())

    def save_preferences(self):
        """Saves current settings to INI file."""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'text': self.text_entry.text(),
            'font_name': self.font_selected[0] if self.font_selected else '',
            'font_size': str(self.size_slider.value()),
            'transparency': str(self.transp_slider.value()),
            'angle': str(self.angle_slider.value()),
            'color_rgb': ','.join(map(str, self.text_color)),
            'color_hex': self.color_hex
        }
        config['Paths'] = {
            'last_image': self.display_image_path,
            'last_save_dir': self.save_dir,
            'last_open_dir': self.root_dir
        }
        try:
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        except IOError as e:
            print(f"Error saving preferences: {e}")

    def load_preferences(self):
        """Loads settings from INI file."""
        if not os.path.exists(CONFIG_FILE):
            return

        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        self.updating_controls = True

        if 'Settings' in config:
            settings = config['Settings']
            self.text_entry.setText(settings.get('text', self.text_entry.text()))

            try:
                size_val = int(settings.get('font_size', '24'))
                self.size_slider.setValue(size_val)
                self.size_val_lbl.setText(str(size_val))
            except ValueError:
                pass

            try:
                transp_val = int(settings.get('transparency', '125'))
                self.transp_slider.setValue(transp_val)
                self.transp_val_lbl.setText(str(transp_val))
            except ValueError:
                pass

            try:
                angle_val = int(settings.get('angle', '45'))
                self.angle_slider.setValue(angle_val)
                self.angle_val_lbl.setText(str(angle_val))
            except ValueError:
                pass

            try:
                rgb_str = settings.get('color_rgb', '0,0,0')
                self.text_color = tuple(map(int, rgb_str.split(',')))
                self.color_hex = settings.get('color_hex', '#000000')
                self.color_hex_btn.setText(self.color_hex)
                self.update_color_swatch_style()
            except (ValueError, IndexError):
                self.text_color = (0, 0, 0)
                self.color_hex = '#000000'

            font_name_to_load = settings.get('font_name')
            if font_name_to_load and self.fonts:
                for i, font_item in enumerate(self.fonts):
                    if font_item[0].lower() == font_name_to_load.lower():
                        self.font_list.setCurrentRow(i)
                        self.font_selected = self.fonts[i]
                        break

        if 'Paths' in config:
            paths = config['Paths']
            last_image = paths.get('last_image', self.display_image_path)
            if os.path.exists(last_image):
                self.display_image_path = last_image
            self.save_dir = paths.get('last_save_dir', self.save_dir)
            self.root_dir = paths.get('last_open_dir', self.root_dir)

        self.updating_controls = False

    def closeEvent(self, event):
        """Handles window closing event to save preferences."""
        self.save_preferences()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = WatermarkerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
