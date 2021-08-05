# coding: utf-8
#!/usr/bin/env python3

import os
import lupa

import item_manager, config_manager

path_core = ''
lua = None
    
def load_vanilla(path_factorio):
    global path_core, lua
    path_data = os.path.join(path_factorio, 'data')
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    lua.globals().package.path += ';' + os.path.join(path_data, 'core', 'lualib', '?.lua') \
                                + ';' + os.path.join(path_data, 'core', '?.lua') \
                                + ';' + os.path.join(path_data, 'base', '?.lua') \
                                + ';' + os.path.join(path_data, '?.lua')
                                    
    # add missing function math.pow()
    lua.execute('function math.pow(num1, num2) return (num1 ^ num2) end')
    
    # defines
    lua.globals().defines = {
        "difficulty_settings": {
            "recipe_difficulty": {"normal": 0, "expensive": 1},
            "technology_difficulty": {"normal": 0, "expensive": 1},
        },
        "direction": {
            "north": 0,
            "east": 2,
            "south": 4,
            "west": 6,
        },
    }
    
    #load core
    lua.require('dataloader')
    lua.require('core.data')
    lua.require('base.data')

def make_item_group():
    global lua
    raw = lua.globals().data.raw
    table_item_group = raw['item-group']
    table_item_sub_group = raw['item-subgroup']
    
    for key in table_item_group:
        elem = table_item_group[key]
        name = elem['name']
        order = elem['order']
        item_manager.ItemGroup(name, order)
        
    for key in table_item_sub_group:
        elem = table_item_sub_group[key]
        name = elem['name']
        name_group = elem['group']
        order = elem['order']
        item_manager.ItemSubGroup(name, name_group, order)

    #Unkown 그룹/서브 그룹 추가
    name_group = '_Unknown'
    name_subgroup = name_group
    order = 'zzz'
    item_manager.ItemGroup(name_group, order)
    item_manager.ItemSubGroup(name_subgroup, name_group, order)
    
def make_item_sub(elem):
    name = elem['name']         #name
    type = elem['type']         #type
    subgroup = elem['subgroup'] #subgroup
    if subgroup is None or subgroup == '' :
        if elem['type'] == 'fluid':
            subgroup = 'fluid'
        else:
            subgroup = '_Unknown'
    #flag
    if elem['flags'] is not None:
        flags = list(elem['flags'].values())
    else: flags = []
    #icon
    path_icon = elem['icon']
    if path_icon is None and elem['icons'] is not None:
        path_icon = elem['icons']['icon']
    
    order = elem['order']
    
    item_manager.Item(name, type, subgroup, flags, path_icon, order)

def make_item():
    global lua
    raw = lua.globals().data.raw

    list_item_kind = [\
        'item', 'item-with-entity-data', 'capsule', \
        'ammo', 'armor', 'gun', 'repair-tool', 'fluid'\
        , 'module', 'rail-planner', 'tool'\
        , 'spidertron-remote']
    
    #TODO : raw의 모든 리스트를 아이템으로 만들어야 할까?
    
    for kind in list_item_kind:
        table = raw[kind]
        for key in table:
            make_item_sub(table[key])

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
    
def make_recipe_time_in_out(table):
    time = table['energy_required']
    if time is None: time = 0.5
    ingredients = make_recipe_sub_list(table['ingredients'])
    results = make_recipe_results(table)
    
    return time, ingredients, results
    
def make_recipe():
    global lua
    raw = lua.globals().data.raw
    table_recipe = raw['recipe']
    
    for key in table_recipe:
        elem = table_recipe[key]
        name = elem['name']             #name
        path_icon = elem['icon']   #icon    
        category = elem['category']     #category
        if category is None: category = 'basic-crafting'
        subgroup = elem['subgroup']     #subgroup
        order = elem['order']
        if order is None: order = 'zzz'

        
        #not normal, expensive
        if elem['expensive'] is None:
            time, ingredients, results = make_recipe_time_in_out(elem)
            time_expensive = 0
            ingredients_expensive = []
            results_expensive = []
        #normal, expensive
        else:
            time, ingredients, results = make_recipe_time_in_out(elem['normal'])
            time_expensive, ingredients_expensive, results_expensive = \
                make_recipe_time_in_out(elem['expensive'])
                
        item_manager.Recipe(name, path_icon, category, subgroup, order, \
            time, ingredients, results, \
            time_expensive, ingredients_expensive, results_expensive)
            
    #resource to recipe
    table_resource = raw['resource']
    
    for key in table_resource:
        elem = table_resource[key]
        name = elem['name']             #name
        path_icon = elem['icon']
        category = elem['category']
        if category is None : category = 'basic-solid'
        subgroup = ''
        order = elem['order']
        if order is None: order = 'zzz'
        
        time = elem['minable']['mining_time']
        if time is None: time = 0.5
        results = make_recipe_results(elem['minable'])
        
        time_expensive = 0
        ingredients = []
        ingredients_expensive = []
        results_expensive = []
        
        item_manager.Recipe(name, path_icon, category, subgroup, order, \
            time, ingredients, results, \
            time_expensive, ingredients_expensive, results_expensive)

