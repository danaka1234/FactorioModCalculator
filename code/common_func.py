# coding: utf-8
import os, traceback
import config_manager, template_manager

from PyQt5.QtGui        import QPixmap

def getAmountPerTime(amount, num_for_round = 3, bTimeStr = True):
    time = config_manager.time_set[config_manager.time_config]
    time_name = config_manager.time_name[config_manager.time_config]
    amount2 = amount*time
    
    str_num = getAmountRound(amount2, num_for_round)
    if bTimeStr:
        str_num = str_num + '/' + time_name
    return str_num
    
def getAmountRound(amount, num_for_round = 3, bUnit = True):
    str_tail = ''
    if bUnit:
        if amount > pow(10, 9):
            amount = amount / pow(10, 9)
            str_tail = 'G'
        elif amount > pow(10, 6):
            amount = amount / pow(10, 6)
            str_tail = 'M'
        elif amount > pow(10, 3):
            amount = amount / pow(10, 3)
            str_tail = 'k'
    amount = round(amount, num_for_round)
    
    str_num = str(amount)
    if amount == int(amount):
        str_num = str(int(amount))
    return str_num + str_tail
    
def getEnergyRound(amount, num_for_round = 3):
    str_num = getAmountRound(amount, num_for_round)
    return str_num + 'W'
    
def getCommonPath(name):
    path = ''
    if name == 'clock':
        path = os.path.join(template_manager.getTemplateDir(), template_manager.name_clock)
    elif name == 'factorio':
        path = os.path.join(template_manager.getTemplateDir(), template_manager.name_fac_icon)
    elif name == 'electric':
        path = os.path.join(template_manager.getTemplateDir(), template_manager.name_electric_icon)
    elif name == 'fuel':
        path = os.path.join(template_manager.getTemplateDir(), template_manager.name_fuel_icon)
    elif name == 'pollution':
        path = os.path.join(template_manager.getTemplateDir(), \
            'graphics','icons', \
            template_manager.name_pollution_icon)
    elif name == 'factory':
        path = os.path.join(template_manager.getTemplateDir(), \
            'graphics','icons', \
            template_manager.name_factory_icon)
    return path
    
def getCommonPixmap(name, x = 32, y = 32):
    path = getCommonPath(name)
    return QPixmap(path).scaled(x, y)

def printCallStack():
    traceback.print_stack()

# -------------------------- debug
def main():
    print("common_func.py has no debug code as main")
    
if __name__ == '__main__':
    main()