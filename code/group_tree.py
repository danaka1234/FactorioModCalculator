# coding: utf-8

#core
from PyQt5.QtWidgets    import QTreeWidget, QTreeWidgetItem, QHeaderView 
#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTreeWidget.html
#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTreeWidgetItem.html
#https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html

from PyQt5.QtWidgets    import QGridLayout
from PyQt5.QtWidgets    import QWidget, QLabel
from PyQt5.QtCore       import Qt

#draw
from PyQt5.QtGui        import QIcon, QPixmap
from PyQt5.QtCore       import QSize

import item_manager, elem_manager, option_widget
import edit_widget, common_func

import math

column_id = 2

tree_widget = None
modify_widget = None

class GroupTreeWidget(QTreeWidget):
    def __init__(self):
        global tree_widget
        
        super().__init__()
        self.initUI()
        
        self.elem_group = None
        
        tree_widget = self
        
    def initUI(self):
        #self.setRootIsDecorated(False)      #루트노드 화살표 안보이게
        self.setAlternatingRowColors(True)  #흰색/회색 번갈아가며 표시
        self.initHeader()
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 노드 클릭시... 는 아이템 체인지로 대체
        #self.itemClicked.connect(self.onClickNode)
        self.currentItemChanged.connect(self.onItemChanged)
        
    def initHeader(self):
        '''
        icon / name / ID / ingredients / result / Factory /
        Module / Etc
        '''
        list_header = ["Icon", "Name", "ID", "Ingredients", "Result", 
            "Factory", "Module", "Etc"]
        self.setHeaderLabels(list_header)
        
        size = QSize(96,32)
        self.headerItem().setSizeHint(0, size)
        self.resizeAll()
        
    def onItemChanged(self, current, previous):
        item = current
        elem = None
        if item is None:
            edit_widget.edit_widget.resetInfo()
        else:
            id = int(item.data(column_id, 0))
            elem = elem_manager.map_elem[id]
            edit_widget.edit_widget.setElem(elem)
        
        global modify_widget
        bEnable = \
            type(elem) == elem_manager.ElemGroup \
            and elem != self.elem_group
        modify_widget.bt_goInto.setEnabled( bEnable )
            
    def setCurrentSelect(self, elem):
        head = self.topLevelItem(0)
        cnt = head.childCount()
        item = None
        for i in range(0, cnt):
            tmp = head.child(i)
            id = int(tmp.data(column_id, 0))
            if id == elem.id:
                item = tmp
        if item is not None:
            self.setCurrentItem(item)
            
    def setTreeRootGroup(self, elem_group):
        self.elem_group = elem_group
        self.rebuildTree()
        
    def rebuildTree(self, keep_sel = False):
        if keep_sel:
            elem_before = edit_widget.edit_widget.elem
        self.clear()
        item_group = ElemTreeItem(self, self.elem_group, None)
        
        if self.elem_group is None:
            return
            
        # 정렬 : 그냥 child 순위
        for elem in self.elem_group.list_child:
            ElemTreeItem(self, elem, item_group)
            
        self.expandAll ()
        self.resizeAll()
        
        if keep_sel:
            edit_widget.edit_widget.setElem(elem_before)
        
    def updateItem(self, elem, bUpdateGroup = True):
        item_group = self.topLevelItem(0)
        if item_group.elem == elem:
            item_group.update()
            return
        for i in range(0, item_group.childCount()):
            child = item_group.child(i)
            child.update()
        if bUpdateGroup:
            item_group.update()
        self.resizeAll()
    
    def createButtonItem(self, icon, text):
        item_tree = QTreeWidgetItem()
        icon_item = QIcon()
        icon_item.addPixmap(common_func.getCommonPixmap(icon))
        item_tree.setText(0, text)
        item_tree.setIcon(0, icon_item)
        return item_tree
        
    def addGroup(self):
        elem = elem_manager.ElemGroup(None, self.elem_group)
        ElemTreeItem(self, elem, self.topLevelItem(0))
        
        #생성된 아이템 고르기
        self.setCurrentSelect(elem)
        self.topLevelItem(0).update()

    def addFactory(self):
        item = item_manager.getSortedItemList()[0]
        elem = elem_manager.ElemFactory(None, self.elem_group, item)
        ElemTreeItem(self, elem, self.topLevelItem(0))
        
        #생성된 아이템 고르기
        self.setCurrentSelect(elem)
        self.topLevelItem(0).update()
        
    def addSpecial(self):
        item = list(item_manager.map_special_factory.values())[0]
        elem = elem_manager.ElemSpecial(None, self.elem_group, item)
        ElemTreeItem(self, elem, self.topLevelItem(0))
        self.setCurrentSelect(elem)
        self.topLevelItem(0).update()

    def addCustom(self):
        elem = elem_manager.ElemCustom(None, self.elem_group)
        ElemTreeItem(self, elem, self.topLevelItem(0))
        self.setCurrentSelect(elem)
        self.topLevelItem(0).update()
        
    def resizeAll(self):
        for idx in range(self.columnCount()):
            self.resizeColumnToContents(idx)
        
