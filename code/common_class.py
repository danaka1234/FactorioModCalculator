# coding: utf-8
import os

from PyQt5.QtCore       import QSize
from PyQt5.QtGui        import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets    import QPushButton, QLabel, QScrollArea
from PyQt5.QtWidgets    import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QWidget, QDialog

#QTooltip : html 문법으로 추정됨
#테이블 세로 중앙
#https://zetawiki.com/wiki/%ED%85%8C%EC%9D%B4%EB%B8%94_TD_%EC%84%B8%EB%A1%9C_%EC%A4%91%EC%95%99
#https://www.codingfactory.net/10232
    
class ChangePopup(QDialog):
    #open_dialog 참고
    def __init__(self, list_item, item_type, custom=False):
        super().__init__()
        self.selected = ''
        self.list_item = list_item
        self.item_type = item_type
        self.list_button = []
        self.custom = custom
        
        self.initUI()
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
        
    def initItems(self):
        y = 0
        if self.item_type in ['recipe','factory', 'module']:
            self.addButtons(self.list_item)
        elif self.item_type == 'item':
            self.initAllItem()
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
                    if not self.custom and \
                        (len(item.list_madeby) == 0 or 'hidden' in item.flags):
                        continue
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
        #if self.item_type == 'link item':
        #    self.bProduct = bt.bProduct
        self.accept()
        
                        
