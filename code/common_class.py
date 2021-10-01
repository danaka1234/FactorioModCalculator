# coding: utf-8
import os

from PyQt5.QtCore       import QSize
from PyQt5.QtGui        import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets    import QPushButton, QLabel, QScrollArea
from PyQt5.QtWidgets    import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QWidget, QDialog

import elem_manager, item_manager, common_func

#QTooltip : html 문법으로 추정됨
#테이블 세로 중앙
#https://zetawiki.com/wiki/%ED%85%8C%EC%9D%B4%EB%B8%94_TD_%EC%84%B8%EB%A1%9C_%EC%A4%91%EC%95%99
#https://www.codingfactory.net/10232
    
def getRecipeToolTipText(recipe):
    name = recipe.getName()
    time = recipe.getTime()
    list_product = recipe.getListProduct()
    list_material = recipe.getListMaterial()
    lem_max = max(len(list_product), len(list_material))
    str_temp = ''
    
    for i in range(lem_max):
        str_temp += '<tr>'
        str_temp +=     '<td>'
        if len(list_material) > i:
            elem = list_material[i]
            item = item_manager.map_item[elem[0]]
            str_temp += '<img src=\"'
            str_temp += item.getIconPath()
            str_temp += '\" width="16" height="16">'
            str_temp += ' : ' + str(elem[1])
        str_temp +=     '</td>'
        
        str_temp +=     '<td>'
        if len(list_product) > i:
            elem = list_product[i]
            item = item_manager.map_item[elem[0]]
            str_temp += '<img src=\"'
            str_temp += item.getIconPath()
            str_temp += '\" width="16" height="16">'
            str_temp += ' : ' + str(elem[1])
        str_temp +=     '</td>'
        str_temp += '</tr>'
    
    str_ret =   '<style>.td_m {vertical-align:top}</style>'+\
        name +\
        '<table><tr><td class=\'td_m\'>' +\
            '<img src=\"' +\
            common_func.getCommonPath('clock') +\
            '\" width="16" height="16">' +\
            ':' + str(time) +\
        '</td></tr></table>' +\
        '<table>'+\
            '<thead><tr><th>Ingred </th><th>Result</th></tr></thead>'+\
            '<tbody>' + str_temp + '</tbody>'+\
        '</table>'
        
    return str_ret
    
def getFactoryToolTipText(factory):
    name = factory.getName()
    speed = factory.crafting_speed
    pollution = factory.energy_source_emissions
    energy = common_func.getEnergyRound(factory.energy_usage)
    energy_type = ''
    if factory.energy_source_type == 'electric':
        energy_type = common_func.getCommonPath('electric')
    else:
        energy_type = common_func.getCommonPath('fuel')
    
    str_ret =   '<style>.td_m {vertical-align:top}</style>'+\
        name +\
        '<table><tr><td>' +\
            '<img src=\"' +\
            common_func.getCommonPath('clock') +\
            '\" width="16" height="16">' +\
            ' : x' + str(speed) +\
        '</td></tr><tr><td>' +\
            '<img src=\"' +\
            energy_type +\
            '\" width="16" height="16">' +\
            ' : ' + energy +\
        '</td></tr><tr><td>' +\
            '<img src=\"' +\
            common_func.getCommonPath('pollution') +\
            '\" width="16" height="16">' +\
            ' : ' + str(pollution) + '/m'\
        '</td></tr></table>'
        
    return str_ret
    
def getModuleToolTipText(module):
    return 'module'

