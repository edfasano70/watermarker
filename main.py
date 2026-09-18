"""
WaterMarker - Implementación PyQt6
Una aplicación de escritorio moderna para aplicar marcas de agua de texto a imágenes.
"""

import sys
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageFont, ImageDraw

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QSlider, QPushButton, QToolButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QFileDialog,
    QColorDialog, QMessageBox, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QIcon, QPixmap, QImage, QFont, QAction, QColor, QCursor, QFontDatabase
from PyQt6.QtCore import Qt, QSize

# **** PATHS & CONSTANTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'watermarker')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.xml')
os.makedirs(CONFIG_DIR, exist_ok=True)
PROGRAM_NAME = 'WaterMarker'
PROGRAM_VERSION = '1.4.0'
PROGRAM_DESCRIPTION = 'Aplica marcas de agua de texto\nde forma sencilla\n\nPrograma por @edfasano70'


class AboutDialog(QDialog):
    """Diálogo modal que muestra información de la aplicación."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de")
        self.setFixedSize(300, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog { border: none; }
            QLabel { border: none; background: transparent; }
        """)

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
        close_btn = QPushButton("Cerrar")
        close_btn.setFixedWidth(90)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


class HelpDialog(QDialog):
    """Diálogo modal que muestra ayuda e instrucciones de la aplicación."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayuda - WaterMarker")
        self.setFixedSize(390, 340)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        logo_path = os.path.join(RESOURCES_DIR, 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Cómo usar WaterMarker")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        instructions = (
            "1. Abre una imagen usando <b>Archivo &rarr; Abrir</b>.<br>"
            "2. Escribe tu texto de marca de agua en el campo <b>Texto</b>.<br>"
            "3. Elige una fuente de la lista <b>Fuente</b>.<br>"
            "4. Ajusta <b>Tamaño</b>, <b>Transparencia</b> y <b>Ángulo</b> usando los controles deslizantes o los botones +/-.<br>"
            "5. Haz clic en el cuadro de <b>Color</b> para elegir un color de texto.<br>"
            "6. Guarda tu imagen con marca de agua usando <b>Archivo &rarr; Guardar</b>.<br><br>"
            "<i>Las preferencias y carpetas recientes se guardan automáticamente al salir.</i>"
        )
        text_label = QLabel(instructions)
        text_label.setFont(QFont("Arial", 9))
        text_label.setWordWrap(True)
        layout.addWidget(text_label)

        layout.addStretch()

        close_btn = QPushButton("Cerrar")
        close_btn.setFixedWidth(90)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)


class FontSelectionDialog(QDialog):
    def __init__(self, current_font='', parent=None):
        super().__init__(parent)
        self.setWindowTitle('Seleccionar fuente')
        self.setModal(True)
        self.setMinimumSize(500, 500)
        self.selected_font = current_font
        self._build_font_ui()

    def _build_font_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Buscar:'))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText('Escriba para filtrar...')
        self.filter_input.textChanged.connect(self._filter_fonts)
        filter_layout.addWidget(self.filter_input)
        layout.addLayout(filter_layout)

        self.preview_label = QLabel('Vista previa')
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(60)
        self.preview_label.setStyleSheet('border: 1px solid gray; padding: 10px; font-size: 24px;')
        layout.addWidget(self.preview_label)

        self.font_list = QListWidget()
        self.font_list.setAlternatingRowColors(True)
        self.font_list.setSpacing(2)
        self.font_list.currentItemChanged.connect(self._on_font_changed)
        
        fonts = QFontDatabase.families()
        self.font_data = {}
        for fname in fonts:
            item = QListWidgetItem(fname)
            try:
                qf = QFont(fname)
                qf.setPointSize(14)
                item.setFont(qf)
            except Exception:
                pass
            self.font_list.addItem(item)
            self.font_data[fname] = fname

        for i in range(self.font_list.count()):
            if self.font_list.item(i).text() == self.selected_font:
                self.font_list.setCurrentRow(i)
                break

        layout.addWidget(self.font_list)

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton('Aceptar')
        btn_cancel = QPushButton('Cancelar')
        btn_ok.clicked.connect(self._accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _filter_fonts(self, text):
        text_lower = text.lower()
        for i in range(self.font_list.count()):
            item = self.font_list.item(i)
            item.setHidden(text_lower not in item.text().lower())

    def _on_font_changed(self, current, _prev):
        if current:
            fname = current.text()
            try:
                self.preview_label.setFont(QFont(fname, 24))
            except Exception:
                self.preview_label.setFont(QFont('serif', 24))
            self.selected_font = fname

    def _accept(self):
        self.hide()
        self.done(QDialog.DialogCode.Accepted)

    def get_selected_font(self):
        return self.selected_font


class WatermarkerApp(QMainWindow):
    """Ventana principal de la aplicación usando PyQt6."""

    DARK_STYLE = """
        QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
        QMenuBar { background-color: #2d2d2d; color: #e0e0e0; }
        QMenuBar::item:selected { background-color: #3d3d3d; }
        QMenu { background-color: #2d2d2d; color: #e0e0e0; }
        QMenu::item:selected { background-color: #FF9800; color: #1e1e1e; }
        QLabel { color: #e0e0e0; border: none; }
        QLineEdit { background-color: #3d3d3d; color: #e0e0e0; border: 1px solid #555; border-radius: 3px; padding: 4px; }
        QListWidget { background-color: #3d3d3d; color: #e0e0e0; border: 1px solid #555; }
        QListWidget::item:selected { background-color: #FF9800; color: #1e1e1e; }
        QSlider::groove:horizontal { background: #555; height: 6px; border-radius: 3px; }
        QSlider::handle:horizontal { background: #FF9800; width: 14px; margin: -4px 0; border-radius: 7px; }
        QToolButton { background-color: #3d3d3d; border: 1px solid #555; border-radius: 3px; }
        QToolButton:hover { background-color: #4d4d4d; }
        QPushButton { background-color: #3d3d3d; border: 1px solid #555; border-radius: 3px; padding: 4px 8px; }
        QPushButton:hover { background-color: #4d4d4d; }
        QFrame { border: none; }
        QMenuBar::item { padding: 4px 8px; }
    """

    LIGHT_STYLE = ""

    def __init__(self):
        super().__init__()
        self.root_dir = BASE_DIR
        self.save_dir = BASE_DIR
        self.display_image_path = os.path.join(RESOURCES_DIR, 'checkers.png')
        self.text_color = (0, 0, 0)
        self.color_hex = "#000000"
        self.updating_controls = False
        self.dark_mode = False

        self.init_fonts()
        self.init_ui()
        self.load_preferences()
        self.refresh()
        self.center_window()

    def init_fonts(self):
        """Discovers system fonts using QFontDatabase."""
        fonts = QFontDatabase.families()
        self.fonts = []
        for font_name in fonts:
            self.fonts.append((font_name, font_name))

        self.fonts.sort(key=lambda x: x[0])
        if not self.fonts:
            self.fonts.append(("Default", ""))
        self.font_selected = self.fonts[0]

    def init_ui(self):
        """Construye la interfaz de usuario PyQt6."""
        self.setWindowTitle(PROGRAM_NAME)
        logo_path = os.path.join(RESOURCES_DIR, 'logo.png')
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Barra de Menú
        menu_bar = self.menuBar()

        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")
        open_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'open.svg'))
        open_action = QAction(open_icon, "Abrir", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'save.svg'))
        save_action = QAction(save_icon, "Guardar", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'exit.svg'))
        exit_action = QAction(exit_icon, "Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú Ver (antes de Ayuda)
        view_menu = menu_bar.addMenu("Ver")
        toggle_mode_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'toggle_mode.svg'))
        self.dark_mode_action = QAction(toggle_mode_icon, "Alternar Modo Oscuro/Claro", self)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        # Menú Presets
        presets_menu = menu_bar.addMenu("Presets")
        
        save_preset_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'save_preset.svg'))
        save_preset_action = QAction(save_preset_icon, "Guardar Preset", self)
        save_preset_action.setShortcut("Ctrl+Shift+S")
        save_preset_action.triggered.connect(self.save_preset)
        presets_menu.addAction(save_preset_action)
        
        load_preset_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'load_preset.svg'))
        load_preset_action = QAction(load_preset_icon, "Cargar Preset", self)
        load_preset_action.setShortcut("Ctrl+Shift+O")
        load_preset_action.triggered.connect(self.load_preset)
        presets_menu.addAction(load_preset_action)

        # Menú Ayuda
        help_menu = menu_bar.addMenu("Ayuda")
        help_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'help.svg'))
        help_action = QAction(help_icon, "Ayuda", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_icon = QIcon(os.path.join(RESOURCES_DIR, 'icons', 'about.svg'))
        about_action = QAction(about_icon, "Acerca de", self)
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
        text_lbl = QLabel("Texto")
        self.text_entry = QLineEdit("El Zorro Peregroso")
        self.text_entry.textChanged.connect(self.on_text_changed)
        controls_layout.addWidget(text_lbl, 0, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.text_entry, 0, 1)

        # 2. Font Selection Button
        font_lbl = QLabel("Fuente")
        self.font_button = QPushButton(self.font_selected[0] if self.font_selected else "Seleccionar fuente")
        self.font_button.clicked.connect(self.open_font_dialog)
        controls_layout.addWidget(font_lbl, 1, 0, Qt.AlignmentFlag.AlignRight)
        controls_layout.addWidget(self.font_button, 1, 1)

        # Icons
        minus_icon_path = os.path.join(RESOURCES_DIR, 'icon_minus.png')
        plus_icon_path = os.path.join(RESOURCES_DIR, 'icon_plus.png')
        minus_icon = QIcon(minus_icon_path) if os.path.exists(minus_icon_path) else QIcon()
        plus_icon = QIcon(plus_icon_path) if os.path.exists(plus_icon_path) else QIcon()

        # 3. Size Control (Slider + Buttons)
        size_lbl = QLabel("Tamaño")
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
        transp_lbl = QLabel("Transparencia")
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
        angle_lbl = QLabel("Ángulo")
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

        # 7. Tiled Mode Checkbox
        from PyQt6.QtWidgets import QCheckBox
        self.tiled_checkbox = QCheckBox("Marca de agua repetida (tiled)")
        self.tiled_checkbox.stateChanged.connect(self.on_tiled_changed)
        controls_layout.addWidget(self.tiled_checkbox, 6, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(controls_widget, 0, Qt.AlignmentFlag.AlignTop)

        # Image Display Area (Right)
        self.image_display_label = QLabel()
        self.image_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_display_label, 1)

        # Status Bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Listo")

    def update_color_swatch_style(self):
        """Updates the color swatch background and border."""
        self.color_swatch.setStyleSheet(
            f"background-color: {self.color_hex}; border: 1px solid #777; border-radius: 3px;"
        )

    def toggle_dark_mode(self):
        """Alterna entre modo oscuro y claro."""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(self.DARK_STYLE)
        else:
            self.setStyleSheet(self.LIGHT_STYLE)

    def on_tiled_changed(self, state):
        """Maneja el cambio del checkbox de modo tiled."""
        self.refresh()

    def on_text_changed(self, text):
        self.refresh()

    def open_font_dialog(self):
        dlg = FontSelectionDialog(current_font=self.font_selected[0], parent=self)
        if dlg.exec():
            font_name = dlg.get_selected_font()
            for i, font_item in enumerate(self.fonts):
                if font_item[0].lower() == font_name.lower():
                    self.font_selected = self.fonts[i]
                    self.font_button.setText(font_name)
                    self.refresh()
                    break

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
        """Abre el diálogo de QColorDialog para seleccionar el color de la marca de agua."""
        initial = QColor(self.color_hex)
        chosen = QColorDialog.getColor(initial, self, "Seleccionar Color")
        if chosen.isValid():
            self.text_color = (chosen.red(), chosen.green(), chosen.blue())
            self.color_hex = chosen.name()
            self.color_hex_btn.setText(self.color_hex)
            self.update_color_swatch_style()
            self.refresh()

    def open_image(self):
        """Abre un diálogo de selección de archivo de imagen."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo de Imagen",
            self.root_dir,
            "Archivos de Imagen (*.png *.jpg *.jpeg *.gif);;Todos los Archivos (*)"
        )
        if file_path:
            self.display_image_path = file_path
            self.root_dir = os.path.dirname(file_path)
            self.refresh()
            self.center_window()

    def save_image(self):
        """Guarda la imagen con marca de agua en la ruta seleccionada por el usuario."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Guardar Imagen",
            os.path.join(self.save_dir, "marcadeagua.png"),
            "Imagen PNG (*.png);;Imagen JPEG (*.jpg);;Todos los Archivos (*)"
        )
        if file_path:
            temp_out = os.path.join(TMP_DIR, 'out.png')
            if os.path.exists(temp_out):
                try:
                    img = Image.open(temp_out)
                    
                    # Si es JPEG, convertir a RGB (sin transparencia)
                    if file_path.lower().endswith(('.jpg', '.jpeg')):
                        if img.mode == 'RGBA':
                            # Crear fondo blanco
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[3])
                            img = background
                        else:
                            img = img.convert('RGB')
                    
                    img.save(file_path)
                    self.save_dir = os.path.dirname(file_path)
                    QMessageBox.information(self, "Info", "Imagen guardada exitosamente")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar la imagen: {str(e)}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo encontrar la imagen con marca de agua.")

    def save_preset(self):
        """Guarda la configuración actual como un preset."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Preset",
            os.path.join(CONFIG_DIR, "preset.xml"),
            "Archivos de Preset (*.xml);;Todos los Archivos (*)"
        )
        if file_path:
            try:
                root = ET.Element('preset')
                ET.SubElement(root, 'text').text = self.text_entry.text()
                ET.SubElement(root, 'font_name').text = self.font_selected[0] if self.font_selected else ''
                ET.SubElement(root, 'font_size').text = str(self.size_slider.value())
                ET.SubElement(root, 'transparency').text = str(self.transp_slider.value())
                ET.SubElement(root, 'angle').text = str(self.angle_slider.value())
                tc = ET.SubElement(root, 'text_color')
                tc.set('r', str(self.text_color[0]))
                tc.set('g', str(self.text_color[1]))
                tc.set('b', str(self.text_color[2]))
                ET.SubElement(root, 'color_hex').text = self.color_hex
                ET.SubElement(root, 'tiled').text = str(self.tiled_checkbox.isChecked()).lower()
                tree = ET.ElementTree(root)
                ET.indent(tree, space='  ')
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
                QMessageBox.information(self, "Info", "Preset guardado exitosamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el preset: {str(e)}")

    def load_preset(self):
        """Carga un preset desde un archivo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar Preset",
            CONFIG_DIR,
            "Archivos de Preset (*.xml);;Todos los Archivos (*)"
        )
        if file_path:
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                text = root.findtext('text')
                if text is not None:
                    self.text_entry.setText(text)
                
                font_name = root.findtext('font_name')
                if font_name and self.fonts:
                    for i, font_item in enumerate(self.fonts):
                        if font_item[0].lower() == font_name.lower():
                            self.font_selected = self.fonts[i]
                            self.font_button.setText(font_name)
                            break
                
                font_size = root.findtext('font_size')
                if font_size is not None:
                    self.size_slider.setValue(int(font_size))
                
                transparency = root.findtext('transparency')
                if transparency is not None:
                    self.transp_slider.setValue(int(transparency))
                
                angle = root.findtext('angle')
                if angle is not None:
                    self.angle_slider.setValue(int(angle))
                
                tc = root.find('text_color')
                if tc is not None and tc.get('r') is not None:
                    self.text_color = (int(tc.get('r')), int(tc.get('g')), int(tc.get('b')))
                    self.update_color_swatch_style()
                
                color_hex = root.findtext('color_hex')
                if color_hex is not None:
                    self.color_hex = color_hex
                    self.color_hex_btn.setText(color_hex)
                    self.update_color_swatch_style()
                
                tiled = root.findtext('tiled')
                if tiled is not None:
                    self.tiled_checkbox.setChecked(tiled.lower() == 'true')
                
                self.refresh()
                QMessageBox.information(self, "Info", "Preset cargado exitosamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el preset: {str(e)}")

    def show_about(self):
        """Muestra el diálogo modal Acerca de."""
        dialog = AboutDialog(self)
        dialog.exec()

    def show_help(self):
        """Muestra el diálogo modal de Ayuda."""
        dialog = HelpDialog(self)
        dialog.exec()

    def refresh(self):
        """Renderiza la vista previa con marca de agua."""
        if not os.path.exists(self.display_image_path):
            return

        try:
            base_image = Image.open(self.display_image_path).convert("RGBA")
            # Update status bar with image info
            img_width, img_height = base_image.size
            file_name = os.path.basename(self.display_image_path)
            file_size = os.path.getsize(self.display_image_path)
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
            self.status_bar.showMessage(f"{file_name} | {img_width}x{img_height} px | {size_str}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir la imagen:\n{e}")
            return

        # Keep preview within 600x600 px
        width, height = base_image.size
        if width > 600 or height > 600:
            base_image.thumbnail((600, 600))
            width, height = base_image.size

        text_layer = Image.new('RGBA', base_image.size, (255, 255, 255, 0))

        font_size = self.size_slider.value()
        font_name = self.font_selected[0] if self.font_selected else None
        if font_name:
            try:
                # Try to find the font file using fc-match
                result = subprocess.run(
                    ['fc-match', '-f', '%{file}', font_name],
                    capture_output=True, text=True, timeout=5
                )
                font_path = result.stdout.strip()
                if font_path and os.path.isfile(font_path):
                    font_obj = ImageFont.truetype(font_path, font_size)
                else:
                    font_obj = ImageFont.load_default()
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
            
            fill_color = (
                self.text_color[0],
                self.text_color[1],
                self.text_color[2],
                self.transp_slider.value()
            )
            
            if self.tiled_checkbox.isChecked():
                # Tiled mode: repeat watermark across the image
                spacing_x = text_width + 100
                spacing_y = text_height + 100
                
                for y_pos in range(-height, height * 2, spacing_y):
                    for x_pos in range(-width, width * 2, spacing_x):
                        draw.text((x_pos, y_pos), text, fill=fill_color, font=font_obj)
            else:
                # Single watermark mode
                x = (width - text_width) / 2 - bbox[0]
                y = (height - text_height) / 2 - bbox[1]
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
        """Centra la ventana en la pantalla principal."""
        self.adjustSize()
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            win_geo = self.frameGeometry()
            win_geo.moveCenter(screen_geo.center())
            self.move(win_geo.topLeft())

    def save_preferences(self):
        """Guarda la configuración actual en el archivo XML."""
        root = ET.Element('watermarker')

        settings = ET.SubElement(root, 'settings')
        ET.SubElement(settings, 'text').text = self.text_entry.text()
        ET.SubElement(settings, 'font_name').text = self.font_selected[0] if self.font_selected else ''
        ET.SubElement(settings, 'font_size').text = str(self.size_slider.value())
        ET.SubElement(settings, 'transparency').text = str(self.transp_slider.value())
        ET.SubElement(settings, 'angle').text = str(self.angle_slider.value())
        ET.SubElement(settings, 'color_rgb').text = ','.join(map(str, self.text_color))
        ET.SubElement(settings, 'color_hex').text = self.color_hex
        ET.SubElement(settings, 'dark_mode').text = str(self.dark_mode).lower()
        ET.SubElement(settings, 'tiled').text = str(self.tiled_checkbox.isChecked()).lower()

        paths = ET.SubElement(root, 'paths')
        ET.SubElement(paths, 'last_image').text = self.display_image_path
        ET.SubElement(paths, 'last_save_dir').text = self.save_dir
        ET.SubElement(paths, 'last_open_dir').text = self.root_dir

        tree = ET.ElementTree(root)
        try:
            tree.write(CONFIG_FILE, encoding='utf-8', xml_declaration=True)
        except IOError as e:
            print(f"Error al guardar preferencias: {e}")

    def load_preferences(self):
        """Carga la configuración desde el archivo XML."""
        if not os.path.exists(CONFIG_FILE):
            return

        try:
            tree = ET.parse(CONFIG_FILE)
            root = tree.getroot()
        except ET.ParseError:
            return

        self.updating_controls = True

        settings = root.find('settings')
        if settings is not None:
            text_elem = settings.find('text')
            if text_elem is not None and text_elem.text:
                self.text_entry.setText(text_elem.text)

            font_size_elem = settings.find('font_size')
            if font_size_elem is not None:
                try:
                    size_val = int(font_size_elem.text)
                    self.size_slider.setValue(size_val)
                    self.size_val_lbl.setText(str(size_val))
                except (ValueError, TypeError):
                    pass

            transparency_elem = settings.find('transparency')
            if transparency_elem is not None:
                try:
                    transp_val = int(transparency_elem.text)
                    self.transp_slider.setValue(transp_val)
                    self.transp_val_lbl.setText(str(transp_val))
                except (ValueError, TypeError):
                    pass

            angle_elem = settings.find('angle')
            if angle_elem is not None:
                try:
                    angle_val = int(angle_elem.text)
                    self.angle_slider.setValue(angle_val)
                    self.angle_val_lbl.setText(str(angle_val))
                except (ValueError, TypeError):
                    pass

            color_rgb_elem = settings.find('color_rgb')
            color_hex_elem = settings.find('color_hex')
            if color_rgb_elem is not None:
                try:
                    self.text_color = tuple(map(int, color_rgb_elem.text.split(',')))
                except (ValueError, IndexError, TypeError):
                    self.text_color = (0, 0, 0)
            if color_hex_elem is not None and color_hex_elem.text:
                self.color_hex = color_hex_elem.text
            else:
                self.color_hex = '#000000'
            self.color_hex_btn.setText(self.color_hex)
            self.update_color_swatch_style()

            font_name_elem = settings.find('font_name')
            if font_name_elem is not None and font_name_elem.text and self.fonts:
                font_name_to_load = font_name_elem.text
                for i, font_item in enumerate(self.fonts):
                    if font_item[0].lower() == font_name_to_load.lower():
                        self.font_selected = self.fonts[i]
                        self.font_button.setText(font_name_to_load)
                        break

            dark_mode_elem = settings.find('dark_mode')
            if dark_mode_elem is not None and dark_mode_elem.text:
                self.dark_mode = dark_mode_elem.text.lower() == 'true'
                if self.dark_mode:
                    self.setStyleSheet(self.DARK_STYLE)

            tiled_elem = settings.find('tiled')
            if tiled_elem is not None and tiled_elem.text:
                self.tiled_checkbox.setChecked(tiled_elem.text.lower() == 'true')

        paths = root.find('paths')
        if paths is not None:
            last_image_elem = paths.find('last_image')
            if last_image_elem is not None and last_image_elem.text:
                last_image = last_image_elem.text
                if os.path.exists(last_image):
                    self.display_image_path = last_image

            last_save_dir_elem = paths.find('last_save_dir')
            if last_save_dir_elem is not None and last_save_dir_elem.text:
                self.save_dir = last_save_dir_elem.text

            last_open_dir_elem = paths.find('last_open_dir')
            if last_open_dir_elem is not None and last_open_dir_elem.text:
                self.root_dir = last_open_dir_elem.text

        self.updating_controls = False

    def closeEvent(self, event):
        """Maneja el evento de cierre de ventana para guardar preferencias."""
        self.save_preferences()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = WatermarkerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
