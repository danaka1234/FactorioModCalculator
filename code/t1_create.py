# coding: utf-8

import sys

#core
from PyQt5.QtWidgets    import QWidget, QFrame, QTabWidget

#layout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout

#widget
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QPushButton
from PyQt5.QtGui import QDoubleValidator, QIntValidator

import item_manager, elem_manager, config_manager
import group_tree, recipe_form

class CreateWidget(QWidget):
    def __init__(self):
        self.auto_update = False
        self.selected = None
        
        super().__init__()
        self.initUI()
        
    def initUI(self):
        #first vbox
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        
        grid = QGridLayout()
        vbox.addLayout(grid)
        f1 = QFrame()   #frame as vertical line
        f1.setFrameShape(QFrame.HLine)
        vbox.addWidget(f1)
        
        grid.addWidget(QLabel('Category'), 0, 0)
        self.cb_group = QComboBox()
        self.cb_group.addItem('ALL')
        for group in item_manager.getGroupList():
            self.cb_group.addItem(group.getName(), group.name)
        self.cb_group.currentIndexChanged.connect(self.updateCBSubgroup)
        self.cb_group.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        grid.addWidget(self.cb_group, 0, 1)
        
        grid.addWidget(QLabel('Subgroup'), 1, 0)
        self.cb_subgroup = QComboBox()
        self.cb_subgroup.currentIndexChanged.connect(self.updateCBItem)
        grid.addWidget(self.cb_subgroup, 1, 1)
        
        grid.addWidget(QLabel('Item'), 2, 0)
        self.cb_item = QComboBox()
        self.cb_item.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cb_item.currentIndexChanged.connect(self.changeCBItem)
        grid.addWidget(self.cb_item, 2, 1)
        
        self.updateCBSubgroup()
        
        grid.addWidget(QLabel('Amount'), 0, 2)
        self.le_amount = QLineEdit()
        self.le_amount.setValidator(QDoubleValidator())
        self.le_amount.setFixedWidth(60)
        self.le_amount.setText("1")
        grid.addWidget(self.le_amount, 0, 3)
        
        #-------------------------------------------------- beacon
        grid.addWidget(QLabel('Beacon(%)'), 2, 2)
        self.le_beacon = QLineEdit()
        self.le_beacon.setValidator(QDoubleValidator())
        self.le_beacon.setFixedWidth(60)
        self.le_beacon.setText("0")
        grid.addWidget(self.le_beacon, 2, 3)
        
        #-------------------------------------------------- factory
        grid.addWidget(QLabel('default factory 1'), 0, 4)
        grid.addWidget(QLabel('default factory 2'), 1, 4)
        grid.addWidget(QLabel('default factory 3'), 2, 4)
        self.cb_factory = [QComboBox(), QComboBox(), QComboBox()]
        list_factory = [['None', '_None']]
        for factory in item_manager.getFactoryListWithItem():
            list_factory.append([factory.getName(), factory.name])
        for i in range(3):
            cb = self.cb_factory[i]
            for factory in list_factory:
                    cb.addItem(factory[0], factory[1])
            cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            grid.addWidget(cb, i, 5)
        
        #-------------------------------------------------- module
        grid.addWidget(QLabel('default module 1'), 0, 6)
        grid.addWidget(QLabel('default module 2'), 1, 6)
        grid.addWidget(QLabel('default module 3'), 2, 6)
        self.cb_module = [QComboBox(), QComboBox(), QComboBox()]
        list_module = [['None', '_None']]
        for factory in item_manager.getModuleListWithRecipe():
            list_module.append([factory.getName(), factory.name])
        for i in range(3):
            cb = self.cb_module[i]
            for module in list_module:
                cb.addItem(module[0], module[1])
            cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            grid.addWidget(cb, i, 7)
        
        grid.setColumnStretch(8, 1)
        
        bt_Apply = QPushButton('Apply')
        bt_Apply.clicked.connect(self.updateAll)
        grid.addWidget(bt_Apply, 0, 9)
        
        #-------------------------------- grid2
        grid_bottom = recipe_form.EditWidgetRapper(bCreateTab = True)
        vbox.addLayout(grid_bottom)
        
        self.edit_widget = grid_bottom.edit_widget
        self.widget_gt = grid_bottom.widget_gt

    def toggleRecipeWidget(self):
        if self.edit_widget.isVisible():
            self.bt_hide.setText("show")
            self.edit_widget.hide()
        else:
            self.bt_hide.setText("hide")
            self.edit_widget.show()
    
    def updateCBSubgroup(self):
        cb = self.cb_subgroup
        cb.currentIndexChanged.disconnect()
        cb.clear()
        
        group = None
        if self.cb_group.currentIndex() != 0:
            group = self.cb_group.currentData()
        
        cb.addItem('ALL')
        for subgroup in item_manager.getSubgroupListWithGroup(group):
            cb.addItem(subgroup.getName(), subgroup.name)
        
        cb.currentIndexChanged.connect(self.updateCBItem)
        self.updateCBItem()
    
    def updateCBItem(self):
        cb = self.cb_item
        cb.currentIndexChanged.disconnect()
        cb.clear()
        
        list_subgroup = []
        if self.cb_subgroup.currentIndex() == 0:
            if self.cb_group.currentIndex() != 0:
                group = self.cb_group.currentData()
                list_subgroup = item_manager.map_group[group].list_subgroup
        else:
            list_subgroup = [self.cb_subgroup.currentData()]

        for item in item_manager.getItemListWithSubgroup(list_subgroup):
            cb.addItem(item.getName(), item.name)
                    
        cb.currentIndexChanged.connect(self.changeCBItem)
        if self.auto_update:
            self.changeCBItem()
        
    def changeCBItem(self):
        old = self.selected
        self.selected = self.cb_item.currentData()
        
        if self.auto_update and old != self.selected :
            self.updateAll()
        
    def updateAll(self):
        self.selected = self.cb_item.currentData()
        
        str_amount = self.le_amount.text()
        if str_amount == '' or str_amount is None:  amount = 1.0
        else: amount = float(str_amount)
        if amount is None or amount <= 0:     amount = 1.0
        time = config_manager.time_set[config_manager.time_config]
        goal_per_sec = amount/time
        
        list_factory = []
        for cb in self.cb_factory:
            if cb.currentIndex() == 0:
                continue
            list_factory.append(cb.currentData())
            
        list_module = []
        for cb in self.cb_module:
            if cb.currentIndex() == 0:
                continue
            list_module.append(cb.currentData())
            
        str_beacon = self.le_beacon.text()
        if str_beacon == '' or str_beacon is None:  ratio_beacon = 0
        else: ratio_beacon = float(str_beacon)
        if ratio_beacon is None or ratio_beacon <= 0:     ratio_beacon = 0
        
        #list_args = [name_product, goal_per_sec, list_factory, list_module, ratio_beacon]
        list_args = [self.selected, goal_per_sec, list_factory, list_module, ratio_beacon]
        self.widget_gt.initTree(list_args)
        

# --------------------------- debug
