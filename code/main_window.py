# coding: utf-8

import sys, os
import PyQt5

#core
from PyQt5.QtWidgets    import QMainWindow, QApplication, QDesktopWidget

#layout

#widget
from PyQt5.QtWidgets    import QWidget, QTabWidget, QGridLayout, QCheckBox, QComboBox

import config_manager
import open_dialog, loading_widget, t2_modify, template_manager, elem_manager, item_manager

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
        self.setGeometry(300, 100, 1000, 600)
        
        # set windows center
        self.moveWindowCenter()
        
        #init load widget
        self.load_widget = loading_widget.LoadingWidget(self)
        self.main_widget = None
        self.tab_widget = None
        
        #move to 2nd or other monitor
        num_monitor = int(config_manager.get_config('ui', 'display_monitor'))
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
        self.main_widget = t2_modify.ModifyWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.show()
        
    '''
    def checkAutoUpdate(self):
        config_manager.auto_update = self.check_auto.isChecked()
    '''
        
    def checkExpensive(self):
        config_manager.expensive = self.check_expensive.isChecked()
        
    def changeCBTime(self):
        config_manager.time_config = self.cb_time.currentIndex()
    

# --------------------------- debug
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainMenu = MainWindow()
    
    #sys.exit(app.exec_())
    app.exec_()

