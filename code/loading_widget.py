# coding: utf-8

import sys, os, time

#core
from PyQt5.QtWidgets    import QMainWindow, QApplication
from PyQt5.QtWidgets    import QWidget

from PyQt5.QtCore       import QThread, pyqtSignal

#layout
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QProgressBar

import config_manager, main_window, item_manager, lua_manager, item_manager, elem_manager
import option_widget
'''
QProgressBar, QThread
https://www.opentutorials.org/module/544/18723

QThread
https://freeprog.tistory.com/351

QMutex, QWaitCondition은 함께 쓰는거고, 지금은 쓸일 없는듯
'''

# 외부 호출 함수 : 카멜식 funcLikeThis
# 모듈 내부 함수 : 언더바 func_like_this
# 귀찮아 대충하자

is_continue_loading = False
load_widget = None

class LoadRapper():
    def __init__(self, msg):
        self.msg = msg
        self.list_sub = []
        
class LoadRapperSub():
    def __init__(self, msg, func, args = None):
        self.msg = msg
        self.func = func
        self.args = args

class LoadingThread(QThread):
    '''
    Thread For Loading
    '''
    #signal
    signal_load_complete = pyqtSignal()
    change_main_bar      = pyqtSignal(int)
    change_sub_bar       = pyqtSignal(int)
    change_label         = pyqtSignal(str)
    str_err              = ''
    bWorking             = False    
    
    def __init__(self, loading_widget):
        super().__init__()
        self.loading_widget = loading_widget
        self.bFinish = False
        self.bWorking = False
        self.list_load = []
        
        #list_load
        #LoadRapper(msg, list_sub[])
        #LoadRapperSub(msg, func)
        
    def run(self):
        global is_continue_loading, msg_load
        is_continue_loading = True
        self.bWorking = True
        
        len_mainBar = len(self.list_load)
        for i in range(len_mainBar):
            r_main = self.list_load[i]
            self.loading_widget.mainLabel.setText(r_main.msg)
            self.change_main_bar.emit(int(100*i/len_mainBar))
            
            len_subBar = len(r_main.list_sub)
            for j in range(len_subBar):
                if not self.bWorking:
                    break;
                r_sub = r_main.list_sub[j]
                self.loading_widget.subLabel.setText(r_sub.msg)
                self.change_sub_bar.emit(int(100*i/len_subBar))
                if r_sub.args is not None:
                    r_sub.func(r_sub.args)
                else:
                    r_sub.func()
                if not is_continue_loading:
                    self.bWorking = False
                    break
                    
            if not is_continue_loading:
                self.bWorking = False
                break

        if self.bWorking:
            self.bWorking = False
            self.signal_load_complete.emit()

