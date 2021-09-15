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
        grid1.addLayout(grid_info, 0, 0, 1, 2)
        
        vbox = QVBoxLayout()
        group_material = QGroupBox('Ingredients')
        group_product  = QGroupBox('Results')
        vbox.addWidget(group_material)
        vbox.addWidget(group_product)
        grid1.addLayout(vbox, 1,0,2,1)
        
        self.grid_link = GridLink(self)
        grid1.addLayout(self.grid_link, 1, 1)
        
        self.grid_module = GridModule(self)
        grid1.addLayout(self.grid_module, 2, 1)
        
        #------------------------- grid_info
        self.grid_icon = common_class.GridIcon(self)
        grid_info.addLayout(self.grid_icon, 0, 0, 5, 2)
        grid_info.setColumnStretch(1,1)
        grid_info.addWidget(QLabel('Order'), 5, 0)
        self.edit_order = QLineEdit()
        self.edit_order.setFixedWidth(80)
        #self.edit_order.editingFinished.connect(self.onNameChanged)
        grid_info.addWidget(self.edit_order, 5, 1)
        
        grid_info.addWidget(QLabel('Name'), 0, 2)
        grid_info.addWidget(QLabel('ID'), 1, 2)
        grid_info.addWidget(QLabel('Goal'), 2, 2)
        grid_info.addWidget(QLabel('Factories'), 3, 2)
        grid_info.addWidget(QLabel('Beacon(%)'), 4, 2)
        grid_info.addWidget(QLabel('Total Fac'), 5, 2)
        
        self.edit_name = QLineEdit()
        self.edit_name.setFixedWidth(80)
        self.edit_name.editingFinished.connect(self.onNameChanged)
        grid_info.addWidget(self.edit_name, 0, 3)
        self.label_id = QLabel('')
        grid_info.addWidget(self.label_id, 1, 3)
        self.edit_goal = QLineEdit()
        self.edit_goal.setFixedWidth(80)
        self.edit_goal.setValidator(QDoubleValidator())
        self.edit_goal.editingFinished.connect(self.onGoalChanged)
        grid_info.addWidget(self.edit_goal, 2, 3)
        self.edit_factories = QLineEdit()
        self.edit_factories.setFixedWidth(80)
        self.edit_factories.setValidator(QDoubleValidator())
        self.edit_factories.editingFinished.connect(self.onFacNumChanged)
        grid_info.addWidget(self.edit_factories, 3, 3)
        self.edit_beacon = QLineEdit()
        self.edit_beacon.setFixedWidth(80)
        self.edit_beacon.setValidator(QDoubleValidator())
        grid_info.addWidget(self.edit_beacon, 4, 3)
        self.label_total = QLabel('0')
        grid_info.addWidget(self.label_total, 5, 3)
        
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
            self.edit_order.setEnabled(False)
            self.edit_name.setEnabled(False)
            self.edit_goal.setEnabled(False)
            self.edit_factories.setEnabled(False)
            self.edit_beacon.setEnabled(False)
            self.grid_icon.setEnabled(False)
            self.grid_link.setEnabled(False)
            self.grid_module.setEnabled(False)
            return
            
        #공용
        self.edit_order.setEnabled(True)
        self.edit_name.setEnabled(True)
        self.edit_factories.setEnabled(True)
        self.grid_icon.setEnabled(True, bGroup)
        self.grid_link.setEnabled(True)
        
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
        self.grid_link.resetInfo()
        self.grid_module.resetInfo()
        self.setEnabled(False)
        
    def setElem(self, elem, bUpdateGroupTree = False):
        self.elem = elem
        
        #공용
        self.edit_name.setText(elem.name)
        self.label_id.setText(str(elem.id))
        time = config_manager.time_set[config_manager.time_config]
        self.edit_factories.setText(common_func.getAmountRound(elem.num_factory))
        self.set_matearial_product()
        
        num_fac_total = elem.num_factory
        group = self.elem.group
        while group is not None:
            num_fac_total *= group.num_factory
            group = group.group
        self.label_total.setText(common_func.getAmountRound(num_fac_total))
        
        self.grid_icon.setInfoGridIcon(elem)
        self.grid_link.setInfoGridLink(elem)
        
        #그룹 전용
        if type(elem) != elem_manager.ElemFactory:
            self.setEnabled(True, True)
            self.edit_beacon.setText('0')
            self.grid_module.resetInfo()

        #팩토리 전용
        else:
            num_goal = elem.num_goal * time
            self.edit_goal.setText(common_func.getAmountRound(num_goal, 5))
            self.setEnabled(True)
            self.edit_beacon.setText(str(elem.beacon))
            self.grid_module.setInfoGridModule(elem)
            
        if bUpdateGroupTree:
            self.tree_widget.updateTree()
            self.setElem(elem)
            self.tree_widget.setCurrentSelect(elem)
            
    def onNameChanged(self):
        if self.elem is None:
            return
        self.elem.name = self.edit_name.text()
        if self.elem.name is None or self.elem.name == '':
            self.elem.name \
                = str(type(self.elem).__name__)[4:] + ' ' + str(self.elem.id)
            self.edit_name.setText(self.elem.name)
        
    def onGoalChanged(self):
        if self.elem is None:
            return
        time = config_manager.time_set[config_manager.time_config]
        goal_tmp = float(self.edit_goal.text())
        goal = goal_tmp / time
        self.elem.changeGoal(goal)
        self.setElem(self.elem, bUpdateGroupTree=True)
        
    def onFacNumChanged(self):
        if self.elem is None:
            return
        if isinstance(self.elem, elem_manager.ElemGroup):
            facNum = float(self.edit_factories.text())
            self.elem.changeFacNum(facNum)
        else:
            if self.elem.num_goal == 0:
                self.elem.changeGoal(1)
            facNum = float(self.edit_factories.text())
            goal = facNum * self.elem.num_goal / self.elem.num_factory 
            self.elem.changeGoal(goal)
        self.setElem(self.elem, bUpdateGroupTree=True)
        
