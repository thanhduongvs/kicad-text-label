from dialog import Ui_Dialog
from fontTools.ttLib import TTFont 
from PySide6.QtWidgets import (
    QDialog, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtGui import (
    QFont, QFontDatabase
)
from PySide6.QtCore import Qt


class IconPickerDialog(QDialog):
    def __init__(self, font_list, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        # --- 1. SETUP UI ---
        # Không cần tạo thủ công self.txt_buffer hay move() vị trí nữa
        # Sử dụng trực tiếp widget có sẵn trong dialog.ui
        self.ui.plainTextEdit.setPlaceholderText("Double-click icons to add them here...")
        
        # --- 2. CẤU HÌNH BẢNG ---
        self.items_per_page = 350
        self.current_page = 0
        self.total_pages = 0
        self.all_chars = []
        self.display_font = None

        self.ui.tableWidget.setColumnCount(10)
        self.ui.tableWidget.horizontalHeader().setVisible(False)
        self.ui.tableWidget.verticalHeader().setVisible(False)
        self.ui.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # --- 3. SỰ KIỆN ---
        self.ui.buttonOK.clicked.connect(self.accept)
        self.ui.comboFonts.currentIndexChanged.connect(self.on_font_changed) 
        self.ui.buttonPrev.clicked.connect(self.prev_page)
        self.ui.buttonNext.clicked.connect(self.next_page)

        # Click 1 lần: Xem trước vào Label
        self.ui.tableWidget.cellClicked.connect(self.show_char_preview)
        
        # Click 2 lần: Cộng dồn vào plainTextEdit
        self.ui.tableWidget.cellDoubleClicked.connect(self.add_icon_to_buffer)

        # --- 4. LOAD DỮ LIỆU ---
        self.ui.comboFonts.clear()
        for name, path, key in font_list:
            self.ui.comboFonts.addItem(name, (path, key)) 
            
        if self.ui.comboFonts.count() > 0:
            self.ui.comboFonts.setCurrentIndex(0)
            self.on_font_changed(0)

    def on_font_changed(self, index):
        data = self.ui.comboFonts.itemData(index)
        if not data: return
        path, key = data
        
        # Load Font hiển thị
        font_id = QFontDatabase.addApplicationFont(path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families: return
        self.display_font = QFont(families[0])
        self.display_font.setPixelSize(24) 
        
        try:
            ttfont = TTFont(path)
            cmap = ttfont.getBestCmap()
            self.all_chars = sorted([chr(c) for c in cmap.keys() if c > 32])
            
            total_items = len(self.all_chars)
            if total_items > 0:
                self.total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
            else:
                self.total_pages = 1
            
            self.current_page = 0
            self.render_current_page()
        except Exception as e:
            print(f"Error reading font: {e}")

    def render_current_page(self):
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setRowCount(0)
        
        if not self.all_chars: return

        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(self.all_chars))
        chars = self.all_chars[start:end]
        
        cols = self.ui.tableWidget.columnCount()
        rows = (len(chars) + cols - 1) // cols
        self.ui.tableWidget.setRowCount(rows)
        self.ui.tableWidget.setUpdatesEnabled(False)
        
        for i, c in enumerate(chars):
            item = QTableWidgetItem(c)
            item.setFont(self.display_font)
            item.setTextAlignment(Qt.AlignCenter)
            item.setToolTip(f"U+{ord(c):04X}")
            
            row = i // cols
            col = i % cols
            self.ui.tableWidget.setItem(row, col, item)
        
        self.ui.tableWidget.setUpdatesEnabled(True)
        self.ui.labelPage.setText(f"Page: {self.current_page + 1}/{self.total_pages}")
        self.ui.buttonPrev.setEnabled(self.current_page > 0)
        self.ui.buttonNext.setEnabled(self.current_page < self.total_pages - 1)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_current_page()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_current_page()

    def show_char_preview(self, row, col):
        """Khi click đơn: Hiện thông tin lên Label"""
        item = self.ui.tableWidget.item(row, col)
        if item:
            char = item.text()
            hex_code = f"U+{ord(char):04X}"
            self.ui.labelText.setText(f"Selected: {char}  ({hex_code})")
            
            preview_font = QFont(item.font())
            preview_font.setPixelSize(14) 
            self.ui.labelText.setFont(preview_font)

    def add_icon_to_buffer(self, row, col):
        """Khi Double Click: Thêm Tag vào ô plainTextEdit có sẵn"""
        item = self.ui.tableWidget.item(row, col)
        if not item: return
        
        char = item.text()
        
        # Lấy Key Font
        data = self.ui.comboFonts.currentData()
        key = data[1] if data else "default"
        
        # Tạo chuỗi Tag
        tagged_text = f" {{{key}}}{char}{{/{key}}} "
        
        # Chèn vào ô plainTextEdit
        self.ui.plainTextEdit.insertPlainText(tagged_text)
        self.ui.plainTextEdit.setFocus()

    def get_result(self):
        """Trả về toàn bộ nội dung trong plainTextEdit"""
        return self.ui.plainTextEdit.toPlainText()