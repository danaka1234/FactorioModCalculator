# coding: utf-8
import configparser
import os.path, sys
config_path_default = 'config.ini'
config_path = config_path_default
config = configparser.ConfigParser()

# config > section > option

config_default = dict()

config_default['template'] = dict()
config_default['template']['path_factorio'] = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio'
config_default['template']['path_mods'] = '%%AppData%%\\Factorio'
config_default['template']['path_template_dir'] = 'fmc_template'
config_default['template']['auto_load_from_template' ] = 'no'
config_default['template']['auto_load_from_data'] = 'no'
config_default['template']['language_1st'] = 'en'
config_default['template']['language_2nd'] = 'ko'
config_default['template']['delete_temp_files'] = 'no'

config_default['factories'] = dict()
config_default['factories']['path_save'] = 'fmc_factories.json'
config_default['factories']['auto_load'] = 'no'
config_default['factories']['auto_save'] = 'yes'

config_default['ui'] = dict()
config_default['ui']['display_monitor'] = '1'
config_default['ui']['window_width']    = '800'
config_default['ui']['window_height']   = '600'

#기타 설정과 전역변수들을 여기에 쑤셔박자
list_mods_all   = []
list_mods       = []

path_factorio = ''
path_mods = ''

str_error = ''

#for factories 
expensive = False
auto_update = True
time_config = 1
time_set = [1, 60, 3600]
time_name = ['s', 'm', 'h']

name_app = 'Factorio Mod Calculator'
    
def save_config(config):
    global config_path
    with open(config_path, 'w') as config_file:    # save
        config.write(config_file)

def create_config():
    for section in config_default.keys():
        config.add_section(section)
        
        for option in config_default[section].keys():
            config.set(section, option, config_default[section][option])
            
    save_config(config)
    
def get_config(section, option, type = None):
    if not config.has_section(section):
        if section not in config_default.keys():
            return None
        config.add_section(section)
    
    if not config.has_option(section, option):
        if option not in config_default[section].keys():
            return None
        config.set(section, option, config_default[section][option])
        
    if type == 'boolean':
        return config.getboolean(section, option)
    return config.get(section, option)
    
def set_config(section, option, value):
    if not config.has_section(section):
        config.add_section(section)
    #config.set(section, option, value)
    #%AppData% 저장할 떄 % 관련 에러가 있다
    
def read_config():
    global config_path
    if not os.path.isfile(config_path):
        create_config()
    file = open(config_path, "r", encoding="utf-8")
    config.read_file(file)
    file.close()

def init_config():
    global config_path, config_path_default, path_factorio, path_mods
    
    if len(sys.argv) > 2:
        config_path = sys.argv[1]
        if not os.path.exists(config_path):
            import log_manager
            log_manager.write_log('Cannot found file \"', config_path, '\"')
            config_path = config_path_default
    read_config()
    
    path_factorio   = get_config('template','path_factorio')
    path_mods       = get_config('template','path_mods')
    
def readModList():
    global list_mods_all, path_mods
    list_mods_all = []
    path_mod_convert  = os.path.expandvars(path_mods)
    path_mod_mods = path_mod_convert + '\\mods'
    
    if not os.path.isdir(path_mod_mods):
        return
    file_list = os.listdir(path_mod_mods)
    for file in file_list:
        path_file = path_mod_mods + '\\' + file
        if not os.path.isfile(path_file):
            continue
        last_str = file[len(file)-4:]
        if last_str != '.zip':
            continue
            
        list_mods_all.append(file)
    #초기화
    list_mods = list_mods_all

init_config()
# -------------------------- debug

def tour_config():
    print('')
    for section in config.sections() :
        print ('[' + section + ']')
        for option in config.options(section):
            print (option + ' = ' + config[section][option])
        print('')

def main() :
    read_config()
    print("print all config")
    tour_config()
    
if __name__ == '__main__':
    main()