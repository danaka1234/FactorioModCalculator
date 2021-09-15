# coding: utf-8

import sys
import queue    #https://docs.python.org/ko/3.8/library/queue.html

#core
from PyQt5.QtWidgets    import QTreeWidget, QTreeWidgetItem, QHeaderView 
#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTreeWidget.html
#https://doc.qt.io/qtforpython/PySide2/QtWidgets/QTreeWidgetItem.html
#https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html

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
        name / ID / result / ingredients / 
        Factory / Speed / Productivity
        '''
        list_header = ["Name", "ID", "Result", "Ingredients", 
            "Factory", "Speed", "Productivity"]
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
            self.updateTree()
            
            #생성된 아이템 고르기
            self.edit_widget.setElem(elem)
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
        item_group = self.createitem_tree(self.elem_group)
        self.addTopLevelItem(item_group)
        
        list_item = []
        
        # 정렬 : 그냥 child 순위
        for elem in self.elem_group.list_child:
            list_item.append(self.createitem_tree(elem))
            
        item_group.addChildren(list_item)
        
        # 팩토리/그룹 추가 버튼
        self.addTopLevelItem(self.createButtonItem('factorio', 'Add Group'))
        self.addTopLevelItem(self.createButtonItem('factory' , 'Add Factory'))
        
        self.expandAll ()
        for idx in range(self.columnCount()):
            self.resizeColumnToContents(idx)
    
    def updateTree(self):
        self.rebuildTree()
            
    # 트리용 아이템 만들기
    def createitem_tree(self, elem):
        if elem is None:
            return
            
        item_tree = QTreeWidgetItem()
        item_tree.bNeedUpdate = False
        
        icon_item = QIcon()
        if type(elem) == elem_manager.ElemFactory and elem.recipe is not None:
            icon_item.addPixmap(elem.recipe.getPixmap())
        elif type(elem) == elem_manager.ElemGroup and elem.item_goal is not None: 
            icon_item.addPixmap(elem.item_goal.getPixmap())
        else:
            icon_item.addPixmap(common_func.getCommonPixmap('factorio'))
        
        str_material = ''
        for key in elem.map_material.keys():
            material = elem.map_material[key]
            name_material = item_manager.getItemName(key)
            str_material = str_material + name_material + ' : ' \
                + common_func.getAmountPerTime(material.num_need)\
                + '\n'
        str_material = str_material[0:-1]
        
        str_product  = ''
        for key in elem.map_product.keys():
            product = elem.map_product[key]
            name_product = item_manager.getItemName(key)
            str_product = str_product + name_product + ' : '\
                + common_func.getAmountPerTime(product.num_real)\
                + '\n'
        str_product = str_product[0:-1]
        
        icon_factory = QIcon()
        if type(elem) == elem_manager.ElemGroup:
            icon_factory.addPixmap(common_func.getCommonPixmap('factorio'))
        else:
            icon_factory.addPixmap(elem.factory.getPixmap())
            
        str_factory_num = common_func.getAmountRound(elem.num_factory)
        
        '''
        name / ID / result / ingredients / 
        Factory / Speed / Productivity
        '''
        item_tree.setIcon(0, icon_item)
        item_tree.setText(0, elem.name)
        item_tree.setText(1, str(elem.id))
        item_tree.setText(2, str_product )
        item_tree.setText(3, str_material)
        
        item_tree.setIcon(4, icon_factory)
        item_tree.setText(4, str_factory_num)
        
        item_tree.setText(5, str(0))
        item_tree.setText(5, str(0))
        
        return item_tree
    
    def createButtonItem(self, icon, text):
        item_tree = QTreeWidgetItem()
        item_tree.bNeedUpdate = False
        icon_item = QIcon()
        icon_item.addPixmap(common_func.getCommonPixmap(icon))
        item_tree.setText(0, text)
        item_tree.setIcon(0, icon_item)
        return item_tree