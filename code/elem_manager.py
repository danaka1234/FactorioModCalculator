# coding: utf-8

import sys, math
import random   #https://docs.python.org/ko/3/library/random.html
import queue    #https://docs.python.org/ko/3.8/library/queue.html
                #http://www.daleseo.com/python-priority-queue
import item_manager, common_func

map_elem = dict()
map_link = dict()
id_max = 10000
#id_temp = 10000

def generageElemId(elem):
    global map_elem, id_max, id_temp
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
    global map_elem
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
    
class ElemProduct:       #내(생산자)가 생산하는것
    def __init__(self, name_product, sum_goal = 0, num_real = 0):
        self.name_product = name_product
        self.sum_goal = sum_goal    #목표 생산량 / 부모(소비자)가 필요로 하는 양의 합
        self.num_real = num_real    #실제 생산량 / 내(생산자)가 생산하는 양 기록
        self.sum_ratio = 0
        self.list_link = [] #ElemLink
 
class ElemMaterial:      #내(소비자)가 필요로 하는것
    def __init__(self, name_material, num_need = 0):
        self.name_material = name_material
        self.num_need = num_need    # 필요 재료 생샨량 / 나(소비자)가 필요한 양
        self.list_link = [] #ElemLink

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
        self.num_factory = 0    # 공장 개수 = 모듈 비율, 시간 적용한 것
        self.order = ''
        
        self.energy = 0
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
            
    def deleteElem(self):
        delElemId(self.id)
        
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
        
        self.deleteElemSub()

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
        
    def updateFactoryNum(self):
        self.num_factory = 1
        if self.factory is None:
            return
        time_recipe = self.recipe.getTime()
        num_recipe = 1
        for output in self.recipe.getListProduct():
            if output[0] == self.item_goal.name:
                num_recipe = output[1]
                break
        goal = self.num_goal
        speed = self.factory.crafting_speed * ( 1 + self.speed ) * ( 1 + self.beacon/100 )
        time = time_recipe / speed
        production = num_recipe * ( 1 + self.productivity )
        
        '''
        생산 = 레시피 수 * 모듈 보너스
        시간 = 레시피 시간 / ( 공장 속도 * 모듈 속도 * 비콘 ) 
       
        결과 = 공장수 * 생산 / 시간
        공장수 = 결과 * 시간 / 생산
        '''
        self.num_factory = goal * time / production
        
        # 나중에 모듈 적용하기

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
    def __init__(self, id_self, group, item_goal=None, num_goal=1, list_factory=[], list_module=[], beacon=0):
        super().__init__(id_self, group)
        self.recipe = None
        self.factory    = None
        self.num_goal = 1
        self.list_module = []
        self.num_module = 0
        self.beacon     = beacon
        self.level = 0
        
        self.speed = 0
        self.productivity = 0
        self.consumption = 0
        self.pollution = 0
        
        self.bFacNumBase = True
        
        self.changeItem(item_goal, False)
        self.changeFactoryFromList(list_factory)
        self.changeModule(list_module, bFillFirst=True)
        self.changeGoal(num_goal)
    
    def changeItem(self, item, bUpdate=True, bResetRecipe=True):
        if item is None:
            if self.recipe is None:
                tmp = item_manager.getSortedItemList()[0]
                while type(tmp) != item_manager.Item:
                    tmp = tmp.list_sub[0]
                item = tmp
            else:
                name_item = self.recipe.getListProduct()[0][0]
                item = item_manager.map_item[name_item]
        
        self.item_goal = item
        
        if bResetRecipe:
            if self.recipe is not None:
                for product in self.recipe.getListProduct():
                    # 목표 생산품이 레시피 안에 있는 경우
                    if product[0] == self.item_goal.name:
                        #self.updateInOut()
                        self.updateElem(all=True)
                        return
            #change recipe
            name_recipe = self.item_goal.list_madeby[0]
            recipe = item_manager.map_recipe[name_recipe]
            self.changeRecipe(recipe, False)
            
        if bUpdate:
            self.updateElem(all=True)
        
    def changeRecipe(self, recipe, bItemChange=True, item_goal=None):
        if self.recipe == recipe:
            return
        self.recipe = recipe
        
        if bItemChange:
            self.changeItem(item_goal)
            
        #팩토리 변경
        if self.factory is None\
            or recipe.category not in self.factory.crafting_categories:
            self.changeFactory(None, bUpdateGroup = False)
            
        #TODO : 처리. 링크 제거?
        self.resetInOut()
        self.list_module = []
        self.updateElem(all=True)
        
    def changeGoal(self, num_goal):
        if self.num_goal == num_goal: return
        self.bFacNumBase = True
        self.num_goal = num_goal
        self.updateElem(inout=True,group=True)
        
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
        
    def changeFactory(self, factory, bUpdateGroup = True):
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
        self.updateElem(group=True)
        
    def changeFacNum(self, num_factory):
        if self.num_factory == num_factory: return
        self.num_factory = num_factory
        self.bFacNumBase = False
        self.updateElem(all=True)
        
    def changeBeaconNum(self, num_beacon):
        self.beacon = num_beacon
        self.updateElem(all=True)
        
    def updateGoalByFacNum(self):
        num_recipe = 1  # 레시피 1회당 생산
        for output in self.recipe.getListProduct():
            if output[0] == self.item_goal.name:
                num_recipe = output[1]
                break
                
        # 속도 = 공장속도 * 보너스 * 비컨 보너스
        speed = self.factory.crafting_speed * (1 + self.speed) * (1 + self.beacon / 100)
        
        # 생산 = 회당 생산 * 공장수 * 속도 * 생산 보너스 / 레시피 시간
        self.num_goal = \
            num_recipe * self.num_factory * \
            speed * (1 + self.productivity) / \
            self.recipe.getTime()
        
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
        
        self.updateElem(all=True)
        
    def resetInOut(self):
        self.map_product  = {}
        self.map_material = {}
        
        for output in self.recipe.getListProduct():
            self.map_product[output[0]] = ElemProduct(output[0])
        for input in self.recipe.getListMaterial():
            self.map_material[input[0]] = ElemMaterial(input[0])
        
    def updateElem(self, module = False, inout = False, group = False, all=False):
        if self.bFacNumBase:
            if all or module:
                self.updateModule()
            if all or inout:
                self.updateInOut()
            self.updateFactoryNum()
        else:
            self.updateGoalByFacNum()
            if all or module:
                self.updateModule()
            if all or inout:
                self.updateInOut()
            
        self.emission = self.factory.energy_source_emissions * self.num_factory * (1 + self.pollution)
        self.energy = \
            self.num_factory * self.factory.energy_usage * (1 + self.consumption) \
            + math.ceil(self.num_factory) * self.factory.drain
            
        if all or group:
            self.group.updateGroupInOut()
        
    def updateInOut(self):
        global map_elem
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
            
            #각 링크에 필요한 양 할당 - TODO : 우선 등비로
            count_child = len(material.list_link)
            for link in material.list_link:
                num_need = material.num_need / count_child
                elem_producer = map_elem[link.producer.id]
                link.num_goal = num_need
                elem_producer.addGoal(key, num_need)
    
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

    def makeGraphByDFS(self, parent_group, map_search_recipe, level, list_factory, list_module, beacon):
        # 겹치지 않기 위한 map 
        map_search_recipe[self.recipe.name] = self
        recipe = item_manager.map_recipe.get(self.recipe.name)

        if recipe is None:
            return
        
        for material in recipe.getListMaterial():
            name_material = material[0]
            item_material = item_manager.map_item[name_material]
            name_recipe = None
            if len(item_material.list_madeby) != 0:
                name_recipe = item_material.list_madeby[0]

            node_child = None
                
            # 이미 들어있지 않을 때만 넣기
            # 루프는 어쩌지
            if map_search_recipe.get(name_recipe) is not None:
                node_child = map_search_recipe[name_recipe]
                if self.id != node_child.id:   # 무한루프 가능성
                    node_child.connectProduct(self, name_material)
                    #self.updateDownLevel() # 이미 들어있는 경우 레벨 꼬임을 대비한 새로고침
            else:
                node_child = ElemFactory(None, parent_group, item_material, 0, list_factory, list_module, beacon)
                node_child.connectProduct(self, name_material)
                node_child.makeGraphByDFS(parent_group, map_search_recipe, self.level, list_factory, list_module, beacon)