# 트리용 아이템
class ElemTreeItem(QTreeWidgetItem):
    def __init__(self, treeWidget, elem, item_group):
        if elem is None:
            return
        super().__init__()
        self.elem = elem
        
        if item_group is None:
            treeWidget.addTopLevelItem(self)
        else:
            item_group.addChild(self)
            
        self.update()
        
    def makeListIcon(self, grid, map, iconSize):
        expend_right = option_widget.is_tree_expend_right
        num_right = option_widget.is_tree_num_right
        num_max = option_widget.tree_num_max
        list_key = list(map.keys())
        
        for i in range(0, len(list_key)):
            key = list_key[i]
            elemSub = map[key]
            num = 0
            if type(elemSub) == elem_manager.ElemMaterial:
                num = elemSub.num_need
            elif type(elemSub) == elem_manager.ElemProduct:
                num = elemSub.num_real
            item = item_manager.map_item[key]
            
            text = common_func.getAmountPerTime(num)
            label1 = QLabel()
            label1.setPixmap(item.getPixmap(iconSize, iconSize))
            label2 = QLabel(text)
            
            if expend_right:
                y = int(i/num_max)
                x = i % num_max
            else:
                y = i % num_max
                x = int(i/num_max)
                
            if num_right:
                grid.addWidget(label1, y, x*2)
                grid.addWidget(label2, y, x*2+1)
            else:
                y *= 2
                grid.addWidget(label1, y*2  , x)
                grid.addWidget(label2, y*2+1, x)
        
        if expend_right:
            strech_col = num_max
            strech_row = math.ceil(len(list_key)/num_max)
        else:
            strech_col = math.ceil(len(list_key)/num_max)
            strech_row = num_max
            
        if num_right:       strech_col *= 2
        else:               strech_row *= 2
        
        grid.setColumnStretch(strech_col, 1)
        grid.setRowStretch(strech_row, 1)
            
    def update(self):
        elem = self.elem
        iconSize = option_widget.icon_size
        
        widget_icon = QLabel()
        if type(elem) in [elem_manager.ElemFactory, elem_manager.ElemSpecial] and elem.recipe is not None:
            widget_icon.setPixmap(elem.recipe.getPixmap(iconSize, iconSize))
        elif type(elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]\
            and elem.item_goal is not None: 
            widget_icon.setPixmap(elem.item_goal.getPixmap(iconSize, iconSize))
        else:
            widget_icon.setPixmap(common_func.getCommonPixmap('factorio', iconSize, iconSize))
        
        widget_material = QWidget()
        grid_material = QGridLayout()
        widget_material.setLayout(grid_material)
        self.makeListIcon(grid_material, elem.map_material, iconSize)
        
        widget_product = QWidget()
        grid_product = QGridLayout()
        widget_product.setLayout(grid_product)
        self.makeListIcon(grid_product, elem.map_product, iconSize)
        
        #Factory
        widget_factory = QWidget()
        grid_factory = QGridLayout()
        widget_factory.setLayout(grid_factory)
        label1 = QLabel()
        if type(elem) == elem_manager.ElemGroup:
            label1.setPixmap(common_func.getCommonPixmap('factorio', iconSize, iconSize))
        elif type(elem) in [elem_manager.ElemFactory, elem_manager.ElemSpecial]:
            if elem.factory is not None:
                label1.setPixmap(elem.factory.getPixmap(iconSize, iconSize))
            else:
                label1.setPixmap(common_func.getCommonPixmap('factorio', iconSize, iconSize))
            
        str_factory_num = common_func.getAmountRound(elem.num_factory)
        label2 = QLabel(str_factory_num)
        grid_factory.addWidget(label1, 0, 0)
        grid_factory.addWidget(label2, 0, 1)
        
        #Module
        widget_module = QWidget()
        if type(elem) in [elem_manager.ElemFactory, elem_manager.ElemSpecial]:
            grid_module = QGridLayout()
            widget_module.setLayout(grid_module)
            x_max = 4
            grid_module.setColumnStretch(x_max+1,1)
            x = 0
            y = 0
            for name_module in elem.list_module:
                if x >= 4:
                    x = 0
                    y += 1
                module = item_manager.map_item[name_module]
                label = QLabel()
                label.setPixmap(module.getPixmap(iconSize, iconSize))
                grid_module.addWidget(label, y, x)
                x += 1
        
        #ETC
        widget_etc = QWidget()
        grid_etc = QGridLayout()
        widget_etc.setLayout(grid_etc)
        grid_etc.setColumnStretch(3,1)
        row = 0
        if type(self.elem) in [elem_manager.ElemGroup, elem_manager.ElemCustom]:
            if elem.energy_elect != 0:
                label1 = QLabel()
                label1.setPixmap(common_func.getCommonPixmap('electric', iconSize, iconSize))
                label2 = QLabel(common_func.getEnergyRound(elem.energy_elect))
                grid_etc.addWidget(label1, row, 0)
                grid_etc.addWidget(label2, row, 1)
                row = row + 1
            if elem.energy_fuel != 0:
                label1 = QLabel()
                label1.setPixmap(common_func.getCommonPixmap('fuel', iconSize, iconSize))
                label2 = QLabel(common_func.getEnergyRound(elem.energy_fuel))
                grid_etc.addWidget(label1, row, 0)
                grid_etc.addWidget(label2, row, 1)
                row = row + 1
        else:
            if elem.factory is not None and \
                (elem.energy_elect != 0 or elem.energy_fuel != 0):
                label1 = QLabel()
                name = 'electric'
                energy = elem.energy_elect
                if elem.factory.energy_source_type != 'electric':
                    name = 'fuel'
                    energy = elem.energy_fuel
                label1.setPixmap(common_func.getCommonPixmap(name, iconSize, iconSize))
                label2 = QLabel(common_func.getEnergyRound(energy))
                grid_etc.addWidget(label1, row, 0)
                grid_etc.addWidget(label2, row, 1)
                row = row + 1
        if elem.emission != 0:
            label1 = QLabel()
            label1.setPixmap(common_func.getCommonPixmap('pollution', iconSize, iconSize))
            label2 = QLabel(common_func.getAmountRound(elem.emission))
            grid_etc.addWidget(label1, row, 0)
            grid_etc.addWidget(label2, row, 1)
            row = row + 1
        
        '''
        icon / name / ID / ingredients / result / Factory /
        Module / Etc
        '''
        treeWidget = self.treeWidget()
        treeWidget.setItemWidget(self, 0, widget_icon)
        self.setText(1, elem.name)
        self.setText(column_id, str(elem.id))
        treeWidget.setItemWidget(self, 3, widget_material)
        treeWidget.setItemWidget(self, 4, widget_product)
        treeWidget.setItemWidget(self, 5, widget_factory)
        treeWidget.setItemWidget(self, 6, widget_module)
        treeWidget.setItemWidget(self, 7, widget_etc)
        
        if type(elem) == elem_manager.ElemGroup :
            self.setBackground(0, Qt.gray);
        