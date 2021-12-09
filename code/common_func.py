# coding: utf-8
import os, traceback
import option_widget, template_manager
import item_manager

from PyQt5.QtGui        import QPixmap

def getAmountPerTime(amount, num_for_round = 3, bUnit = True, bTimeStr = True):
    time = option_widget.time_set[option_widget.time_config]
    time_name = option_widget.time_name[option_widget.time_config]
    amount2 = amount*time
    
    str_num = getAmountRound(amount2, num_for_round, bUnit=bUnit)
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
        path = os.path.join(template_manager.getTemplateDir(), template_manager.name_pollution_icon)
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

# -------------------------- tooltip
def getRecipeToolTipText(recipe):
    name = recipe.getName()
    time = recipe.getTime()
    list_product = recipe.getListProduct()
    list_material = recipe.getListMaterial()
    lem_max = max(len(list_product), len(list_material))
    str_temp = ''
    
    for i in range(lem_max):
        str_temp += '<tr>'
        str_temp +=     '<td>'
        if len(list_material) > i:
            elem = list_material[i]
            item = item_manager.map_item[elem[0]]
            str_temp += '<img src=\"'
            str_temp += item.getIconPath()
            str_temp += '\" width="16" height="16">'
            str_temp += ' : ' + str(elem[1])
        str_temp +=     '</td>'
        
        str_temp +=     '<td>'
        if len(list_product) > i:
            elem = list_product[i]
            item = item_manager.map_item[elem[0]]
            str_temp += '<img src=\"'
            str_temp += item.getIconPath()
            str_temp += '\" width="16" height="16">'
            str_temp += ' : ' + str(elem[1])
        str_temp +=     '</td>'
        str_temp += '</tr>'
    
    str_ret =   '<style>.td_m {vertical-align:top}</style>'+\
        name +\
        '<table><tr><td class=\'td_m\'>' +\
            '<img src=\"' +\
            getCommonPath('clock') +\
            '\" width="16" height="16">' +\
            ':' + str(time) +\
        '</td></tr></table>' +\
        '<table>'+\
            '<thead><tr><th>Ingred </th><th>Result</th></tr></thead>'+\
            '<tbody>' + str_temp + '</tbody>'+\
        '</table>'
        
    return str_ret
    
def getFactoryToolTipText(factory):
    name = factory.getName()
    speed = factory.crafting_speed
    pollution = factory.energy_source_emissions
    energy = getEnergyRound(factory.energy_usage)
    energy_type = ''
    if factory.energy_source_type == 'electric':
        energy_type = getCommonPath('electric')
    else:
        energy_type = getCommonPath('fuel')
    
    str_ret =   '<style>.td_m {vertical-align:top}</style>'+\
        name +\
        '<table><tr><td>' +\
            '<img src=\"' +\
            getCommonPath('clock') +\
            '\" width="16" height="16">' +\
            ' : x' + str(speed) +\
        '</td></tr><tr><td>' +\
            '<img src=\"' +\
            energy_type +\
            '\" width="16" height="16">' +\
            ' : ' + energy +\
        '</td></tr><tr><td>' +\
            '<img src=\"' +\
            getCommonPath('pollution') +\
            '\" width="16" height="16">' +\
            ' : ' + str(pollution) + '/m'\
        '</td></tr></table>'
        
    return str_ret
    
def getModuleTextSub(num, str_name):
    if num == 0: return ''
    str_sub = ''
    if num > 0: str_sub = '+'
    return '<tr><td>' + str_name + '</td><td>: ' + str_sub + str(num*100) + '%</td></tr>'
    
def getModuleToolTipText(item):
    module = item_manager.map_module[item.name]
    name = module.getName()
    num_speed   = 0
    num_prob    = 0
    num_consume = 0
    num_poll    = 0
    
    for key in module.effect.keys():
        value = module.effect[key]['bonus']
        if key == 'speed':
            num_speed   += value
        elif key == 'productivity':
            num_prob    += value
        elif key == 'consumption':
            num_consume += value
        elif key == 'pollution':
            num_poll    += value
    
    str_ret =   '<style>.td_m {vertical-align:top}</style>'+\
        name +\
        '<table>' 
        
    str_ret += getModuleTextSub(num_speed   , 'Speed')
    str_ret += getModuleTextSub(num_prob    , 'Productivity')
    str_ret += getModuleTextSub(num_consume , 'Consumption')
    str_ret += getModuleTextSub(num_poll    , 'Pollution')
    
    str_ret += '</table>'
        
    return str_ret

# -------------------------- debug
def main():
    print("common_func.py has no debug code as main")
    
if __name__ == '__main__':
    main()