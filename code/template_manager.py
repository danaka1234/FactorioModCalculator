# coding: utf-8
#import tempfile
#https://docs.python.org/ko/3/library/tempfile.html
import sys, os
import shutil
#https://docs.python.org/ko/3/library/shutil.html
import atexit
#https://docs.python.org/ko/3/library/atexit.html

import config_manager, item_manager, json_manager
from PyQt5.QtGui import QPixmap

path_tempdir = ''
load_template = 'None'
version_current = 1.1

name_template_json = 'fmc_template.json'

name_clock = 'clock-icon.png'
name_fac_icon = 'factorio.png'
name_factory_icon = 'assembling-machine-1.png'
name_electric_icon = 'electricity-icon-unplugged.png'
name_fuel_icon = 'fuel-icon-red.png'

def setTemplateDir(path_template_dir):
    global path_tempdir
    path_tempdir = path_template_dir
    if not os.path.isdir(path_tempdir):
        os.mkdir(path_tempdir)
            
def getTemplateDir():
    global path_tempdir
    if path_tempdir == '':
        path_tempdir = config_manager.get_config('template', 'path_template_dir')
    if not os.path.isdir(path_tempdir):
        os.mkdir(path_tempdir)
    return path_tempdir
    
def cleanTemplateDir():
    path_tempdir = getTemplateDir()
    if os.path.isdir(path_tempdir):
        shutil.rmtree(path_tempdir)
    os.mkdir(path_tempdir)

def loadIcon(str_icon):
    path_template = getTemplateDir()
    n1 = str_icon.find('__')
    n2 = str_icon.find('__', n1+1)
    str_base = str_icon[n1+2:n2].replace('/', '\\')
    str_path = str_icon[n2+2:]  .replace('/', '\\')
    
    path_origin = ''
    path_icon_sub = os.path.join('icon', str_base, str_path)
    path_icon = path_template + path_icon_sub
    path_base = os.path.join(config_manager.path_factorio , 'data', 'base')
    path_core = os.path.join(config_manager.path_factorio , 'data', 'core')
    
    if str_base == 'base':  #base
        path_origin = path_base + str_path
    if str_base == 'core':  #core
        path_origin = path_core + str_path
    else: #mod
        #TODO : 모드 로드 완성하기
        pass
        
    if not os.path.isfile(path_icon):
        idx = path_icon.rfind('\\')
        path_dir = path_icon[:idx]
        if not os.path.isdir(path_dir):
            os.makedirs(path_dir)
        pixmap = QPixmap(path_origin)
        rect = pixmap.rect()
        if rect.width() != rect.height():
            rect.setWidth(rect.height())
            pixmap = pixmap.copy(rect)
            pixmap.save(path_icon)
        else:
            shutil.copyfile(path_origin, path_icon)
    
    return path_icon_sub
    
def copyDefaultIcon():
    path_template = getTemplateDir()
    path_graphics = os.path.join(config_manager.path_factorio , 'data', 'core', 'graphics')
    path_alerts =  os.path.join(path_graphics, 'icons', 'alerts')
    
    path_clock = os.path.join(path_graphics, name_clock)
    path_dest_clock = os.path.join(path_template, name_clock)
    shutil.copyfile(path_clock, path_dest_clock)
    
    path_fac_icon = os.path.join(path_graphics, name_fac_icon)
    path_dest_fac_icon = os.path.join(path_template, name_fac_icon)
    shutil.copyfile(path_fac_icon, path_dest_fac_icon)
    
    path_electro_icon = os.path.join(path_alerts, name_electric_icon)
    path_dest_electro_icon = os.path.join(path_template, name_electric_icon)
    shutil.copyfile(path_electro_icon, path_dest_electro_icon)
    
    path_fuel_icon = os.path.join(path_alerts, name_fuel_icon)
    path_dest_fuel_icon = os.path.join(path_template, name_fuel_icon)
    shutil.copyfile(path_fuel_icon, path_dest_fuel_icon)
    
def saveTemplateFile():
    global name_template_json, version_current
    
    map = {}
    
    map['version'] = version_current
    
    #item 등
    list_map = [\
    ['item'     , item_manager.map_item     ],\
    ['recipe'   , item_manager.map_recipe   ],\
    ['group'    , item_manager.map_group    ],\
    ['subgroup' , item_manager.map_subgroup ],\
    ['factory'  , item_manager.map_factory  ],\
    ['module'   , item_manager.map_module   ],\
    ]
    for elem in list_map:
        key = elem[0]
        map[key] = {}
        for key2 in elem[1]:
            item = elem[1][key2]
            map[key][key2] = item.toMap()
    
    #locale
    map['locale1'] = item_manager.map_locale_1st
    map['locale2'] = item_manager.map_locale_2nd
    
    path_temp = getTemplateDir()
        
    if not os.path.isdir(path_temp):
        os.makedirs(path_temp)
     
    # json 저장
    path_template_json = path_temp + '\\' + name_template_json
    json_manager.save_json(path_template_json, map)
    
def loadTemplateFromDir(args):
    global load_template, name_template_json, version_current
    load_widget = args[0]
    path_template_dir = args[1]
    path_template_json = path_template_dir + '\\' + name_template_json
    if not os.path.isdir(path_template_dir):
        if load_widget is not None:
            msg = 'load fail from \'' + path_template_dir + '\''
            load_widget.setMsg(msg, True)
        return
    if not os.path.isfile(path_template_json):
        if load_widget is not None:
            msg = 'load fail from \'' + path_template_dir + '\''
            load_widget.setMsg(msg, True)
        return
        
    # json 불러오기
    map = json_manager.load_json(path_template_json)
    
    version = map['version']
    if version != version_current:
        if load_widget is not None:
            msg = 'Template version is not same'
            load_widget.setMsg(msg, True)
        return
    
    #item
    list_class = [\
    ['group',    item_manager.ItemGroup],\
    ['subgroup', item_manager.ItemSubGroup],\
    ['item',     item_manager.Item],\
    ['recipe',   item_manager.Recipe],\
    ['factory',  item_manager.Factory],\
    ['module',  item_manager.Module],\
    ]
    
    for elem in list_class:
        list_item = map[elem[0]]
        TYPE = elem[1]
        if type(list_item) == dict:
            for item in list_item.values():
                TYPE.fromMap(item)
        else:
            for item in list_item:
                TYPE.fromMap(item)
            
    list_map = [\
    ['locale1', item_manager.map_locale_1st],\
    ['locale2', item_manager.map_locale_2nd],\
    ]
    
    for elem in list_map:
        map_src = map[elem[0]]
        map_dst = elem[1]
        map_dst.update(map_src)
        
    load_template = 'json'
    setTemplateDir(path_template_dir)
    return True
    
def loadFactories(load_type, path):
    return False

#atexit.register(onExitForFile)

# -------------------------- debug
def main() :
    #icon = "__base__/graphics/icons/steel-chest.png"
    #str_icon, icon_copied = loadIcon(icon)
    #print(getTemplateDir())
    loadTemplateFromDir([None, 'fmc_template'])
    
if __name__ == '__main__':
    main()