#-*- coding:utf-8 -*-

import sys, os
import PyQt5

#core
from PyQt5.QtCore       import Qt
from PyQt5.QtWidgets    import QApplication, QWidget, QDialog

#layout
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QVBoxLayout

#widget
from PyQt5.QtWidgets import QLabel, QCheckBox, QLineEdit, QPushButton
from PyQt5.QtWidgets import QScrollArea, QGroupBox, QRadioButton

import config_manager, item_manager

class OpenDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()
        self.list_check = []
        
    def initUI(self):
        #vboxTop > scrollArea > widgetTop > vboxMiddle ----------
        vboxTop = QVBoxLayout()
        sa = QScrollArea()
        widgetTop = QWidget()
        vboxMiddle = QVBoxLayout()
        gb1 = QGroupBox('Load Template')
        gb2 = QGroupBox('Load Factories')
        vboxTop.addWidget(sa)
        sa.setWidget(widgetTop)
        sa.setWidgetResizable(True)
        widgetTop.setLayout(vboxMiddle)
        vboxMiddle.addWidget(gb1)
        vboxMiddle.addWidget(gb2)

        # gb1 > vbox1 ------------------------------
        vbox1 = QVBoxLayout()
        gb1.setLayout(vbox1)
        
        self.radio_tmp_origin = QRadioButton('Load Template by original file')
        vbox1.addWidget(self.radio_tmp_origin)
        vbox1.addSpacing(5)
        
        vbox1.addWidget(QLabel('Original Factorio Path'))
        self.edit_factorio = QLineEdit(config_manager.path_factorio)
        vbox1.addWidget(self.edit_factorio)
        vbox1.addWidget(QLabel('Factorio MOD Path')) #path_mods
        self.edit_mod = QLineEdit(config_manager.path_mods)
        vbox1.addWidget(self.edit_mod)
        vbox1.addSpacing(5)
        
        button = QPushButton('Reload MOD List')
        button.clicked.connect(self.initScrollbar_Mods)
        vbox1.addWidget(button)
        vbox1.addSpacing(5)
        
        mods_area = QScrollArea(self)
        mods_area.setWidgetResizable(True)
        #mods_area.setStyleSheet("background-color: white;")
        mods_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        vbox1.addWidget(mods_area)
        
        #https://stackoverflow.com/questions/47930677/pythonpyqt5-how-to-use-qscrollarea-for-one-or-many-qgroupbox
        #QScrollArea 안에 Widget 넣고 거기에 setLayout 해야 정상작동함
        widget = QWidget()
        mods_area.setWidget(widget)
        self.vbox_mods = QVBoxLayout(widget)
        self.initScrollbar_Mods()
        vbox1.addSpacing(5)
        
        self.radio_tmp_jcon = QRadioButton('Load Template by JSON, Directory')
        vbox1.addWidget(self.radio_tmp_jcon)
        vbox1.addWidget(QLabel('Directory Path'))
        self.edit_tdir = QLineEdit(config_manager.get_config('template', 'path_template_dir'))
        vbox1.addWidget(self.edit_tdir)
        vbox1.addSpacing(5)
        
        # gb2 > vbox2 ------------------------------
        vbox2 = QVBoxLayout()
        gb2.setLayout(vbox2)
        
        self.radio4 = QRadioButton('Don\'t load factories')
        #TODO : delete
        self.radio4.setEnabled(False)
        vbox2.addWidget(self.radio4)
        vbox2.addSpacing(5)
        
        self.radio6 = QRadioButton('Load by json file')
        #TODO : delete
        self.radio6.setEnabled(False)
        vbox2.addWidget(self.radio6)
        self.edit_ffile = QLineEdit(config_manager.get_config('factories', 'path_save'))
        #TODO : delete
        self.edit_ffile.setEnabled(False)
        vbox2.addWidget(self.edit_ffile)
        
        # ------------------------------
        vboxTop.addWidget(QLabel('Template Path'))
        self.label_template = QLabel()
        vboxTop.addWidget(self.label_template)
        vboxTop.addWidget(QLabel('Factories Path'))
        self.label_factories = QLabel()
        vboxTop.addWidget(self.label_factories)
        
        hboxButton = QHBoxLayout()
        buttonOpen = QPushButton('Open')
        buttonOpen.clicked.connect(self.onButtonOpen)
        hboxButton.addWidget(buttonOpen)
        buttonCancel = QPushButton('Cancel')
        buttonCancel.clicked.connect(self.onButtonCancel)
        hboxButton.addWidget(buttonCancel)
        vboxTop.addLayout(hboxButton)
        
        self.radio_tmp_origin.clicked.connect(self.onCheckRadioTemplate)
        self.radio_tmp_jcon.clicked.connect(self.onCheckRadioTemplate)
        self.radio4.clicked.connect(self.onCheckRadioFactories)
        self.radio6.clicked.connect(self.onCheckRadioFactories)
        self.radio_tmp_origin.setChecked(True)
        self.radio4.setChecked(True)
        self.onCheckRadioTemplate()
        self.onCheckRadioFactories()
        
        self.setWindowTitle('Open Dialog')
        self.setGeometry(300, 100, 500, 800)
        #show를 할 경우 modal로 작동하지 않는다 https://wikidocs.net/5249
        #self.show()
        self.setLayout(vboxTop)
        
    def initScrollbar_Mods(self):
        self.readModsList()
        vbox_mods = self.vbox_mods
        list_mods_all = config_manager.list_mods_all
        config_manager.path_base = self.edit_factorio.text()
        
        for i in reversed(range(vbox_mods.count())): 
            widget = vbox_mods.itemAt(i).widget()
            if widget is not None: widget.deleteLater()
            
        
        if len(list_mods_all) == 0:
            vbox_mods.addWidget(QLabel('There\'s no Mod File'))
            return
            
        if not os.path.isdir(config_manager.path_base):
            vbox_mods.addWidget(QLabel('Invalid factorio directory'))
            return
            
        self.list_check = []
        for mod in list_mods_all:
            checkbox = QCheckBox(mod)
            checkbox.setChecked(True)
            vbox_mods.addWidget(checkbox)
            self.list_check.append(checkbox)
            
    def readModsList(self):
        config_manager.path_mods  = self.edit_mod .text()
        config_manager.readModList()
        
    def onCheckRadioTemplate(self):
        if self.radio_tmp_origin.isChecked() :
            str_edit = 'Load from origin dir : ' + self.edit_factorio.text()
        elif self.radio_tmp_jcon.isChecked() :
            str_edit = 'Load from dir : ' + self.edit_tdir.text()
        self.label_template.setText(str_edit)
        
    def onCheckRadioFactories(self):
        if self.radio4.isChecked() :
            str_edit = 'Don\'t Load'
        elif self.radio6.isChecked() :
            str_edit = 'Load from zip : ' + self.edit_ffile.text()
        self.label_factories.setText(str_edit)
    
    def onButtonOpen(self):
        bInit = False
        if   self.radio_tmp_origin.isChecked() :
            bInit = self.initLoadTemplateByOrigin()
            self.type = 'origin'
        elif self.radio_tmp_jcon.isChecked() :
            bInit = True
            self.type = 'dir'
        if not bInit: return
            
        if   self.radio4.isChecked() :
            pass
        elif self.radio6.isChecked() :
            pass
        if not bInit: return
        
        self.accept()
        
    def initLoadTemplateByOrigin(self):
        config_manager.path_factorio = self.edit_factorio.text()
        vbox_mods = self.vbox_mods
        if not os.path.isdir(config_manager.path_factorio):
            for i in reversed(range(vbox_mods.count())): 
                widget = vbox_mods.itemAt(i).widget()
                if widget is not None: widget.deleteLater()
            vbox_mods.addWidget(QLabel('Invalid factorio directory'))
            return False
        list_check = self.list_check
        
        for i in range(len(list_check)):
            if list_check[i].isChecked():
                config_manager.list_mods.append(config_manager.list_mods_all[i])
        return True
        
    def initLoadTemplateByDir(self):
        config_manager.path_template_dir = self.edit_tdir.text()
        if not os.path.isdir(config_manager.path_template_dir):
            str_edit = '\'' + config_manager.path_template_dir + '\' is not valid path'
            self.label_template.setText(str_edit)
            return False
        return True
        
    def onButtonCancel(self):
        self.reject()

# --------------------------- debug

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    mainMenu = OpenDialog()
    mainMenu.show()
    
    sys.exit(app.exec_())