def make_factory():
    global lua
    raw = lua.globals().data.raw
    
    #furnace
    for key in raw['furnace']:
        item_manager.Factory( raw['furnace'][key] )
        
    #assembling-machine
    for key in raw['assembling-machine']:
        item_manager.Factory( raw['assembling-machine'][key] )
        
    #mining-drill
    for key in raw['mining-drill']:
        item_manager.Factory( raw['mining-drill'][key] )
        
def get_map_from_table(table):
    map_result = dict()
    for key in table:
        elem = table[key]
        if lupa.lua_type(elem) == 'table':
            elem = get_map_from_table(elem)
        map_result[key] = elem
        
    return map_result
    
def make_module():
    global lua
    raw = lua.globals().data.raw
    table_module = raw['module']
    
    for key in table_module:
        elem = table_module[key]
        name = elem['name']             #name
        path_icon = elem['icon']   #icon
        category = elem['category']     #category
        subgroup = elem['subgroup']     #subgroup
        tier = elem['tier']
        effect = get_map_from_table(elem['effect'])
        order = elem['order']
        
        if elem['limitation'] is None: limitation = []
        else : limitation = list(elem['limitation'].values())
        
        item_manager.Module(name, path_icon, category, subgroup, tier, limitation, effect, order)
    
def parse_locale(path_file, map):
    import configparser
    
    #locale 구성
    #[item-name]
    #advanced-circuit=고급 회로
    #artillery-shell=대포용 포탄
    #...
    #locale[item-name][advanced-circuit] = '고급 회로'

    config = configparser.ConfigParser()
    file = open(path_file, "r", encoding="utf-8")
    config.read_file(file)
    
    list_section = ['recipe-name', 'item-name', 'item-limitation', \
        'item-group-name', 'fluid-name', 'entity-name', 'equipment-name']
        
    for section in list_section:
        map[section] = dict()
        
    for section in config.sections() :
        if section not in list_section:
            continue
        for option in config.options(section):
            map[section][option] = config.get(section, option)
    file.close()
    
def make_locale(path):
    locale1 = config_manager.get_config('template', 'language_1st')
    locale2 = config_manager.get_config('template', 'language_2nd')
    
    path_base = os.path.join(path, 'data', 'base')
    path_locale = path_base + '\\locale'
    path_locale1 = path_locale + '\\' + locale1
    path_locale2 = path_locale + '\\' + locale2
    
    #init locale
    list_path_locale = [    \
        [path_locale1, item_manager.map_locale_1st], \
        [path_locale2, item_manager.map_locale_2nd]  \
    ]
    
    for elem in list_path_locale:
        if os.path.isdir(elem[0]):
            list_item_path = os.listdir(elem[0])
            for path_file in list_item_path:
                path = elem[0] + '\\' + path_file
                parse_locale(path, elem[1])

def fluid_str_to_float(str_fluid):
    str_fluid = str_fluid[:-1]
    num = 1
    while True:
        if str_fluid[-1] == 'M':
            num *= 1000000
        elif str_fluid[-1] == 'K':
            num *= 1000
        else:
            break
        str_fluid = str_fluid[:-1]
    num *= float(str_fluid)
    return num

def make_fluid_sub(table):
    global lua
    raw = lua.globals().data.raw
    
    name = '_fluid_' + table['name']
    name_factory = table['name']
    path_icon = ''
    category = name
    subgroup = '_Unknown'
    time = 1
    time_expensive = time
    list_input = []
    list_input_expensive = None
    list_output = []
    list_output_expensive = None
        
    flags = []
    energy_usage = 0
    crafting_categories = [category]
    crafting_speed = 1
    next_upgrade = ''
    module_slots = 0
    energy_source_type = None
    energy_source_emissions = None
    
    list_fluid_box_key = ['fluid_box', 'in_fluid_box', 'output_fluid_box']
    etc = {}
    amount = 0
    temper = None
    
    if table['pumping_speed'] is not None:      #offshore-pump 처리
        amount = table['pumping_speed'] * 60
    elif table['target_temperature'] is not None :  #boiler, heat-exchanger 처리
        temper = table['target_temperature']
        energy_consumption = table['energy_consumption']
        etc['target_temperature'] = temper
        etc['energy_consumption'] = energy_consumption
        consume = fluid_str_to_float(energy_consumption)
        
        temper_default = 0
        for key in list_fluid_box_key:
            elem = table[key]
            if elem is None: continue
            type_prob = elem['production_type']
            if not (type_prob == 'input' or type_prob == 'input-output'):
                continue
            filter = elem['filter']
            fluid = raw['fluid'][filter]
            temper_default = fluid['default_temperature']
            heat_capacity = fluid['heat_capacity']
            heat = fluid_str_to_float(heat_capacity)
            break
        amount = consume / ( (temper - temper_default) * heat )
        
    for key in list_fluid_box_key:
        elem = table[key]
        if elem is None: continue
        type_prob = elem['production_type']
        filter = elem['filter']
        item = item_manager.map_item[filter]
        
        if type_prob == 'input' or type_prob == 'input-output':
            list_input.append([filter, amount])
        elif type_prob == 'output':
            list_output.append([filter, amount])
            
    recipe_temp = item_manager.Recipe(name, path_icon, category, subgroup, 'zzz', \
        time, list_input, list_output, \
        time_expensive, list_input_expensive, list_output_expensive)
    recipe_temp.etc = etc
    
    map = { 'name' : name_factory, 'path_icon' : path_icon, 'flags' : flags, 'energy_usage' : energy_usage,\
        'crafting_categories' : crafting_categories, 'crafting_speed' : crafting_speed, \
        'next_upgrade' : next_upgrade, 'module_slots' : module_slots,\
        'energy_source_type' : energy_source_type, 'energy_source_emissions' : energy_source_emissions}
    factory_temp = item_manager.Factory(map)
        

