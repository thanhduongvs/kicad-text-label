from dialog import Ui_Dialog
from fontTools.ttLib import TTFont 
from PySide6.QtWidgets import (
    QDialog, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtGui import (
    QFont, QFontDatabase, QTextCursor
)
from PySide6.QtCore import Qt


class IconPickerDialog(QDialog):
    def __init__(self, font_list, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        # Cờ chặn chèn tag khi setup UI ban đầu
        self.dialog_ready = False
        
        # --- 1. SETUP UI ---
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
        self.ui.buttonClear.clicked.connect(self.clear_text)
        self.ui.buttonCancel.clicked.connect(self.reject)

        self.ui.tableWidget.cellClicked.connect(self.show_char_preview)
        self.ui.tableWidget.cellDoubleClicked.connect(self.add_icon_to_buffer)

        # --- 4. LOAD DỮ LIỆU ---
        self.ui.comboFonts.clear()
        for name, path, key in font_list:
            self.ui.comboFonts.addItem(name, (path, key)) 
            
        if self.ui.comboFonts.count() > 0:
            # Block signals để tránh gọi on_font_changed 2 lần (1 lần do setCurrentIndex, 1 lần do mình gọi thủ công)
            self.ui.comboFonts.blockSignals(True)
            self.ui.comboFonts.setCurrentIndex(0)
            self.ui.comboFonts.blockSignals(False)

            # [QUAN TRỌNG] Bật cờ Ready -> Để lần gọi dưới đây sẽ chèn tag ngay lập tức
            self.dialog_ready = True
            self.on_font_changed(0) 
        else:
            self.dialog_ready = True

    def on_font_changed(self, index):
        data = self.ui.comboFonts.itemData(index)
        if not data: return
        path, key = data
        
        # --- 1. Render lại bảng ký tự ---
        font_id = QFontDatabase.addApplicationFont(path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
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

        # --- 2. Tự động chèn tag khi đổi Font (Và khi khởi tạo) ---
        if self.dialog_ready:
            cursor = self.ui.plainTextEdit.textCursor()
            cursor.movePosition(QTextCursor.End)
            
            # Tạo tag
            start_tag = f" {{{key}}}"
            end_tag = f"{{/{key}}}"
            
            cursor.insertText(start_tag + end_tag)
            
            # Đưa con trỏ vào giữa
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(end_tag))
            
            self.ui.plainTextEdit.setTextCursor(cursor)
            self.ui.plainTextEdit.setFocus()

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
    
    def clear_text(self):
        self.ui.plainTextEdit.setPlainText("")
        self.on_font_changed(0)

    def show_char_preview(self, row, col):
        item = self.ui.tableWidget.item(row, col)
        if item:
            char = item.text()
            hex_code = f"U+{ord(char):04X}"
            self.ui.labelText.setText(f"{char}  ({hex_code})")
            
            preview_font = QFont(item.font())
            preview_font.setPixelSize(14) 
            self.ui.labelText.setFont(preview_font)

    def add_icon_to_buffer(self, row, col):
        """
        Khi Double Click: CHỈ chèn ký tự, KHÔNG chèn tag.
        """
        item = self.ui.tableWidget.item(row, col)
        if not item: return
        
        char = item.text()
        
        # Chỉ chèn ký tự vào vị trí con trỏ hiện tại (thường là giữa cặp tag vừa tạo)
        self.ui.plainTextEdit.insertPlainText(char)
        self.ui.plainTextEdit.setFocus()

    def get_result(self):
        return self.ui.plainTextEdit.toPlainText()