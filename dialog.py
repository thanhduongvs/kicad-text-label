# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QHeaderView,
    QLabel, QPlainTextEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(478, 524)
        self.labelFont = QLabel(Dialog)
        self.labelFont.setObjectName(u"labelFont")
        self.labelFont.setGeometry(QRect(70, 20, 81, 18))
        self.labelPage = QLabel(Dialog)
        self.labelPage.setObjectName(u"labelPage")
        self.labelPage.setGeometry(QRect(180, 60, 66, 18))
        self.buttonPrev = QPushButton(Dialog)
        self.buttonPrev.setObjectName(u"buttonPrev")
        self.buttonPrev.setGeometry(QRect(50, 60, 100, 26))
        self.buttonNext = QPushButton(Dialog)
        self.buttonNext.setObjectName(u"buttonNext")
        self.buttonNext.setGeometry(QRect(280, 60, 100, 26))
        self.tableWidget = QTableWidget(Dialog)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(30, 111, 411, 231))
        self.buttonOK = QPushButton(Dialog)
        self.buttonOK.setObjectName(u"buttonOK")
        self.buttonOK.setGeometry(QRect(330, 450, 94, 26))
        self.labelText = QLabel(Dialog)
        self.labelText.setObjectName(u"labelText")
        self.labelText.setGeometry(QRect(50, 460, 231, 18))
        self.comboFonts = QComboBox(Dialog)
        self.comboFonts.setObjectName(u"comboFonts")
        self.comboFonts.setGeometry(QRect(200, 20, 191, 26))
        self.plainTextEdit = QPlainTextEdit(Dialog)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setGeometry(QRect(30, 360, 381, 70))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Icon / Character Picker", None))
        self.labelFont.setText(QCoreApplication.translate("Dialog", u"Select Font:", None))
        self.labelPage.setText(QCoreApplication.translate("Dialog", u"Page: 0/0", None))
        self.buttonPrev.setText(QCoreApplication.translate("Dialog", u"\u25c0 Prev Page", None))
        self.buttonNext.setText(QCoreApplication.translate("Dialog", u"Next Page \u25b6", None))
        self.buttonOK.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.labelText.setText(QCoreApplication.translate("Dialog", u"Select Font:", None))
    # retranslateUi

