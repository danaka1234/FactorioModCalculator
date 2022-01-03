# coding: utf-8

import sys, math, os
import random   #https://docs.python.org/ko/3/library/random.html
import queue    #https://docs.python.org/ko/3.8/library/queue.html
                #http://www.daleseo.com/python-priority-queue

import item_manager, common_func, option_widget
import json_manager, config_manager, item_manager

map_elem = dict()
map_link = dict()
id_max = 10000
#id_temp = 10000

name_elem_json = 'fmc_factories.json'
version_current = 0.1
factories_changed = False

def generageElemId(elem):
    global map_elem, id_max, id_temp, factories_changed
    factories_changed = True
    id = random.randrange(id_max)
    #id_temp = id_temp-1
    #id = id_temp
    while map_elem.get(id) is not None:
        id = random.randrange(id_max)
        #id_temp = id_temp-1
        #id = id_temp
    map_elem[id] = elem
    return id

def delElemId(id_elem):
    global map_elem, factories_changed
    factories_changed = True
    elem = map_elem.get(id_elem)
    if elem is None:
        return
    del map_elem[id_elem]

def generageLinkId(link):
    global map_link
    id = random.randrange(id_max)
    while map_link.get(id) is not None:
        id = random.randrange(id_max)
    map_link[id] = link
    return id

def delLinkId(id_link):
    global map_link
    link = map_link.get(id_link)
    if link is None:
        return
    del map_link[id_link]
'''
def changeLinkId(link):
    global map_link
    id = link.id
    generageLinkId(link)
    del map_link[id]
'''
'''
class ElemLink:
    def __init__(self, name, consumer, producer, ratio):
        self.name = name
        self.id = generageLinkId(self)
        self.consumer = consumer    #소비자, 부모
        self.producer = producer    #생산자, 자식
        self.ratio = ratio          #소비 비율
    
    def deleteLink(self):
        delLinkId(self.id)
        self.consumer.map_material[self.name].list_link.remove(self)
        self.producer.map_product [self.name].list_link.remove(self)
'''
class ElemProduct:       #내(생산자)가 생산하는것
    def __init__(self, name_product, sum_goal = 0, num_real = 0):
        self.name_product = name_product
        self.sum_goal = sum_goal    #목표 생산량 / 부모(소비자)가 필요로 하는 양의 합
        self.num_real = num_real    #실제 생산량 / 내(생산자)가 생산하는 양 기록
        self.sum_ratio = 0
        self.list_link = [] #ElemLink
        
    def toMap(self):
        map = {
            'name' : self.name_product,
            'sum_goal' : self.sum_goal,
            'num_real' : self.num_real,
            'sum_ratio' : self.sum_ratio,
        }
        return map
        
    def fromMap(map):
        elem = ElemProduct(map['name'])
        elem.sum_goal = map['sum_goal']
        elem.num_real = map['num_real']
        elem.sum_ratio = map['sum_ratio']
        return elem
 
class ElemMaterial:      #내(소비자)가 필요로 하는것
    def __init__(self, name_material, num_need = 0):
        self.name_material = name_material
        self.num_need = num_need    # 필요 재료 생샨량 / 나(소비자)가 필요한 양
        self.list_link = [] #ElemLink
        
    def toMap(self):
        map = {
            'name' : self.name_material,
            'num_need' : self.num_need,
        }
        return map
        
    def fromMap(map):
        elem = ElemMaterial(map['name'])
        elem.num_need = map['num_need']
        return elem