class ElemGroup(Elem):
    def __init__(self, id_self, group, id_root):
        super().__init__(id_self, group)
        self.list_child = []
        self.id_root       = id_root    #이거는 create에서만 쓰자
        self.energy_fuel = 0
    
    def deleteElem(self):
        super().deleteElem()
        
        for child in self.list_child:
            child.delElem()
    
    def changeItem(self, item):
        self.item_goal = item
        
    #list_args = [name_product, goal_per_sec, list_factory, list_module, ratio_beacon]
    '''
    def initGroup(self, args):
        global map_elem
        name_product    = args[0]
        goal_per_sec    = args[1]
        list_factory    = args[2]
        list_module     = args[3]
        ratio_beacon    = args[4]
        
        item_goal = item_manager.map_item[name_product]
        self.item_goal = item_goal
        self.num_goal = goal_per_sec
        self.num_factory = 1
        
        #root가 factory 일 때만 고려한다
        node_root = ElemFactory(None, self, item_goal, goal_per_sec \
            , list_factory, list_module, ratio_beacon)
        self.id_root = node_root.id
    
        # ----- make graph - DFS
        node_root.makeGraphByDFS(self, dict(), 0, list_factory, list_module, ratio_beacon)
        
        # ----- product, material의 goal, num 초기화
        for child in self.list_child:
            child.clearGoalNeed()
        node_root.addGoal(item_goal.name, goal_per_sec)
        
        # ----- update num_goal/ratio
        q = queue.SimpleQueue()
        m = dict()
        q.put(node_root)
        m[node_root.id] = node_root
        
        while(not q.empty()):
            node = q.get()
            node.updateAllBySumGoal()
            node.updateNumGoalBySumGoal()
            node.updateFactoryNum()
            
            for key in node.map_material.keys():
                material = node.map_material[key]
                for link in material.list_link:
                    if not m.get(link.producer.id):
                        elem_child = map_elem[link.producer.id]
                        m[link.producer.id] = elem_child
                        q.put(elem_child)
                     
        # ----- update self
        self.updateGroupInOut()
    '''
    def updateGroupInOut(self):
        map_all = {}
        
        self.energy = 0
        self.emission = 0
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
                        self.energy         = self.energy + child.energy
                    else:
                        self.energy_fuel    = self.energy_fuel + child.energy
            else:
                self.energy         = self.energy + child.energy
                self.energy_fuel    = self.energy_fuel + child.energy_fuel
                
            self.emission   = self.emission + child.emission
                
        #원래는 따로 만들고 업데이트 해야함
        self.map_product = {}
        self.map_material = {}
        for name in map_all:
            num = map_all[name]
            if   num > 0: #생산
                self.map_product[name] = ElemProduct(name, num, num)
            elif num < 0: #소비
                num = -num
                self.map_material[name] = ElemMaterial(name, num)
            else:
                continue
    '''
    def updateDown(self, bNumber = False, bLevel = False, bLink = False, bUpdateGroup = False):
        #map_material = {}
        #map_product  = {}
        
        #link, level, number 순 업데이트
        if bLink:   #link Update
            pass
            
        if bLevel:  #level Update
            pass
            
        if bNumber:    #number Update
            node_root = map_elem[self.id_root]
            node_root.updateDown(True)
    '''

def initElemManager():
    group = ElemGroup(0, None, None)
    group.changeFacNum(1)
    