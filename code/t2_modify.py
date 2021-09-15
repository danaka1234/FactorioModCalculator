# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel

import group_tree, recipe_form, elem_manager

class ModifyWidget(QWidget):
    def __init__(self):
        self.group = elem_manager.map_elem[0]
        
        super().__init__()
        self.initUI()
        self.setGroup(self.group)
    
    def initUI(self):
        vbox = QVBoxLayout()
        grid = QGridLayout()
        grid_bottom = recipe_form.EditWidgetRapper(bCreateTab = True)
        vbox.addLayout(grid)
        vbox.addLayout(grid_bottom)
        
        self.bt_goOut = QPushButton('Go out')
        self.bt_goInto = QPushButton('Go into')
        grid.setColumnStretch(4,1)
        grid.addWidget(self.bt_goOut,   0, 2)
        grid.addWidget(self.bt_goInto,  0, 3)
        
        self.label_group = QLabel('None(0)')
        grid.addWidget(QLabel('Current Group')  , 0, 0)
        grid.addWidget(self.label_group         , 0, 1)
    
        self.edit_widget = grid_bottom.edit_widget
        self.tree_widget = grid_bottom.tree_widget
        
        self.setLayout(vbox)
        
    def setGroup(self, group):
        self.group = group
        text = group.name + '(' + str(group.id) + ')'
        self.label_group.setText(text)
        self.bt_goOut.setEnabled(group.id != 0)
        self.tree_widget.setTreeRootGroup(group)
            