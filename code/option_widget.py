# coding: utf-8
from PyQt5.QtWidgets    import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets    import QPushButton, QLabel, QComboBox, QGroupBox
from PyQt5.QtWidgets    import QCheckBox, QLineEdit, QScrollArea
from PyQt5.QtGui        import QDoubleValidator, QIntValidator
from PyQt5.QtCore       import Qt

import json, os

import group_tree, elem_manager, config_manager
'''
TabWidget : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QTabWidget.html
ComboBox : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QComboBox.html
checkbox : https://doc.qt.io/qtforpython/PySide6/QtWidgets/QCheckBox.html
'''

option_widget = None

#for project option
# --- global
expensive = False
time_config = 1
min_ignore = 0.0001
# --- tree
icon_size = 16
tree_num_max = 5
is_tree_num_right = True
is_tree_expend_right = False

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
    
    global expensive, time_config, min_ignore
    global icon_size, tree_num_max, is_tree_num_right, is_tree_expend_right
    if dic_opt.get('expensive') is not None :
        expensive = dic_opt['expensive']
    if dic_opt.get('time_config') is not None :
        time_config = dic_opt['time_config']
    if dic_opt.get('min_ignore') is not None :
        min_ignore = dic_opt['min_ignore']
    if dic_opt.get('icon_size') is not None :
        icon_size = dic_opt['icon_size']
    if dic_opt.get('tree_num_max') is not None :
        tree_num_max = dic_opt['tree_num_max']
    if dic_opt.get('is_tree_num_right') is not None :
        is_tree_num_right = dic_opt['is_tree_num_right']
    if dic_opt.get('is_tree_expend_right') is not None :
        is_tree_expend_right = dic_opt['is_tree_expend_right']
        
def save_option():
    global option_changed
    if not option_changed:
        return
        
    # 옵션 추가시 여기서 처리...
    global expensive, time_config, min_ignore
    global icon_size, tree_num_max, is_tree_num_right, is_tree_expend_right
    dic_opt = {
        'expensive':expensive,
        'time_config':time_config,
        'min_ignore':min_ignore,
        'icon_size':icon_size,
        'tree_num_max':tree_num_max,
        'is_tree_num_right':is_tree_num_right,
        'is_tree_expend_right':is_tree_expend_right,
    }
    str_temp = json.dumps(dic_opt, indent=4)
    
    global path_option
    path_template_dir = config_manager.get_config('template', 'path_template_dir')
    path_file = os.path.join(path_template_dir, path_option)
    
    with open(path_file, 'w') as file:    # save
        file.write(str_temp)

