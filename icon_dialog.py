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
        
        # Flag to block tag insertion during initial UI setup
        self.dialog_ready = False
        
        # --- 1. UI SETUP ---
        self.ui.plainTextEdit.setPlaceholderText("Double-click icons to add them here...")
        
        # --- 2. TABLE CONFIGURATION ---
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

        # --- 3. EVENTS ---
        self.ui.buttonOK.clicked.connect(self.accept)
        self.ui.comboFonts.currentIndexChanged.connect(self.on_font_changed) 
        self.ui.buttonPrev.clicked.connect(self.prev_page)
        self.ui.buttonNext.clicked.connect(self.next_page)
        self.ui.buttonClear.clicked.connect(self.clear_text)
        self.ui.buttonCancel.clicked.connect(self.reject)

        self.ui.tableWidget.cellClicked.connect(self.show_char_preview)
        self.ui.tableWidget.cellDoubleClicked.connect(self.add_icon_to_buffer)

        # --- 4. LOAD DATA ---
        self.ui.comboFonts.clear()
        for name, path, key in font_list:
            self.ui.comboFonts.addItem(name, (path, key)) 
            
        if self.ui.comboFonts.count() > 0:
            # Block signals to avoid calling on_font_changed twice (once by setCurrentIndex, once manually called)
            self.ui.comboFonts.blockSignals(True)
            self.ui.comboFonts.setCurrentIndex(0)
            self.ui.comboFonts.blockSignals(False)

            # [IMPORTANT] Enable Ready flag -> So the call below will insert tags immediately
            self.dialog_ready = True
            self.on_font_changed(0) 
        else:
            self.dialog_ready = True

    def on_font_changed(self, index):
        data = self.ui.comboFonts.itemData(index)
        if not data: return
        path, key = data
        
        # --- 1. Re-render character table ---
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

        # --- 2. Automatically insert tag when changing Font (And on initialization) ---
        if self.dialog_ready:
            cursor = self.ui.plainTextEdit.textCursor()
            cursor.movePosition(QTextCursor.End)
            
            # Create tags
            start_tag = f" {{{key}}}"
            end_tag = f"{{/{key}}}"
            
            cursor.insertText(start_tag + end_tag)
            
            # Move cursor to the middle (between tags)
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
        # 1. Clear text box
        self.ui.plainTextEdit.setPlainText("")
        
        # 2. Get current font data
        data = self.ui.comboFonts.currentData()
        if not data: return
        path, key = data
        
        # --- 3. Re-render character table (Reset to Page 0) ---
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

        # --- 4. Automatically insert tag ---
        if self.dialog_ready:
            cursor = self.ui.plainTextEdit.textCursor()
            cursor.movePosition(QTextCursor.End)
            
            # Create tags
            start_tag = f" {{{key}}}"
            end_tag = f"{{/{key}}}"
            
            cursor.insertText(start_tag + end_tag)
            
            # Move cursor to the middle (between tags)
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(end_tag))
            
            self.ui.plainTextEdit.setTextCursor(cursor)
            self.ui.plainTextEdit.setFocus()

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
        On Double Click: ONLY insert character, DO NOT insert tag.
        """
        item = self.ui.tableWidget.item(row, col)
        if not item: return
        
        char = item.text()
        
        # Only insert character at current cursor position (usually between the newly created tags)
        self.ui.plainTextEdit.insertPlainText(char)
        self.ui.plainTextEdit.setFocus()

    def get_result(self):
        return self.ui.plainTextEdit.toPlainText()
