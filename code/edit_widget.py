# coding: utf-8

import sys
import traceback
import copy

#core
from PyQt5.QtCore       import QSize
from PyQt5.QtWidgets    import QWidget, QFrame, QWidgetItem, QTabWidget

#draw
from PyQt5.QtGui       import QPixmap, QIcon

#layout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QCheckBox, QLabel, QLineEdit, QGroupBox
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QMessageBox
from PyQt5.QtGui     import QDoubleValidator, QIntValidator
#https://www.delftstack.com/tutorial/pyqt5/pyqt-grid-layout/
#grid layout 셀 합치기

'''
https://doc.qt.io/qtforpython/PySide2/QtWidgets/QLabel.html
https://doc.qt.io/qtforpython/PySide2/QtWidgets/QVBoxLayout.html
https://doc.qt.io/qtforpython/PySide2/QtWidgets/QLayout.html

공백 http://blog.bluekyu.me/2010/08/pyqt-%EB%82%98%EC%95%84%EA%B0%80%EA%B8%B0-5-1.html
init label_icon image https://pythonspot.com/pyqt5-image/
'''

import elem_manager, item_manager, common_func, group_tree, option_widget, common_class

edit_widget = None

class EditWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.elem = None
        self.initUI()
        
        global edit_widget
        edit_widget = self
        
    def initUI(self):
        grid1 = QGridLayout()
        self.setLayout(grid1)
        
        grid_info = QGridLayout()
        grid1.addLayout(grid_info, 0, 0)
        
        group_material = QGroupBox('Ingredients')
        group_product  = QGroupBox('Results')
        hbox = QHBoxLayout()
        hbox.addWidget(group_material)
        hbox.addWidget(group_product)
        grid1.addLayout(hbox, 1,0,1,2)
        
        self.grid_module = GridModule()
        grid1.addLayout(self.grid_module, 0, 1)
        
        grid1.setRowStretch(0, 1)
        grid1.setRowStretch(1, 1)
        grid1.setColumnStretch(0, 1)
        grid1.setColumnStretch(1, 1)
        
        #------------------------- grid_info
        self.grid_icon = GridIcon()
        grid_info.addLayout(self.grid_icon, 0, 0, 1, 2)
        
        grid_info.addWidget(QLabel('Name')      , 1, 0)
        grid_info.addWidget(QLabel('ID')        , 2, 0)
        grid_info.addWidget(QLabel('Goal')      , 3, 0)
        grid_info.addWidget(QLabel('Factories') , 4, 0)
        grid_info.addWidget(QLabel('Beacon(%)') , 5, 0)
        
        self.edit_name = QLineEdit()
        self.edit_name.setFixedWidth(80)
        self.edit_name.editingFinished.connect(self.onNameChanged)
        self.label_id = QLabel('')
        self.edit_goal = QLineEdit()
        self.edit_goal.setFixedWidth(80)
        self.edit_goal.setValidator(QDoubleValidator())
        self.edit_goal.editingFinished.connect(self.onGoalChanged)
        self.edit_factories = QLineEdit()
        self.edit_factories.setFixedWidth(80)
        self.edit_factories.setValidator(QDoubleValidator())
        self.edit_factories.editingFinished.connect(self.onFacNumChanged)
        self.edit_beacon = QLineEdit()
        self.edit_beacon.setFixedWidth(80)
        self.edit_beacon.setValidator(QDoubleValidator())
        self.edit_beacon.editingFinished.connect(self.onBeaconChagned)
        grid_info.addWidget(self.edit_name      , 1, 1)
        grid_info.addWidget(self.label_id       , 2, 1)
        grid_info.addWidget(self.edit_goal      , 3, 1)
        grid_info.addWidget(self.edit_factories , 4, 1)
        grid_info.addWidget(self.edit_beacon    , 5, 1)
        
        grid_info_bt = QGridLayout()
        bt_delete = QPushButton('Delete')
        bt_delete.clicked.connect(self.onClickDelete)
        grid_info_bt.addWidget(bt_delete        , 0, 0)
        grid_info.addLayout(grid_info_bt        , 6, 0, 1, 2)
        
        grid_info.setRowStretch(7, 1)
        grid_info.setColumnStretch(2, 1)
        
        #------------------------- group material product
        self.grid_mat = QGridLayout()
        self.grid_pro = QGridLayout()
        group_material.setLayout(self.grid_mat)
        group_product .setLayout(self.grid_pro)
        
        self.resetInfo()

    def set_matearial_product(self):
        if self.elem is None:
            init_grid_item_list(self.grid_mat, [])
            init_grid_item_list(self.grid_pro, [])
            return
        
        list_mat = []
        list_pro = []

        #self.grid_mat
        for material in self.elem.map_material.values():
            elem_sub = [material.name_material, material.num_need]
            list_mat.append(elem_sub)
        
        #self.grid_pro
        for product  in self.elem.map_product .values():
            elem_sub = [product .name_product, product .num_real]
            list_pro.append(elem_sub)

        init_grid_item_list(self.grid_mat, list_mat)
        init_grid_item_list(self.grid_pro, list_pro)
        
    def setEnabled(self, bEnable, bGroup = False):
        if not bEnable:
            self.edit_name.setEnabled(False)
            self.edit_goal.setEnabled(False)
            self.edit_factories.setEnabled(False)
            self.edit_beacon.setEnabled(False)
            self.grid_icon.setEnabled(False)
            self.grid_module.setEnabled(False)
            return
            
        #공용
        self.edit_name.setEnabled(True)
        self.edit_factories.setEnabled(True)
        self.grid_icon.setEnabled(True, bGroup)
        
        #각자
        if bGroup:
            self.edit_goal.setEnabled(False)
            self.edit_beacon.setEnabled(False)
            self.grid_module.setEnabled(False)
        else:
            self.edit_goal.setEnabled(True)
            self.edit_beacon.setEnabled(True)
            self.grid_module.setEnabled(True)
        
    def resetInfo(self):
        self.elem = None
        self.edit_name.setText('name')
        self.label_id.setText('id')
        self.edit_factories.setText('1.0')
        self.edit_beacon.setText('0')
        self.set_matearial_product()
        
        self.grid_icon.resetInfo()
        self.grid_module.resetInfo()
        self.setEnabled(False)
        
    def setElem(self, elem, bUpdateItem = False):
        self.elem = elem
        
        #공용
        self.edit_name.setText(elem.name)
        self.label_id.setText(str(elem.id))
        time = option_widget.time_set[option_widget.time_config]
        self.edit_factories.setText(common_func.getAmountRound(elem.num_factory))
        self.set_matearial_product()
        
        self.grid_icon.setInfoGridIcon(elem)
        
        #그룹 전용
        if type(elem) != elem_manager.ElemFactory:
            self.setEnabled(True, True)
            self.edit_beacon.setText('0')
            self.grid_module.resetInfo()
        #팩토리 전용
        else:
            self.edit_goal.setText(common_func.getAmountPerTime(elem.num_goal, 5, bUnit=False, bTimeStr=False))
            self.setEnabled(True)
            self.edit_beacon.setText(str(elem.beacon))
            self.grid_module.updateGridModule()
            
        if bUpdateItem:
            # TODO : 링크 있으면 링크 업뎃...
            
            # 아이템 업뎃
            group_tree.tree_widget.updateItem(elem)
            
    def onNameChanged(self):
        if self.elem is None:
            return
        self.elem.name = self.edit_name.text()
        if self.elem.name is None or self.elem.name == '':
            self.elem.name \
                = str(type(self.elem).__name__)[4:] + ' ' + str(self.elem.id)
            self.edit_name.setText(self.elem.name)
        group_tree.tree_widget.updateItem(self.elem)
        
    def onGoalChanged(self):
        if self.elem is None:
            return
        time = option_widget.time_set[option_widget.time_config]
        goal = float(self.edit_goal.text()) / time
        self.elem.changeGoal(goal)
        group_tree.tree_widget.updateItem(self.elem)
        self.setElem(self.elem, bUpdateItem=True)
        
    def onFacNumChanged(self):
        if self.elem is None:
            return
        facNum = float(self.edit_factories.text())
        self.elem.changeFacNum(facNum)
        group_tree.tree_widget.updateItem(self.elem)
        self.setElem(self.elem, bUpdateItem=True)
        
    def onBeaconChagned(self):
        if self.elem is None:
            return
        num_beacon = float(self.edit_beacon.text())
        self.elem.changeBeaconNum(num_beacon)
        group_tree.tree_widget.updateItem(self.elem)
        self.setElem(self.elem, bUpdateItem=True)
        
    def onClickDelete(self):
        self.elem.deleteElem()
        group_tree.tree_widget.elem_group.updateGroupInOut()
        group_tree.tree_widget.rebuildTree()