class GridIcon(QVBoxLayout):
    def __init__(self, parent):
        self.edit_widget = parent
        
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
        self.grid = QGridLayout()
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.bt_item)
        hbox.addWidget(self.bt_recipe)
        hbox.addWidget(self.bt_factory)
        self.addLayout(hbox)
        self.addLayout(self.grid)
        self.addStretch(1)
        
        self.elem = None
        
        self.resetInfo()
        
    def resetInfo(self):
        for i in reversed(range(self.grid.count())): 
            self.grid.itemAt(i).widget().setParent(None)

        pixmap = common_func.getCommonPixmap('factorio')
        self.bt_item.setIcon(QIcon(pixmap))
        self.bt_item.setToolTip('')
        self.bt_recipe.setIcon(QIcon(pixmap))
        self.bt_recipe.setToolTip('')
        self.bt_factory.setIcon(QIcon(pixmap))
        self.bt_factory.setToolTip('')
        self.elem = None
        self.setEnabled(False)
        
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
        self.bt_recipe.setToolTip(getRecipeToolTipText(elem.recipe))
        if elem.factory is not None:
            self.bt_factory.setIcon(elem.factory.getIcon())
            self.bt_factory.setToolTip(getFactoryToolTipText(elem.factory))
        
        map_module = dict()
        for module in elem.list_module:
            if map_module.get(module) is None:
                map_module[module] = 0
            map_module[module] += 1
        
        i = 0
        for key in map_module:
            num = map_module[key]
            module = item_manager.map_item[key]
            x = i % 2 * 2
            y = i / 2
            label1 = QLabel()
            label1.setPixmap(module.getPixmap(16, 16))
            label2 = QLabel('x' + str(num))
            self.grid.addWidget(label1, y, x)
            self.grid.addWidget(label2, y, x+1)
            i += 1
        self.setEnabled(True)
            
    def onClickItem(self):
        dlg = ChangePopup(item_manager.getSortedItemList(), 'item')
        ret = dlg.exec_()
        if ret == 1:
            item = item_manager.map_item[dlg.selected]
            self.edit_widget.elem.changeItem(item)
            self.edit_widget.setElem(self.edit_widget.elem, True)
        
    def onClickRecipe(self):
        if self.elem is None or self.elem.item_goal is None:
            return
            
        list_recipe = []
        
        for name_recipe in self.elem.item_goal.list_madeby:
            recipe = item_manager.map_recipe[name_recipe]
            list_recipe.append(recipe)
        list_recipe.sort(key=lambda elem: elem.order)
        
        dlg = ChangePopup(list_recipe, 'recipe')
        ret = dlg.exec_()
        if ret == 1:
            if dlg.selected == self.elem.recipe.name:
                return
            recipe = item_manager.map_recipe[dlg.selected]
            self.edit_widget.elem.changeRecipe(recipe, bItemChange=False)
            self.edit_widget.setElem(self.edit_widget.elem, True)
        
    def onClickFactory(self):
        if self.elem is None or self.elem.item_goal is None:
            return
            
        list_factory = item_manager.getFactoryListByRecipe(self.elem.recipe)
        
        dlg = ChangePopup(list_factory, 'factory')
        ret = dlg.exec_()
        if ret == 1:
            if dlg.selected == self.elem.factory.name:
                return
            factory = item_manager.map_factory[dlg.selected]
            self.edit_widget.elem.changeFactory(factory)
            self.edit_widget.setElem(self.elem, True)
            self.edit_widget.tree_widget.updateItem(self.elem)
        
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
        
class ChangePopup(QDialog):
    #open_dialog 참고
    def __init__(self, list_item, item_type):
        super().__init__()
        self.selected = ''
        self.list_item = list_item
        self.item_type = item_type
        self.list_button = []
        
        self.initUI()
        if item_type == 'item':
            self.initAllItem()
        else:
            self.initItems()
        
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
        
        pos = QCursor().pos()
        width = 380
        if self.item_type == 'item':
            height = 800
        elif self.item_type == 'link item':
            height = min(800, \
                (\
                    int(len(self.list_item[0]) / 10 + 1) + \
                    int(len(self.list_item[1]) / 10 + 1)  \
                ) * 60 + 60)
        else:
            height = min(800, int(len(self.list_item) / 10 + 1) * 60)
        x = pos.x() - width/2
        y = max(pos.y() - height/2, 30)
        
        self.grid.setColumnStretch(11, 1)
        
        self.setWindowTitle('Select '+ self.item_type)
        self.setGeometry(x, y, width, height)
        
    def addButton(self, item, x, y, bAddProduct=False, bProduct=False):
        bt_item = QPushButton()
        bt_item.setFixedSize(32, 32)
        bt_item.setIconSize(QSize(32, 32))
        bt_item.clicked.connect(self.onButton)
        if item is not None:
            bt_item.setIcon(item.getIcon())
            bt_item.setToolTip(item.getName())
            bt_item.name_item = item.name
        else:
            bt_item.name_item = None
        if bAddProduct:
            bt_item.bProduct = bProduct
        
        self.grid.addWidget(bt_item, y, x)
        self.list_button.append([bt_item])
        return bt_item
        
    def initItems(self):
        y = 0
        if self.item_type in ['recipe','factory', 'module']:
            self.addButtons(self.list_item)
        elif self.item_type == 'link item':
            y = 1
            self.grid.addWidget(QLabel('Ingredients'), 0, 0, 1, -1)
            self.grid.setRowMinimumHeight(0, 30)
            y = self.addButtons(self.list_item[0], y, True, False)
            self.grid.addWidget(QLabel('Results'), y+1, 0, 1, -1)
            self.grid.setRowMinimumHeight(y+1, 30)
            y += 2
            y = self.addButtons(self.list_item[1], y, True, True)
        else:
            pass
        self.grid.setRowStretch(y+1, 1)
            
    def addButtons(self, list_item, y=0, bAddProduct=False, bProduct=False):
        x = 0
        for item in list_item:
            if x >= 10:
                x = 0
                y += 1
            self.addButton(item, x, y, bAddProduct, bProduct)
            x += 1
        return y
        
    def initAllItem(self):
        list_recipe_popup = self.list_item
        
        y = 0
        for rap_g in list_recipe_popup:
            self.grid.addWidget(QLabel(rap_g.item.getName()), y, 0, 1, -1)
            self.grid.setRowMinimumHeight(y, 30)
            y += 1
            for rap_s in rap_g.list_sub:
                x = 0
                for item in rap_s.list_sub:
                    if x >= 10:
                        x = 0
                        y += 1
                    self.addButton(item, x, y)
                    x += 1
                y += 1
        self.grid.setRowStretch(y+1, 1)
        
    def onButton(self):
        bt = self.sender()
        self.selected = bt.name_item
        if self.item_type == 'link item':
            self.bProduct = bt.bProduct
        self.accept()
        
                        
