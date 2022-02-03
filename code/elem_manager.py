# coding: utf-8

import sys, math, os
import random
import queue
import copy

import item_manager, common_func, option_widget, loading_widget
import json_manager, config_manager, item_manager, log_manager

map_elem = dict()
id_max = 10000

name_elem_json = 'fmc_factories.json'
factories_changed = False

def generageElemId(elem):
    global map_elem, id_max, factories_changed
    factories_changed = True
    id = random.randrange(id_max)
    while map_elem.get(id) is not None:
        id = random.randrange(id_max)
    map_elem[id] = elem
    return id

def delElemId(id_elem):
    global map_elem, factories_changed
    factories_changed = True
    elem = map_elem.get(id_elem)
    if elem is None:
        return
    del map_elem[id_elem]
    
traced = set()
visited = set()
def is_not_loop(elem):
    global traced, visited
    traced = set()
    visited = set()
    return dfs_link(elem, True) and dfs_link(elem, False)
    
def dfs_link(v, isUp):
    global traced, visited, map_elem
    
    # 이미 탐색을 마친 노드이면 dfs 종료
    if v.id in visited:
        return True
    # 경로에 포함되어 있는 노드이면 순환 그래프
    if v.id in traced:
        return False
    # 경로에 v 노드 추가
    traced.add(v.id)
    
    if isUp:
        for list_id in v.link_pro.values():
            for id in list_id:
                elem = map_elem[id]
                if not dfs_link(elem, True):
                    return False
    else:
        for id in v.list_mat.values():
            elem = map_elem[id]
            if not dfs_link(elem, False):
                return False
        
    # 경로에 v노드 제거
    traced.remove(v.id)
    # 방문한 노드에 v 추가
    visited.add(v.id)
    return True