class Elem:
    def __init__(self, id_self, group):
        if id_self is not None:
            self.id = id_self
            map_elem[self.id] = self
        else:
            self.id = generageElemId(self)
        self.x = 0
        self.y = 0
        self.name = str(type(self).__name__)[4:] + ' ' + str(self.id)
        self.item_goal = None
        self.num_factory = 1    # 공장 개수 = 모듈 비율, 시간 적용한 것
        self.order = ''
        
        self.energy_elect = 0
        self.energy_fuel = 0
        self.emission = 0
        
        self.map_product  = dict()  # ElemProduct
        self.map_material = dict()  # ElemMaterial
        self.group = group
        
        if group is not None:
            group.list_child.append(self)
            
    def __lt__(self, other):
        if self.order != other.order:
            return self.order < other.order
        return self.id < other.id
        
    # 하위(Factory) 호출 > 상위(Elem) 호출 > 하위 toMap 진행
    def toMap(self):
        map_p = dict()
        map_m = dict()
        for item in self.map_product.items():
            map_p[item[0]] = item[1].toMap()
        for item in self.map_material.items():
            map_m[item[0]] = item[1].toMap()
        map = {
            'id' : self.id,
            'x' : self.x,
            'y' : self.y,
            'name' : self.name,
            'item_goal' : \
                self.item_goal.name \
                if self.item_goal is not None \
                else None,  \
            'num_factory' : self.num_factory,
            'order' : self.order,
            'energy_elect' : self.energy_elect,
            'energy_fuel' : self.energy_fuel,
            'emission' : self.emission,
            'map_product' : map_p,
            'map_material' : map_m,
            'group' : 
                self.group.id \
                if self.group is not None\
                else None,
        }
        return map
        
    # 상위(Elem) 호출 > 하위(Factory) 호출 > 상위 fromMap 진행
    def fromMap(map):
        global map_elem
        elem = None
        if map['_type'] == 'factory':
            elem = ElemFactory.fromMap(map)
        elif map['_type'] == 'group':
            elem = ElemGroup.fromMap(map)
        elif map['_type'] == 'custom':
            elem = ElemCustom.fromMap(map)
        elif map['_type'] == 'special':
            elem = ElemSpecial.fromMap(map)
            
        elem.x = map['x']
        elem.y = map['y']
        elem.name = map['name']
        elem.item_goal = \
            item_manager.map_item[map['item_goal']] \
            if map['item_goal'] is not None \
            else None
        elem.num_factory = map['num_factory']
        elem.order = map['order']
        elem.energy_elect = map['energy_elect']
        elem.energy_fuel = map['energy_fuel']
        elem.emission = map['emission']
        map_p = dict()
        map_m = dict()
        for item in map['map_product'].items():
            map_p[item[0]] = ElemProduct.fromMap(item[1])
        for item in map['map_material'].items():
            map_m[item[0]] = ElemMaterial.fromMap(item[1])
        elem.map_product = map_p
        elem.map_material = map_m
        elem.group = None
        
        return elem
        
    def changeName(self, name):
        if name is None or name == '':
            name = str(type(self).__name__)[4:] + ' ' + str(self.id)
        self.name = name
        global factories_changed
        factories_changed = True
            
    def deleteElem(self):
        if self.group is None:
            return
        self.group.list_child.remove(self)
        delElemId(self.id)
        self.group.updateGroupInOut()
        
        # 현재 링크는 없으니 일단 제거
        '''
        for key in self.map_product:
            product = self.map_product[key]
            list_link = product.list_link
            for link in list_link:
                link.deleteLink()
            del list_link
        
        for key in self.map_material:
            material = self.map_material[key]
            list_link = material.list_link
            for link in list_link:
                link.deleteLink()
            del list_link
        '''
        #self.deleteElemSub()

    '''
    def connectProduct(self, consumer, name_product, ratio = 1):
        if self    .map_product .get(name_product) is None :
            self    .map_product [name_product] = ElemProduct(name_product)
        if consumer.map_material.get(name_product) is None :
            consumer.map_material[name_product] = ElemMaterial(name_product)
        
        bFind = False
        for link in self.map_product[name_product].list_link:
            if link.consumer.id == consumer.id:
                bFind = True
                break
                
        if not bFind:
            link = ElemLink(name_product, consumer, self, ratio)
            self    .map_product [name_product].list_link.append(link)
            consumer.map_material[name_product].list_link.append(link)
    '''
    
    def clearGoalNeed(self):
        for key in self.map_product .keys():
            self.map_product[key] .sum_goal = 0
            self.map_product[key] .num_real = 0
        for key in self.map_material.keys():
            self.map_material[key].num_need = 0
        
    
    def addGoal(self, name_product, num_goal):
        if self.map_product.get(name_product) is not None:
            self.map_product[name_product].sum_goal += num_goal
        self.updateGoalByAllProduct()
    
    def changeFacNum(self, num_factory):
        self.num_factory = num_factory
    
    #TODO : 이 아래로 수정
    #제거한것 : 레벨
    
    def updateGoalByAllProduct(self):
        self.num_goal = 0
        for product in self.recipe.getListProduct():
            pass
    
    '''
    def updateAllBySumGoal(self):
        self.updateNumGoalBySumGoal()   #update num_goal
        self.updateFactoryNum()         #update factory
        self.updateInOut()              #update material product
        pass
        
    # product.sum_goal 에 따라 self.num_goal 을 변경
    def updateNumGoalBySumGoal(self):
        self.num_goal    = 0.0
        
        product = self.map_product[self.item_goal.name]
        self.num_goal = product.sum_goal
    '''
    
    def updateModule(self):
        pass
        
    # self.num_goal 에 따라 product.num_real, material.link.num_need 세팅
    
    '''
    def updateDownLevel(self, map_id = dict()):
        map_id[self.id] = self.id
        level = 0
        for key in self.map_product:
            product = self.map_product[key]
            for id in product.list_id_link:
                link = map_link[id]
                node_consumer = map_elem[link.id_consumer]
                level = max(level, node_consumer.level)
        
        self.level = level+1
        
        for key in self.map_material:
            material = self.map_material[key]
            for id in material.list_id_link:
                link = map_link[id]
                node_producer = map_elem[link.id_producer]
                if map_id.get(node_producer.id) is not None:
                    continue
                node_producer.updateDownLevel(map_id)
        
    def __lt__(self, other):
        if self.level != other.level:
            return self.level < other.level
        else:
            return self.id < other.id
    '''
    
