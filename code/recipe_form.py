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
from PyQt5.QtWidgets import QCheckBox, QLabel, QLineEdit, QGroupBox, QComboBox
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

import elem_manager, item_manager, common_func, common_class, group_tree, config_manager

class EditWidgetRapper(QGridLayout):
    def __init__(self, bCreateTab = False):
        self.bCreateTab = bCreateTab

        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.bt_hide = QPushButton('Hide')
        self.bt_hide.setMaximumWidth(50)
        self.bt_hide.clicked.connect(self.toggleRecipeWidget)
        
        tab_widget = QTabWidget()
        self.edit_widget = EditWidget(bCreateTab = self.bCreateTab)
        self.tree_widget = group_tree.GroupTreeWidget(self.edit_widget, bCreateTab = self.bCreateTab)
        self.edit_widget.tree_widget = self.tree_widget
        tab_widget.addTab(self.tree_widget, 'Tree view')
        
        self.addWidget(tab_widget, 0, 0, 2, 1)
        self.addWidget(self.bt_hide, 0, 2)
        self.addWidget(self.edit_widget, 1, 1, 1, 2)
        self.setRowStretch(1, 1)
        
    def toggleRecipeWidget(self):
        if self.edit_widget.isVisible():
            self.bt_hide.setText("show")
            self.edit_widget.hide()
        else:
            self.bt_hide.setText("hide")
            self.edit_widget.show()

class EditWidget(QWidget):
    def __init__(self, bCreateTab = False):
        super().__init__()
        self.elem = None
        self.tree_widget = None
        self.bCreateTab = bCreateTab
        self.initUI()
        
    def initUI(self):
        grid1 = QGridLayout()
        self.setLayout(grid1)
        
        grid_info = QGridLayout()
        grid1.addLayout(grid_info, 0, 0, 1, 1)
        
        group_material = QGroupBox('Ingredients')
        group_product  = QGroupBox('Results')
        hbox = QHBoxLayout()
        hbox.addWidget(group_material)
        hbox.addWidget(group_product)
        grid1.addLayout(hbox, 1,0,1,2)
        
        self.grid_module = GridModule(self)
        grid1.addLayout(self.grid_module, 0, 1)
        
        grid1.setRowStretch(0, 1)
        grid1.setRowStretch(1, 1)
        grid1.setColumnStretch(0, 1)
        grid1.setColumnStretch(1, 1)
        
        #------------------------- grid_info
        self.grid_icon = common_class.GridIcon(self)
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
        grid_info.addWidget(self.edit_name      , 1, 1)
        grid_info.addWidget(self.label_id       , 2, 1)
        grid_info.addWidget(self.edit_goal      , 3, 1)
        grid_info.addWidget(self.edit_factories , 4, 1)
        grid_info.addWidget(self.edit_beacon    , 5, 1)
        
        grid_info.setRowStretch(7, 1)
        
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
        time = config_manager.time_set[config_manager.time_config]
        self.edit_factories.setText(common_func.getAmountRound(elem.num_factory))
        self.set_matearial_product()
        
        #self.grid_icon.setInfoGridIcon(elem)
        
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
            self.tree_widget.updateItem(elem)
            
    def onNameChanged(self):
        if self.elem is None:
            return
        self.elem.name = self.edit_name.text()
        if self.elem.name is None or self.elem.name == '':
            self.elem.name \
                = str(type(self.elem).__name__)[4:] + ' ' + str(self.elem.id)
            self.edit_name.setText(self.elem.name)
        self.tree_widget.updateItem(self.elem)
        
    def onGoalChanged(self):
        if self.elem is None:
            return
        time = config_manager.time_set[config_manager.time_config]
        goal = float(self.edit_goal.text()) / time
        self.elem.changeGoal(goal)
        self.tree_widget.updateItem(self.elem)
        self.setElem(self.elem, bUpdateItem=True)
        
    def onFacNumChanged(self):
        if self.elem is None:
            return
        facNum = float(self.edit_factories.text())
        self.elem.changeFacNum(facNum)
        self.tree_widget.updateItem(self.elem)
        self.setElem(self.elem, bUpdateItem=True)
        
class GridModule(QGridLayout):
    def __init__(self, parent):
        self.edit_widget = parent
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
        elem = self.edit_widget.elem
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
                bt.setToolTip(module.name)
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
        '''
        if len(self.list_cb) == 0:
            return
        index = self.list_cb[0]
        for i in range(len(self.list_cb)):
            if i == 0: continue
            cb = self.list_cb[i]
            cb.setCurrentIndex(i)
        
        #set module
        elem = elem_manager.map_elem[self.id_elem]
        module = item_manager.getModuleListWithRecipe(self.name_recipe)[i]
        elem.list_module = [module.name] * elem.num_module
        
        self.updateModule()
        '''
        pass
        
    def onClickItem(self):
        elem = self.edit_widget.elem
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
            self.edit_widget.setElem(elem)
            self.edit_widget.tree_widget.updateItem(elem)
            
def init_grid_item_list(grid, list_item):
    for i in reversed(range(grid.count())): 
        grid.itemAt(i).widget().setParent(None)
            
    for i in range(len(list_item)):
        elem = list_item[i]
        item = item_manager.map_item[elem[0]]
        
        label_icon = QLabel()
        label_icon.setPixmap(item.getPixmap(16, 16))
        
        str_name = item_manager.getItemName(elem[0])
        str_num = common_func.getAmountPerTime(elem[1])
        
        grid.addWidget(label_icon, i, 0)
        grid.addWidget(QLabel(str_name), i, 1)
        grid.addWidget(QLabel(str_num), i, 2)

# --------------------------- debug
