# coding: utf-8
import sys, os
import shutil
#https://docs.python.org/ko/3/library/shutil.html

from PyQt5.QtGui        import QPixmap, QIcon

import option_widget, log_manager, loading_widget, lua_manager
import config_manager, json_manager

# data 관련 변수 ------------------------------
map_item = dict()
map_recipe = dict()
map_group = dict()
map_subgroup = dict()
map_factory = dict()
map_module = dict()

map_locale_1st = dict()
map_locale_2nd = dict()

list_item_sorted = []
list_recipe_popup = []

# save 관련 변수 ------------------------------
path_tempdir = ''
version_current = 0.1

name_template_json = 'fmc_template.json'

name_clock = 'clock-icon.png'
name_fac_icon = 'factorio.png'
name_factory_icon = 'assembling-machine-1.png'
name_electric_icon = 'electricity-icon-unplugged.png'
name_fuel_icon = 'fuel-icon-red.png'

# data 관련 코드 ------------------------------

def convert_list(source):
    if type(source) == list:
        return source
    else:
        return list(source.values())

class FCITEM:
    def getName(self):
        global map_locale_1st, map_locale_2nd
        list_locale_group = None
        if      type(self) == Item or type(self) == Module or type(self) == Factory:
            list_locale_group = ['item-name', 'fluid-name', 'entity-name', 'equipment-name']
        elif    type(self) == Recipe:
            list_locale_group = ['item-name', 'recipe-name', 'entity-name', 'equipment-name']
        elif type(self) == ItemGroup or type(self) == ItemSubGroup:
            list_locale_group = ['item-group-name']
        elif    type(self) == Factory:
            list_locale_group = ['entity-name', 'item-name']
        
        for group in list_locale_group:
            if map_locale_1st[group].get(self.name):
                return map_locale_1st[group].get(self.name)
                
        for group in list_locale_group:
            if map_locale_2nd[group].get(self.name):
                return map_locale_2nd[group].get(self.name)
                
        return self.name

    def getPixmap(self, x = 32, y = 32):
        path = self.getIconPath()
        return QPixmap(path).scaled(x, y)
        
    def getIconPath(self):
        path = ''
        if type(self) == Item:
            path = self.path_icon
        elif type(self) in [Recipe, Factory, Module]:
            if self.path_icon is not None and self.path_icon != '':
                path = self.path_icon
            else:
                if type(self) == Recipe:
                    if map_item.get(self.name) is None:
                        name_item = self.getListProduct()[0][0]
                    else:
                        name_item = self.name
                else:
                    name_item = self.name
                item = map_item[name_item]
                path = item.path_icon
        
        # 경로가 슬래시로 시작하면 os.path.join에서 절대경로로 인식함...
        while path[0] == '\\':
            path = path[1:]
            
        return os.path.join(getTemplateDir(), path)
        
    def getIcon(self, x = 32, y = 32):
        pixmap = self.getPixmap(x, y)
        return QIcon(pixmap)
        
class ItemGroup(FCITEM):
    def __init__(self, elem):
        global map_group
        self.name = elem['name']
        self.order = elem['order']
        self.list_subgroup = []
        
        if self.name is not None:
            map_group[self.name] = self
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['list_subgroup'] = self.list_subgroup
        map['order'] = self.order
        return map
        
    def fromMap(map):
        global map_group
        inst = ItemGroup(map)
        inst.list_subgroup = map['list_subgroup']
        
class ItemSubGroup(FCITEM):
    def __init__(self, elem):
        global map_subgroup, map_group
        self.name = elem['name']
        self.group = elem['group']
        self.order = elem['order']
        self.list_item = []
        
        if self.name is not None:
            map_subgroup[self.name] = self
        
        inst_group = map_group.get(self.group)
        if inst_group is not None:
            if not self.name in inst_group.list_subgroup:
                inst_group.list_subgroup.append(self.name)
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['group'] = self.group
        map['list_item'] = self.list_item
        map['order'] = self.order
        return map
        
    def fromMap(map):
        global map_subgroup
        inst = ItemSubGroup(map)
        inst.list_item = map['list_item']
        
