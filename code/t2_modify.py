# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel

import group_tree, recipe_form, elem_manager

modify_widget = None

class ModifyWidget(QWidget):
    def __init__(self):
        self.group = elem_manager.map_elem[0]
        
        super().__init__()
        self.initUI()
        self.setGroup(self.group)
        
        global modify_widget
        modify_widget = self
    
    def initUI(self):
        vbox = QVBoxLayout()
        grid = QGridLayout()
        edit_widget_rapper = recipe_form.EditWidgetRapper()
        vbox.addLayout(grid)
        vbox.addLayout(edit_widget_rapper)
        
        self.bt_goOut = QPushButton('Go out')
        self.bt_goInto = QPushButton('Go into')
        grid.addWidget(self.bt_goOut,   0, 2)
        grid.addWidget(self.bt_goInto,  0, 3)
        
        self.bt_addGroup = QPushButton('Add Group')
        self.bt_addFactory = QPushButton('Add Factory')
        grid.addWidget(self.bt_addGroup,    0, 4)
        grid.addWidget(self.bt_addFactory,  0, 5)
        grid.setColumnStretch(6,1)
        self.bt_edit = QPushButton('Hide')
        self.bt_edit.setMaximumWidth(50)
        grid.addWidget(self.bt_edit,        0, 7)
        
        self.label_group = QLabel('None(0)')
        grid.addWidget(QLabel('Current Group')  , 0, 0)
        grid.addWidget(self.label_group         , 0, 1)
        
        self.bt_addGroup.clicked.connect(group_tree.tree_widget.addGroup)
        self.bt_addFactory.clicked.connect(group_tree.tree_widget.addFactory)
        self.bt_edit.clicked.connect(edit_widget_rapper.toggleRecipeWidget)
        
        self.setLayout(vbox)
        
    def setGroup(self, group):
        self.group = group
        text = group.name + '(' + str(group.id) + ')'
        self.label_group.setText(text)
        self.bt_goOut.setEnabled(group.id != 0)
        group_tree.tree_widget.setTreeRootGroup(group)
            