class ElemFactory(Elem):
    def __init__(self, id_self, group, item_goal):
        super().__init__(id_self, group)
        self.recipe     = None
        self.factory    = None
        self.num_goal   = 1
        self.list_module = []
        self.num_module = 0
        self.beacon     = 0
        self.level = 0
        
        self.speed = 0
        self.productivity = 0
        self.consumption = 0
        self.pollution = 0
        
        self.bFacNumBase = False
        
        # 옵션 있으면 읽어서 설정
        if item_goal != None:
            self.changeItem(item_goal)
        
    def toMap(self):
        map = super().toMap()
        map['_type'] = 'factory'
        map['recipe'] = \
            self.recipe.name\
            if self.recipe is not None\
            else None
        map['factory'] = \
            self.factory.name\
            if self.factory is not None\
            else None
        map['list_module'] = self.list_module
        map['num_module'] = self.num_module
        map['num_goal'] = self.num_goal
        map['beacon'] = self.beacon
        map['level'] = self.level
        
        map['speed'] = self.speed
        map['productivity'] = self.productivity
        map['consumption'] = self.consumption
        map['pollution'] = self.pollution
        
        map['bFacNumBase'] = self.bFacNumBase
        
        return map
    
    def fromMap(map):
        id = map['id']
        e = ElemFactory(id, None, None)
        
        e.recipe = \
            item_manager.map_recipe[map['recipe']]\
            if map['recipe'] is not None\
            else None
        e.factory = \
            item_manager.map_factory[map['factory']]\
            if map['factory'] is not None\
            else None
        e.num_goal = map['num_goal']
        e.list_module = map['list_module']
        e.num_module = map['num_module']
        e.beacon = map['beacon']
        e.level = map['level']
        
        e.speed = map['speed']
        e.productivity = map['productivity']
        e.consumption = map['consumption']
        e.pollution = map['pollution']
        
        e.bFacNumBase = map['bFacNumBase']
        
        return e
    
    def changeItem(self, item, bUpdate=True, bResetRecipe=True):
        if item is None:
            if self.recipe is None:
                item = item_manager.getSortedItemList()[0]
            else:
                name_item = self.recipe.getListProduct()[0][0]
                item = item_manager.map_item[name_item]
        
        if self.item_goal == item:
            return
            
        item_before = self.item_goal
        self.item_goal = item
        
        if bResetRecipe:
            if self.recipe is not None:
                for product in self.recipe.getListProduct():
                    # 목표 생산품이 레시피 안에 있는 경우
                    if product[0] == self.item_goal.name:
                        for product2 in self.recipe.getListProduct():
                            if product2[0] == item_before.name:
                                break
                        # 두 생산물의 생산비율이 같은 경우 그냥 리턴
                        if product[1] == product2[1]:
                            return
            #change recipe
            name_recipe = self.item_goal.list_madeby[0]
            recipe = item_manager.map_recipe[name_recipe]
            self.changeRecipe(recipe, bUpdate=False)
            
        if bUpdate:
            self.resetInOut()
            self.updateElem(module=True)
        
    def changeRecipe(self, recipe, bUpdate=True):
        if self.recipe == recipe:
            return
        self.recipe = recipe
            
        #팩토리 변경
        if self.factory is None\
            or recipe.category not in self.factory.crafting_categories:
            self.changeFactory(None, bUpdate=False)
            
        #TODO : 처리. 링크 제거?
        self.list_module = []
        if bUpdate:
            self.resetInOut()
            self.updateElem(module=True)
        
    def changeGoal(self, num_goal):
        if self.num_goal == num_goal: return
        self.bFacNumBase = False
        self.num_goal = num_goal
        self.updateElem()
        
    def changeFactoryFromList(self, list_factory):
        if self.recipe is None: return
        
        factory_tmp = None
        for name_factory in list_factory:
            factory = item_manager.map_factory[name_factory]
            if self.recipe.category not in factory.crafting_categories:
                continue
            factory_tmp = factory
            break
        if factory_tmp is None:
            factory_tmp = item_manager.getFactoryListByRecipe(self.recipe)[-1]
        self.changeFactory(factory_tmp)
        
    def changeFactory(self, factory, bUpdate=True):
        if factory is None:
            list_factory = item_manager.getFactoryListByRecipe(self.recipe)
            if len(list_factory) > 0:
                factory = list_factory[-1]
                self.num_module = factory.module_slots
            else:
                factory = None
                self.num_module = 0
        else:
            self.num_module = factory.module_slots
        self.factory = factory
        
        if bUpdate:
            self.updateElem()
        
    def changeFacNum(self, num_factory):
        if self.num_factory == num_factory: return
        self.num_factory = num_factory
        self.bFacNumBase = True
        self.updateElem()
        
    def changeBeaconNum(self, num_beacon):
        self.beacon = num_beacon
        self.updateElem(module=True)
        
    def updateGoalOrFac(self):
        if self.factory is None:
            return
            
        # backup
        num_factory = self.num_factory
        num_goal = self.num_goal
            
        # 생산 = 레시피 당 생산 * 모듈 보너스
        num_recipe = 1  # 레시피 1회당 생산
        for output in self.recipe.getListProduct():
            if output[0] == self.item_goal.name:
                num_recipe = output[1]
                break
                
        production = num_recipe * ( 1 + self.productivity )
                
        # 속도 = 공장 속도 * 모듈 속도 * 비콘
        speed = self.factory.crafting_speed * \
                (1 + self.speed) * (1 + self.beacon / 100)
        
        # 개당 생산 시간 = 레시피 시간 / 속도
        time_recipe = self.recipe.getTime()
        time = time_recipe / speed
        
        if self.bFacNumBase:
            # 결과 = 공장수 * 생산 / 시간
            self.num_goal = self.num_factory * production / time
        else:
            # 공장수 = 결과 * 시간 / 생산량
            self.num_factory = self.num_goal * time / production
            
        return num_factory != self.num_factory or num_goal != self.num_goal
        
    def changeModule(self, list_module, bFillFirst=False):
        self.list_module = []
        
        list_module_tmp = []
        for name_module in list_module:
            module = item_manager.map_module[name_module]
            if len(module.limitation) > 0 and self.recipe.name not in module.limitation:
                continue
            if bFillFirst:
                list_module_tmp = [module.name] * self.num_module
                break
            else:
                list_module_tmp.append(module.name)
        
        if len(list_module_tmp) > self.num_module:
            list_module_tmp = list_module_tmp[:self.num_module]
        self.list_module = list_module_tmp
        
        self.updateElem(module=True)
        
    def resetInOut(self):
        self.map_product  = {}
        self.map_material = {}
        
        for output in self.recipe.getListProduct():
            self.map_product[output[0]] = ElemProduct(output[0])
        for input in self.recipe.getListMaterial():
            self.map_material[input[0]] = ElemMaterial(input[0])
        
    def updateElem(self, module = False):
        if module:
            self.updateModule()
            
        bUpdate = self.updateGoalOrFac()
        
        self.updateInOut()
            
        self.energy_elect = 0
        self.energy_fuel = 0
        self.emission = 0
        if self.factory is not None:
            self.emission = self.factory.energy_source_emissions * self.num_factory * (1 + self.pollution)
            energy = \
                self.num_factory * self.factory.energy_usage * (1 + self.consumption) \
                + math.ceil(self.num_factory) * self.factory.drain
            if self.factory.energy_source_type == 'electric':
                self.energy_elect = energy
            else:
                self.energy_fuel = energy
                
        self.group.updateGroupInOut()
            
        global factories_changed
        factories_changed = True
        
    def updateInOut(self):
        #global map_elem
        num_recipe = 1
        for output in self.recipe.getListProduct():
            if output[0] == self.item_goal.name:
                num_recipe = output[1]
                break
        #(초당)생산회수 = 목표 / 레시피 생산
        ratio = self.num_goal / num_recipe
        
        #product 초기화
        #1개 이상 생산하는 것은 비율 맞춰줌
        for key in self.map_product.keys():
            product = self.map_product[key]
            num_product = self.recipe.getProductNumByName(key)
            product.num_real = num_product * ratio
        
        #material 초기화 및 트리의 자식노드 초기화
        #(초당)소비량 = 생산회수 * 레시피 소비 / 보너스
        bonus = 1 + self.productivity
        for key in self.map_material.keys():
            material = self.map_material[key]
            num_material = self.recipe.getMaterialNumByName(key)
            material.num_need = num_material * ratio / bonus
            
        
    def updateModule(self):
        #backup
        speed = self.speed 
        productivity = self.productivity
        consumption = self.consumption
        pollution = self.pollution
        
        #reset
        self.speed = 0
        self.productivity = 0
        self.consumption = 0
        self.pollution = 0
        
        # 채취생산성
        if self.factory is not None and self.factory.type == 'mining-drill':
            self.productivity += option_widget.mine_product / 100
        
        #calculate
        for name_module in self.list_module:
            module = item_manager.map_module[name_module]
            
            for key in module.effect.keys():
                value = module.effect[key]['bonus']
                if key == 'speed':
                    self.speed += value
                elif key == 'productivity':
                    self.productivity += value
                elif key == 'consumption':
                    self.consumption += value
                elif key == 'pollution':
                    self.pollution += value
                    
        self.consumption = max(-0.8, self.consumption)
        
    def __lt__(self, other):
        if self.level != other.level:
            return self.level < other.level
        elif self.item_goal.name != other.item_goal.name:
            return self.item_goal.name < other.item_goal.name
        else:
            return self.id < other.id
        
    def setRecipeByItem(self, item_goal, num_goal):
        #if item_goal is None:
        #    key = list(item_manager.map_item)[0]
        #    item_goal = item_manager.map_item[key]
        #name_product = item_goal.name
        #self.item_goal = item_goal
        #self.map_material = dict()
        #self.map_product  = dict()
        #
        if len(item_goal.list_madeby) > 0:
            self.recipe = item_manager.map_recipe[item_goal.list_madeby[0]]
            
            for material in self.recipe.getListMaterial():
                self.map_material[material[0]] = ElemMaterial(material[0])
            
            for product  in self.recipe.getListProduct ():
                if product[0] == name_product:
                    self.map_product[name_product] = ElemProduct(name_product, num_goal)
                else:
                    self.map_product [product[0] ] = ElemProduct(product[0])
        else:
            log_manager.writelog('error : item has no recipe -', name_product)
            self.recipe = None
            self.map_product[name_product] = ElemProduct(name_product, num_goal)

