# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui.ui'
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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QMainWindow, QMenuBar,
    QPlainTextEdit, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(820, 902)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_7 = QGridLayout(self.centralwidget)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.groupBoxPreview = QGroupBox(self.centralwidget)
        self.groupBoxPreview.setObjectName(u"groupBoxPreview")
        self.groupBoxPreview.setMinimumSize(QSize(800, 400))

        self.verticalLayout_5.addWidget(self.groupBoxPreview)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBoxEdges = QGroupBox(self.centralwidget)
        self.groupBoxEdges.setObjectName(u"groupBoxEdges")
        self.gridLayout_5 = QGridLayout(self.groupBoxEdges)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.labelLeftEdge = QLabel(self.groupBoxEdges)
        self.labelLeftEdge.setObjectName(u"labelLeftEdge")

        self.gridLayout_5.addWidget(self.labelLeftEdge, 0, 0, 1, 1)

        self.comboLeftEdge = QComboBox(self.groupBoxEdges)
        self.comboLeftEdge.setObjectName(u"comboLeftEdge")

        self.gridLayout_5.addWidget(self.comboLeftEdge, 0, 1, 1, 1)

        self.labelRightEdge = QLabel(self.groupBoxEdges)
        self.labelRightEdge.setObjectName(u"labelRightEdge")

        self.gridLayout_5.addWidget(self.labelRightEdge, 1, 0, 1, 1)

        self.comboRightEdge = QComboBox(self.groupBoxEdges)
        self.comboRightEdge.setObjectName(u"comboRightEdge")

        self.gridLayout_5.addWidget(self.comboRightEdge, 1, 1, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBoxEdges)

        self.groupBoxGeometry = QGroupBox(self.centralwidget)
        self.groupBoxGeometry.setObjectName(u"groupBoxGeometry")
        self.gridLayout_4 = QGridLayout(self.groupBoxGeometry)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.labelAlignment = QLabel(self.groupBoxGeometry)
        self.labelAlignment.setObjectName(u"labelAlignment")

        self.gridLayout_4.addWidget(self.labelAlignment, 0, 0, 1, 1)

        self.comboAlignment = QComboBox(self.groupBoxGeometry)
        self.comboAlignment.setObjectName(u"comboAlignment")

        self.gridLayout_4.addWidget(self.comboAlignment, 0, 1, 1, 1)

        self.labelHeight = QLabel(self.groupBoxGeometry)
        self.labelHeight.setObjectName(u"labelHeight")

        self.gridLayout_4.addWidget(self.labelHeight, 1, 0, 1, 1)

        self.doubleSpinHeight = QDoubleSpinBox(self.groupBoxGeometry)
        self.doubleSpinHeight.setObjectName(u"doubleSpinHeight")
        self.doubleSpinHeight.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinHeight.setDecimals(1)
        self.doubleSpinHeight.setSingleStep(0.100000000000000)
        self.doubleSpinHeight.setValue(5.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinHeight, 1, 1, 1, 1)

        self.labelSpacing = QLabel(self.groupBoxGeometry)
        self.labelSpacing.setObjectName(u"labelSpacing")

        self.gridLayout_4.addWidget(self.labelSpacing, 2, 0, 1, 1)

        self.doubleSpinSpacing = QDoubleSpinBox(self.groupBoxGeometry)
        self.doubleSpinSpacing.setObjectName(u"doubleSpinSpacing")
        self.doubleSpinSpacing.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinSpacing.setDecimals(1)
        self.doubleSpinSpacing.setSingleStep(0.100000000000000)
        self.doubleSpinSpacing.setValue(1.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinSpacing, 2, 1, 1, 1)

        self.labelBorder = QLabel(self.groupBoxGeometry)
        self.labelBorder.setObjectName(u"labelBorder")

        self.gridLayout_4.addWidget(self.labelBorder, 3, 0, 1, 1)

        self.doubleSpinBorder = QDoubleSpinBox(self.groupBoxGeometry)
        self.doubleSpinBorder.setObjectName(u"doubleSpinBorder")
        self.doubleSpinBorder.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinBorder.setDecimals(1)
        self.doubleSpinBorder.setSingleStep(0.100000000000000)
        self.doubleSpinBorder.setValue(1.000000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinBorder, 3, 1, 1, 1)

        self.labelCorner = QLabel(self.groupBoxGeometry)
        self.labelCorner.setObjectName(u"labelCorner")

        self.gridLayout_4.addWidget(self.labelCorner, 4, 0, 1, 1)

        self.doubleSpinCorner = QDoubleSpinBox(self.groupBoxGeometry)
        self.doubleSpinCorner.setObjectName(u"doubleSpinCorner")
        self.doubleSpinCorner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinCorner.setDecimals(1)
        self.doubleSpinCorner.setSingleStep(0.100000000000000)

        self.gridLayout_4.addWidget(self.doubleSpinCorner, 4, 1, 1, 1)

        self.checkNegative = QCheckBox(self.groupBoxGeometry)
        self.checkNegative.setObjectName(u"checkNegative")

        self.gridLayout_4.addWidget(self.checkNegative, 5, 0, 1, 2)

        self.checkNoFrame = QCheckBox(self.groupBoxGeometry)
        self.checkNoFrame.setObjectName(u"checkNoFrame")
        self.checkNoFrame.setStyleSheet(u"font-weight: bold; color: #e74c3c;")

        self.gridLayout_4.addWidget(self.checkNoFrame, 6, 0, 1, 2)


        self.verticalLayout_3.addWidget(self.groupBoxGeometry)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBoxInput = QGroupBox(self.centralwidget)
        self.groupBoxInput.setObjectName(u"groupBoxInput")
        self.gridLayout_6 = QGridLayout(self.groupBoxInput)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.plainTextEdit = QPlainTextEdit(self.groupBoxInput)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.gridLayout_6.addWidget(self.plainTextEdit, 0, 0, 1, 1)


        self.verticalLayout_4.addWidget(self.groupBoxInput)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxPadding = QGroupBox(self.centralwidget)
        self.groupBoxPadding.setObjectName(u"groupBoxPadding")
        self.gridLayout_3 = QGridLayout(self.groupBoxPadding)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.labelTop = QLabel(self.groupBoxPadding)
        self.labelTop.setObjectName(u"labelTop")

        self.gridLayout_3.addWidget(self.labelTop, 0, 0, 1, 1)

        self.doubleSpinTop = QDoubleSpinBox(self.groupBoxPadding)
        self.doubleSpinTop.setObjectName(u"doubleSpinTop")
        self.doubleSpinTop.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinTop.setDecimals(1)
        self.doubleSpinTop.setSingleStep(0.100000000000000)
        self.doubleSpinTop.setValue(2.000000000000000)

        self.gridLayout_3.addWidget(self.doubleSpinTop, 0, 1, 1, 1)

        self.labelBottom = QLabel(self.groupBoxPadding)
        self.labelBottom.setObjectName(u"labelBottom")

        self.gridLayout_3.addWidget(self.labelBottom, 1, 0, 1, 1)

        self.doubleSpinBottom = QDoubleSpinBox(self.groupBoxPadding)
        self.doubleSpinBottom.setObjectName(u"doubleSpinBottom")
        self.doubleSpinBottom.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinBottom.setDecimals(1)
        self.doubleSpinBottom.setSingleStep(0.100000000000000)
        self.doubleSpinBottom.setValue(2.000000000000000)

        self.gridLayout_3.addWidget(self.doubleSpinBottom, 1, 1, 1, 1)

        self.labelLeft = QLabel(self.groupBoxPadding)
        self.labelLeft.setObjectName(u"labelLeft")

        self.gridLayout_3.addWidget(self.labelLeft, 2, 0, 1, 1)

        self.doubleSpinLeft = QDoubleSpinBox(self.groupBoxPadding)
        self.doubleSpinLeft.setObjectName(u"doubleSpinLeft")
        self.doubleSpinLeft.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinLeft.setDecimals(1)
        self.doubleSpinLeft.setSingleStep(0.100000000000000)
        self.doubleSpinLeft.setValue(2.000000000000000)

        self.gridLayout_3.addWidget(self.doubleSpinLeft, 2, 1, 1, 1)

        self.labelRight = QLabel(self.groupBoxPadding)
        self.labelRight.setObjectName(u"labelRight")

        self.gridLayout_3.addWidget(self.labelRight, 3, 0, 1, 1)

        self.doubleSpinRight = QDoubleSpinBox(self.groupBoxPadding)
        self.doubleSpinRight.setObjectName(u"doubleSpinRight")
        self.doubleSpinRight.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.doubleSpinRight.setDecimals(1)
        self.doubleSpinRight.setSingleStep(0.100000000000000)
        self.doubleSpinRight.setValue(2.000000000000000)

        self.gridLayout_3.addWidget(self.doubleSpinRight, 3, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBoxPadding)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBoxFootprint = QGroupBox(self.centralwidget)
        self.groupBoxFootprint.setObjectName(u"groupBoxFootprint")
        self.gridLayout_2 = QGridLayout(self.groupBoxFootprint)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.labelLayer = QLabel(self.groupBoxFootprint)
        self.labelLayer.setObjectName(u"labelLayer")

        self.gridLayout_2.addWidget(self.labelLayer, 0, 0, 1, 1)

        self.comboLayer = QComboBox(self.groupBoxFootprint)
        self.comboLayer.setObjectName(u"comboLayer")

        self.gridLayout_2.addWidget(self.comboLayer, 0, 1, 1, 1)

        self.labelAnchor = QLabel(self.groupBoxFootprint)
        self.labelAnchor.setObjectName(u"labelAnchor")

        self.gridLayout_2.addWidget(self.labelAnchor, 1, 0, 1, 1)

        self.comboAnchor = QComboBox(self.groupBoxFootprint)
        self.comboAnchor.setObjectName(u"comboAnchor")

        self.gridLayout_2.addWidget(self.comboAnchor, 1, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBoxFootprint)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelFont = QLabel(self.centralwidget)
        self.labelFont.setObjectName(u"labelFont")

        self.horizontalLayout.addWidget(self.labelFont)

        self.comboFont = QComboBox(self.centralwidget)
        self.comboFont.setObjectName(u"comboFont")

        self.horizontalLayout.addWidget(self.comboFont)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonSymbol = QPushButton(self.centralwidget)
        self.buttonSymbol.setObjectName(u"buttonSymbol")

        self.gridLayout.addWidget(self.buttonSymbol, 0, 2, 1, 1)

        self.buttonIcon = QPushButton(self.centralwidget)
        self.buttonIcon.setObjectName(u"buttonIcon")

        self.gridLayout.addWidget(self.buttonIcon, 0, 1, 1, 1)

        self.buttonSave = QPushButton(self.centralwidget)
        self.buttonSave.setObjectName(u"buttonSave")

        self.gridLayout.addWidget(self.buttonSave, 1, 2, 1, 1)

        self.buttonCopy = QPushButton(self.centralwidget)
        self.buttonCopy.setObjectName(u"buttonCopy")

        self.gridLayout.addWidget(self.buttonCopy, 2, 2, 1, 1)

        self.buttonClear = QPushButton(self.centralwidget)
        self.buttonClear.setObjectName(u"buttonClear")

        self.gridLayout.addWidget(self.buttonClear, 1, 1, 1, 1)

        self.buttonClose = QPushButton(self.centralwidget)
        self.buttonClose.setObjectName(u"buttonClose")

        self.gridLayout.addWidget(self.buttonClose, 2, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.verticalLayout_4.setStretch(0, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout_4)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.labelFontDir = QLabel(self.centralwidget)
        self.labelFontDir.setObjectName(u"labelFontDir")
        self.labelFontDir.setMinimumSize(QSize(0, 50))

        self.verticalLayout_5.addWidget(self.labelFontDir)

        self.verticalLayout_5.setStretch(0, 1)

        self.gridLayout_7.addLayout(self.verticalLayout_5, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 820, 23))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Text Label Generator", None))
        self.groupBoxPreview.setTitle(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.groupBoxEdges.setTitle(QCoreApplication.translate("MainWindow", u"Edges", None))
        self.labelLeftEdge.setText(QCoreApplication.translate("MainWindow", u"Left Edge:", None))
        self.labelRightEdge.setText(QCoreApplication.translate("MainWindow", u"Right Edge:", None))
        self.groupBoxGeometry.setTitle(QCoreApplication.translate("MainWindow", u"Geometry & Style", None))
        self.labelAlignment.setText(QCoreApplication.translate("MainWindow", u"Alignment:", None))
        self.labelHeight.setText(QCoreApplication.translate("MainWindow", u"Height (mm):", None))
        self.labelSpacing.setText(QCoreApplication.translate("MainWindow", u"Line Spacing:", None))
        self.labelBorder.setText(QCoreApplication.translate("MainWindow", u"Border Width:", None))
        self.labelCorner.setText(QCoreApplication.translate("MainWindow", u"Corner Radius:", None))
        self.checkNegative.setText(QCoreApplication.translate("MainWindow", u"Negative (Inverted)", None))
        self.checkNoFrame.setText(QCoreApplication.translate("MainWindow", u"No Frame (Text Only)", None))
        self.groupBoxInput.setTitle(QCoreApplication.translate("MainWindow", u"Text Input", None))
        self.groupBoxPadding.setTitle(QCoreApplication.translate("MainWindow", u"Padding", None))
        self.labelTop.setText(QCoreApplication.translate("MainWindow", u"Top:", None))
        self.labelBottom.setText(QCoreApplication.translate("MainWindow", u"Bottom:", None))
        self.labelLeft.setText(QCoreApplication.translate("MainWindow", u"Left:", None))
        self.labelRight.setText(QCoreApplication.translate("MainWindow", u"Right:", None))
        self.groupBoxFootprint.setTitle(QCoreApplication.translate("MainWindow", u"Footprint Setup", None))
        self.labelLayer.setText(QCoreApplication.translate("MainWindow", u"Layer:", None))
        self.labelAnchor.setText(QCoreApplication.translate("MainWindow", u"Anchor:", None))
        self.labelFont.setText(QCoreApplication.translate("MainWindow", u"Fonts", None))
        self.buttonSymbol.setText(QCoreApplication.translate("MainWindow", u"Symbol \u25bc", None))
        self.buttonIcon.setText(QCoreApplication.translate("MainWindow", u"Pick Icon", None))
        self.buttonSave.setText(QCoreApplication.translate("MainWindow", u"Save .kicad_mod", None))
        self.buttonCopy.setText(QCoreApplication.translate("MainWindow", u"Copy to Clipboard", None))
        self.buttonClear.setText(QCoreApplication.translate("MainWindow", u"Clear Text", None))
        self.buttonClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.labelFontDir.setText(QCoreApplication.translate("MainWindow", u"Font Path:", None))
    # retranslateUi

