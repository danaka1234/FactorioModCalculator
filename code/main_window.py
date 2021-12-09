# coding: utf-8

import sys, os
import PyQt5

#core
from PyQt5.QtWidgets    import QMainWindow, QApplication, QDesktopWidget

#layout
from PyQt5.QtWidgets    import QVBoxLayout

#widget
from PyQt5.QtWidgets    import QWidget, QTabWidget, QGridLayout, QCheckBox, QComboBox
from PyQt5.QtWidgets    import QPushButton, QLabel

import config_manager
import open_dialog, template_manager, elem_manager, item_manager
import loading_widget, option_widget

import group_tree, edit_widget, elem_manager

modify_widget = None

class MainWindow(QMainWindow):
    '''
    QMainWIndow 의 경우, layout 쓰면 already has a layout 에러 메시지가 뜨는 듯 함
    setCentralWidget 을 사용해야 한다
    https://freeprog.tistory.com/326
    '''
    bLoad_file    = False
    load_widget   = None
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadTemplate()
        list = item_manager.getSortedItemList()
        
    def initUI(self):
        self.title = config_manager.name_app
        self.setWindowTitle(self.title)
        w = int(config_manager.get_config('display', 'window_width'))
        h = int(config_manager.get_config('display', 'window_height'))
        self.setGeometry(0, 0, w, h)
        
        # set windows center
        self.moveWindowCenter()
        
        #init load widget
        self.load_widget = loading_widget.LoadingWidget(self)
        self.main_widget = None
        self.tab_widget = None
        
        #move to 2nd or other monitor
        num_monitor = int(config_manager.get_config('display', 'display_monitor'))
        num_monitor = max(0, num_monitor - 1)
        pos_cur = self.pos()
        pos_monitor = QDesktopWidget().screenGeometry(num_monitor)
        
        self.move(pos_cur.x() + pos_monitor.left(), pos_cur.y() + pos_monitor.top())
        
        self.setCentralWidget(self.load_widget)
        self.show()
    
    def moveWindowCenter(self):
        frameGm = self.frameGeometry()
        #screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        screen = 0
        centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
    
    def loadTemplate(self):
        auto_load_from_data = config_manager.get_config('template', 'auto_load_from_data', 'boolean')
        auto_load_from_template  = config_manager.get_config('template', 'auto_load_from_template' , 'boolean')
        
        if auto_load_from_template or auto_load_from_data:
            self.setCentralWidget(self.load_widget)
            bLoadTmpDir = auto_load_from_template
            self.load_widget.doLoad(bLoadTmpDir, False, \
                path_template_dir = config_manager.get_config('template', 'path_template_dir'))
        else:
            self.load_widget.setMsg('Waiting for selecting load mode')
            self.loadFromDlg()
        
    def loadFromDlg(self):
        #modal open
        dlg = open_dialog.OpenDialog(self)
        ret = dlg.exec_()
        if ret == True :
            bLoadTmpDir = (dlg.type == 'dir')
            path_template_dir = None
            if dlg.type == 'dir':
                path_template_dir = dlg.edit_tdir.text()
            self.setCentralWidget(self.load_widget)
            self.load_widget.doLoad(bLoadTmpDir, False, \
                path_template_dir = path_template_dir)
        else:
            self.load_widget.setMsg('Don\'t load', False)
            
    def setTabWidget(self):
        self.setCentralWidget(ModifyWidget())

class ModifyWidget(QWidget):
    def __init__(self):
        self.group = elem_manager.map_elem[0]
        
        super().__init__()
        self.initUI()
        self.setGroup(self.group)
        
        global modify_widget
        modify_widget = self
    
    def initUI(self):
        vbox = QVBoxLayout()
        grid = QGridLayout()
        grid_rapper = QGridLayout()
        vbox.addLayout(grid)
        vbox.addLayout(grid_rapper)
        
        # grid
        self.bt_goOut = QPushButton('Go out')
        self.bt_goInto = QPushButton('Go into')
        grid.addWidget(self.bt_goOut,   0, 2)
        grid.addWidget(self.bt_goInto,  0, 3)
        
        self.bt_addGroup = QPushButton('Add Group')
        self.bt_addFactory = QPushButton('Add Factory')
        grid.addWidget(self.bt_addGroup,    0, 4)
        grid.addWidget(self.bt_addFactory,  0, 5)
        grid.setColumnStretch(6,1)
        self.bt_edit = QPushButton('Hide\nEdit')
        self.bt_edit.setMaximumWidth(50)
        grid.addWidget(self.bt_edit,        0, 7)
        self.bt_option = QPushButton('Hide\nOption')
        self.bt_option.setMaximumWidth(50)
        grid.addWidget(self.bt_option,      0, 8)
        
        self.label_group = QLabel('None(0)')
        grid.addWidget(QLabel('Current Group')  , 0, 0)
        grid.addWidget(self.label_group         , 0, 1)
        
        # grid_rapper
        grid_rapper.addWidget(group_tree.GroupTreeWidget()  , 0, 0)
        grid_rapper.addWidget(edit_widget.EditWidget()      , 0, 1)
        grid_rapper.addWidget(option_widget.OptionWidget()  , 0, 2)
        grid_rapper.setColumnStretch(0, 1)
        
        self.bt_addGroup.clicked.connect(group_tree.tree_widget.addGroup)
        self.bt_addFactory.clicked.connect(group_tree.tree_widget.addFactory)
        self.bt_edit.clicked.connect(self.toggleEditWidget)
        self.bt_option.clicked.connect(self.toggleOptionWidget)
        
        self.setLayout(vbox)
        
    def setGroup(self, group):
        self.group = group
        text = group.name + '(' + str(group.id) + ')'
        self.label_group.setText(text)
        self.bt_goOut.setEnabled(group.id != 0)
        group_tree.tree_widget.setTreeRootGroup(group)

    def toggleEditWidget(self):
        global modify_widget
        if edit_widget.edit_widget.isVisible():
            if modify_widget is not None:
                modify_widget.bt_edit.setText("Show\nEdit")
            edit_widget.edit_widget.hide()
        else:
            if modify_widget is not None:
                modify_widget.bt_edit.setText("Hide\nEdit")
            edit_widget.edit_widget.show()
    
    def toggleOptionWidget(self):
        global modify_widget
        if option_widget.option_widget.isVisible():
            if modify_widget is not None:
                modify_widget.bt_option.setText("Show\nOption")
            option_widget.option_widget.hide()
        else:
            if modify_widget is not None:
                modify_widget.bt_option.setText("Hide\nOption")
            option_widget.option_widget.show()
            

# --------------------------- debug
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainMenu = MainWindow()
    
    #sys.exit(app.exec_())
    app.exec_()