class ElemGroup(Elem):
    def __init__(self, id_self, group):
        super().__init__(id_self, group)
        self.list_child = []
        
    def toMap(self):
        map = super().toMap()
        map['_type'] = 'group'
        map['energy_fuel'] = self.energy_fuel
        
        return map
        
    def fromMap(map):
        id = map['id']
        e = ElemGroup(id, None)
        return e
    
    def deleteElem(self):
        if self.group is None:
            return
            
        super().deleteElem()
        
        for child in self.list_child:
            child.deleteElem()
    
    def changeItem(self, item):
        self.item_goal = item
        global factories_changed
        factories_changed = True
        
    def changeFacNum(self, num_factory):
        if self.num_factory == num_factory: return
        self.num_factory = num_factory
        self.updateGroupInOut()
        
    def updateGroupInOut(self):
        map_all = {}
        
        self.emission = 0
        self.energy_elect = 0
        self.energy_fuel = 0
        
        for child in self.list_child:
            for name_material in child.map_material:
                material = child.map_material[name_material]
                if map_all.get(name_material) is None:
                    map_all[name_material] = 0
                map_all[name_material] = map_all[name_material] - material.num_need

            for name_product in child.map_product:
                product = child.map_product[name_product]
                if map_all.get(name_product) is None:
                    map_all[name_product] = 0
                map_all[name_product] = map_all[name_product] + product.num_real
                
            if type(child) == ElemFactory:
                if child.factory is not None:
                    if child.factory.energy_source_type == 'electric':
                        self.energy_elect   += child.energy_elect
                    else:
                        self.energy_fuel    += child.energy_fuel
            else:
                self.energy_elect   += child.energy_elect
                self.energy_fuel    += child.energy_fuel
                
            self.emission   = self.emission + child.emission
        self.emission       *= self.num_factory
        self.energy_elect   *= self.num_factory
        self.energy_fuel    *= self.num_factory
                
        #원래는 따로 만들고 업데이트 해야함
        self.map_product = {}
        self.map_material = {}
        for name in map_all:
            num = map_all[name] * self.num_factory
            if abs(num) < option_widget.min_ignore:
                continue
            elif num > 0: #생산
                self.map_product[name] = ElemProduct(name, num, num)
            elif num < 0: #소비
                num = -num
                self.map_material[name] = ElemMaterial(name, num)
            else:
                continue
                
        if self.group is not None:
            self.group.updateGroupInOut()
            
        global factories_changed
        factories_changed = True
            
