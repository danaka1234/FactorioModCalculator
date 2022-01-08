# coding: utf-8
import os

from PyQt5.QtCore       import QSize
from PyQt5.QtGui        import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets    import QPushButton, QLabel, QScrollArea
from PyQt5.QtWidgets    import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QWidget, QDialog

    
class ChangePopup(QDialog):
    #open_dialog 참고
    def __init__(self, list_item, title, hidden=False, group=False):
        super().__init__()
        self.selected = ''
        self.list_item = list_item
        self.hidden = hidden
        self.group = group
        
        self.initUI(title)
        self.initItems()
        
    def initUI(self, title):
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
        if self.group:
            height = 800
        else:
            height = min(800, int(len(self.list_item) / 10 + 1) * 60)
        x = pos.x() - width/2
        y = max(pos.y() - height/2, 30)
        
        self.grid.setColumnStretch(11, 1)
        
        self.setWindowTitle('Select '+ title)
        self.setGeometry(x, y, width, height)
        
    def initItems(self):
        y = 0
        if not self.group:
            self.addButtons(self.list_item)
        else:
            self.initAllItem()
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
        
    def initAllItem(self):
        list_item_group = self.list_item
        
        y = 0
        for rap_g in list_item_group:
            self.grid.addWidget(QLabel(rap_g.item.getName()), y, 0, 1, -1)
            self.grid.setRowMinimumHeight(y, 30)
            y += 1
            for rap_s in rap_g.list_sub:
                x = 0
                for item in rap_s.list_sub:
                    if not self.hidden and \
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
        self.accept()
        