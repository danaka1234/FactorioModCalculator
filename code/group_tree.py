# coding: utf-8

#core
from PyQt5.QtWidgets    import QTreeWidget, QTreeWidgetItem, QHeaderView 
#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTreeWidget.html
#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTreeWidgetItem.html
#https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html

from PyQt5.QtWidgets    import QGridLayout
from PyQt5.QtWidgets    import QWidget, QLabel

#draw
from PyQt5.QtGui        import QIcon, QPixmap

import item_manager, elem_manager, config_manager
import recipe_form, common_func

class GroupTreeWidget(QTreeWidget):
    def __init__(self, edit_widget, bCreateTab):
        super().__init__()
        self.bCreateTab = bCreateTab
        self.edit_widget = edit_widget
        self.initUI()
        
        self.elem_group = None
        
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
        name / ID / ingredients / result / Factory /
        Module / Etc
        '''
        list_header = ["Name", "ID", "Ingredients", "Result", 
            "Factory", "Module", "Etc"]
        self.setHeaderLabels(list_header)
        
        for idx in range(self.columnCount()):
            self.resizeColumnToContents(idx)
        
    def onItemChanged(self, current, previous):
        item = current
        if item is None:
            self.edit_widget.resetInfo()
            return
        if item.text(0) == 'Add Group' or item.text(0) == 'Add Factory':
            bGroup = item.text(0) == 'Add Group'
            elem = None
            if bGroup:
                elem = elem_manager.ElemGroup(None, self.elem_group, None)
            else:
                elem = elem_manager.ElemFactory(None, self.elem_group)
            ElemTreeItem(self, elem, self.topLevelItem(0))
            
            #생성된 아이템 고르기
            self.edit_widget.setElem(elem)
            self.topLevelItem(0).update()
        else:
            id = int(item.data(1, 0))
            elem = elem_manager.map_elem[id]
            self.edit_widget.setElem(elem)
            
    def setCurrentSelect(self, elem):
        head = self.topLevelItem(0)
        cnt = head.childCount()
        item = None
        for i in range(0, cnt):
            tmp = head.child(i)
            id = int(tmp.data(1, 0))
            if id == elem.id:
                item = tmp
        if item is not None:
            self.setCurrentItem(item)
            
    def setTreeRootGroup(self, elem_group):
        self.elem_group = elem_group
        self.rebuildTree()
        
    def rebuildTree(self):
        self.clear()
        item_group = ElemTreeItem(self, self.elem_group, None)
        
        # 정렬 : 그냥 child 순위
        for elem in self.elem_group.list_child:
            ElemTreeItem(self, elem, item_group)
            
        
        # 팩토리/그룹 추가 버튼
        self.addTopLevelItem(self.createButtonItem('factorio', 'Add Group'))
        self.addTopLevelItem(self.createButtonItem('factory' , 'Add Factory'))
        
        self.expandAll ()
        for idx in range(self.columnCount()):
            self.resizeColumnToContents(idx)
        
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
    
    def createButtonItem(self, icon, text):
        item_tree = QTreeWidgetItem()
        icon_item = QIcon()
        icon_item.addPixmap(common_func.getCommonPixmap(icon))
        item_tree.setText(0, text)
        item_tree.setIcon(0, icon_item)
        return item_tree

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
        
    def update(self):
        elem = self.elem
        
        icon_item = QIcon()
        if type(elem) == elem_manager.ElemFactory and elem.recipe is not None:
            icon_item.addPixmap(elem.recipe.getPixmap())
        elif type(elem) == elem_manager.ElemGroup and elem.item_goal is not None: 
            icon_item.addPixmap(elem.item_goal.getPixmap())
        else:
            icon_item.addPixmap(common_func.getCommonPixmap('factorio'))
            
        widget_material = QWidget()
        grid_material = QGridLayout()
        widget_material.setLayout(grid_material)
        list_key = list(elem.map_material.keys())
        for i in range(0, len(list_key)):
            key = list_key[i]
            material = elem.map_material[key]
            item = item_manager.map_item[key]
            
            text = common_func.getAmountPerTime(material.num_need)
            label1 = QLabel()
            label1.setPixmap(item.getPixmap(16, 16))
            label2 = QLabel(text)
            grid_material.addWidget(label1, i, 0)
            grid_material.addWidget(label2, i, 1)
        
        widget_product = QWidget()
        grid_product = QGridLayout()
        widget_product.setLayout(grid_product)
        list_key = list(elem.map_product.keys())
        for i in range(0, len(list_key)):
            key = list_key[i]
            product = elem.map_product[key]
            item = item_manager.map_item[key]
            
            text = common_func.getAmountPerTime(product.num_real)
            label1 = QLabel()
            label1.setPixmap(item.getPixmap(16, 16))
            label2 = QLabel(text)
            grid_product.addWidget(label1, i, 0)
            grid_product.addWidget(label2, i, 1)
        
        icon_factory = QIcon()
        if type(elem) == elem_manager.ElemGroup:
            icon_factory.addPixmap(common_func.getCommonPixmap('factorio'))
        else:
            if elem.factory is not None:
                icon_factory.addPixmap(elem.factory.getPixmap())
            else:
                icon_factory.addPixmap(common_func.getCommonPixmap('factorio'))
            
        str_factory_num = common_func.getAmountRound(elem.num_factory)
        
        str_energy      = 'Energy    : ' + common_func.getEnergyRound(elem.energy)
        str_emission    = 'Pollution : ' + common_func.getAmountRound(elem.emission) + '/m'
        str_etc = str_energy + '\n' + str_emission
        
        '''
        name / ID / ingredients / result / Factory /
        Module / Etc
        '''
        treeWidget = self.treeWidget()
        self.setIcon(0, icon_item)
        self.setText(0, elem.name)
        self.setText(1, str(elem.id))
        treeWidget.setItemWidget(self, 2, widget_material)
        treeWidget.setItemWidget(self, 3, widget_product)
        
        self.setIcon(4, icon_factory)
        self.setText(4, str_factory_num)
        
        self.setText(5, str(0))
        self.setText(6, str_etc)
        