class Elem:
    def __init__(self, id_self, group):
        if id_self is not None:
            self.id = id_self
            map_elem[self.id] = self
        else:
            self.id = generageElemId(self)
        self.name = str(type(self).__name__)[4:] + ' ' + str(self.id)
        self.item_goal = None
        self.num_factory = 1    # 공장 개수 = 모듈 비율, 시간 적용한 것
        self.order = ''
        
        self.energy_elect = 0
        self.energy_fuel = 0
        self.emission = 0
        
        self.map_product  = dict()
        self.map_material = dict()
        self.link_pro = dict()      #[ name : [id,...] ]
        self.link_mat = dict()      #[ name : id ] 
        self.group = group
        
        if group is not None:
            group.list_child.append(self)
            
        self.error = 'None'
            
    # 하위(Factory) 호출 > 상위(Elem) 호출 > 하위 toMap 진행
    def toMap(self):
        map = {
            'id' : self.id,
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
            'map_product' : self.map_product,
            'map_material' : self.map_material,
            'link_pro' : self.link_pro,
            'link_mat' : self.link_mat,
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
        elem.map_product = map['map_product']
        elem.map_material = map['map_material']
        elem.link_pro = map['link_pro']
        elem.link_mat = map['link_mat']
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
        self.delLinkAll()
        delElemId(self.id)
        self.group.updateGroupInOut()
        
    def changeFacNum(self, num_factory, bUpdate=True):
        self.num_factory = num_factory
    
    # 소비자(consumer)가 호출, self 는 소비자(consumer)
    def addLink(self, name_item, id_producer, bUpdate=True):
        self.error = 'None'
        
        # consumer(self) 처리
        if name_item not in self.map_material.keys():
            log_manager.write_log('addLink : item not exist in consumer '+ str(self.id) + ', ' + name_item)
            return False
            
        id_link = self.link_mat.get(name_item)
        if id_link == id_producer: # 이미 들어있으면 실패
            log_manager.write_log('addLink : Already linked '+ str(id_producer) + ', ' + str(self.id))
            return False
            
        # producer(elem) 처리
        global map_elem
        elem = map_elem[id_producer]
        
        if name_item not in elem.map_product.keys():
            log_manager.write_log('addLink : item not exist in producer '+ str(elem.id) + ', ' + name_item)
            return False
            
        if elem.link_pro.get(name_item) is None:
            elem.link_pro[name_item] = []
            
        if self.id in elem.link_pro[name_item]:
            log_manager.write_log('addLink : Already linked '+ str(id_producer) + ', ' + str(self.id))
            return False
            
        # 연결
        if id_link is not None:  # 기존 링크 연결끊기
            self.delLink(name_item, id_link)
        
        self.link_mat[name_item] = id_producer
        elem.link_pro[name_item].append(self.id)
        
        # 마무리
        ret = is_not_loop(self)
        if not ret:
            self.error = 'Loop'
        if ret and bUpdate:
            ret = elem.updateFacNumByLink()
        if not ret:
            del self.link_mat[name_item]
            elem.link_pro[name_item].remove(self.id)
        return ret
        
    # self 는 소비자(consumer)
    def delLink(self, name_item, id_producer, bUpdate=True):
        # consumer(self) 처리
        global map_elem
        if name_item not in self.link_mat.keys():
            import traceback
            traceback.print_stack()
            log_manager.write_log('delLink : item not exist '+ str(self.id) + ', ' + name_item)
            return False
            
        if self.link_mat.get(name_item) != id_producer: # 동일하지 않으면 실패
            log_manager.write_log('delLink : not linked '+ str(id_producer) + ', ' + str(self.id))
            return False
        del self.link_mat[name_item]
        
        # producer(elem) 처리
        global map_elem
        elem = map_elem[id_producer]
        
        if name_item not in elem.map_product.keys():
            log_manager.write_log('delLinkSub : item not exist '\
                + str(self.id) + ', ' + str(elem.id) + ', ' + name_item)
            return False
            
        list_id = elem.link_pro.get(name_item)
        if list_id is None:
            log_manager.write_log('delLinkSub : not linked '\
                + str(self.id) + ', ' + str(elem.id) + ', ' + name_item)
                
        # 안 들어있으면 실패
        if self.id not in list_id :
            log_manager.write_log('delLinkSub : not linked '+ str(self.id) + ', ' + str(id_consumer))
            return False
            
        list_id.remove(self.id)
        if len(list_id) == 0:
            del elem.link_pro[name_item]
        
        ret = True
        if bUpdate:
            ret = self.updateFacNumByLink()
        return ret
        
    def delLinkAll(self):
        self.delLinkDownAll()
        self.delLinkUpAll()
        
    def delLinkDownAll(self):
        list_name = copy.deepcopy(list(self.link_mat.keys()))
        list_id   = copy.deepcopy(list(self.link_mat.values()))
        for idx in range(len(list_name)):
            self.delLink(list_name[idx], list_id[idx])
        self.link_mat = dict()
        
    def delLinkUpAll(self):
        global map_elem
        list_name = copy.deepcopy(list(self.link_pro.keys()))
        list_link = copy.deepcopy(list(self.link_pro.values()))
        
        for idx in range(len(list_name)):
            name = list_name[idx]
            list_id = list_link[idx]
            for id in list_id:
                elem = map_elem[id]
                elem.delLink(name, self.id)
        self.link_pro = dict()
            
    def haveLink(self, isResult):
        if isResult:
            for tuple in self.link_pro.items():
                if len(tuple[1]) != 0:
                    return True
            return False
        else:
            for tuple in self.link_mat.items():
                if tuple[1] not in [-1, 0]:
                    return True
        return False
            
    def updateFacNumByLink(self, bUpdate=True):
        global map_elem
        
        num_fac_max = 0     # 필요한 값 중 가장 큰 값
        name_max = ''
        for tuple in self.link_pro.items():
            num_sum = 0
            name_item = tuple[0]
            list_id = tuple[1]
            
            for id in list_id:
                elem = map_elem[id]
                id_sub = elem.link_mat.get(name_item)
                num = elem.map_material.get(name_item)
                if id_sub is None or num is None:
                    log_manager.write_log('updateFacNumByLink : Not Linked '\
                        + str(self.id) + ', ' + str(id)\
                        + ', item : ' + name_item)
                    return False
                num_sum += num
                
            num_recipe = self.getItemPerRecipe(name_item)
            num_factory = num_sum/num_recipe
            if num_fac_max < num_factory:
                num_fac_max = num_factory
                name_max = name_item
            
        if name_max == '' : # 링크가 하나도 없는 경우 그냥 리턴
            if type(self) == ElemFactory:
                self.updateElem()
            return True
            
        if type(self) in (ElemFactory, ElemSpecial) :
            # 팩토리는 생산성을 고려해야 한다... 다시 곱함
            num_recipe = self.getItemPerRecipe(name_item)
            num_goal = num_fac_max * num_recipe
            self.changeGoal(num_goal, bUpdate)
        else:
            self.changeFacNum( num_fac_max, bUpdate=bUpdate )
        return True
        
    def getLinkIdList(self, name, isResult):
        if isResult:
            list_id = self.link_pro.get(name)
            if list_id is None:
                return []
            return list_id
        else:
            link_id = self.link_mat.get(name)
            if link_id is None:
                return []
            return [link_id]
        
class ElemFactory(Elem):
    def __init__(self, id_self, group, item_goal):
        super().__init__(id_self, group)
        self.recipe     = None
        self.factory    = None
        self.num_goal   = 1
        self.list_module = []
        self.num_module = 0
        self.beacon     = 0
        
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
        
        e.speed = map['speed']
        e.productivity = map['productivity']
        e.consumption = map['consumption']
        e.pollution = map['pollution']
        
        e.bFacNumBase = map['bFacNumBase']
        
        return e
    
    def changeItem(self, item, bUpdate=True, bResetRecipe=True):
        if item is None:
            if self.recipe is None:
                item = item_manager.list_item_sorted[0]
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
            
        self.list_module = []
        if bUpdate:
            self.resetInOut()
            self.updateElem(module=True, bUpdateGroup=True)
        
    def changeGoal(self, num_goal, bUpdate=True):
        if self.num_goal == num_goal: return
        self.bFacNumBase = False
        self.num_goal = num_goal
        self.updateElem(bUpdateGroup=bUpdate)
      
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
            self.updateElem(bUpdateGroup=bUpdate)
        
    def changeFacNum(self, num_factory, bUpdate=True):
        if self.num_factory == num_factory: return
        self.num_factory = num_factory
        self.bFacNumBase = True
        self.updateElem(bUpdateGroup=bUpdate)
        
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
        # 레시피 1회당 생산
        num_recipe = self.getItemPerRecipe(self.item_goal.name)
                
        production = num_recipe * ( 1 + self.productivity )
                
        # 속도 = 공장 속도 * 모듈 속도
        speed = self.factory.crafting_speed * (1 + self.speed)
        
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
        self.delLinkAll()
        self.map_product  = {}
        self.map_material = {}
        
        for output in self.recipe.getListProduct():
            self.map_product[output[0]] = 0
        for input in self.recipe.getListMaterial():
            self.map_material[input[0]] = 0
        
    def updateElem(self, module = False, bUpdateGroup = True):
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
                + math.ceil(self.num_factory) * self.factory.drain * (1 + self.consumption)
            if self.factory.energy_source_type == 'electric':
                self.energy_elect = energy
            else:
                self.energy_fuel = energy
                
        # Link 업뎃
        for id in self.link_mat.values():
            global map_elem
            elem = map_elem[id]
            elem.updateFacNumByLink(bUpdate=False)
            
        if bUpdateGroup:
            self.group.updateGroupInOut()
            
        global factories_changed
        factories_changed = True
        
    def updateInOut(self):
        #global map_elem
        # 레시피 1회당 생산
        num_recipe = self.getItemPerRecipe(self.item_goal.name)
        
        #(초당)생산회수 = 목표 / 레시피 생산
        ratio = self.num_goal / num_recipe
        
        #product 초기화
        #1개 이상 생산하는 것은 비율 맞춰줌
        for key in self.map_product.keys():
            num_product = self.recipe.getProductNumByName(key)
            self.map_product[key] = num_product * ratio
        
        #material 초기화 및 트리의 자식노드 초기화
        #(초당)소비량 = 생산회수 * 레시피 소비 / 보너스
        bonus = 1 + self.productivity
        for key in self.map_material.keys():
            num_material = self.recipe.getMaterialNumByName(key)
            self.map_material[key] = num_material * ratio / bonus
        
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
                    
        # 비컨은 여기에...
        self.speed += self.beacon / 100
                    
        self.consumption = max(-0.8, self.consumption)
        
    def getItemPerRecipe(self, name_item, isResult = True):
        if isResult:    list_item = self.recipe.getListProduct()
        else:           list_item = self.recipe.getListMaterial()
        for tuple in list_item:
            if tuple[0] == name_item:
                return tuple[1]
        log_manager.write_log('getItemPerRecipe : cannot find '\
                + str(self.id) + ', ' + name_item\
                + ', ' + str(isResult) )
        return -1
        
class ElemGroup(Elem):
    def __init__(self, id_self, group):
        super().__init__(id_self, group)
        self.recipe_mat = {}
        self.recipe_pro = {}
        self.list_etc = [0, 0, 0]   #emission, elect, fuel
        self.list_child = []
        
    def toMap(self):
        map = super().toMap()
        map['_type'] = 'group'
        map['recipe_mat'] = self.recipe_mat
        map['recipe_pro'] = self.recipe_pro
        map['list_etc'] = self.list_etc
        
        return map
        
    def fromMap(map):
        id = map['id']
        e = ElemGroup(id, None)
        e.recipe_mat = map['recipe_mat']
        e.recipe_pro = map['recipe_pro']
        e.list_etc = map['list_etc']
        return e
    
    def deleteElem(self):
        if self.group is None:
            return
        
        list_child_id = []
        for child in self.list_child:
            list_child_id.append(child.id)
            
        global map_elem
        for id in list_child_id:
            child = map_elem[id]
            child.deleteElem()
            
        super().deleteElem()
    
    def changeItem(self, item):
        self.item_goal = item
        global factories_changed
        factories_changed = True
        
    def changeFacNum(self, num_factory, bUpdate=True):
        if self.num_factory == num_factory: return
        self.num_factory = num_factory
        self.multiplyNum()
        
    def multiplyNum(self):   # 리셋 처리 및 단순 곱셈
        self.map_material = {}
        self.map_product = {}
        
        for tuple in self.recipe_mat.items():
            name = tuple[0]
            num = tuple[1]
            if abs(num) < option_widget.min_ignore:
                continue
            self.map_material[name] = num * self.num_factory
            
        for tuple in self.recipe_pro.items():
            name = tuple[0]
            num = tuple[1]
            if abs(num) < option_widget.min_ignore:
                continue
            self.map_product[name] = num * self.num_factory
            
        # 없어진 아이템의 링크 삭제
        list_key = copy.deepcopy(list(self.link_mat.keys()))
        for key in list_key:
            if key not in self.recipe_mat.keys():
                id = self.link_mat[key]
                self.delLink(key, id)
                
        list_key = list(self.link_pro.keys())
        for key in list_key:
            if key not in self.recipe_pro.keys():
                list_id = copy.deepcopy(self.link_pro[key])
                for id in list_id:
                    global map_elem
                    elem = map_elem[id]
                    elem.delLink(key, self.id)
            
        self.emission       = self.list_etc[0] * self.num_factory
        self.energy_elect   = self.list_etc[1] * self.num_factory
        self.energy_fuel    = self.list_etc[2] * self.num_factory
        
        if self.group is not None:
            self.group.updateGroupInOut()
            
        global factories_changed
        factories_changed = True
            
    def updateGroupInOut(self):
        # 호출전 링크 변경 필요
        map_all = {}
        self.list_etc = [0, 0, 0]
        
        for child in self.list_child:
            for tuple in child.map_material.items():
                name_material = tuple[0]
                if map_all.get(name_material) is None:
                    map_all[name_material] = 0
                map_all[name_material] -= tuple[1]

            for tuple in child.map_product.items():
                name_product = tuple[0]
                if map_all.get(name_product) is None:
                    map_all[name_product] = 0
                map_all[name_product] += tuple[1]
                
            if type(child) in [ElemFactory, ElemSpecial]:
                if child.factory is not None:
                    if child.factory.energy_source_type == 'electric':
                        self.list_etc[1]    += child.energy_elect
                    else:
                        self.list_etc[2]    += child.energy_fuel
            else:   # ElemGroup, ElemCustom
                self.list_etc[1]    += child.energy_elect
                self.list_etc[2]    += child.energy_fuel
                
            self.list_etc[0]        += child.emission
            
        self.recipe_pro = dict()
        self.recipe_mat = dict()
            
        for name in map_all:
            num = map_all[name] * self.num_factory
            if abs(num) < option_widget.min_ignore:
                continue    # 삭제 필요할까
            elif num > 0:   #생산
                self.recipe_pro[name] = num
            elif num < 0:   #소비
                num = -num
                self.recipe_mat[name] = num
                
        self.multiplyNum()
            
    def getItemPerRecipe(self, name_item, isResult = True):
        if isResult:    map = self.recipe_pro
        else:           map = self.recipe_mat
            
        if map.get(name_item) is not None:
            return map[name_item]
        return -1
        
class ElemCustom(Elem):
    def __init__(self, id_self, group):
        super().__init__(id_self, group)
        self.recipe_pro = dict()
        self.recipe_mat = dict()
        
    def toMap(self):
        map = super().toMap()
        map['_type'] = 'custom'
        map['recipe_pro'] = self.recipe_pro
        map['recipe_mat'] = self.recipe_mat
        return map
        
    def fromMap(map):
        id = map['id']
        e = ElemCustom(id, None)
        e.recipe_pro = map['recipe_pro']
        e.recipe_mat = map['recipe_mat']
        return e
    
    def deleteElem(self):
        super().deleteElem()
        
    def changeItem(self, item):
        self.item_goal = item
        global factories_changed
        factories_changed = True
        
    def changeFacNum(self, num_factory, bUpdate=True):
        if self.num_factory == num_factory: return
        self.num_factory = num_factory
        self.updateCustom()
        
    def updateCustom(self):
        self.map_product = dict()
        self.map_material = dict()
        for name in self.recipe_pro.keys():
            self.map_product[name] = self.recipe_pro[name] * self.num_factory
        for name in self.recipe_mat.keys():
            self.map_material[name] = self.recipe_mat[name] * self.num_factory
            
        self.group.updateGroupInOut()
        
    def changeEtc(self, power, fuel, pollution):
        self.energy_elect = power
        self.energy_fuel = fuel
        self.emission = pollution
        
        self.group.updateGroupInOut()
        
    def editSubNum(self, isResult, name, num):
        if isResult:    self.recipe_pro[name] = num
        else:           self.recipe_mat[name] = num
        self.updateCustom()
    
    def addSubItem(self, isResult):
        idx = 0
        list_item = item_manager.list_item_sorted
        name_item = list_item[idx].name
        if isResult:    map = self.recipe_pro
        else:           map = self.recipe_mat
        
        while map.get(name_item) is not None:
            idx += 1
            name_item = list_item[idx].name
            
        if isResult:
            self.recipe_pro[name_item] = 1
        else:
            self.recipe_mat[name_item] = 1
            
        self.updateCustom()
    
    def delSubItem(self, isResult, name):
        global map_elem
        list_id = self.getLinkIdList(name, isResult)
        for id in list_id:
            if isResult:
                elem = map_elem[id]
                elem.delLink(name, self.id)
            else:
                self.delLink(name, id)
        
        if isResult:
            del self.recipe_pro[name]
        else:
            del self.recipe_mat[name]
            
        self.updateCustom()
        
    def changeSubItem(self, isResult, before, after):
        if isResult:
            num = self.recipe_pro[before]
            del self.recipe_pro[before]
            self.recipe_pro[after] = num
        else:
            num = self.recipe_mat[before]
            del self.recipe_mat[before]
            self.recipe_mat[after] = num
            
        self.updateCustom()
        
    def getItemPerRecipe(self, name_item, isResult = True):
        return ElemGroup.getItemPerRecipe(self, name_item, isResult)
        
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
            self.changeFactory(item_factory, bUpdate=False)
            
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
        
        # 생산 = 레시피 당 생산 * 모듈 보너스
        # 레시피 1회당 생산
        num_recipe = self.getItemPerRecipe(self.item_goal.name)
        production = num_recipe
                
        # 1개당 속도 = 공장 속도 * 모듈 속도
        speed_per_1 = self.factory.crafting_speed * (1 + self.speed)
                
        # 개당 생산 시간 = 레시피 시간 / 속도
        time_recipe = self.recipe.getTime()
        time_per_1 = time_recipe / speed_per_1
                
        # 총 시간 = 1개 시간 * 100개(모듈 고려) + 발사시간(모듈 무시)
        time = time_per_1 \
            * self.factory.rocket_parts_required / ( 1 + self.productivity )\
            + self.factory.fixed_time
        
        if self.bFacNumBase:
            # 결과 = 공장수 * 생산 / 시간
            self.num_goal = self.num_factory * production / time
        else:
            # 공장수 = 결과 * 시간 / 생산량
            self.num_factory = self.num_goal * time / production
        
        return num_factory != self.num_factory or num_goal != self.num_goal
        
    def resetInOut(self):
        self.delLinkAll()
        self.map_product  = {}
        self.map_material = {}
        
        result = []
        for elem in self.factory.list_result:
            if elem[1] == self.item_goal.name:
                result = elem
        self.map_product[result[1]] = 0
        self.map_material[result[0]] = 0
            
        for input in self.recipe.getListMaterial():
            self.map_material[input[0]] = 0
            
    def updateInOut(self):
        # result
        result = []
        for elem in self.factory.list_result:
            if elem[1] == self.item_goal.name:
                result = elem
        num_recipe = result[2]
        
        #(초당)생산회수 = 목표 / 레시피 생산
        ratio = self.num_goal / num_recipe
        
        #product 초기화
        self.map_product[self.item_goal.name] = self.num_goal
        
        #material 초기화 및 트리의 자식노드 초기화
        #(초당)소비량 = 생산회수 * 레시피 소비 / 보너스
        bonus = 1 + self.productivity
        for key in self.map_material.keys():
            if key == result[0]:
                num_material = 1 * (1 + self.productivity)
            else:
                num_part = self.factory.rocket_parts_required
                num_material = self.recipe.getMaterialNumByName(key) * num_part
            self.map_material[key] = num_material * ratio / bonus
            
    def getItemPerRecipe(self, name_item, isResult = True):
        if isResult:
            for elem in self.factory.list_result:
                if elem[1] == name_item:
                    return elem[2]  
        else:
            list_item = self.recipe.getListMaterial()
            for tuple in list_item:
                if tuple[0] == name_item:
                    return tuple[1]
        return -1
        
def resourceChanged():
    global map_elem
    for elem in map_elem.values():
        if type(elem) != ElemFactory:
            continue
        if elem.factory is None or elem.factory.type != 'mining-drill':
            continue
            
        elem.updateElem(module=True)
                
def save_elem():
    global map_elem, factories_changed
    if not factories_changed:
        return
        
    map_e = dict()
    for item in map_elem.items():
        map_e[item[0]] = item[1].toMap()
        
    map = {
        'factory'   : map_e,
        'version'   : common_func.version_current
    }
    
    path_template_dir = item_manager.getTemplateDir()
    path_elem_json = os.path.join(path_template_dir, name_elem_json)
    json_manager.save_json(path_elem_json, map)
    
def load_elem():
    global map_elem
    path_template_dir = item_manager.getTemplateDir()
    path_elem_json = os.path.join(path_template_dir, name_elem_json)
    map = json_manager.load_json(path_elem_json)
    
    if map is None:
        return
    
    version = map.get('version')
    if version is None:
        version = common_func.version_current
    # TODO : 버전별 작업하기
    if version != common_func.version_current:
        if loading_widget.load_widget is not None:
            loading_widget.load_widget.setMsg('Factories version is not same', True)
        return
        
    map_e = map.get('factory')
    if map_e is None:
        map_e = dict()
    
    # json에서 key는 무조건 string
    # https://stackoverflow.com/questions/1450957/pythons-json-module-converts-int-dictionary-keys-to-strings
    for item in map_e.items():
        Elem.fromMap(item[1])
        
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
    