# coding: utf-8

import sys
from functools import partial 

#core
from PyQt5.QtCore       import QSize
from PyQt5.QtWidgets    import QWidget, QFrame, QWidgetItem

#draw
from PyQt5.QtGui       import QPixmap, QIcon, QFont, QCursor

#layout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QGroupBox
from PyQt5.QtWidgets import QPushButton, QMessageBox, QDialog, QScrollArea
from PyQt5.QtGui     import QDoubleValidator, QIntValidator

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
        
        grid1.setRowStretch(2, 1)
        grid1.setColumnStretch(2, 1)
        #------------------------- grid_info
        self.grid_icon = GridIcon()
        grid_info.addLayout(self.grid_icon, 0, 0, 1, 2)
        
        grid_info.addWidget(QLabel('Name')      , 1, 0)
        grid_info.addWidget(QLabel('ID')        , 2, 0)
        grid_info.addWidget(QLabel('Goal')      , 3, 0)
        grid_info.addWidget(QLabel('Factories') , 4, 0)
        grid_info.addWidget(QLabel('Beacon(%)') , 5, 0)
        grid_info.addWidget(QLabel('Power')     , 6, 0)
        grid_info.addWidget(QLabel('Fuel')      , 7, 0)
        grid_info.addWidget(QLabel('Pollution') , 8, 0)
        
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
        self.edit_beacon.editingFinished.connect(self.onBeaconChanged)
        self.edit_power = QLineEdit()
        self.edit_power.setFixedWidth(80)
        self.edit_power.setValidator(QDoubleValidator())
        self.edit_power.editingFinished.connect(self.onEditCustomEtc)
        self.edit_fuel = QLineEdit()
        self.edit_fuel.setFixedWidth(80)
        self.edit_fuel.setValidator(QDoubleValidator())
        self.edit_fuel.editingFinished.connect(self.onEditCustomEtc)
        self.edit_pollution = QLineEdit()
        self.edit_pollution.setFixedWidth(80)
        self.edit_pollution.setValidator(QDoubleValidator())
        self.edit_pollution.editingFinished.connect(self.onEditCustomEtc)
        grid_info.addWidget(self.edit_name      , 1, 1)
        grid_info.addWidget(self.label_id       , 2, 1)
        grid_info.addWidget(self.edit_goal      , 3, 1)
        grid_info.addWidget(self.edit_factories , 4, 1)
        grid_info.addWidget(self.edit_beacon    , 5, 1)
        grid_info.addWidget(self.edit_power     , 6, 1)
        grid_info.addWidget(self.edit_fuel      , 7, 1)
        grid_info.addWidget(self.edit_pollution , 8, 1)
        
        bt_delete = QPushButton('Delete')
        bt_delete.clicked.connect(self.onClickDelete)
        grid_info.addWidget(bt_delete           , 9, 1)
        
        grid_info.setRowStretch(7, 1)
        grid_info.setColumnStretch(2, 1)
        
        #------------------------- group material product
        self.grid_mat = QGridLayout()
        self.grid_pro = QGridLayout()
        group_material.setLayout(self.grid_mat)
        group_product .setLayout(self.grid_pro)
        self.map_in = dict()
        self.map_out = dict()
        
        self.resetInfo()

    def set_matearial_product(self):
        if self.elem is None:
            self.init_grid_item_list(dict(), False)
            self.init_grid_item_list(dict(), True)
            return
            
        list_mat = []
        list_pro = []
        for key in self.elem.map_material.keys():
            list_mat.append(key)
        for key in self.elem.map_product.keys():
            list_pro.append(key)
        
        self.init_grid_item_list(list_mat, False)
        self.init_grid_item_list(list_pro, True)
        self.update_grid_inout()
        
    def init_grid_item_list(self, list_item, isResult):
        if not isResult:
            grid = self.grid_mat
            map = self.map_in
        else:
            grid = self.grid_pro
            map = self.map_out
            
        # 지우기
        for i in reversed(range(grid.count())):
            widget = grid.itemAt(i).widget()
            if widget is not None: widget.deleteLater()
        map.clear()
                
        for i in range(len(list_item)):
            name_item = list_item[i]
            item = item_manager.map_item[name_item]
            iconSize = 32
            
            if type(self.elem) != elem_manager.ElemCustom:
                widget_icon = QLabel()
                widget_icon.setPixmap(item.getPixmap(iconSize, iconSize))
                widget_icon.setToolTip(item.getName())
                
                widget_num = QLabel('0')
                map[name_item] = [widget_num]
            else:
                widget_icon = QPushButton()
                widget_icon.setFixedSize(32, 32)
                widget_icon.setIconSize(QSize(32, 32))
                widget_icon.setIcon(item.getIcon())
                widget_icon.clicked.connect(\
                    partial(self.onClickChangeCustom, isResult, name_item)\
                )
                
                label_num = QLabel('0')
                
                edit_num = QLineEdit()
                edit_num.setFixedWidth(50)
                edit_num.setValidator(QDoubleValidator())
                edit_num.setText('0')
                edit_num.editingFinished.connect(\
                    partial(self.onEditNumCustom, isResult, name_item)\
                )
                
                vbox = QVBoxLayout()
                vbox.addWidget(label_num)
                vbox.addWidget(edit_num)
                widget_num = QWidget()
                widget_num.setLayout(vbox)
                map[name_item] = [label_num, edit_num]
            
            grid.addWidget(widget_icon, i, 0)
            grid.addWidget(widget_num, i, 1)
            
            size_button = 20
            
            bt_link = QPushButton("L")
            bt_link.setFixedSize(size_button, size_button)
            bt_link.clicked.connect(\
                partial(self.onClickLink, isResult, name_item)\
            )
            grid.addWidget(bt_link, i, 2)
            
            if type(self.elem) == elem_manager.ElemCustom:
                bt_del = QPushButton("-")
                bt_del.setFixedSize(size_button, size_button)
                bt_del.clicked.connect(\
                    partial(self.onClickDelCustom, isResult, name_item)\
                )
                grid.addWidget(bt_del, i, 3)
        
        if type(self.elem) == elem_manager.ElemCustom:
            bt_add = QPushButton("+")
            bt_add.setFixedSize(20, 20)
            bt_add.clicked.connect(\
                partial(self.onClickAddCustom, isResult)\
            )
            grid.addWidget(bt_add, len(list_item), 0)
        
    def update_grid_inout(self):
        for tuple in self.elem.map_material.items():
            self.map_in[tuple[0]][0].setText(common_func.getAmountPerTime(tuple[1][0]))
            if type(self.elem) == elem_manager.ElemCustom:
                num = self.elem.recipe_mat[tuple[0]]
                self.map_in[tuple[0]][1].setText(common_func.getAmountRound(num))
        
        for tuple in self.elem.map_product.items():
            self.map_out[tuple[0]][0].setText(common_func.getAmountPerTime(tuple[1][0]))
            if type(self.elem) == elem_manager.ElemCustom:
                num = self.elem.recipe_pro[tuple[0]]
                self.map_out[tuple[0]][1].setText(common_func.getAmountRound(num))
                
    def setEnabled(self, bEnable):
        if not bEnable:
            self.edit_name.setEnabled(False)
            self.edit_goal.setEnabled(False)
            self.edit_factories.setEnabled(False)
            self.edit_beacon.setEnabled(False)
            self.edit_power.setEnabled(False)
            self.edit_fuel.setEnabled(False)
            self.edit_pollution.setEnabled(False)
            self.grid_module.setEnabled(False)
            return
            
        #공용
        self.edit_name.setEnabled(True)
        if self.elem.haveLink(is_result=True):
            self.edit_factories.setEnabled(False)
        else:
            self.edit_factories.setEnabled(True)
        self.grid_icon.setEnabled(True)
        
        # Enable > Disable 하면 포커스가 옮겨져서 귀찮다... 각자 설정
        if type(self.elem) in [elem_manager.ElemFactory, elem_manager.ElemSpecial]:
            if self.elem.haveLink(is_result=True):
                self.edit_goal.setEnabled(False)
            else:
                self.edit_goal.setEnabled(True)
            self.edit_beacon.setEnabled(True)
            self.edit_power.setEnabled(False)
            self.edit_fuel.setEnabled(False)
            self.edit_pollution.setEnabled(False)
            self.grid_module.setEnabled(True)
            
        if type(self.elem) == elem_manager.ElemGroup:
            self.edit_goal.setEnabled(False)
            self.edit_beacon.setEnabled(False)
            self.edit_power.setEnabled(False)
            self.edit_fuel.setEnabled(False)
            self.edit_pollution.setEnabled(False)
            self.grid_module.setEnabled(False)
            
        if type(self.elem) == elem_manager.ElemCustom:
            self.edit_goal.setEnabled(False)
            self.edit_beacon.setEnabled(False)
            self.edit_power.setEnabled(True)
            self.edit_fuel.setEnabled(True)
            self.edit_pollution.setEnabled(True)
            self.grid_module.setEnabled(False)
        
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
        
    def setElem(self, elem, bUpdateItem = False, bResetInout = False):
        self.elem = elem
        if elem is None:
            return
        
        #공용
        self.edit_name.setText(elem.name)
        self.label_id.setText(str(elem.id))
        self.edit_factories.setText(common_func.getAmountRound(elem.num_factory))
        if bResetInout:
            self.set_matearial_product()
        else:
            self.update_grid_inout()
        self.edit_pollution.setText(common_func.getAmountRound(elem.emission))
        
        self.grid_icon.setInfoGridIcon(elem)
        
        self.setEnabled(True)
        #그룹, 커스텀
        if type(elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]:
            self.edit_beacon.setText('0')
            self.grid_module.resetInfo()
            self.edit_power.setText(common_func.getAmountRound(elem.energy_elect))
            self.edit_fuel.setText(common_func.getAmountRound(elem.energy_fuel))
        #팩토리, 스페셜
        else:
            self.edit_goal.setText(common_func.getAmountPerTime(elem.num_goal, 5, bUnit=False, bTimeStr=False))
            self.edit_beacon.setText(str(elem.beacon))
            self.grid_module.updateGridModule()
            if self.elem.factory is None:
                self.edit_power.setText('0')
                self.edit_fuel.setText('0')
            elif self.elem.factory.energy_source_type == 'electric':
                self.edit_power.setText(common_func.getAmountRound(elem.energy_elect))
                self.edit_fuel.setText('0')
            else:
                self.edit_power.setText('0')
                self.edit_fuel.setText(common_func.getAmountRound(elem.energy_elect))
            
        if bUpdateItem:
            # 아이템 업뎃
            group_tree.tree_widget.updateItem(elem)
            
    def onNameChanged(self):
        if self.elem is None:
            return
        self.elem.changeName( self.edit_name.text() )
        self.edit_name.setText(self.elem.name)
        group_tree.tree_widget.updateItem(self.elem)
        
    def onGoalChanged(self):
        if self.elem is None:
            return
        goal = common_func.getNumFromText(self.edit_goal.text())
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
        
    def onBeaconChanged(self):
        if self.elem is None:
            return
        num_beacon = float(self.edit_beacon.text())
        self.elem.changeBeaconNum(num_beacon)
        group_tree.tree_widget.updateItem(self.elem)
        self.setElem(self.elem, bUpdateItem=True)
        
    def onEditCustomEtc(self):
        if type(self.elem) != elem_manager.ElemCustom: return
        power = float(self.edit_power.text())
        fuel = float(self.edit_fuel.text())
        pollution = float(self.edit_pollution.text())
        self.elem.changeEtc(power, fuel, pollution)
        group_tree.tree_widget.updateItem(self.elem)
        
    def onClickDelete(self):
        self.elem.deleteElem()
        group_tree.tree_widget.rebuildTree()
    
    def onClickAddCustom(self, isResult):
        self.elem.addSubItem(isResult)
        self.set_matearial_product()
        group_tree.tree_widget.updateItem(self.elem)
        
    def onClickLink(self, isResult, name):
        dlg = LinkPopup(name, isResult)
        ret = dlg.exec_()
        if ret == 1:
        # TODO : 링크 추가
            print(dlg.selected)
            return
        pass
    
    def onClickDelCustom(self, isResult, name):
        self.elem.delSubItem(isResult, name)
        self.set_matearial_product()
        group_tree.tree_widget.updateItem(self.elem)
        
    def onClickChangeCustom(self, isResult, name):
        dlg = common_class.ChangePopup(item_manager.list_item_group, 'item', hidden=True, group=True)
        ret = dlg.exec_()
        if ret == 1:
            if name == dlg.selected:
                return
            self.elem.changeSubItem(isResult, name, dlg.selected)
            self.set_matearial_product()
            group_tree.tree_widget.updateItem(self.elem)

    def onEditNumCustom(self, isResult, name):
        sender = self.sender()
        num = common_func.getNumFromText(sender.text())
        self.elem.editSubNum(isResult, name, num)
        group_tree.tree_widget.updateItem(self.elem)
        num_factory = self.elem.num_factory
        if isResult:    label_num = self.map_out[name][0]
        else:           label_num = self.map_in [name][0]
        label_num.setText(common_func.getAmountPerTime(num * num_factory))

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
        
        if type(self.elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]:
            if elem.item_goal is not None:
                self.bt_item.setIcon(elem.item_goal.getIcon())
                self.bt_item.setToolTip(elem.item_goal.getName())
            else:
                self.bt_item.setIcon(QIcon(common_func.getCommonPixmap('factorio')))
            self.bt_recipe.setIcon(QIcon(common_func.getCommonPixmap('factorio')))
            self.bt_factory.setIcon(QIcon(common_func.getCommonPixmap('factorio')))
        else:
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
        
        if type(self.elem) == elem_manager.ElemSpecial:
            list_item = []
            for elem in self.elem.factory.list_result:
                item = item_manager.map_item[elem[1]]
                list_item.append(item)
            dlg = common_class.ChangePopup(list_item, 'item', False)
        else:
            hidden = type(self.elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]
            dlg = common_class.ChangePopup(item_manager.list_item_group, 'item', hidden=hidden, group=True)
        ret = dlg.exec_()
        if ret == 1:
            item = item_manager.map_item[dlg.selected]
            edit_widget.elem.changeItem(item)
            edit_widget.setElem(edit_widget.elem, bUpdateItem=True, bResetInout=True)
        
    def onClickRecipe(self):
        global edit_widget
        
        if self.elem is None or self.elem.item_goal is None\
            or type(self.elem) == elem_manager.ElemSpecial:
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
            edit_widget.elem.changeRecipe(recipe)
            edit_widget.setElem(edit_widget.elem, bUpdateItem=True, bResetInout=True)
        
    def onClickFactory(self):
        global edit_widget
        
        if self.elem is None or self.elem.item_goal is None\
            or type(self.elem) == elem_manager.ElemSpecial:
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
        
    def setEnabled(self, bEnable):
        if bEnable:
            self.bt_item.setEnabled(True)
            if type(self.elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]:
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
        for i in reversed(range(self.grid_btn.count())): 
            widget = self.grid_btn.itemAt(i).widget()
            if widget is not None: widget.deleteLater()
            
    def updateGridModule(self):
        global edit_widget
        elem = edit_widget.elem
        if type(elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]:
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
        if type(elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]:
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
            edit_widget.setElem(elem, bResetInout=True)
            group_tree.tree_widget.updateItem(elem)