class Item(FCITEM):
    def __init__(self, elem):
        global map_item, map_subgroup
        self.name = elem['name']         #name
        self.type = elem['type']         #type
        #subgroup
        self.subgroup = elem['subgroup'] 
        if self.subgroup is None or self.subgroup == '' :
            if elem['type'] == 'fluid':
                self.subgroup = 'fluid'
            else:
                self.subgroup = '_Unknown'
        #flag
        if elem['flags'] is not None:
            if type(elem['flags']) == list:
                self.flags = elem['flags']
            else:
                self.flags = list(elem['flags'].values())
        else: self.flags = []
        #icon
        self.path_icon = elem['icon']
        if self.path_icon is None:
            if type(elem) != dict and elem['icons'] is not None:
                self.path_icon = elem['icons']['icon']
            else:
                self.path_icon = ''
        
        self.order = elem['order']
        if self.order is None:
            self.order = 'zzz'
        
        self.list_madeby = []
        self.list_usedto = []
        
        if self.name is not None:
            map_item[self.name] = self
            
        inst_subgroup = map_subgroup.get(self.subgroup)
        if inst_subgroup is not None:
            if not self.name in inst_subgroup.list_item:
                inst_subgroup.list_item.append(self.name)
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['type'] = self.type
        map['subgroup'] = self.subgroup
        map['flags'] = self.flags
        map['icon'] = self.path_icon
        map['order'] = self.order
        #map['list_madeby'] = self.list_madeby
        #map['list_usedto'] = self.list_usedto
        return map
        
    def fromMap(map):
        global map_item
        inst = Item(map)

def make_recipe_time_in_out(table):
    time = table['energy_required']
    if time is None: time = 0.5
    if table['list_input'] is None:
        ingredients = make_recipe_sub_list(table['ingredients'])
    else:
        ingredients = table['list_input']
    if table['list_output'] is None:
        results = make_recipe_results(table)
    else:
        results = table['list_output']
    
    return time, ingredients, results

def make_recipe_sub_list(table):
    list_result = []
    
    for value in table.values():
        if 'name' not in value.keys():  #[name, num] 나열
            elem = []
            for key_sub in value:
                value_sub = value[key_sub]
                elem.append(value_sub)
        else:                           #['name'=name, 'amount'=num, ...] 등
            num = value['amount']
            if num is None:
                if value['amount_min'] is not None:
                    num = (value['amount_min'] + value['amount_max']) / 2
                elif value['fluid_amount'] is not None:
                    num = value['fluid_amount']
                else : num = 1
                
            if value['probability'] is not None:
                num = num * value['probability']
            elem = [value['name'], num]
        list_result.append(elem)
    return list_result
    
def make_recipe_results(table):
    if table['results'] is not None:
        return make_recipe_sub_list(table['results'])
    if table['result_count'] is not None:
        num = table['result_count']
    elif table['amount_min'] is not None:
        num = (table['amount_min'] + table['amount_max']) / 2
    elif table['fluid_amount'] is not None:
        num = table['fluid_amount']
    else :
        num = 1
    return [[table['result'], num]]

