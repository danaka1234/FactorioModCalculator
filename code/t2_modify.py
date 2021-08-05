# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel

import group_tree, recipe_form, elem_manager

class ModifyWidget(QWidget):
    def __init__(self):
        self.group = elem_manager.map_elem[0]
        
        super().__init__()
        self.initUI()
        self.initGroup(self.group)
    
    def initUI(self):
        vbox = QVBoxLayout()
        grid = QGridLayout()
        grid_bottom = recipe_form.EditWidgetRapper(bCreateTab = True)
        vbox.addLayout(grid)
        vbox.addLayout(grid_bottom)
        
        bt_goOut = QPushButton('Go out')
        bt_goInto = QPushButton('Go into')
        bt_addGroup = QPushButton('Add Empty Group')
        bt_addGroup.clicked.connect(self.addGroup)
        bt_addFactory = QPushButton('Add Empty Factory')
        bt_addFactory.clicked.connect(self.addFactory)
        grid.setColumnStretch(1,1)
        grid.addWidget(bt_goOut,        0, 2)
        grid.addWidget(bt_goInto,       1, 2)
        grid.addWidget(bt_addGroup,     0, 3)
        grid.addWidget(bt_addFactory,   1, 3)
        
        self.label_group = QLabel('None(0)')
        grid.addWidget(QLabel('Current Group')  , 0, 0)
        grid.addWidget(self.label_group         , 1, 0)
    
        self.edit_widget = grid_bottom.edit_widget
        self.widget_gt = grid_bottom.widget_gt
        
        self.setLayout(vbox)
        
    def initGroup(self, group):
        self.widget_gt.initTreeByGroup(group)
        text = group.name + '(' + str(group.id) + ')'
        self.label_group.setText(text)
        
    def addGroup(self):
        elem_manager.ElemGroup(None, self.group.id, None)
        self.initGroup(self.group)
        
    def addFactory(self):
        elem_manager.ElemFactory(None, self.group)
        self.initGroup(self.group)
        
    
            