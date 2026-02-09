import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QMessageBox, QFileDialog, QVBoxLayout
)
from PySide6.QtGui import QFontDatabase, QTextCursor
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
        
        # Cờ kiểm soát khởi động
        self.app_ready = False 

        # =========================================================================
        # 1. SETUP PREVIEW WIDGET
        # =========================================================================
        self.canvas = PreviewWidget()
        layout = QVBoxLayout(self.ui.groupBoxPreview)
        layout.setContentsMargins(10, 25, 10, 10) 
        layout.addWidget(self.canvas)

        # =========================================================================
        # 2. DATA & TIMERS
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
        AlignmentFields = ["Left", "Center", "Right"]
        EdgeFields = ["Square", "Round", "Triangle", "Pointed", "Ribbon_Out", "Ribbon_In", "Trap_Left", "Trap_Right"]
        LayerFields = ["F.SilkS", "F.Paste" , "F.Mask", "F.Cu", "F.Cu/F.Mask"]
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

        # =========================================================================
        # 4. LOAD FONTS & INIT TEXT WITH TAGS
        # =========================================================================
        self.load_text_fonts(os.path.join("fonts", "texts"))
        self.scan_symbol_fonts(os.path.join("fonts", "symbols"))

        # Tạo text mặc định
        initial_text = "Text Label"
        if self.ui.comboFont.count() > 0:
            data = self.ui.comboFont.itemData(0)
            if data:
                _, key = data
                initial_text = f"{{{key}}}Text Label{{/{key}}}"
        
        self.ui.plainTextEdit.setPlainText(initial_text)

        # =========================================================================
        # 5. CONNECT SIGNALS
        # =========================================================================
        self.ui.buttonCopy.clicked.connect(self.button_copy_clicked)
        self.ui.buttonSave.clicked.connect(self.button_save_clicked)
        self.ui.buttonClose.clicked.connect(self.button_close_clicked)
        self.ui.buttonIcon.clicked.connect(self.button_icon_clicked)

        self.ui.plainTextEdit.textChanged.connect(self.trigger_refresh) 
        
        self.ui.checkNegative.toggled.connect(self.update_ui_states)
        self.ui.checkNoFrame.toggled.connect(self.update_ui_states)
        
        self.ui.checkNegative.toggled.connect(self.trigger_refresh)
        self.ui.checkNoFrame.toggled.connect(self.trigger_refresh)
        self.ui.comboAlignment.currentIndexChanged.connect(self.trigger_refresh)
        self.ui.comboLeftEdge.currentIndexChanged.connect(self.trigger_refresh)
        self.ui.comboRightEdge.currentIndexChanged.connect(self.trigger_refresh)
        self.ui.comboLayer.currentIndexChanged.connect(self.trigger_refresh)
        self.ui.comboAnchor.currentIndexChanged.connect(self.trigger_refresh)
        
        # Signal thay đổi font -> Chèn tag vào cuối
        self.ui.comboFont.currentIndexChanged.connect(self.on_font_changed) 
        
        for spin in [self.ui.doubleSpinHeight, self.ui.doubleSpinSpacing, 
                     self.ui.doubleSpinBorder, self.ui.doubleSpinCorner,
                     self.ui.doubleSpinTop, self.ui.doubleSpinBottom,
                     self.ui.doubleSpinLeft, self.ui.doubleSpinRight]:
            spin.valueChanged.connect(self.trigger_refresh)

        # =========================================================================
        # 6. FINAL INITIALIZATION
        # =========================================================================
        self.update_ui_states() 
        
        # Init Default font logic
        if self.ui.comboFont.count() > 0:
            self.ui.comboFont.setCurrentIndex(0)
            data = self.ui.comboFont.itemData(0)
            if data:
                _, key = data
                if key in self.font_library:
                    self.font_library['default'] = self.font_library[key]
        
        self.trigger_refresh()
        self.app_ready = True

    def update_ui_states(self):
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
                self.font_library[font_key] = ttfont
                self.ui.comboFont.addItem(f, (full_path, font_key))
            except Exception as e:
                print(f"Error loading font {f}: {e}")
                
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
        """
        Khi đổi font: 
        1. Nhảy xuống cuối văn bản.
        2. Chèn cặp tag.
        3. Đưa con trỏ vào giữa.
        """
        if not self.app_ready: return

        data = self.ui.comboFont.itemData(index)
        if not data: return
        _, font_key = data

        cursor = self.ui.plainTextEdit.textCursor()
        
        # 1. Di chuyển con trỏ xuống cuối cùng
        cursor.movePosition(QTextCursor.End)
        
        # 2. Tạo chuỗi tag
        end_tag = f"{{/{font_key}}}"
        start_tag = f"{{{font_key}}}"
        
        # 3. Chèn vào cuối
        cursor.insertText(start_tag + end_tag)
        
        # 4. Lùi lại vào giữa cặp tag
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(end_tag))
        
        # 5. Cập nhật giao diện
        self.ui.plainTextEdit.setTextCursor(cursor)
        self.ui.plainTextEdit.setFocus()
        self.trigger_refresh()

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
    
    def render_preview_worker(self):
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
            
            layer_colors = { 
                "F.Cu": "#840000", "B.Cu": "#008400", 
                "F.SilkS": "#00C2C2", "B.SilkS": "#C200C2", 
                "F.Paste": "#848484", "F.Mask": "#840084" 
            }
            color = layer_colors.get(self.ui.comboLayer.currentText(), "#F5B041")

            if hasattr(self.canvas, 'update_content'):
                self.canvas.update_content(self.current_polys, color=color)
                
        except Exception as e:
            print(f"Render Error: {e}")