class Recipe(FCITEM):
    def __init__(self, elem, bResource = False):
        global map_recipe, map_item
        
        self.name = elem['name']                #name
        self.path_icon = elem['icon']           #icon
        self.category = elem['category']        #category
        if self.category is None:
            if bResource == False:
                self.category = 'basic-crafting'
            else:
                self.category = 'basic-solid'
        self.subgroup = elem['subgroup']        #subgroup
        
        '''
        #hidden 레시피 제외
        if type(elem) != dict:
            if elem['hidden'] == True:
                return
        '''
                
        if type(elem) == dict:
            self.time = elem['time']
            self.list_input = elem['list_input']
            self.list_output = elem['list_output']
            self.time_expensive = elem.get('time_expensive')
            self.list_input_expensive = elem.get('list_input_expensive')
            self.list_output_expensive = elem.get('list_output_expensive')
        elif bResource == False:
            #not normal, expensive
            if elem['expensive'] is None:
                time, ingredients, results = make_recipe_time_in_out(elem)
                self.time = time
                self.list_input = ingredients
                self.list_output = results
                self.time_expensive = 0
                self.list_input_expensive = []
                self.list_output_expensive = []
            #normal, expensive
            else:
                time, ingredients, results = make_recipe_time_in_out(elem['normal'])
                time_expensive, ingredients_expensive, results_expensive = \
                    make_recipe_time_in_out(elem['expensive'])
                self.time = time
                self.list_input = ingredients
                self.list_output = results
                self.time_expensive = time_expensive
                self.list_input_expensive = ingredients_expensive
                self.list_output_expensive = results_expensive
        else:
            self.time = None
            if elem['minable'] is not None:
                self.time = elem['minable']['mining_time']
            if self.time is None: self.time = 0.5
            
            self.time_expensive = 0
            self.list_input = []
            self.list_input_expensive = []
            
            self.time_expensive = []
            self.list_output = make_recipe_results(elem['minable'])
            self.list_output_expensive = []
            
        self.etc = dict()
        
        self.order = elem['order']
        if self.order is None:
            self.order = 'zzz'
        
        #connect recipe item
        for input in self.list_input:
            item = map_item.get(input[0])
            if item is None:
                log_manager.write_log('item is None 1 : '+ input[0] + ' not found while loading ' + self.name)
                exit()
            item.list_usedto.append(self.name)
            
        for output in self.list_output:
            item = map_item.get(output[0])
            if item is None:
                log_manager.write_log('item is None 2 : '+ output[0] + ' not found while loading ' + self.name)
                exit()
            item.list_madeby.append(self.name)
            
        if self.name is not None:
            map_recipe[self.name] = self;
        
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['icon'] = self.path_icon
        map['category'] = self.category
        map['subgroup'] = self.subgroup
        map['time'] = self.time
        map['time_expensive'] = self.time_expensive
        map['list_input'] = self.list_input
        map['list_input_expensive'] = self.list_input_expensive
        map['list_output'] = self.list_output
        map['list_output_expensive'] = self.list_output_expensive
        map['etc'] = self.etc
        map['order'] = self.order
        return map
        
    def fromMap(map):
        global map_recipe
        inst = Recipe(map)
    
    def getListProduct(self):
        if option_widget.expensive == True:
            if len(self.list_output_expensive) != 0:
                return self.list_output_expensive
        return self.list_output
        
    def getListMaterial(self):
        if option_widget.expensive == True:
            if len(self.list_input_expensive) != 0:
                return self.list_input_expensive
        return self.list_input
        
    def getProductNumByName(self, name):
        ls = self.getListProduct()
        for elem in ls:
            if elem[0] == name:
                return elem[1]
        return None
        
    def getMaterialNumByName(self, name):
        ls = self.getListMaterial()
        for elem in ls:
            if elem[0] == name:
                return elem[1]
        return None
        
    def getTime(self):
        if option_widget.expensive == True:
            if self.time_expensive != 0:
                return self.time_expensive
        return self.time
        
    def __lt__(self, other):    # popup 정렬용
        if self.order != other.order:
            return self.order < other.order
        return self.name < other.name
        