# 현재 링크 상태 보여줌
class LinkPopup(QDialog):
    def __init__(self, name_item, is_result):
        super().__init__()
        self.selected = ''
        self.name_item = name_item
        self.is_result = is_result
        
        self.initUI()
        self.drawGrid()
        
    def initUI(self):
        vbox = QVBoxLayout()
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        widgetTop = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        
        widgetTop.setLayout(self.grid)
        sa.setWidget(widgetTop)
        vbox.addWidget(sa)
        self.setLayout(vbox)
        # vbox > sa > widgetTop > self.grid
        
        pos = QCursor().pos()
        width = 250
        height = 400
        x = pos.x() - width/2
        y = max(pos.y() - height/2, 30)
        
        if self.is_result:  title = 'Link ingredient'
        else:               title = 'Link result'
        self.setWindowTitle(title)
        self.setGeometry(x, y, width, height)
        
    def drawGrid(self):
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget is not None: widget.deleteLater()
            
        item = item_manager.map_item[self.name_item]
        iconSize = 32
        label_item = QLabel()
        label_item.setPixmap(item.getPixmap(iconSize, iconSize))
        self.grid.addWidget(label_item, 0, 0)
        self.grid.addWidget(QLabel(item.getName()), 0, 1)
        
        row = 1
        
        global edit_widget
        if self.is_result:
            map = edit_widget.elem.map_product
            list_link = map[self.name_item][1]
        else:
            map = edit_widget.elem.map_material
            id_link = map[self.name_item][1]
            if id_link == -1:
                list_link = []
            else:
                list_link = [id_link]
        
        for id_link in list_link:
            self.addLinkList(row, id_link)
            row += 1
        
        size_button = 32
        bt_add = QPushButton("+")
        bt_add.setFixedSize(size_button, size_button)
        bt_add.clicked.connect(self.onClickAdd)
        self.grid.addWidget(bt_add, row, 0)
        row += 1
        
        self.grid.setRowStretch(row, 1)
                
    def addLinkList(self, y, id_elem):
        elem = elem_manager.map_elem[id_elem]
        item = elem.item_goal
        
        iconSize = 32
        label_item = QLabel()
        label_item.setPixmap(item.getPixmap(iconSize, iconSize))
        
        label_text = QLabel(elem.name + '\nID:' + str(elem.id))
        
        size_button = 20
        bt_del = QPushButton("-")
        bt_del.setFixedSize(size_button, size_button)
        bt_del.clicked.connect(\
            partial(self.onClickDel, id_elem)\
        )
        
        self.grid.addWidget(label_item, y, 0)
        self.grid.addWidget(label_text, y, 1)
        self.grid.addWidget(bt_del, y, 2)
        
    def onClickDel(self, id_elem):
        global edit_widget
        elem = edit_widget.elem
        if self.is_result:  # elem이 producer
            consumer = elem_manager.map_elem[id_elem]
            consumer.delLink(self.name_item, elem.id)
        else:               # elem이 consumer
            producer = elem_manager.map_elem[id_elem]
            elem.delLink(self.name_item, producer.id)
        self.drawGrid()
        edit_widget.setElem(edit_widget.elem, bUpdateItem=True)
        
    def onClickAdd(self):
        global edit_widget
        dlg = LinkAddPopup(self.name_item, self.is_result)
        ret = dlg.exec_()
        if ret == 1:
            id = dlg.selected
            if id is None:  # 새로 추가하기
                item = item_manager.map_item[self.name_item]
                if self.is_result:  # product Link, 불가능
                    return
                else:               # material Link, 호출 elem이 consumer
                    name_recipe = item.list_madeby[0]
                    recipe = item_manager.map_recipe[name_recipe]
                    name_goal = recipe.getListMaterial()[0][0]
                    item_goal = item_manager.map_item[name_goal]
                elem = elem_manager.ElemFactory(\
                    None, edit_widget.elem.group, item_goal)
                elem.changeRecipe(recipe)
            else:           # 기존 elem
                elem = elem_manager.map_elem[id]
            # 연결
            if self.is_result:
                elem.addLink(self.name_item, edit_widget.elem.id)
            else:
                edit_widget.elem.addLink(self.name_item, elem.id)
                
            self.drawGrid()
            edit_widget.setElem(edit_widget.elem, bUpdateItem=True)
            if id is None:  # 새로 추가하기
                group_tree.tree_widget.rebuildTree(keep_sel = True)

