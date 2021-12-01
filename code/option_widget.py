# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel, QComboBox

import group_tree, recipe_form, elem_manager
'''
TabWidget : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QTabWidget.html
ComboBOx : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QComboBox.html
'''

iconSize = 16

class OptionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)
        
        self.comboIconSize = QComboBox()
        self.comboIconSize.insertItems(0, ['Small(16x16)', 'big(32x32)'])
        self.comboIconSize.currentIndexChanged.connect(self.iconSizeChanged)
        
        row = 0
        grid.setRowStretch(0, 1)
        row += 1
        grid.addWidget(QLabel('IconSize'), row, 1)
        grid.addWidget(self.comboIconSize, row, 2)
        row += 1    
        grid.setRowStretch(row, 1)
        
        calumn = 0
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(3, 1)
        
    def iconSizeChanged(self):
        global iconSize
        idx = self.comboIconSize.currentIndex ()
        if idx == 0:
            iconSize = 16
        elif idx == 1:
            iconSize = 32
        else:
            iconSize = 16
        #TODO : Refresh