# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel, QComboBox

import group_tree, elem_manager, option_widget
'''
TabWidget : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QTabWidget.html
ComboBOx : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QComboBox.html
'''

option_widget = None

#for project option
expensive = False
icon_size = 16

time_config = 1
time_set = [1, 60, 3600]
time_name = ['s', 'm', 'h']

class OptionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        global option_widget
        option_widget = self
    
    def initUI(self):
        global time_config
        grid = QGridLayout()
        self.setLayout(grid)
        
        self.comboIconSize = QComboBox()
        self.comboIconSize.insertItems(0, ['Small(16x16)', 'big(32x32)'])
        self.comboIconSize.currentIndexChanged.connect(self.iconSizeChanged)
        
        self.comboTime = QComboBox()
        self.comboTime.insertItems(0, ['second', 'minute', 'hour'])
        self.comboTime.currentIndexChanged.connect(self.timeChanged)
        self.comboTime.setCurrentIndex(time_config)
        
        row = 0
        grid.setRowStretch(0, 1)
        row += 1
        grid.addWidget(QLabel('IconSize'), row, 1)
        grid.addWidget(self.comboIconSize, row, 2)
        row += 1
        grid.addWidget(QLabel('Time'), row, 1)
        grid.addWidget(self.comboTime, row, 2)
        row += 1    
        grid.setRowStretch(row, 1)
        
        calumn = 0
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(3, 1)
        
    def iconSizeChanged(self):
        global icon_size
        idx = self.comboIconSize.currentIndex ()
        if idx == 0:
            icon_size = 16
        elif idx == 1:
            icon_size = 32
        else:
            icon_size = 16
        
        group_tree.tree_widget.rebuildTree()
        
    def timeChanged(self):
        global time_config
        idx = self.comboTime.currentIndex ()
        if idx == 0:
            time_config = 0
        elif idx == 1:
            time_config = 1
        elif idx == 2:
            time_config = 2
        else:
            time_config = 0
            
        group_tree.tree_widget.rebuildTree()