class ElemCustom(Elem):
    def __init__(self, id_self, group):
        super().__init__(id_self, group)
        
    def toMap(self):
        map = super().toMap()
        map['_type'] = 'custom'
        return map
        
    def fromMap(map):
        id = map['id']
        e = ElemCustom(id, None)
        e.energy_fuel = map['energy_fuel']
        return e
    
    def deleteElem(self):
        super().deleteElem()
        
    def changeItem(self, item):
        self.item_goal = item
        global factories_changed
        factories_changed = True
        
    def changeEtc(self, power, fuel, pollution):
        self.energy_elect = power
        self.energy_fuel = fuel
        self.emission = pollution
        
        self.group.updateGroupInOut()
        
    def changeNum(self, isResult, name, num):
        if isResult:
            self.map_product[name].num_real = num
        else:
            self.map_material[name].num_need = num
            
        self.group.updateGroupInOut()
    
    def addSubItem(self, isResult):
        idx = 0
        list_item = item_manager.getSortedItemList()
        name_item = list_item[idx].name
        map = self.map_material
        if isResult: map = self.map_product
            
        while map.get(name_item) is not None:
            idx += 1
            name_item = list_item[idx].name
            
        if isResult:
            self.map_product[name_item] = ElemProduct(name_item, 0, 1)
        else:
            self.map_material[name_item] = ElemMaterial(name_item, 1)
            
        self.group.updateGroupInOut()
    
    def delSubItem(self, isResult, name):
        if isResult:
            del self.map_product[name]
        else:
            del self.map_material[name]
            
        self.group.updateGroupInOut()
        
    def changeSubItem(self, isResult, before, after):
        if isResult:
            num = self.map_product[before].num_real
            del self.map_product[before]
            self.map_product[after] = ElemProduct(after, 0, num)
        else:
            num = self.map_material[before].num_need
            del self.map_material[before]
            self.map_material[after] = ElemMaterial(after, num)
            
        self.group.updateGroupInOut()
        
