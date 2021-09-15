# coding: utf-8
import os
import config_manager, template_manager

from PyQt5.QtGui        import QPixmap

def getAmountPerTime(amount, num_for_round = 3):
    time = config_manager.time_set[config_manager.time_config]
    time_name = config_manager.time_name[config_manager.time_config]
    
    if amount == int(amount):
        str_num = str(int(amount))
    else:
        str_num = str(round(amount*time, num_for_round))
    str_num += '/' + time_name
    return str_num
    
def getAmountRound(amount, num_for_round = 3):
    if amount == int(amount):
        return str(int(amount))
    str_num = str(round(amount, num_for_round))
    return str_num
    
def getCommonPath(name):
    path = ''
    if name == 'clock':
        path = os.path.join(template_manager.getTemplateDir(), template_manager.name_clock)
    elif name == 'factorio':
        path = os.path.join(template_manager.getTemplateDir(), template_manager.name_fac_icon)
    elif name == 'factory':
        path = os.path.join(template_manager.getTemplateDir(), \
            'graphics','icons', \
            template_manager.name_factory_icon)
    return path
    
def getCommonPixmap(name, x = 32, y = 32):
    path = getCommonPath(name)
    return QPixmap(path).scaled(x, y)


# -------------------------- debug
def main():
    print("common_func.py has no debug code as main")
    
if __name__ == '__main__':
    main()