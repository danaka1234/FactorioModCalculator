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
        id = int(item.data(1, 0))
        elem = elem_manager.map_elem[id]
        self.edit_widget.setInfoEW(elem)
        
    def initTree(self, list_args):
        if self.bCreateTab and self.elem_group is not None:
            elem_manager.delElemId(self.elem_group)
    
        elem_group = elem_manager.ElemGroup(None, None, None)
        elem_group.initGroup(list_args)
        
        self.initTreeByGroup(elem_group)

    def initTreeByGroup(self, elem_group):
        self.clear()
        
        self.elem_group = elem_group
        
        item_group = self.initItemByElem(elem_group)
        self.addTopLevelItem(item_group)
        
        list_item = []
        
        if elem_group.id_root is not None:
            # 정렬 type 1 : 레벨 단위
            # TODO : 언젠간 없애야함
            node_root = elem_manager.map_elem[elem_group.id_root]
        
            map = dict()
            map[node_root.id] = node_root
            q = queue.PriorityQueue()
            q.put(node_root)
            while not q.empty():
                elem = q.get()
                list_item.append(self.initItemByElem(elem))
                
                for key in elem.map_material:
                    for link_child in elem.map_material[key].list_link:
                        node = link_child.producer
                        map[id] = node
                        q.put(node)
        else:
            # 정렬 type 2 : 그냥 child 순위
            for elem in elem_group.list_child:
                list_item.append(self.initItemByElem(elem))
        
        item_group.addChildren(list_item)
        self.expandAll ()
        for idx in range(self.columnCount()):
            self.resizeColumnToContents(idx)
            
    def initItemByElem(self, elem):
        item = QTreeWidgetItem()
        self.setInfoGT(elem, item)
        return item
            
    def setInfoGT(self, elem, item = None):
        if elem is None:
            return
        if item is None:
            if self.elem_group.id == elem.id:
                item = self.topLevelItem(0)
            else:
                item_parent = self.topLevelItem(0)
                for i in range(item_parent.childCount()):
                    item_tmp = item_parent.child(i)
                    if int(item_tmp.data(1, 0)) == elem.id:
                        item = item_tmp
                        break
                        
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
        item.setIcon(0, icon_item)
        item.setText(0, elem.name)
        item.setText(1, str(elem.id))
        item.setText(2, str_product )
        item.setText(3, str_material)
        
        item.setIcon(4, icon_factory)
        item.setText(4, str_factory_num)
        
        item.setText(5, str(0))
        item.setText(5, str(0))
        