class ElemSpecial(ElemFactory):
    def __init__(self, id_self, group, item_factory):
        super().__init__(id_self, group, None)
        
        # 처음 로딩
        if item_factory is not None:
            self.factory = item_factory
            name_recipe = item_factory.fixed_recipe
            self.recipe = item_manager.map_recipe[name_recipe]
            name_result = item_factory.list_result[0][1]
            self.changeItem(item_manager.map_item[name_result])
            
    def toMap(self):
        map = super().toMap()
        map['_type'] = 'special'
        
        return map
        
    def fromMap(map):
        id = map['id']
        e = ElemSpecial(id, None, None)
        
        e.recipe = \
            item_manager.map_recipe[map['recipe']]\
            if map['recipe'] is not None\
            else None
        e.factory = \
            item_manager.map_factory[map['factory']]\
            if map['factory'] is not None\
            else None
        e.num_goal = map['num_goal']
        e.list_module = map['list_module']
        e.num_module = map['num_module']
        e.beacon = map['beacon']
        e.level = map['level']
        
        e.speed = map['speed']
        e.productivity = map['productivity']
        e.consumption = map['consumption']
        e.pollution = map['pollution']
        
        e.bFacNumBase = map['bFacNumBase']
        
        return e
    
    def changeItem(self, item, bUpdate=True):
        if self.item_goal == item:
            return
            
        self.item_goal = item
        
        if bUpdate:
            self.resetInOut()
            self.updateElem(module=True)
            
    def updateGoalOrFac(self):
        if self.factory is None:
            return
        
        # backup
        num_factory = self.num_factory
        num_goal = self.num_goal
        
        # result
        result = []
        for elem in self.factory.list_result:
            if elem[1] == self.item_goal.name:
                result = elem
                
        # 생산 = 레시피 당 생산 * 모듈 보너스
        num_recipe = result[2]  # 레시피 1회당 생산
        for output in self.recipe.getListProduct():
            if output[0] == self.item_goal.name:
                num_recipe = output[1]
                break
                
        production = num_recipe * ( 1 + self.productivity )
                
        
        # 1개당 속도 = 공장 속도 * 모듈 속도 * 비콘
        speed_per_1 = self.factory.crafting_speed * \
                (1 + self.speed) * (1 + self.beacon / 100)
                
        # 개당 생산 시간 = 레시피 시간 / 속도
        time_recipe = self.recipe.getTime()
        time_per_1 = time_recipe / speed_per_1
                
        # 총 시간 = 100개 / 1개 속도 + 발사시간
        time = time_per_1 * self.factory.rocket_parts_required\
            + self.factory.fixed_time
        
        if self.bFacNumBase:
            # 결과 = 공장수 * 생산 / 시간
            self.num_goal = self.num_factory * production / time
        else:
            # 공장수 = 결과 * 시간 / 생산량
            self.num_factory = self.num_goal * time / production
            
        return num_factory != self.num_factory or num_goal != self.num_goal
        
    def resetInOut(self):
        self.map_product  = {}
        self.map_material = {}
        
        result = []
        for elem in self.factory.list_result:
            if elem[1] == self.item_goal.name:
                result = elem
        self.map_product[result[1]] = ElemProduct(result[1])
        self.map_material[result[0]] = ElemMaterial(result[0])
            
        for input in self.recipe.getListMaterial():
            self.map_material[input[0]] = ElemMaterial(input[0])
            
    def updateInOut(self):
        # result
        result = []
        for elem in self.factory.list_result:
            if elem[1] == self.item_goal.name:
                result = elem
        num_recipe = elem[2]
        
        #(초당)생산회수 = 목표 / 레시피 생산
        ratio = self.num_goal / num_recipe
        
        #product 초기화
        list(self.map_product.values())[0].num_real = self.num_goal
        
        #material 초기화 및 트리의 자식노드 초기화
        #(초당)소비량 = 생산회수 * 레시피 소비 / 보너스
        bonus = 1 + self.productivity
        for key in self.map_material.keys():
            material = self.map_material[key]
            if key == result[0]:
                num_part = 1
                num_material = 1
            else:
                num_part = self.factory.rocket_parts_required
                num_material = self.recipe.getMaterialNumByName(key)
            material.num_need = num_material * ratio / bonus * num_part
            