class GridIcon(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.bt_item = QPushButton()
        self.bt_item.setFixedSize(32, 32)
        self.bt_item.setIconSize(QSize(32, 32))
        self.bt_item.clicked.connect(self.onClickItem)
        self.bt_recipe = QPushButton()
        self.bt_recipe.setFixedSize(32, 32)
        self.bt_recipe.setIconSize(QSize(32, 32))
        self.bt_recipe.clicked.connect(self.onClickRecipe)
        self.bt_factory = QPushButton()
        self.bt_factory.setFixedSize(32, 32)
        self.bt_factory.setIconSize(QSize(32, 32))
        self.bt_factory.clicked.connect(self.onClickFactory)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.bt_item)
        hbox.addWidget(self.bt_recipe)
        hbox.addWidget(self.bt_factory)
        self.addLayout(hbox)
        
        self.elem = None
        
        self.resetInfo()
        
    def setInfoGridIcon(self, elem):
        self.resetInfo()
        self.elem = elem
        
        if type(elem) == elem_manager.ElemGroup:
            if elem.item_goal is not None:
                self.bt_item.setIcon(elem.item_goal.getIcon())
                self.bt_item.setToolTip(elem.item_goal.getName())
            else:
                self.bt_item.setIcon(QIcon(common_func.getCommonPixmap('factorio')))
            self.bt_recipe.setIcon(QIcon(common_func.getCommonPixmap('factorio')))
            self.bt_factory.setIcon(QIcon(common_func.getCommonPixmap('factorio')))
            self.setEnabled(True, True)
            return
        self.bt_item.setIcon(elem.item_goal.getIcon())
        self.bt_item.setToolTip(elem.item_goal.getName())
        self.bt_recipe.setIcon(elem.recipe.getIcon())
        self.bt_recipe.setToolTip(common_func.getRecipeToolTipText(elem.recipe))
        if elem.factory is not None:
            self.bt_factory.setIcon(elem.factory.getIcon())
            self.bt_factory.setToolTip(common_func.getFactoryToolTipText(elem.factory))
            
        self.setEnabled(True)
        
    def resetInfo(self):
        pixmap = common_func.getCommonPixmap('factorio')
        self.bt_item.setIcon(QIcon(pixmap))
        self.bt_item.setToolTip('')
        self.bt_recipe.setIcon(QIcon(pixmap))
        self.bt_recipe.setToolTip('')
        self.bt_factory.setIcon(QIcon(pixmap))
        self.bt_factory.setToolTip('')
        self.elem = None
        self.setEnabled(False)
        
            
    def onClickItem(self):
        global edit_widget
        
        dlg = common_class.ChangePopup(item_manager.getSortedItemList(), 'item')
        ret = dlg.exec_()
        if ret == 1:
            item = item_manager.map_item[dlg.selected]
            edit_widget.elem.changeItem(item)
            edit_widget.setElem(edit_widget.elem, True)
        
    def onClickRecipe(self):
        global edit_widget
        
        if self.elem is None or self.elem.item_goal is None:
            return
            
        list_recipe = []
        
        for name_recipe in self.elem.item_goal.list_madeby:
            recipe = item_manager.map_recipe[name_recipe]
            list_recipe.append(recipe)
        list_recipe.sort(key=lambda elem: elem.order)
        
        dlg = common_class.ChangePopup(list_recipe, 'recipe')
        ret = dlg.exec_()
        if ret == 1:
            if dlg.selected == self.elem.recipe.name:
                return
            recipe = item_manager.map_recipe[dlg.selected]
            edit_widget.elem.changeRecipe(recipe, bItemChange=False)
            edit_widget.setElem(edit_widget.elem, True)
        
    def onClickFactory(self):
        global edit_widget
        
        if self.elem is None or self.elem.item_goal is None:
            return
            
        list_factory = item_manager.getFactoryListByRecipe(self.elem.recipe)
        
        dlg = common_class.ChangePopup(list_factory, 'factory')
        ret = dlg.exec_()
        if ret == 1:
            if dlg.selected == self.elem.factory.name:
                return
            factory = item_manager.map_factory[dlg.selected]
            edit_widget.elem.changeFactory(factory)
            edit_widget.setElem(self.elem, True)
            group_tree.tree_widget.updateItem(self.elem)
        
    def setEnabled(self, bEnable, bGroup = False):
        if bEnable:
            self.bt_item.setEnabled(True)
            if bGroup:
                self.bt_recipe.setEnabled(False)
                self.bt_factory.setEnabled(False)
            else:
                self.bt_recipe.setEnabled(True)
                self.bt_factory.setEnabled(True)
        else:
            self.bt_item.setEnabled(False)
            self.bt_recipe.setEnabled(False)
            self.bt_factory.setEnabled(False)
        