def make_fluid():
    global lua
    raw = lua.globals().data.raw
    
    #boiler , offshore-pump
    #레시피 / 전용 팩토리 추가
    list_boiler_kind = ['boiler', 'offshore-pump']
    for kind in list_boiler_kind:
        table = raw[kind]
        for key in table:
            elem = table[key]
            make_fluid_sub(elem)

#-------------------------------------------------- util
def get_list_key(table):
    list_save = []
    for key in table:
        elem = table[key]
        list_key = list(elem.keys())
        list_save = list(set( list_save + list_key) )
        
    return list_save

def printKey(table):
    list_key = list(dict(table).keys())
    list_key.sort()
    for key in list_key:
        print(key)
        
def printSubKey(table):
    for key in get_list_key(table):
        print(key)

def printTable(table, depth_max = 100, depth = 1):
    str_tab = depth * '  '
    for key in table:
        value = table[key]
        type_value = lupa.lua_type(value)
        if type_value == 'table':
            print(str_tab, key, ' : ')
            if depth >= depth_max:
                #print(str_tab, 'name : ', dict(value).get('name'))
                pass
            else:
                printTable(dict(value), depth_max, depth+1)
        else:
            print(str_tab, key, ' : ', value)
            
def make_link_base(path):
    path_base = os.path.join(path, 'data', 'base')
    
    # 링크 점검
    if os.path.isfile('__base__') or \
        (os.path.isdir('__base__') and not os.path.islink('__base__')):
        print('__base__ alread exist but not same')
        exit()
    if os.path.islink('__base__'):
        realpath = os.readlink('__base__')
        if os.path.samefile(path_base, realpath):
            return
        else:
            os.remove('__base__')
    
    '''
    mklink /D "./__base__" "C:\Program Files (x86)\Steam\steamapps\common\Factorio\data\base"
    mklink /D __base__ path_base
    '''
    # bat 파일 생성
    cwd = os.getcwd()
    cmd = 'mklink /D "' + os.path.join(cwd, '__base__') + '" "' \
        + path_base + '"'
    
    fp = open('mklink.bat', 'w')
    fp.write(cmd)
    fp.close()
    
    # 관리자 권한 실행 - https://myinbox.tistory.com/112
    import subprocess
    
    bat_path = '"' + os.path.join(cwd, 'mklink.bat') + '"'
    cmd = [ 'powershell.exe', 'Start-Process', '-Verb', 'runAs', '-FilePath', bat_path]
    
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()
    #subprocess.run(cmd ,shell=True)
    
def del_link_base():
    if os.path.exists('mklink.bat'):
        os.remove('mklink.bat')
    if os.path.exists('__base__'):
        os.remove('__base__')
    
    
#-------------------------------------------------- main
def main() :
    from PyQt5.QtWidgets    import QMainWindow, QApplication
    import sys
    app = QApplication(sys.argv)

    #loading_widget.doLoad 참고

    path_factorio = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio'

    make_link_base(path_factorio)

    load_vanilla(path_factorio)
    
    import template_manager
    template_manager.cleanTemplateDir()
    
    make_item_group()
    make_item()
    make_recipe()
    make_factory()
    make_module()
    make_fluid()
    make_locale(path_factorio)
    
    
    item_manager.deleteHidden()
    item_manager.searchItemNoRecipe()
    item_manager.sortRecipe()
    item_manager.copyIcon()
    
    template_manager.copyDefaultIcon()
    template_manager.saveTemplateFile()
        
    # Common Post Process
    import elem_manager
    item_manager.sortItemList()
    elem_manager.initElemManager()
    
    if config_manager.get_config('template', 'delete_temp_files', 'boolean'):
        del_link_base()
    
    print('end')
    #exit()
    #sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()