class OptionWidget(QWidget):
    def __init__(self, name = 'tree'):
        super().__init__()
        self.initUI(name)
        
        global option_widget
        option_widget = self
    
    def initUI(self, name):
        global time_config, expensive, min_ignore
        global icon_size, tree_col, tree_row, is_tree_num_right, is_tree_expend_right
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        vbox = QVBoxLayout()
        widget = QWidget()
        vbox_main = QVBoxLayout()
        
        widget.setLayout(vbox_main)
        scroll.setWidget(widget)
        vbox.addWidget(scroll)
        self.setLayout(vbox)
        #vbox_main.addStretch(1)
        
        #global
        group_global = QGroupBox('Global')
        grid_global = QGridLayout()
        group_global.setLayout(grid_global)
        vbox_main.addWidget(group_global)
            
        self.comboTime = QComboBox()
        self.comboTime.insertItems(0, ['sec', 'min', 'hr'])
        self.comboTime.setCurrentIndex(time_config)
        self.comboTime.currentIndexChanged.connect(self.timeChanged)
        grid_global.addWidget(QLabel('Time'), 0, 0)
        grid_global.addWidget(self.comboTime, 0, 1)
        
        self.checkExpensive = QCheckBox()
        self.checkExpensive.setCheckState(expensive)
        self.checkExpensive.stateChanged.connect(self.expensiveChanged)
        grid_global.addWidget(QLabel('Expensive'), 1, 0)
        grid_global.addWidget(self.checkExpensive, 1, 1)
        
        self.editIgnore = QLineEdit()
        self.editIgnore.setFixedWidth(60)
        self.editIgnore.setText(str(min_ignore))
        self.editIgnore.setValidator(QDoubleValidator())
        self.editIgnore.editingFinished.connect(self.ignoreChanged)
        grid_global.addWidget(QLabel('Min Number'), 2,0)
        grid_global.addWidget(self.editIgnore, 2, 1)
        
        #tree
        #if name == 'tree':
        group_tree = QGroupBox('Table')
        grid_tree = QGridLayout()
        group_tree.setLayout(grid_tree)
        vbox_main.addWidget(group_tree)
        
        self.editTreeIconSize = QLineEdit()
        self.editTreeIconSize.setFixedWidth(60)
        self.editTreeIconSize.setText(str(icon_size))
        self.editTreeIconSize.setValidator(QIntValidator())
        self.editTreeIconSize.editingFinished.connect(self.treeIconChanged)
        grid_tree.addWidget(QLabel('Icon Size'), 0, 0)
        grid_tree.addWidget(self.editTreeIconSize, 0, 1)
        
        #tree detail
        btTreeDetail = QPushButton('Detail')
        self.widgetTreeDetail = QWidget()
        btTreeDetail.clicked.connect(self.clickwidgetTreeDetail)
        grid_treeDetail = QGridLayout()
        self.widgetTreeDetail.setLayout(grid_treeDetail)
        self.widgetTreeDetail.setVisible(False)
        grid_tree.addWidget(btTreeDetail, 1, 0, 1, -1)
        grid_tree.addWidget(self.widgetTreeDetail, 2, 0, 1, -1)
        
        self.checkTreeNumberRight = QCheckBox()
        check = Qt.Checked if is_tree_num_right else Qt.Unchecked
        self.checkTreeNumberRight.setCheckState(check)
        self.checkTreeNumberRight.stateChanged.connect(self.treeIconChanged)
        grid_treeDetail.addWidget(QLabel('Number Right'), 0, 0)
        grid_treeDetail.addWidget(self.checkTreeNumberRight, 0, 1)
        
        self.checkTreeExpendRight = QCheckBox()
        check = Qt.Checked if is_tree_expend_right else Qt.Unchecked
        self.checkTreeExpendRight.setCheckState(check)
        self.checkTreeExpendRight.stateChanged.connect(self.treeIconChanged)
        grid_treeDetail.addWidget(QLabel('Expend Right'), 1, 0)
        grid_treeDetail.addWidget(self.checkTreeExpendRight, 1, 1)
        
        self.editTreeIconNum = QLineEdit()
        self.editTreeIconNum.setFixedWidth(60)
        self.editTreeIconNum.setText(str(tree_num_max))
        self.editTreeIconNum.setValidator(QIntValidator())
        self.editTreeIconNum.editingFinished.connect(self.treeIconChanged)
        grid_treeDetail.addWidget(QLabel('Num Max'), 2, 0)
        grid_treeDetail.addWidget(self.editTreeIconNum, 2, 1)
        
        vbox_main.addStretch(1)
            
    def treeIconChanged(self):
        global icon_size, tree_num_max, is_tree_num_right, is_tree_expend_right
        global option_changed
        
        icon_size = int(self.editTreeIconSize.text())
        is_tree_num_right = self.checkTreeNumberRight.checkState() == Qt.Checked
        is_tree_expend_right = self.checkTreeExpendRight.checkState() == Qt.Checked
        tree_num_max = int(self.editTreeIconNum.text())
        
        if icon_size <= 0 :
            icon_size = 32
            print('check')
            self.editTreeIconSize.setText(str(icon_size))
        if tree_num_max <= 0 :
            tree_col = 5
            self.editTreeIconCol.setText(str(tree_num_max))
        
        group_tree.tree_widget.rebuildTree()
        option_changed = True
        
    def clickwidgetTreeDetail(self):
        visible = self.widgetTreeDetail.isVisible()
        self.widgetTreeDetail.setVisible(not visible)
        
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
        
    def expensiveChanged(self):
        global expensive
        expensive = self.checkExpensive.checkState()
        group_tree.tree_widget.rebuildTree()
        option_changed = True
        
    def ignoreChanged(self):
        global min_ignore, option_changed
        min_ignore = float(self.editIgnore.text())
        if min_ignore <= 0 :
            min_ignore = 0.0001
            self.editIgnore.setText(str(min_ignore))
        
        group_tree.tree_widget.rebuildTree()
        option_changed = True
        
# -------------------------- debug
def main() :
    load_option()
    
if __name__ == '__main__':
    main()