def resourceChanged():
    global map_elem
    for elem in map_elem.values():
        if type(elem) != ElemFactory:
            continue
        if elem.factory is None or elem.factory.type != 'mining-drill':
            continue
            
        elem.updateElem(module=True)
                
def save_elem():
    global map_elem, map_link, factories_changed
    if not factories_changed:
        return
        
    map_e = dict()
    map_l = dict()
    for item in map_elem.items():
        map_e[item[0]] = item[1].toMap()
    for item in map_link.items():
        map_l[item[0]] = item[1].toMap()
        
    map = {
        'factory'   : map_e,
        'link'      : map_l
    }
    
    path_template_dir = item_manager.getTemplateDir()
    path_elem_json = os.path.join(path_template_dir, name_elem_json)
    json_manager.save_json(path_elem_json, map)
    
def load_elem():
    global map_elem, map_link
    path_template_dir = item_manager.getTemplateDir()
    path_elem_json = os.path.join(path_template_dir, name_elem_json)
    map = json_manager.load_json(path_elem_json)
    if map is None:
        return
    map_e = map['factory']
    map_l = map['link']
    
    # json에서 key는 무조건 string
    # https://stackoverflow.com/questions/1450957/pythons-json-module-converts-int-dictionary-keys-to-strings
    for item in map_e.items():
        Elem.fromMap(item[1])
        
    for item in map_l.items():
        ElemLink.fromMap(item[1])
    
    #group 링크하기
    for item in map_elem.items():
        id = item[0]
        e = item[1]
        id_group = map_e[str(id)]['group']
        if id_group is not None:
            g = map_elem[id_group]
            e.group = g
            g.list_child.append(e)
    
def initElemManager():
    global map_elem, factories_changed
    if len(map_elem) == 0:
        group = ElemGroup(0, None)
        group.changeFacNum(1)
        factories_changed = True
    