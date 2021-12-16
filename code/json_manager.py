# coding: utf-8

import sys, os
#import PyQt5

import json
#https://docs.python.org/ko/3/library/json.html

import config_manager

def change_dict_to_list(data):
    if type(data) != dict and type(data) != list:
        return data
    
    # 리스트 하위에 딕셔너리이 있을 수 있으므로... 딕셔너리만 변형
    if type(data) == dict:
        array = list(data.items())
        
    # 리스트와 딕셔너리 모두 하위를 변경
    for i in range(len(array)):
        item = array[i]
        if type(item[1]) == dict:
            array[i] = (item[0], change_dict_to_list(item[1]))
    
    array.sort()
    # 딕셔너리만 추가... 변형을 용이하게 하기 위해 타입 item 추가...
    if type(data) == dict:
        array = [('__type', 'dict')] + array
        
    return array
    
def save_json(path, data):
    if config_manager.get_config('template','save_as_list', 'boolean'):
        array = change_dict_to_list(data)
    else:
        array = data
    
    str_temp = json.dumps(array, indent=4)
    with open(path, 'w') as file:    # save
        file.write(str_temp)
    
def change_list_to_dict(array):
    if type(array) != list:
        return array
        
    # 일단 하위 변형
    for elem in array:
        if type(elem) == list and type(elem[1]) == list:
            elem[1] = change_list_to_dict(elem[1])
        
    # 딕셔너리 일 때만 타입 item 추가
    if len(array) > 0 and array[0][0] == '__type' and array[0][1] == 'dict':
        array = array[1:]
        map = {elem[0] : elem[1] for elem in array}
        return map
        
    return array
    
def load_json(path):
    if not os.path.exists(path):
        return None
    
    str_temp = ''
    with open(path, 'r') as file:    # save
        str_temp = file.read()
    data = json.loads(str_temp)
    
    ret = change_list_to_dict(data)
    return ret
    
# -------------------------- debug
def main() :
    #path = 'input.json'
    path = 'E:\[Working]\FactorioModCalculator\code\input.json'
    map = load_json(path)
    
    str_temp = json.dumps(map, indent=4)
    with open('output.json', 'w') as file:    # save
        file.write(str_temp)
    '''
    array = [["__type","dict"],["test1"],"test2"]
    print(array)
    array = array[1:]
    print(array)
    '''
    
if __name__ == '__main__':
    main()