class Factory(FCITEM):
    def __init__(self, map):
        global map_factory, map_item
        
        map = dict(map)
        self.name = map.get('name')
        self.type = map.get('type')
        self.path_icon = map.get('icon')
        self.flags = None
        self.energy_usage = map.get('energy_usage')
        self.crafting_categories = None
        self.crafting_speed = map.get('crafting_speed')
        self.next_upgrade = map.get('next_upgrade')
        self.module_slots = None
        self.energy_source_type = None
        self.energy_source_emissions = None
        
        item = map_item[self.name]
        self.order = item.order
        
        '''
        #hidden 저장 안함
        if self.flags is not None and 'hidden' in self.flags:
            return
        '''
        
        if self.type == 'mining-drill':
            self.crafting_speed = map.get('mining_speed')
        
        if map.get('flags'):
            self.flags = convert_list(map['flags'])
        
        if map.get('crafting_categories'):
            self.crafting_categories = convert_list(map.get('crafting_categories'))
            
        if map.get('resource_categories'):
            self.crafting_categories = convert_list(map.get('resource_categories'))
        
        if map.get('module_specification'):
            self.module_slots = map['module_specification']['module_slots']
        elif map.get('module_slots'):
            self.module_slots = map['module_slots']
        if self.module_slots is None:
            self.module_slots = 0
        
        if map.get('energy_source'):
            table = dict(map['energy_source'])
            self.energy_source_type = table.get('type')
            self.energy_source_emissions = table.get('emissions_per_minute')
            
        if self.name is not None:
            map_factory[self.name] = self
            
        if type(self.energy_usage) == str:
            self.energy_usage = self.energy_usage.replace('W', '')
            self.energy_usage = self.energy_usage.replace('k', '000')
            self.energy_usage = self.energy_usage.replace('K', '000')
            self.energy_usage = int(self.energy_usage)
        
        self.drain = 0
        # 대기전력 추가
        if self.energy_source_type == 'electric':
            self.drain = self.energy_usage / 30
        
    def __lt__(self, other):
        if self.crafting_speed != other.crafting_speed:
            return self.crafting_speed < other.crafting_speed
        else:
            return self.name < other.name
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['type'] = self.type
        map['icon'] = self.path_icon
        map['flags'] = self.flags
        map['energy_usage'] = self.energy_usage
        map['crafting_categories'] = self.crafting_categories
        map['crafting_speed'] = self.crafting_speed
        if self.type == 'mining-drill':
           map['mining_speed'] = self.crafting_speed
           map.pop('crafting_speed', None)
        map['next_upgrade'] = self.next_upgrade
        map['module_slots'] = self.module_slots
        energy_source = {}
        energy_source['type'] = self.energy_source_type
        energy_source['emissions_per_minute'] = self.energy_source_emissions
        map['energy_source'] = energy_source
        return map
        
    def fromMap(map):
        global map_factory
        inst = Factory(map)
        
def get_map_from_table(table):
    map_result = dict()
    for key in table:
        elem = table[key]
        if lua_manager.lupa.lua_type(elem) == 'table':
            elem = get_map_from_table(elem)
        map_result[key] = elem
        
    return map_result
    
class Module(FCITEM):
    def __init__(self, elem):
        self.name = elem['name']             #name
        self.path_icon = elem['icon']        #icon
        self.category = elem['category']     #category
        self.subgroup = elem['subgroup']     #subgroup
        self.tier = elem['tier']
        self.effect = get_map_from_table(elem['effect'])
        self.order = elem['order']
        
        if elem['limitation'] is not None:
            if type(elem) == dict:
                self.limitation = elem['limitation']
            else:
                self.limitation = list(elem['limitation'].values())
        else:
            self.limitation = []
    
        if self.name is not None:
            map_module[self.name] = self
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['icon'] = self.path_icon
        map['category'] = self.category
        map['subgroup'] = self.subgroup
        map['tier'] = self.tier
        map['limitation'] = self.limitation
        map['effect'] = self.effect
        map['order'] = self.order
        return map
        
    def fromMap(map):
        global map_module
        inst = Module(map)

