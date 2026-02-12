import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenu,
    QMessageBox, QFileDialog, QVBoxLayout,
    QCheckBox, QDoubleSpinBox, QLabel, QComboBox, QWidget, QRadioButton, QButtonGroup
)
from PySide6.QtGui import QFontDatabase, QTextCursor, QDoubleValidator
from PySide6.QtCore import Qt, QPointF, QTimer

# Import Custom Widget & Utils
from gui import Ui_MainWindow
from icon_dialog import IconPickerDialog
from preview_widget import PreviewWidget
from version import version
from fontTools.ttLib import TTFont 
from utils import (
    generate_kicad_sexpr, 
    generate_polygons_logic, 
    scale_polys_to_target_height, 
    apply_anchor_point, 
    sanitize_font_key
)

SYMBOL_MAP = {
    ":gnd:": "\u23DA", ":ohm:": "\u03A9", ":mu:": "\u00B5", ":warn:": "\u26A0",
    ":l:": "\u2190", ":r:": "\u2192", ":u:": "\u2191", ":d:": "\u2193"
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(f"Text Label Generator v{version}")
        
        self.app_ready = False 
        self.circular_ratio = 0.5 

        # =========================================================================
        # 1. SETUP PREVIEW WIDGET
        # =========================================================================
        self.canvas = PreviewWidget()
        layout = QVBoxLayout(self.ui.groupBoxPreview)
        layout.setContentsMargins(10, 25, 10, 10) 
        layout.addWidget(self.canvas)

        # =========================================================================
        # 2. DATA & TIMERS (PHẦN BỊ THIẾU ĐÃ ĐƯỢC THÊM LẠI)
        # =========================================================================
        self.font_library = {}
        self.symbol_font_list = []
        self.current_polys = []

        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(200) 
        self.preview_timer.timeout.connect(self.render_preview_worker)

        # =========================================================================
        # 3. SETUP UI ELEMENTS
        # =========================================================================
        
        # --- Height ComboBox ---
        self.ui.gridLayout_4.removeWidget(self.ui.doubleSpinHeight)
        self.ui.doubleSpinHeight.deleteLater()
        self.ui.doubleSpinHeight = None 

        self.comboHeight = QComboBox()
        self.comboHeight.setEditable(True)
        self.comboHeight.setValidator(QDoubleValidator(0.1, 1000.0, 2))
        self.comboHeight.addItems(["0.8", "1.0", "1.2", "1.5", "2.0", "2.5", "3.0", "4.0", "5.0", "6.0", "8.0", "10.0"])
        self.comboHeight.setCurrentText("5.0")
        self.ui.gridLayout_4.addWidget(self.comboHeight, 1, 1)

        # --- Standard Comboboxes ---
        AlignmentFields = ["Left", "Center", "Right"]
        EdgeFields = ["Square", "Round", "Triangle", "Pointed", "Ribbon_Out", "Ribbon_In", "Trap_Left", "Trap_Right"]
        LayerFields = ["F.SilkS", "F.Paste" , "F.Mask", "F.Cu", "F.Cu/F.Mask", "B.SilkS", "B.Paste" , "B.Mask", "B.Cu", "B.Cu/B.Mask"]
        AnchorFields = ["Top-Left", "Top-Center", "Top-Right", "Center-Left", "Center-Center", "Center-Right", "Bottom-Left", "Bottom-Center", "Bottom-Right"]
        
        self.ui.comboAlignment.addItems(AlignmentFields)
        self.ui.comboLeftEdge.addItems(EdgeFields)
        self.ui.comboRightEdge.addItems(EdgeFields)
        self.ui.comboLayer.addItems(LayerFields)
        self.ui.comboAnchor.addItems(AnchorFields)
        
        self.ui.comboAlignment.setCurrentText("Center")
        self.ui.comboLeftEdge.setCurrentText("Square")
        self.ui.comboRightEdge.setCurrentText("Square")
        self.ui.comboLayer.setCurrentText("F.SilkS")
        self.ui.comboAnchor.setCurrentText("Center-Center")
        self.ui.labelFontDir.setWordWrap(True)
        
        # --- CIRCULAR MODE UI ---
        self.checkCircular = QCheckBox("Circular Text Mode (Curve)")
        self.ui.gridLayout_4.addWidget(self.checkCircular, 7, 0, 1, 2)

        self.labelRadius = QLabel("Radius (mm):")
        self.spinRadius = QDoubleSpinBox()
        self.spinRadius.setRange(1.0, 1000.0)
        self.spinRadius.setValue(10.0)
        self.ui.gridLayout_4.addWidget(self.labelRadius, 8, 0)
        self.ui.gridLayout_4.addWidget(self.spinRadius, 8, 1)

        # --- Start Angle vs Alignment Angle ---
        self.radioStart = QRadioButton("Start Angle:")
        self.spinStartAngle = QDoubleSpinBox()
        self.spinStartAngle.setRange(-360.0, 360.0)
        self.spinStartAngle.setValue(-90.0) 
        self.spinStartAngle.setSuffix(" °")
        self.ui.gridLayout_4.addWidget(self.radioStart, 9, 0)
        self.ui.gridLayout_4.addWidget(self.spinStartAngle, 9, 1)

        self.radioAlign = QRadioButton("Align Angle:")
        self.spinAlignAngle = QDoubleSpinBox()
        self.spinAlignAngle.setRange(-360.0, 360.0)
        self.spinAlignAngle.setValue(90.0) 
        self.spinAlignAngle.setSuffix(" °")
        self.ui.gridLayout_4.addWidget(self.radioAlign, 10, 0)
        self.ui.gridLayout_4.addWidget(self.spinAlignAngle, 10, 1)

        self.angleGroup = QButtonGroup(self)
        self.angleGroup.addButton(self.radioStart)
        self.angleGroup.addButton(self.radioAlign)

        # Presets
        self.labelPreset = QLabel("Quick Preset:")
        self.comboAnglePreset = QComboBox()
        self.comboAnglePreset.addItems(["Custom", "Top (12h)", "Bottom (6h)", "Left (9h)", "Right (3h)"])
        self.comboAnglePreset.setCurrentText("Custom")
        self.ui.gridLayout_4.addWidget(self.labelPreset, 11, 0)
        self.ui.gridLayout_4.addWidget(self.comboAnglePreset, 11, 1)

        # --- TOTAL ANGLE FIT ---
        self.checkFitAngle = QCheckBox("Fit to Total Angle:")
        self.spinTotalAngle = QDoubleSpinBox()
        self.spinTotalAngle.setRange(1.0, 360.0)
        self.spinTotalAngle.setValue(180.0)
        self.spinTotalAngle.setSuffix(" °")
        
        self.ui.gridLayout_4.addWidget(self.checkFitAngle, 12, 0)
        self.ui.gridLayout_4.addWidget(self.spinTotalAngle, 12, 1)
        
        # Disable states initialization
        self.spinRadius.setEnabled(False)
        self.radioStart.setEnabled(False)
        self.spinStartAngle.setEnabled(False)
        self.radioAlign.setEnabled(False)
        self.spinAlignAngle.setEnabled(False)
        self.comboAnglePreset.setEnabled(False)
        self.checkFitAngle.setEnabled(False)
        self.spinTotalAngle.setEnabled(False)

        # =========================================================================
        # 4. LOAD FONTS
        # =========================================================================
        self.load_text_fonts(os.path.join("fonts", "texts"))
        self.scan_symbol_fonts(os.path.join("fonts", "symbols"))

        initial_text = "Text Label"
        if self.ui.comboFont.count() > 0:
            data = self.ui.comboFont.itemData(0)
            if data:
                _, key = data
                initial_text = f"{{{key}}}Text Label{{/{key}}}"
        
        self.ui.plainTextEdit.setPlainText(initial_text)

        # =========================================================================
        # 5. SIGNALS
        # =========================================================================
        self.ui.buttonCopy.clicked.connect(self.button_copy_clicked)
        self.ui.buttonSave.clicked.connect(self.button_save_clicked)
        self.ui.buttonClose.clicked.connect(self.button_close_clicked)
        self.ui.buttonIcon.clicked.connect(self.button_icon_clicked)
        self.ui.buttonSymbol.clicked.connect(self.button_symbol_clicked)
        self.ui.buttonClear.clicked.connect(self.button_clear_clicked)

        self.ui.plainTextEdit.textChanged.connect(self.trigger_refresh) 
        
        self.ui.checkNegative.toggled.connect(self.update_ui_states)
        self.ui.checkNoFrame.toggled.connect(self.update_ui_states)
        self.ui.checkNegative.toggled.connect(self.trigger_refresh)
        self.ui.checkNoFrame.toggled.connect(self.trigger_refresh)
        
        self.ui.comboLeftEdge.currentIndexChanged.connect(self.trigger_refresh)
        self.ui.comboRightEdge.currentIndexChanged.connect(self.trigger_refresh)
        self.ui.comboLayer.currentIndexChanged.connect(self.trigger_refresh)
        self.ui.comboAnchor.currentIndexChanged.connect(self.trigger_refresh)

        self.radioStart.toggled.connect(self.on_angle_mode_changed)
        self.radioAlign.toggled.connect(self.on_angle_mode_changed)
        self.ui.comboAlignment.currentIndexChanged.connect(self.on_alignment_combo_changed)

        self.checkCircular.toggled.connect(self.toggle_circular_mode)
        self.checkCircular.toggled.connect(self.trigger_refresh)
        self.spinRadius.valueChanged.connect(self.trigger_refresh)
        self.spinStartAngle.valueChanged.connect(self.trigger_refresh)
        self.spinAlignAngle.valueChanged.connect(self.trigger_refresh)
        self.comboAnglePreset.currentIndexChanged.connect(self.on_angle_preset_changed)
        
        # Signals for Fit Angle
        self.checkFitAngle.toggled.connect(self.on_fit_angle_toggled)
        self.checkFitAngle.toggled.connect(self.trigger_refresh)
        self.spinTotalAngle.valueChanged.connect(self.trigger_refresh)

        self.spinStartAngle.valueChanged.connect(self.on_manual_angle_change)
        self.spinAlignAngle.valueChanged.connect(self.on_manual_angle_change)

        self.spinRadius.valueChanged.connect(self.on_radius_changed)
        self.comboHeight.editTextChanged.connect(self.on_height_changed)
        self.comboHeight.currentIndexChanged.connect(self.trigger_refresh)
        self.comboHeight.editTextChanged.connect(self.trigger_refresh)

        self.ui.comboFont.currentIndexChanged.connect(self.on_font_changed) 
        
        for spin in [self.ui.doubleSpinSpacing, self.ui.doubleSpinBorder, self.ui.doubleSpinCorner,
                     self.ui.doubleSpinTop, self.ui.doubleSpinBottom,
                     self.ui.doubleSpinLeft, self.ui.doubleSpinRight]:
            spin.valueChanged.connect(self.trigger_refresh)

        # =========================================================================
        # 6. INIT
        # =========================================================================
        self.update_ui_states() 
        
        if self.ui.comboFont.count() > 0:
            self.ui.comboFont.setCurrentIndex(0)
            data = self.ui.comboFont.itemData(0)
            if data:
                _, key = data
                if key in self.font_library:
                    self.font_library['default'] = self.font_library[key]
        
        self.on_alignment_combo_changed()
        self.trigger_refresh()
        self.app_ready = True

    def get_current_height(self):
        try: return float(self.comboHeight.currentText())
        except ValueError: return 5.0

    def on_angle_mode_changed(self):
        is_start = self.radioStart.isChecked()
        self.spinStartAngle.setEnabled(is_start)
        self.spinAlignAngle.setEnabled(not is_start)
        
        if self.app_ready:
            current_align = self.ui.comboAlignment.currentText()
            if is_start and current_align != "Left":
                self.ui.comboAlignment.setCurrentText("Left")
            elif not is_start and current_align == "Left":
                self.ui.comboAlignment.setCurrentText("Center")
        self.trigger_refresh()

    def on_alignment_combo_changed(self):
        align = self.ui.comboAlignment.currentText()
        if align == "Left": self.radioStart.setChecked(True)
        else: self.radioAlign.setChecked(True)
        self.trigger_refresh()

    def on_fit_angle_toggled(self, checked):
        self.spinTotalAngle.setEnabled(checked)

    def on_angle_preset_changed(self):
        txt = self.comboAnglePreset.currentText()
        val = None
        if "Top" in txt: val = -90.0
        elif "Bottom" in txt: val = 90.0
        elif "Left" in txt: val = 180.0
        elif "Right" in txt: val = 0.0
        
        if val is not None:
            target_spin = self.spinStartAngle if self.radioStart.isChecked() else self.spinAlignAngle
            target_spin.blockSignals(True)
            target_spin.setValue(val)
            target_spin.blockSignals(False)
            self.trigger_refresh()

    def on_manual_angle_change(self):
        if self.comboAnglePreset.currentText() != "Custom":
            self.comboAnglePreset.blockSignals(True)
            self.comboAnglePreset.setCurrentText("Custom")
            self.comboAnglePreset.blockSignals(False)

    def on_radius_changed(self, r_value):
        if self.checkCircular.isChecked():
            new_h = r_value * self.circular_ratio
            self.comboHeight.blockSignals(True)
            self.comboHeight.setEditText(f"{new_h:.2f}")
            self.comboHeight.blockSignals(False)

    def on_height_changed(self, text_val):
        if self.checkCircular.isChecked():
            try:
                h_value = float(text_val)
                r = self.spinRadius.value()
                if r > 0.1: self.circular_ratio = h_value / r
            except ValueError: pass

    def toggle_circular_mode(self, checked):
        self.spinRadius.setEnabled(checked)
        self.radioStart.setEnabled(checked)
        self.radioAlign.setEnabled(checked)
        self.comboAnglePreset.setEnabled(checked)
        self.checkFitAngle.setEnabled(checked)
        self.spinTotalAngle.setEnabled(checked and self.checkFitAngle.isChecked())
        
        self.on_angle_mode_changed()
        
        self.ui.groupBoxEdges.setEnabled(not checked)
        self.ui.checkNoFrame.setChecked(True if checked else False)
        self.ui.checkNoFrame.setEnabled(not checked)
        
        if checked:
            h = self.get_current_height()
            r = self.spinRadius.value()
            if r > 0.1: self.circular_ratio = h / r
            else: self.circular_ratio = 0.5

    def update_ui_states(self):
        if self.checkCircular.isChecked(): return

        is_neg = self.ui.checkNegative.isChecked()
        no_frame = self.ui.checkNoFrame.isChecked()
        self.ui.groupBoxEdges.setEnabled(not no_frame)
        self.ui.groupBoxPadding.setEnabled(not no_frame)
        self.ui.doubleSpinCorner.setEnabled(not no_frame)
        self.ui.checkNegative.setEnabled(not no_frame) 
        self.ui.doubleSpinBorder.setEnabled(not is_neg and not no_frame)

    def trigger_refresh(self):
        self.preview_timer.start()

    def load_text_fonts(self, folder_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, folder_path)
        self.ui.comboFont.clear()
        if not os.path.exists(abs_path): return
        files = sorted([f for f in os.listdir(abs_path) if f.lower().endswith(('.ttf', '.otf'))])
        for f in files:
            full_path = os.path.join(abs_path, f)
            QFontDatabase.addApplicationFont(full_path)
            font_key = sanitize_font_key(f)
            try:
                ttfont = TTFont(full_path)
                self.font_library[font_key] = (ttfont, full_path, 'text')
                self.ui.comboFont.addItem(f, (full_path, font_key))
            except Exception as e: print(f"Error loading font {f}: {e}")
        self.ui.labelFontDir.setText(f"Fonts loaded from: {os.path.dirname(abs_path)}")

    def scan_symbol_fonts(self, folder_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, folder_path)
        self.symbol_font_list = [] 
        if not os.path.exists(abs_path): return
        files = [f for f in os.listdir(abs_path) if f.lower().endswith(('.ttf', '.otf'))]
        files.sort()
        for filename in files:
            full_path = os.path.join(abs_path, filename)
            QFontDatabase.addApplicationFont(full_path)
            font_key = sanitize_font_key(filename)
            try:
                ttfont = TTFont(full_path)
                self.font_library[font_key] = (ttfont, full_path, 'symbol')
                self.symbol_font_list.append((filename, full_path, font_key))
            except Exception as e: print(f"Failed to load symbol font {filename}: {e}")

    def on_font_changed(self, index):
        if not self.app_ready: return
        data = self.ui.comboFont.itemData(index)
        if not data: return
        _, font_key = data
        if font_key in self.font_library: self.font_library['default'] = self.font_library[font_key]
        cursor = self.ui.plainTextEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        end_tag = f"{{/{font_key}}}"
        start_tag = f"{{{font_key}}}"
        cursor.insertText(start_tag + end_tag)
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(end_tag))
        self.ui.plainTextEdit.setTextCursor(cursor)
        self.ui.plainTextEdit.setFocus()
        self.trigger_refresh()

    def preprocess_text(self, text):
        processed = text
        for key, char in SYMBOL_MAP.items(): processed = processed.replace(key, char)
        return processed
    
    def button_copy_clicked(self):
        if not self.current_polys: return
        t = self.ui.plainTextEdit.toPlainText().strip()
        safe_text = "".join(c for c in (t.split('\n')[0] if t else "FP") if c.isalnum() or c in (' ', '_', '-')).strip()
        try:
            content = generate_kicad_sexpr(self.current_polys, f"tlg_{safe_text}", layer=self.ui.comboLayer.currentText())
            QApplication.clipboard().setText(content)
            self.ui.statusbar.showMessage(f"Footprint copied to clipboard")
        except Exception as e: self.ui.statusbar.showMessage(f"Error: {str(e)}")
    
    def button_save_clicked(self):
        if not self.current_polys: return
        t = self.ui.plainTextEdit.toPlainText().strip()
        safe_text = "".join(c for c in (t.split('\n')[0] if t else "FP") if c.isalnum() or c in (' ', '_', '-')).strip()
        path, _ = QFileDialog.getSaveFileName(self, "Save Footprint", f"tlg_{safe_text}.kicad_mod", "KiCad Footprint (*.kicad_mod)")
        if path:
            try:
                content = generate_kicad_sexpr(self.current_polys, f"tlg_{safe_text}", layer=self.ui.comboLayer.currentText())
                with open(path, "w", encoding="utf-8") as f: f.write(content)
                QMessageBox.information(self, "Success", f"Saved to: {path}")
            except Exception as e: QMessageBox.critical(self, "Error", str(e))
    
    def button_icon_clicked(self):
        dialog = IconPickerDialog(self.symbol_font_list, self)
        if dialog.exec(): 
            text_result = dialog.get_result()
            if text_result:
                self.ui.plainTextEdit.insertPlainText(text_result)
                self.ui.plainTextEdit.setFocus()
    
    def button_symbol_clicked(self):
        menu = QMenu(self)
        for k, v in SYMBOL_MAP.items():
            menu.addAction(f"{v} {k}").triggered.connect(lambda c, s=k: self.insert_symbol(s))
        menu.exec(self.ui.buttonSymbol.mapToGlobal(QPointF(0, self.ui.buttonSymbol.height()).toPoint()))

    def insert_symbol(self, symbol_key):
        self.ui.plainTextEdit.insertPlainText(symbol_key + " ")
        self.ui.plainTextEdit.setFocus()

    def button_clear_clicked(self):
        self.ui.plainTextEdit.setPlainText("")
        if not self.app_ready: return
        data = self.ui.comboFont.currentData()
        if not data: return
        _, font_key = data
        if font_key in self.font_library: self.font_library['default'] = self.font_library[font_key]
        cursor = self.ui.plainTextEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        start_tag = f"{{{font_key}}}"
        end_tag = f"{{/{font_key}}}"
        cursor.insertText(start_tag + end_tag)
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(end_tag))
        self.ui.plainTextEdit.setTextCursor(cursor)
        self.ui.plainTextEdit.setFocus()
        self.trigger_refresh()

    def button_close_clicked(self):
        self.close()
    
    def render_preview_worker(self):
        if 'default' not in self.font_library: return
        raw_text = self.ui.plainTextEdit.toPlainText()
        text = self.preprocess_text(raw_text) 
        
        try:
            current_height = self.get_current_height()
            
            if self.radioStart.isChecked():
                final_angle = self.spinStartAngle.value()
            else:
                final_angle = self.spinAlignAngle.value()

            raw_polys = generate_polygons_logic(
                text, 
                self.font_library, 
                'default',
                self.ui.doubleSpinTop.value(),
                self.ui.doubleSpinBottom.value(),
                self.ui.doubleSpinLeft.value(),
                self.ui.doubleSpinRight.value(),
                self.ui.comboAlignment.currentText(), 
                self.ui.comboLeftEdge.currentText(), 
                self.ui.comboRightEdge.currentText(), 
                self.ui.doubleSpinSpacing.value(), 
                self.ui.doubleSpinBorder.value(), 
                self.ui.doubleSpinCorner.value(), 
                self.ui.checkNegative.isChecked(),
                self.ui.checkNoFrame.isChecked(),
                is_circular=self.checkCircular.isChecked(),
                radius=self.spinRadius.value(),
                start_angle=final_angle,
                is_fit_angle=self.checkFitAngle.isChecked(),
                total_angle=self.spinTotalAngle.value()
            )
            
            scaled_polys = scale_polys_to_target_height(raw_polys, current_height)
            self.current_polys = apply_anchor_point(scaled_polys, self.ui.comboAnchor.currentText())
            
            layer_colors = { 
                "F.SilkS": "#F2EDA1", "F.Paste": "#B4A09A", "F.Mask": "#D864FF",
                "F.Cu": "#C83434", "F.Cu/F.Mask": "#D04C99",
                "B.SilkS": "#E8B2A7", "B.Paste": "#00C2C2", "B.Mask": "#02FFEE",
                "B.Cu": "#4D7FC4", "B.Cu/B.Mask": "#27BFD9" 
            }
            color = layer_colors.get(self.ui.comboLayer.currentText(), "#F5B041")

            if hasattr(self.canvas, 'update_content'):
                self.canvas.update_content(self.current_polys, color=color)
                
        except Exception as e: print(f"Render Error: {e}")