class GridModule(QGridLayout):
    def __init__(self):
        super().__init__()
        self.list_bt = []
        self.initUI()
        
    def initUI(self):
        groupbox = QGroupBox('Module')
        grid = QGridLayout()
        self.addWidget(groupbox, 0,0)
        groupbox.setLayout(grid)
        
        grid.addWidget(QLabel('Speed')  , 0,0)
        grid.addWidget(QLabel('Prod')   , 1,0)
        grid.addWidget(QLabel('Consume'), 2,0)
        grid.addWidget(QLabel('Poll')   , 3,0)
        
        self.label_mod_speed = QLabel('0')
        grid.addWidget(self.label_mod_speed, 0,1)
        self.label_mod_prob = QLabel('0')
        grid.addWidget(self.label_mod_prob, 1,1)
        self.label_mod_consume = QLabel('0')
        grid.addWidget(self.label_mod_consume, 2,1)
        self.label_mod_poll = QLabel('0')
        grid.addWidget(self.label_mod_poll, 3,1)
        
        self.bt_fill = QPushButton('Fill 1st Module')
        self.bt_fill.clicked.connect(self.onClickFillModule)
        self.addWidget(self.bt_fill, 1,0)
        
        self.grid_btn = QGridLayout()
        self.grid_btn.setSpacing(0)
        self.addLayout(self.grid_btn, 2,0)
        
        self.setRowStretch(3, 1)
        
    def resetInfo(self):
        self.label_mod_speed    .setText('0')
        self.label_mod_prob     .setText('0')
        self.label_mod_consume  .setText('0')
        self.label_mod_poll     .setText('0')
        
        self.list_bt.clear()
        list_tmp = []
        for i in reversed(range(self.grid_btn.count())): 
            widget = self.grid_btn.itemAt(i).widget()
            widget.deleteLater()
            #widget.setParent(None)
            
    def updateGridModule(self):
        global edit_widget
        
        elem = edit_widget.elem
        if type(elem) != elem_manager.ElemFactory:
            return
            
        self.resetInfo()
        
        x = 0
        y = 0
        iconSize = 32
        for i in range(elem.num_module):
            if x >= 4:
                x = 0
                y += 1
            bt = QPushButton()
            bt.setFixedSize(iconSize, iconSize)
            bt.setIconSize(QSize(iconSize, iconSize))
            bt.clicked.connect(self.onClickItem)
            bt.module = None
            if len(elem.list_module) > i:
                name_module = elem.list_module[i]
                module = item_manager.map_item[name_module]
                bt.module = name_module
                bt.setIcon(module.getIcon())
                bt.setToolTip(common_func.getModuleToolTipText(module))
            self.list_bt.append(bt)
            self.grid_btn.addWidget(bt, y, x)
            x += 1
            
        self.label_mod_speed    .setText(common_func.getAmountRound(elem.speed,5))
        self.label_mod_prob     .setText(common_func.getAmountRound(elem.productivity,5))
        self.label_mod_consume  .setText(common_func.getAmountRound(elem.consumption,5))
        self.label_mod_poll     .setText(common_func.getAmountRound(elem.pollution,5))
        
    def setEnabled(self, bEnable):
        if bEnable:
            self.bt_fill.setEnabled(True)
        else:
            self.bt_fill.setEnabled(False)
        
    def onClickFillModule(self):
        global edit_widget
        elem = edit_widget.elem
        list_module = [self.list_bt[0].module]
        elem.changeModule(list_module, bFillFirst=True)
        edit_widget.setElem(elem)
        group_tree.tree_widget.updateItem(elem)
        
    def onClickItem(self):
        global edit_widget
        
        elem = edit_widget.elem
        if type(elem) != elem_manager.ElemFactory:
            return
        if elem.recipe is None:
            return
        
        button = self.sender()
        list_module = item_manager.getModuleListWithRecipe(elem.recipe.name)
        dlg = common_class.ChangePopup(list_module, 'module')
        ret = dlg.exec_()
        if ret == 1:
            if dlg.selected == button.module:
                return
            button.module = dlg.selected
            list_module = []
            for bt in self.list_bt:
                if bt.module != None:
                    list_module.append(bt.module)
            elem.changeModule(list_module)
            edit_widget.setElem(elem)
            group_tree.tree_widget.updateItem(elem)
            
def init_grid_item_list(grid, list_item):
    for i in reversed(range(grid.count())): 
        grid.itemAt(i).widget().setParent(None)
            
    for i in range(len(list_item)):
        elem = list_item[i]
        item = item_manager.map_item[elem[0]]
        iconSize = 32
        
        label_icon = QLabel()
        label_icon.setPixmap(item.getPixmap(iconSize, iconSize))
        label_icon.setToolTip(item.getName())
        
        str_num = common_func.getAmountPerTime(elem[1])
        
        grid.addWidget(label_icon, i, 0)
        grid.addWidget(QLabel(str_num), i, 1)

# --------------------------- debug