def getGroupList():
    global map_group
    list_group = []
    for name_group in map_group:
        group = map_group[name_group]
        bEmpty = True
        for subgroup in group.list_subgroup:
            if len(map_subgroup[subgroup].list_item) != 0:
                bEmpty = False
                break
        if bEmpty: continue
        list_group.append(group)
    list_group.sort(key=lambda elem: elem.order)
    return list_group

def getSubgroupListWithGroup(group = None):
    global map_subgroup, map_group
    list_subgroup = []
    if group is None:
        for subgroup in list(map_subgroup.values()):
            if len(subgroup.list_item) == 0:    continue
            list_subgroup.append(subgroup)
        
    else:
        for name_subgroup in map_group[group].list_subgroup:
            subgroup = map_subgroup[name_subgroup]
            if len(subgroup.list_item) == 0:    continue
            list_subgroup.append(subgroup)
    list_subgroup.sort(key=lambda elem: elem.order)
    return list_subgroup
    
def getItemListWithSubgroup(list_subgroup = None):
    global map_item, map_subgroup
    list_item = []
    if len(list_subgroup) == 0:
        list_item = list(map_item.values())
    else:
        for subgroup in list_subgroup:
            for name_item in map_subgroup[subgroup].list_item:
                list_item.append(map_item[name_item])
    list_item.sort(key=lambda elem: elem.order)
    return list_item
    
def getFactoryListByRecipe(recipe = None):
    global map_factory, map_recipe
    list_factory = []
    if recipe is None:
        list_factory = list(map_factory.values())
    else:
        category = recipe.category
        if category == '': category = 'basic-crafting'
        for factory in map_factory.values():
            if category in factory.crafting_categories:
                list_factory.append(factory)
    list_factory.sort(key=lambda elem: elem.order)
    return list_factory
    
def getModuleListWithRecipe(name_recipe = None):
    global map_module
    list_module = []
    if name_recipe is None:
        list_module = list(map_module.values())
    else:
        for module in map_module.values():
            if len(module.limitation) > 0 and name_recipe not in module.limitation:
                continue
            list_module.append(module)
    list_module.sort(key=lambda elem: elem.order)
    list_module.append(None)
    return list_module
    
def copyIcon():
    global map_item, map_recipe
    
    for key in map_item.keys():
        item = map_item[key]
        if item.path_icon == '' or item.path_icon is None:
            continue
        item.path_icon = loadIcon(item.path_icon)
        
    for key in map_recipe.keys():
        recipe = map_recipe[key]
        if recipe.path_icon == '' or recipe.path_icon is None : continue
        recipe.path_icon = loadIcon(recipe.path_icon)
        
    for key in map_factory.keys():
        factory = map_factory[key]
        if factory.path_icon == '' or factory.path_icon is None : continue
        factory.path_icon = loadIcon(factory.path_icon)
        
    for key in map_module.keys():
        module = map_module[key]
        if module.path_icon == '' or module.path_icon is None : continue
        module.path_icon = loadIcon(module.path_icon)

def searchItemNoRecipe():
    global map_item
    for item in map_item.values():
        if len(item.list_madeby) == 0:
            if 'hidden' not in item.flags:
                log_manager.write_log("Item has no recipe : " + item.name)
                
                map = {
                    'name' : item.name, 'icon' : '', 'category' : '_Unknown', 'subgroup' : '_Unknown', \
                    'time' : 1, 'list_input' : [], 'list_output' : [[item.name, 1]], \
                    'order' : 'zzz', 'expensive' : None
                }
                Recipe(map)
                
def sortRecipe():
    global map_item, map_recipe
    for item in map_item.values():
        item.list_madeby.sort(key=lambda elem: map_recipe[elem].order)
        item.list_usedto.sort(key=lambda elem: map_recipe[elem].order)
        
def getItemName(name):
    item = map_item.get(name)
    if item is None:
        return name
    return item.getName()

class ItemRapper:
    def __init__(self, item):
        self.item = item
        self.list_sub = []
            
