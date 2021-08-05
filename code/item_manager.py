# coding: utf-8
#import tokenize
'''
토크나이즈는 쓸모없나...
https://docs.python.org/ko/3/library/tokenize.html
'''

#import zipfile
'''
#https://code.tutsplus.com/ko/tutorials/compressing-and-extracting-files-in-python--cms-26816
'''
import os

from PyQt5.QtGui        import QPixmap, QIcon

import config_manager, log_manager, loading_widget, template_manager, lua_manager

map_item = dict()
map_recipe = dict()
map_group = dict()
map_subgroup = dict()
map_factory = dict()
map_module = dict()

map_locale_1st = dict()
map_locale_2nd = dict()

list_recipe_popup = []

debug_name_file = ''

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
        elif type(self) == Recipe or type(self) == Factory:
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
        return template_manager.getTemplateDir() + "\\" + path
        
    def getIcon(self, x = 32, y = 32):
        pixmap = self.getPixmap(x, y)
        return QIcon(pixmap)
        
class ItemGroup(FCITEM):
    def __init__(self, name, order):
        global map_group
        self.name = name
        self.list_subgroup = []
        self.order = order
        
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
        inst = ItemGroup(None, None)
        inst.name = map['name']
        inst.list_subgroup = map['list_subgroup']
        inst.order = map['order']
        map_group[inst.name] = inst
        
class ItemSubGroup(FCITEM):
    def __init__(self, name, name_group, order):
        global map_subgroup, map_group
        self.name = name
        self.group = name_group
        self.list_item = []
        self.order = order
        
        if self.name is not None:
            map_subgroup[self.name] = self
        
        inst_group = map_group.get(name_group)
        if inst_group is not None:
            if not name in inst_group.list_subgroup:
                inst_group.list_subgroup.append(name)
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['group'] = self.group
        map['list_item'] = self.list_item
        map['order'] = self.order
        return map
        
    def fromMap(map):
        global map_subgroup
        inst = ItemSubGroup(None,None,None)
        inst.name = map['name']
        inst.group = map['group']
        inst.list_item = map['list_item']
        inst.order = map['order']
        map_subgroup[inst.name] = inst
        
class Item(FCITEM):
    def __init__(self, name, type, subgroup, flags, path_icon, order):
        global map_item, map_subgroup
        self.name = name
        self.type = type
        self.subgroup = subgroup
        self.flags = flags
        if path_icon is None:   self.path_icon = ''
        else:                   self.path_icon = path_icon
        self.order = order
        
        self.list_madeby = []
        self.list_usedto = []
        
        if self.name is not None:
            map_item[self.name] = self
            
        if self.order is None:
            self.order = 'zzz'
        
        #TODO : 제거
        if flags is not None and 'hidden' in flags:
            return
        
        inst_subgroup = map_subgroup.get(subgroup)
        if inst_subgroup is not None:
            if not name in inst_subgroup.list_item:
                inst_subgroup.list_item.append(name)
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['type'] = self.type
        map['subgroup'] = self.subgroup
        map['flags'] = self.flags
        map['path_icon'] = self.path_icon
        map['order'] = self.order
        map['list_madeby'] = self.list_madeby
        map['list_usedto'] = self.list_usedto
        return map
        
    def fromMap(map):
        global map_item
        inst = Item(None,None,None,None,None,None)
        inst.type = map['type']
        inst.name = map['name']
        inst.subgroup = map['subgroup']
        inst.flags = map['flags']
        inst.path_icon = map['path_icon']
        inst.order = map['order']
        inst.list_madeby = map['list_madeby']
        inst.list_usedto = map['list_usedto']
        map_item[inst.name] = inst
    
