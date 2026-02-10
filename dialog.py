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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QPlainTextEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(420, 448)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.labelFont = QLabel(Dialog)
        self.labelFont.setObjectName(u"labelFont")

        self.horizontalLayout.addWidget(self.labelFont)

        self.comboFonts = QComboBox(Dialog)
        self.comboFonts.setObjectName(u"comboFonts")

        self.horizontalLayout.addWidget(self.comboFonts)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.buttonPrev = QPushButton(Dialog)
        self.buttonPrev.setObjectName(u"buttonPrev")

        self.horizontalLayout_2.addWidget(self.buttonPrev)

        self.labelPage = QLabel(Dialog)
        self.labelPage.setObjectName(u"labelPage")
        self.labelPage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.labelPage)

        self.buttonNext = QPushButton(Dialog)
        self.buttonNext.setObjectName(u"buttonNext")

        self.horizontalLayout_2.addWidget(self.buttonNext)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.tableWidget = QTableWidget(Dialog)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setMinimumSize(QSize(400, 250))

        self.verticalLayout.addWidget(self.tableWidget)

        self.plainTextEdit = QPlainTextEdit(Dialog)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setMaximumSize(QSize(16777215, 200))

        self.verticalLayout.addWidget(self.plainTextEdit)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.labelText = QLabel(Dialog)
        self.labelText.setObjectName(u"labelText")

        self.horizontalLayout_3.addWidget(self.labelText)

        self.buttonCancel = QPushButton(Dialog)
        self.buttonCancel.setObjectName(u"buttonCancel")
        self.buttonCancel.setAutoDefault(False)

        self.horizontalLayout_3.addWidget(self.buttonCancel)

        self.buttonClear = QPushButton(Dialog)
        self.buttonClear.setObjectName(u"buttonClear")
        self.buttonClear.setAutoDefault(False)

        self.horizontalLayout_3.addWidget(self.buttonClear)

        self.buttonOK = QPushButton(Dialog)
        self.buttonOK.setObjectName(u"buttonOK")
        self.buttonOK.setAutoDefault(False)

        self.horizontalLayout_3.addWidget(self.buttonOK)

        self.horizontalLayout_3.setStretch(0, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalLayout.setStretch(2, 3)
        self.verticalLayout.setStretch(3, 1)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Icon / Character Picker", None))
        self.labelFont.setText(QCoreApplication.translate("Dialog", u"Select Font:", None))
        self.buttonPrev.setText(QCoreApplication.translate("Dialog", u"\u25c0 Prev Page", None))
        self.labelPage.setText(QCoreApplication.translate("Dialog", u"Page: 0/0", None))
        self.buttonNext.setText(QCoreApplication.translate("Dialog", u"Next Page \u25b6", None))
        self.labelText.setText(QCoreApplication.translate("Dialog", u"Symbol", None))
        self.buttonCancel.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.buttonClear.setText(QCoreApplication.translate("Dialog", u"Clear", None))
        self.buttonOK.setText(QCoreApplication.translate("Dialog", u"OK", None))
    # retranslateUi