def sortItemList():
    global list_recipe_popup, map_item, map_recipe, map_group, map_subgroup
    global list_item_sorted
    
    # 아이템 정렬
    list_item_sorted = list(map_item.values())
    list_item_sorted.sort(key=lambda elem: elem.order)
    
    # 아이템 초기화 & 정렬
    for group in map_group.values():
        rap_g = ItemRapper(group)
        bAddGroup = False
        
        for name_subgroup in group.list_subgroup:
            subgroup = map_subgroup[name_subgroup]
            rap_s = ItemRapper(subgroup)
            bAddSubgroup = False
            
            for name_item in subgroup.list_item:
                item = map_item[name_item]
                
                # hidden 제외
                if 'hidden' in item.flags:
                    continue
                
                bAddGroup = True
                bAddSubgroup = True
                rap_s.list_sub.append(item)
                
            if bAddSubgroup:    #서브그룹 추가 & 아이템 정렬
                rap_s.list_sub.sort(key=lambda elem: elem.order)
                rap_g.list_sub.append(rap_s)
        
        if bAddGroup:           #그룹 추가 & 서브그룹 정렬
            rap_g.list_sub.sort(key=lambda elem: elem.item.order)
            list_recipe_popup.append(rap_g)
            
    list_recipe_popup.sort(key=lambda elem: elem.item.order)    #그룹 정렬
    
def getSortedItemList():
    global list_item_sorted
    return list_item_sorted
    
def getPopupRecipeList():
    global list_recipe_popup
    return list_recipe_popup

# save 관련 코드 ------------------------------

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
    global map_item, map_recipe, map_group, map_subgroup, map_factory, map_module
    
    map = {}
    
    map['version'] = version_current
    
    #item 등
    list_map = [\
    ['item'     , map_item     ],\
    ['recipe'   , map_recipe   ],\
    ['group'    , map_group    ],\
    ['subgroup' , map_subgroup ],\
    ['factory'  , map_factory  ],\
    ['module'   , map_module   ],\
    ]
    for elem in list_map:
        key = elem[0]
        map[key] = {}
        for key2 in elem[1]:
            item = elem[1][key2]
            map[key][key2] = item.toMap()
    
    #locale
    map['locale1'] = map_locale_1st
    map['locale2'] = map_locale_2nd
    
    path_template_dir = getTemplateDir()
        
    if not os.path.isdir(path_template_dir):
        os.makedirs(path_template_dir)
     
    # json 저장
    path_template_json = os.path.join(path_template_dir, name_template_json)
    json_manager.save_json(path_template_json, map)
    
def loadTemplateFromDir(args):
    global name_template_json, version_current
    load_widget = args[0]
    path_template_dir = args[1]
    path_template_json = os.path.join(path_template_dir, name_template_json)
    if not os.path.isdir(path_template_dir):
        if load_widget is not None:
            msg = '\'' + path_template_dir + '\' not exist'
            load_widget.setMsg(msg, True)
        return
    if not os.path.isfile(path_template_json):
        if load_widget is not None:
            msg = '\'' + path_template_json + '\' not exist'
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
    ['group',    ItemGroup],\
    ['subgroup', ItemSubGroup],\
    ['item',     Item],\
    ['recipe',   Recipe],\
    ['factory',  Factory],\
    ['module',   Module],\
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
    ['locale1', map_locale_1st],\
    ['locale2', map_locale_2nd],\
    ]
    
    for elem in list_map:
        map_src = map[elem[0]]
        map_dst = elem[1]
        map_dst.update(map_src)
        
    setTemplateDir(path_template_dir)
    return True
    
def loadFactories(load_type, path):
    return False


# -------------------------- debug
def main() :
    #icon = "__base__/graphics/icons/steel-chest.png"
    #str_icon, icon_copied = loadIcon(icon)
    #print(getTemplateDir())
    loadTemplateFromDir([None, 'fmc_template'])
    
if __name__ == '__main__':
    main()