class Recipe(FCITEM):
    def __init__(self, name, path_icon, category, subgroup, order, \
        time, ingredients, results, \
        time_expensive, ingredients_expensive, results_expensive):
        global map_recipe, map_item
        self.name = name
        self.path_icon = path_icon
        self.category = category
        self.subgroup = subgroup
        self.time = time
        self.time_expensive = time_expensive
        self.list_input = ingredients
        self.list_input_expensive = ingredients_expensive
        self.list_output = results
        self.list_output_expensive = results_expensive
        self.etc = dict()
        self.order = order
        
        if self.name is not None:
            map_recipe[self.name] = self;
        
        #connect recipe item
        for input in self.list_input:
            item = map_item.get(input[0])
            if item is None:
                log_manager.write_log('item is None 1 : '+ input[0] + ' not found while loading ' + self.name)
                exit()
            if 'hidden' in item.flags: continue
            item.list_usedto.append(self.name)
            
        for output in self.list_output:
            item = map_item.get(output[0])
            if item is None:
                log_manager.write_log('item is None 2 : '+ output[0] + ' not found while loading ' + self.name)
                exit()
            if 'hidden' in item.flags: continue
            item.list_madeby.append(self.name)
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['path_icon'] = self.path_icon
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
        inst = Recipe(None,None,None,None,None,\
            None,[],[],\
            None,[],[])
        inst.name = map['name']
        inst.path_icon = map['path_icon']
        inst.category = map['category']
        inst.subgroup = map['subgroup']
        inst.time = map['time']
        inst.time_expensive = map['time_expensive']
        inst.list_input = map['list_input']
        inst.list_input_expensive = map['list_input_expensive']
        inst.list_output = map['list_output']
        inst.list_output_expensive = map['list_output_expensive']
        inst.etc = map['etc']
        inst.order = map['order']
        map_recipe[inst.name] = inst
    
    def getListProduct(self):
        if config_manager.expensive == True:
            if len(self.list_output_expensive) != 0:
                return self.list_output_expensive
        return self.list_output
        
    def getListMaterial(self):
        if config_manager.expensive == True:
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
        if config_manager.expensive == True:
            if self.time_expensive != 0:
                return self.time_expensive
        return self.time
        
    def __lt__(self, other):    # popup 정렬용
        if self.order != other.order:
            return self.order < other.order
        return self.name < other.name
        
class Factory(FCITEM):
    def __init__(self, map):
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
        
        if self.flags is not None and 'hidden' in self.flags:
            return
            
        if self.name is not None:
            map_factory[self.name] = self
        
    def __lt__(self, other):
        if self.crafting_speed != other.crafting_speed:
            return self.crafting_speed < other.crafting_speed
        else:
            return self.name < other.name
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['type'] = self.type
        map['path_icon'] = self.path_icon
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

class Module(FCITEM):
    def __init__(self, name, path_icon, category, subgroup, tier, limitation, effect, order):
        self.name = name
        self.path_icon = path_icon
        self.category = category
        self.subgroup = subgroup
        self.tier = tier
        self.limitation = limitation
        self.effect = effect
        self.order = order
        
        if self.name is not None:
            map_module[self.name] = self
        
    def toMap(self):
        map = {}
        map['name'] = self.name
        map['path_icon'] = self.path_icon
        map['category'] = self.category
        map['subgroup'] = self.subgroup
        map['tier'] = self.tier
        map['limitation'] = self.limitation
        map['effect'] = self.effect
        map['order'] = self.order
        return map
        
    def fromMap(map):
        global map_module
        inst = Module(None,None,None,None,None,None,None,None)
        inst.name = map['name']
        inst.path_icon = map['path_icon']
        inst.category = map['category']
        inst.subgroup = map['subgroup']
        inst.tier = map['tier']
        inst.limitation = map['limitation']
        inst.effect = map['effect']
        inst.order = map['order']
        map_module[inst.name] = inst

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
    
def getFactoryListWithItem(recipe = None):
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
    list_factory.sort()
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
    return list_module
    
def copyIcon():
    global map_item, map_recipe
    
    for key in map_item.keys():
        item = map_item[key]
        if item.path_icon == '' or item.path_icon is None:
            continue
        item.path_icon = template_manager.loadIcon(item.path_icon)
        
    for key in map_recipe.keys():
        recipe = map_recipe[key]
        if recipe.path_icon == '' or recipe.path_icon is None : continue
        recipe.path_icon = template_manager.loadIcon(recipe.path_icon)
        
    for key in map_factory.keys():
        factory = map_factory[key]
        if factory.path_icon == '' or factory.path_icon is None : continue
        factory.path_icon = template_manager.loadIcon(factory.path_icon)

def deleteHidden():
    global map_item
    list_delete = []
    for key in map_item:
        item = map_item[key]
        if 'hidden' in item.flags:
            list_delete.append(key)
    
    for key in list_delete:
        del map_item[key]
        
def searchItemNoRecipe():
    global map_item
    for item in map_item.values():
        if len(item.list_madeby) == 0:
            log_manager.write_log("Item has no recipe : " + item.name)
            Recipe(item.name, '', '_Unknown', '_Unknown', 'zzz', \
                1, [], [[item.name, 1]], \
                1, None, None)
                
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
    return list_recipe_popup

# -------------------------- debug
if __name__ == '__main__':
    exit()