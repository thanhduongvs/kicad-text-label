import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QMessageBox, QFileDialog, QVBoxLayout
)
from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import Qt, QPointF

# Import Custom Widget & Utils
from gui import Ui_MainWindow
from icon_dialog import IconPickerDialog
from preview_widget import PreviewWidget
from version import version
from fontTools.ttLib import TTFont 
from utils import generate_kicad_sexpr, generate_polygons_logic, scale_polys_to_target_height, apply_anchor_point, sanitize_font_key

SYMBOL_MAP = {
    ":gnd:": "\u23DA", ":ohm:": "\u03A9", ":mu:": "\u00B5", ":warn:": "\u26A0",
    ":l:": "\u2190", ":r:": "\u2192", ":u:": "\u2191", ":d:": "\u2193"
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # =========================================================================
        # SETUP PREVIEW WIDGET
        # =========================================================================
        
        
        self.canvas = PreviewWidget()
        preview_container = self.ui.groupBoxPreview
        
        # 2. Tạo Layout cho GroupBox (vật chứa) và nhét Canvas vào
        # Vì bạn đã xóa graphicsView cũ trong UI, ta chỉ cần add cái mới vào Layout là xong
        preview_container = self.ui.groupBoxPreview
        layout = QVBoxLayout(preview_container)
        layout.setContentsMargins(10, 25, 10, 10) # Căn lề
        layout.addWidget(self.canvas)
        # =========================================================================

        self.setWindowTitle(f"Text Label Generator v{version}")

        # Dữ liệu Font
        self.font_library = {}
        self.symbol_font_list = []
        self.current_polys = []

        # --- 1. SETUP UI DATA ---
        AlignmentFields = ["Left", "Center", "Right"]
        EdgeFields = ["Square", "Round", "Triangle", "Pointed", "Ribbon_Out", "Ribbon_In", "Trap_Left", "Trap_Right"]
        LayerFields = ["F.SilkS", "F.Paste" , "F.Mask", "F.Cu", "F.Cu/F.Mask"]
        AnchorFields = ["Top-Left", "Top-Center", "Top-Right", "Center-Left", "Center-Center", "Center-Right", "Bottom-Left", "Bottom-Center", "Bottom-Right"]
        
        self.ui.comboAlignment.addItems(AlignmentFields)
        self.ui.comboLeftEdge.addItems(EdgeFields)
        self.ui.comboRightEdge.addItems(EdgeFields)
        self.ui.comboLayer.addItems(LayerFields)
        self.ui.comboAnchor.addItems(AnchorFields)
        
        # Default values
        self.ui.comboAlignment.setCurrentText("Center")
        self.ui.comboLeftEdge.setCurrentText("Square")
        self.ui.comboRightEdge.setCurrentText("Square")
        self.ui.comboLayer.setCurrentText("F.SilkS")
        self.ui.comboAnchor.setCurrentText("Center-Center")
        self.ui.labelFontDir.setWordWrap(True)
        self.ui.plainTextEdit.setPlainText("Text Label")

        # --- 2. LOAD FONTS ---
        self.load_text_fonts(os.path.join("fonts", "texts"))
        self.scan_symbol_fonts(os.path.join("fonts", "symbols"))

        # --- 3. CONNECT SIGNALS ---
        self.ui.buttonCopy.clicked.connect(self.button_copy_clicked)
        self.ui.buttonSave.clicked.connect(self.button_save_clicked)
        self.ui.buttonClose.clicked.connect(self.button_close_clicked)
        self.ui.buttonIcon.clicked.connect(self.button_icon_clicked)

        self.ui.plainTextEdit.textChanged.connect(self.render_preview) 

        # Signal thay đổi UI State
        self.ui.checkNegative.toggled.connect(self.update_ui_states)
        self.ui.checkNoFrame.toggled.connect(self.update_ui_states)
        
        # Signal vẽ lại hình
        self.ui.checkNegative.toggled.connect(self.render_preview)
        self.ui.checkNoFrame.toggled.connect(self.render_preview)
        
        self.ui.comboAlignment.currentIndexChanged.connect(self.render_preview)
        self.ui.comboLeftEdge.currentIndexChanged.connect(self.render_preview)
        self.ui.comboRightEdge.currentIndexChanged.connect(self.render_preview)
        self.ui.comboLayer.currentIndexChanged.connect(self.render_preview)
        self.ui.comboAnchor.currentIndexChanged.connect(self.render_preview)
        self.ui.comboFont.currentIndexChanged.connect(self.on_font_changed) 
        
        for spin in [self.ui.doubleSpinHeight, self.ui.doubleSpinSpacing, 
                     self.ui.doubleSpinBorder, self.ui.doubleSpinCorner,
                     self.ui.doubleSpinTop, self.ui.doubleSpinBottom,
                     self.ui.doubleSpinLeft, self.ui.doubleSpinRight]:
            spin.valueChanged.connect(self.render_preview)

        # --- 4. INIT STATES & RENDER ---
        self.update_ui_states() # Cập nhật trạng thái disable/enable lần đầu
        
        if self.ui.comboFont.count() > 0:
            self.ui.comboFont.setCurrentIndex(0)
            self.on_font_changed(0) 
        else:
            self.render_preview()

    def update_ui_states(self):
        """
        Hàm logic quản lý trạng thái Enable/Disable của các control
        để đúng với logic ban đầu.
        """
        is_neg = self.ui.checkNegative.isChecked()
        no_frame = self.ui.checkNoFrame.isChecked()

        # 1. Nếu No Frame (Chỉ hiện chữ) -> Tắt hết các tính năng chỉnh khung
        self.ui.groupBoxEdges.setEnabled(not no_frame)
        self.ui.groupBoxPadding.setEnabled(not no_frame)
        self.ui.doubleSpinCorner.setEnabled(not no_frame)
        self.ui.checkNegative.setEnabled(not no_frame) # Không thể Negative nếu không có khung
        
        # 2. Border Width chỉ có tác dụng khi CÓ KHUNG và KHÔNG PHẢI NEGATIVE
        # (Vì Negative là khung đặc, không có viền)
        self.ui.doubleSpinBorder.setEnabled(not is_neg and not no_frame)

    def load_text_fonts(self, folder_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(base_dir, folder_path)
        
        self.ui.comboFont.clear()
        if not os.path.exists(abs_path): return

        for f in os.listdir(abs_path):
            if f.lower().endswith(('.ttf', '.otf')):
                full_path = os.path.join(abs_path, f)
                QFontDatabase.addApplicationFont(full_path)
                self.ui.comboFont.addItem(f, full_path)
        self.ui.labelFontDir.setText(f"Fonts loaded from: {folder_path}")

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
                self.font_library[font_key] = ttfont
                self.symbol_font_list.append((filename, full_path, font_key))
            except Exception as e:
                print(f"Failed to load symbol font {filename}: {e}")

    def on_font_changed(self, index):
        font_path = self.ui.comboFont.itemData(index)
        if font_path and os.path.exists(font_path):
            try:
                ttfont = TTFont(font_path)
                self.font_library['default'] = ttfont
                self.render_preview()
            except: pass

    def preprocess_text(self, text):
        processed = text
        for key, char in SYMBOL_MAP.items(): 
            processed = processed.replace(key, char)
        return processed
    
    def button_copy_clicked(self):
        if not self.current_polys: return
        t = self.ui.plainTextEdit.toPlainText().strip()
        safe_text = "".join(c for c in (t.split('\n')[0] if t else "FP") if c.isalnum() or c in (' ', '_', '-')).strip()
        try:
            content = generate_kicad_sexpr(self.current_polys, f"KiBuzzard_{safe_text}", layer=self.ui.comboLayer.currentText())
            QApplication.clipboard().setText(content)
            QMessageBox.information(self, "Success", "Footprint copied to clipboard!")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))
    
    def button_save_clicked(self):
        if not self.current_polys: return
        t = self.ui.plainTextEdit.toPlainText().strip()
        safe_text = "".join(c for c in (t.split('\n')[0] if t else "FP") if c.isalnum() or c in (' ', '_', '-')).strip()
        path, _ = QFileDialog.getSaveFileName(self, "Save Footprint", f"KiBuzzard_{safe_text}.kicad_mod", "KiCad Footprint (*.kicad_mod)")
        if path:
            try:
                content = generate_kicad_sexpr(self.current_polys, f"KiBuzzard_{safe_text}", layer=self.ui.comboLayer.currentText())
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
    
    def button_close_clicked(self):
        self.close()
    
    def render_preview(self):
        if 'default' not in self.font_library: return

        raw_text = self.ui.plainTextEdit.toPlainText()
        text = self.preprocess_text(raw_text) 
        
        try:
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
                self.ui.checkNoFrame.isChecked()
            )
            
            target_h = self.ui.doubleSpinHeight.value()
            scaled_polys = scale_polys_to_target_height(raw_polys, target_h)
            self.current_polys = apply_anchor_point(scaled_polys, self.ui.comboAnchor.currentText())
            
            layer_colors = { "F.Cu": "#840000", "B.Cu": "#008400", "F.SilkS": "#00C2C2", "B.SilkS": "#C200C2", "F.Paste": "#848484", "F.Mask": "#840084" }
            
            if hasattr(self.canvas, 'update_content'):
                self.canvas.update_content(self.current_polys, color=layer_colors.get(self.ui.comboLayer.currentText(), "#F5B041"))
        except Exception as e:
            print(f"Render Error: {e}")