# 기존 링크 + 새로 추가할 버튼 보여줌
class LinkAddPopup(QDialog):
    def __init__(self, name_item, is_result):
        super().__init__()
        self.selected = ''
        self.name_item = name_item
        self.is_result = is_result
        
        self.initUI()
        self.drawGrid()
        
    def initUI(self):
        vbox = QVBoxLayout()
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        widgetTop = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        
        widgetTop.setLayout(self.grid)
        sa.setWidget(widgetTop)
        vbox.addWidget(sa)
        self.setLayout(vbox)
        # vbox > sa > widgetTop > self.grid
        
        pos = QCursor().pos()
        width = 200
        height = 400
        x = pos.x() - width/2
        y = max(pos.y() - height/2, 30)
        
        self.setWindowTitle('Select Link')
        self.setGeometry(x, y, width, height)
        
    def drawGrid(self):
        item = item_manager.map_item[self.name_item]
        group = group_tree.tree_widget.elem_group
        
        # find elem
        global edit_widget
        list_elem = []
        for elem in group.list_child:
            if self.is_result:  map = elem.map_material
            else:               map = elem.map_product
            
            if self.name_item in map.keys():
                # 이미 연결된거 제외
                if self.is_result:
                    if map[self.name_item][1] == edit_widget.elem.id:
                        continue
                else:
                    if edit_widget.elem.id in map[self.name_item][1]:
                        continue
                
                list_elem.append(elem)
        
        # draw elem
        row = 0
        for elem in list_elem:
            self.addLinkNew(row, elem)
            row += 1
        
        # draw add
        if not self.is_result:  # 재료만 넣자...
            bt_add = QPushButton("New Factory")
            bt_add.clicked.connect(self.onClickAdd)
            self.grid.addWidget(bt_add, row, 0, 1, 2)
            row += 1
        
        self.grid.setRowStretch(row, 1)
        
    def addLinkNew(self, y, elem):
        item = elem.item_goal
        iconSize = 32
        bt_item = QPushButton()
        bt_item.setFixedSize(iconSize, iconSize)
        bt_item.setIconSize(QSize(iconSize, iconSize))
        bt_item.setIcon(item.getIcon())
        bt_item.id_elem = elem.id
        bt_item.clicked.connect(\
            partial(self.onClickSelect, elem.id)\
        )
        
        label_text = QLabel('ID:' + str(elem.id) + '\n' + elem.name)
        
        self.grid.addWidget(bt_item, y, 0)
        self.grid.addWidget(label_text, y, 1)
        
    def onClickSelect(self, id_elem):
        bt = self.sender()
        self.selected = bt.id_elem
        self.accept()
        
    def onClickAdd(self):
        self.selected = None
        self.accept()

# --------------------------- debug