class GridModule(QGridLayout):
    def __init__(self, parent):
        self.edit_widget = parent
        super().__init__()
        self.list_bt = []
        self.initUI()
        
    def initUI(self):
        self.addWidget(QLabel('Module'), 0,0)
        self.addWidget(QLabel('Speed'), 1,0)
        self.addWidget(QLabel('Prod'), 2,0)
        self.addWidget(QLabel('Consume'), 3,0)
        self.addWidget(QLabel('Poll'), 4,0)
        
        self.label_mod_speed = QLabel('0')
        self.addWidget(self.label_mod_speed, 1,1)
        self.label_mod_prob = QLabel('0')
        self.addWidget(self.label_mod_prob, 2,1)
        self.label_mod_consume = QLabel('0')
        self.addWidget(self.label_mod_consume, 3,1)
        self.label_mod_poll = QLabel('0')
        self.addWidget(self.label_mod_poll, 4,1)
        
        self.bt_fill = QPushButton('Fill 1st Module')
        self.bt_fill.clicked.connect(self.onClickFillModule)
        self.addWidget(self.bt_fill, 5,0,1,2)
        
        self.grid_btn = QGridLayout()
        self.grid_btn.setSpacing(0)
        self.addLayout(self.grid_btn, 6,0,1,2)
        
    def resetInfo(self):
        self.label_mod_speed    .setText('0')
        self.label_mod_prob     .setText('0')
        self.label_mod_consume  .setText('0')
        self.label_mod_poll     .setText('0')
        
        self.list_bt.clear()
        for i in reversed(range(self.grid_btn.count())): 
            self.grid_btn.itemAt(i).widget().setParent(None)
            #self.grid_btn.itemAt(i).widget().deleteLater()
        
    def setInfoGridModule(self, elem):
        self.list_module = [['None', '_None']]
        list_module_from_recipe = item_manager.getModuleListWithRecipe(elem.recipe.name)
        for module in list_module_from_recipe :
            self.list_module.append([module.getName(), module.name])
            
        self.list_bt = []
        x = 0
        y = 0
        iconSize = 32
        for i in range(elem.num_module):
            if x >= 10:
                x = 0
                y += 1
            bt = QPushButton()
            bt.setFixedSize(iconSize, iconSize)
            bt.setIconSize(QSize(iconSize, iconSize))
            bt.clicked.connect(self.onClickItem)
            bt.selected = 'None'
            self.list_bt.append(bt)
            self.grid_btn.addWidget(bt, y, x)
            x += 1
        
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
        elem.modules = [module.name] * elem.num_module
        
        self.updateModule()
        '''
        pass
        
    def onClickItem(self):
        #TODO : 제작
        pass

class GridLink(QGridLayout):
    def __init__(self, parent):
        super().__init__()
        
        self.edit_widget = parent
        self.bProduct = True
        self.selected = None
        self.elem = None
        self.initUI()
        
    def initUI(self):
        self.list_link = QListWidget()
        self.list_link.setFixedWidth(120)
        self.addWidget(self.list_link, 0, 0, 1, 2)
        
        label = QLabel('ID')
        label.setFixedWidth(60)
        self.addWidget(label, 1,0)
        label = QLabel('Ratio')
        label.setFixedWidth(60)
        self.addWidget(label, 2,0)
        label = QLabel('Item')
        label.setFixedWidth(60)
        self.addWidget(label, 3,0)
        self.label_type = QLabel('(Result)')
        self.label_type.setFixedWidth(60)
        self.addWidget(self.label_type, 4,0)
        self.le_linkID = QLineEdit()
        self.le_linkID.setFixedWidth(60)
        self.le_linkID.setValidator(QIntValidator())
        self.addWidget(self.le_linkID, 1,1)
        self.le_linkAmount = QLineEdit()
        self.le_linkAmount.setFixedWidth(60)
        self.le_linkAmount.setValidator(QDoubleValidator())
        self.addWidget(self.le_linkAmount, 2,1)
        self.bt_item = QPushButton()
        self.bt_item.setFixedSize(32, 32)
        self.bt_item.setIconSize(QSize(32, 32))
        self.bt_item.clicked.connect(self.onClickLinkItem)
        self.addWidget(self.bt_item, 3,1,2,1)
        
        hbox = QHBoxLayout()
        self.addLayout(hbox,5,0,1,2)
        self.bt_add = QPushButton('Add')
        self.bt_add.clicked.connect(self.onAddLink)
        self.bt_add.setFixedWidth(50)
        hbox.addWidget(self.bt_add)
        self.bt_del = QPushButton('Del')
        self.bt_del.clicked.connect(self.onDelLink)
        self.bt_del.setFixedWidth(50)
        hbox.addWidget(self.bt_del)
        
    def resetInfo(self):
        self.bt_item.setIcon(QIcon())
        self.bt_item.setToolTip('')
        
    def setInfoGridLink(self, elem):
        self.elem = elem
        list_product = list(elem.map_product.values())
        name_item = None
        if len(list_product) != 0:
            name_item = list_product[0].name_product
            self.bProduct = True
        else:
            list_material = list(elem.map_material.values())
            if len(list_material) == 0:
                self.resetInfo()
                return
            name_item = list_material[0].name_material
            self.bFalse = True
        
        item = item_manager.map_item[name_item]
        self.bt_item.setIcon(item.getIcon())
        self.bt_item.setToolTip(item.getName())
        self.selected = item
        
        self.list_link.clear()
        
        for product in elem.map_product.values():
            for link in product.list_link:
                item = item_manager.map_item[link.name]
                #str_item = item.getName() + ':' + str(link.ratio) + ' > ' + str(link.consumer.id)
                str_item = ':' + str(link.ratio) + ' > ' + str(link.consumer.id)
                item_list = QListWidgetItem(item.getIcon(), str_item)
                self.list_link.addItem(item_list)
        for material in elem.map_material.values():
            for link in material.list_link:
                item = item_manager.map_item[link.name]
                str_item = ':' + str(link.ratio) + ' < ' + str(link.producer.id)
                item_list = QListWidgetItem(item.getIcon(), str_item)
                self.list_link.addItem(item_list)

    def setEnabled(self, bEnable):
        if bEnable:
            self.bt_add.setEnabled(True)
            self.bt_del.setEnabled(True)
            self.bt_item.setEnabled(True)
        else:
            self.bt_add.setEnabled(False)
            self.bt_del.setEnabled(False)
            self.bt_item.setEnabled(False)
        
    def onClickLinkItem(self):
        list_material_tmp = self.elem.recipe.getListMaterial()
        list_product_tmp = self.elem.recipe.getListProduct()
        list_material = []
        list_product = []
        for elem in list_material_tmp:
            item = item_manager.map_item[elem[0]]
            list_material.append(item)
        for elem in list_product_tmp:
            item = item_manager.map_item[elem[0]]
            list_product.append(item)
        dlg = common_class.ChangePopup([list_material, list_product], 'link item')
        ret = dlg.exec_()
        if ret == 1:
            item = item_manager.map_item[dlg.selected]
            self.bt_item.setIcon(item.getIcon())
            self.bt_item.setToolTip(item.getName())
            self.bProduct = dlg.bProduct
            self.selected = item
            if self.bProduct:
                self.label_type.setText('(Result)')
            else:
                self.label_type.setText('(Ingredients)')
            
    def onAddLink(self):
        try:
            id = int(self.le_linkID.text())
            ratio = float(self.le_linkAmount.text())
        except:
            return
        item = self.selected
        bProduct = self.bProduct
        
        # elem 검사
        if bProduct:
            producer = self.elem
            consumer = elem_manager.map_elem.get(id)
        else:
            producer = elem_manager.map_elem.get(id)
            consumer = self.elem
            
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
            
        if producer is None or consumer is None or producer.id == consumer.id:
            msg.setText('Id is same or not exist')
            msg.exec_()
            return
        if producer.group != consumer.group:
            msg.setText('Not same group')
            msg.exec_()
            return
        if producer.map_product.get(item.name) is None\
            or consumer.map_material.get(item.name) is None:
            msg.setText('Result or Ingredient not exist')
            msg.exec_()
            return
        
        # 링크 있는지 찾아보기
        for link in producer.map_product[item.name].list_link:
            if link.consumer == consumer:
                msg.setText('Already linked')
                msg.exec_()
                return
        
        # 넣기
        producer.connectProduct(consumer, item.name)
        
        # 비율 업데이트
        #TODO : 작성중
        
        # UI 업데이트
        self.edit_widget.setElem(self.elem)
        
    def onDelLink(self):
        pass
        
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