class LoadingWidget(QWidget):
    def __init__(self, main_window):
        global load_widget
        super().__init__()
        self.main_window = main_window
        self.thread = LoadingThread(self)
        self.initUI()
        
        load_widget = self
        
    def __del__(self):
        if self.thread.bWorking:
            self.thread.wait()
            
    def initUI(self):
        self.mainLabel = QLabel()
        self.mainBar = QProgressBar()
        self.subLabel = QLabel()
        self.subBar  = QProgressBar()
        self.errorLabel = QLabel()
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.mainLabel)
        vbox.addWidget(self.mainBar)
        vbox.addWidget(self.subLabel)
        vbox.addWidget(self.subBar)
        vbox.addWidget(self.errorLabel)
        
        self.thread.change_main_bar.connect(self.mainBar.setValue)
        self.thread.change_sub_bar .connect(self.subBar .setValue)
        self.thread.signal_load_complete.connect(self.completeLoad)
        
        self.setLayout(vbox)
        
    def setMsg(self, msg, bFail = False):
        global is_continue_loading
        if bFail:
            msg = 'Loading canceled or fail : '+ msg
            is_continue_loading = False
        self.mainLabel.setText(msg)
            
    def doLoad(self, bLoadTmpDir, bLoadFac, path_template_dir = None):
    
        if not bLoadTmpDir: # 최초 로드    
            #---------------------------------------- Load Factorio Lua
            main = LoadRapper('Load Factorio Lua')
            self.thread.list_load.append(main)
            
            config_manager.readModList()
            list_mods = config_manager.list_mods
            
            # 스레드 쓰면 안됨
            lua_manager.make_link_base(config_manager.path_factorio)
            time.sleep(0.1)
            
            main.list_sub.append(\
                LoadRapperSub('Load Factorio Base Lua', \
                    lua_manager.load_vanilla, config_manager.path_factorio))
                    
            if not os.path.isdir(config_manager.path_factorio):
                msg = 'Cannot find factorio dir'
                self.setMsg(msg, True)
                return
                    
            #TODO : 모드는 나중에...
            #---------------------------------------- Make template
            main = LoadRapper('Make template')
            self.thread.list_load.append(main)
            
            
            main.list_sub.append(\
                LoadRapperSub('Clean Template Dir', \
                    item_manager.cleanTemplateDir))
            
            main.list_sub.append(\
                LoadRapperSub('Doing make_item_group', \
                    lua_manager.make_item_group))
                    
            main.list_sub.append(\
                LoadRapperSub('Doing make_item', \
                    lua_manager.make_item))
            
            main.list_sub.append(\
                LoadRapperSub('Doing make_recipe', \
                    lua_manager.make_recipe))
                    
            main.list_sub.append(\
                LoadRapperSub('Doing make_factory', \
                    lua_manager.make_factory))
                    
            main.list_sub.append(\
                LoadRapperSub('Doing make_module', \
                    lua_manager.make_module))
                    
            main.list_sub.append(\
                LoadRapperSub('Doing make_fluid', \
                    lua_manager.make_fluid))
                    
            main.list_sub.append(\
                LoadRapperSub('Doing make_locale', \
                    lua_manager.make_locale, config_manager.path_factorio))
                    
            #---------------------------------------- Post Process
            main = LoadRapper('Post Process')
            self.thread.list_load.append(main)
            
            main.list_sub.append(\
                LoadRapperSub('Sort Recipe', \
                    item_manager.sortRecipe))
            
            main.list_sub.append(\
                LoadRapperSub('Copy Icon', \
                    item_manager.copyIcon))
            
            main.list_sub.append(\
                LoadRapperSub('Copy Default Icon', \
                    item_manager.copyDefaultIcon))
            
            main.list_sub.append(\
                LoadRapperSub('Save Template', \
                    item_manager.saveTemplateFile))
                    
            main.list_sub.append(\
                LoadRapperSub('Save Option', \
                    option_widget.save_option))
        else:   # 템플릿(기존 프로젝트)에서 로드
            #---------------------------------------- Load Template
            main = LoadRapper('Load Template From Dir')
            self.thread.list_load.append(main)
            
            main.list_sub.append(\
                LoadRapperSub('Load Template From Dir', \
                    item_manager.loadTemplateFromDir, \
                    [self, path_template_dir]))
                    
            main.list_sub.append(\
                LoadRapperSub('Load Option', \
                    option_widget.load_option))
                    
        ##------------------------------ 2nd Process
        main = LoadRapper('2nd Process')
        self.thread.list_load.append(main)
        
        main.list_sub.append(\
            LoadRapperSub('Sort Popup Item list', \
                item_manager.sortItemList))
                
        if config_manager.get_config('template', 'delete_temp_files', 'boolean'):
            main.list_sub.append(\
                LoadRapperSub('Delete Temporary Files', \
                    lua_manager.del_link_base))
                    
        
        ##------------------------------ 3rd Process
        main = LoadRapper('3rd Process')
        self.thread.list_load.append(main)
        
        if not bLoadTmpDir: # 최초 로드
            pass
        else:
            main.list_sub.append(\
                LoadRapperSub('Load Factories', \
                    elem_manager.load_elem))
                    
        main.list_sub.append(\
            LoadRapperSub('Init Elem Manager', \
                elem_manager.initElemManager))
    
        self.thread.start()
    
    def completeLoad(self):
        self.thread.wait()
        #self.thread = None
        #위 문장으로 스레드 파괴가능(단 이 함수를 스레드가 직접호출이 아닌 emit으로 해야함)
        
        self.main_window.setTabWidget()

# --------------------------- debug

if __name__ == '__main__':
    exit()
