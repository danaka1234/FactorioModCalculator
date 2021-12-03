# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel, QComboBox

import group_tree, elem_manager, config_manager
'''
TabWidget : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QTabWidget.html
ComboBOx : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QComboBox.html
'''

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
        
        self.comboTime = QComboBox()
        self.comboTime.insertItems(0, ['second', 'minute', 'hour'])
        self.comboTime.currentIndexChanged.connect(self.timeChanged)
        self.comboTime.setCurrentIndex(config_manager.time_config)
        
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
        idx = self.comboIconSize.currentIndex ()
        if idx == 0:
            config_manager.iconSize = 16
        elif idx == 1:
            config_manager.iconSize = 32
        else:
            config_manager.iconSize = 16
        
        group_tree.tree_widget.rebuildTree()
        
    def timeChanged(self):
        idx = self.comboTime.currentIndex ()
        if idx == 0:
            config_manager.time_config = 0
        elif idx == 1:
            config_manager.time_config = 1
        elif idx == 2:
            config_manager.time_config = 2
        else:
            config_manager.time_config = 0
            
        group_tree.tree_widget.rebuildTree()