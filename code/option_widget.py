# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel, QComboBox

import json, os

import group_tree, elem_manager, config_manager
'''
TabWidget : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QTabWidget.html
ComboBOx : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QComboBox.html
'''

option_widget = None

#for project option
expensive = False
icon_size = 16
time_config = 1

#sub data
time_set = [1, 60, 3600]
time_name = ['s', 'm', 'h']

path_option = 'option.json'
option_changed = False

def load_option():
    global path_option, option_changed
    path_template_dir = config_manager.get_config('template', 'path_template_dir')
    path_file = os.path.join(path_template_dir, path_option)
    
    if not os.path.exists(path_file):
        option_changed = True
        save_option()
        return
        
    str_temp = ''
    with open(path_file, 'r') as file:    # save
        str_temp = file.read()
    dic_opt = json.loads(str_temp)
    
    global expensive, icon_size, time_config
    if dic_opt.get('expensive') is not None :
        expensive = dic_opt['expensive']
    if dic_opt.get('icon_size') is not None :
        icon_size = dic_opt['icon_size']
    if dic_opt.get('time_config') is not None :
        time_config = dic_opt['time_config']
        
def save_option():
    global option_changed
    if not option_changed:
        return
        
    # 옵션 추가시 여기서 처리...
    global expensive, icon_size, time_config
    dic_opt = {
        'expensive':expensive,
        'icon_size':icon_size,
        'time_config':time_config,
    }
    str_temp = json.dumps(dic_opt, indent=4)
    
    global path_option
    path_template_dir = config_manager.get_config('template', 'path_template_dir')
    path_file = os.path.join(path_template_dir, path_option)
    
    with open(path_file, 'w') as file:    # save
        file.write(str_temp)

class OptionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        global option_widget
        option_widget = self
    
    def initUI(self):
        global time_config
        grid = QGridLayout()
        self.setLayout(grid)
        
        self.comboIconSize = QComboBox()
        self.comboIconSize.insertItems(0, ['Small(16x16)', 'big(32x32)'])
        self.comboIconSize.currentIndexChanged.connect(self.iconSizeChanged)
        
        self.comboTime = QComboBox()
        self.comboTime.insertItems(0, ['second', 'minute', 'hour'])
        self.comboTime.currentIndexChanged.connect(self.timeChanged)
        self.comboTime.setCurrentIndex(time_config)
        
        row = 0
        grid.setRowStretch(0, 1)
        row += 1
        grid.addWidget(QLabel('IconSize'), row, 1)
        grid.addWidget(self.comboIconSize, row, 2)
        row += 1
        grid.addWidget(QLabel('Time'), row, 1)
        grid.addWidget(self.comboTime, row, 2)
        row += 1    
        grid.setRowStretch(row, 1)
        
        calumn = 0
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(3, 1)
        
    def iconSizeChanged(self):
        global icon_size
        idx = self.comboIconSize.currentIndex ()
        if idx == 0:
            icon_size = 16
        elif idx == 1:
            icon_size = 32
        else:
            icon_size = 16
        
        group_tree.tree_widget.rebuildTree()
        global option_changed
        option_changed = True
        
    def timeChanged(self):
        global time_config
        idx = self.comboTime.currentIndex ()
        if idx == 0:
            time_config = 0
        elif idx == 1:
            time_config = 1
        elif idx == 2:
            time_config = 2
        else:
            time_config = 0
            
        group_tree.tree_widget.rebuildTree()
        global option_changed
        option_changed = True

# -------------------------- debug
def main() :
    load_option()
    
if __name__ == '__main__':
    main()