import random
from src.game_constants import SnipePriority, TowerType
from src.robot_controller import RobotController
from src.player import Player
from src.map import Map
from src.game_constants import Tile, TowerType

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.gunship_count = 1
        self.bomb_count = 1
        self.farm_count = 1
        self.reinforcer_count = 1
        self.gf_ratio = 1
        self.gb_ratio = 1
        self.turn = 0
        self.stage = 1

    def paths_in_range(self, map: Map, x: int, y: int, tower):
        res = 0
        max_dist = tower.range
        if (tower == TowerType.SOLAR_FARM):
            max_dist = TowerType.GUNSHIP.range
        for (xp,yp) in map.path:
            if (x - xp)**2 + (y-yp)**2 <= max_dist:
                res+=1
        if (tower == TowerType.SOLAR_FARM):
            return -res
        return res
    
    def sell_bombers(self, rc):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            if tower.type == TowerType.BOMBER:
                rc.sell_tower(tower.id)

    def play_turn(self, rc: RobotController):
        if (self.turn == 1000):
            self.gf_ratio = 0.4
        if (self.turn == 4500):
            self.gb_ratio = 9999999999999999999
            self.sell_bombers(rc)
            self.bomb_count = 1
            while (self.stage1(rc) == 1):
                self.stage1(rc)
        while (self.build_towers(rc) == 1):
            self.build_towers(rc)
        self.towers_attack(rc)
        self.turn += 1

    def stage1(self, rc):
        tower = TowerType.GUNSHIP #what tower to build?
        if (self.gunship_count / self.bomb_count > self.gb_ratio and self.bomb_count < 10):
            tower = TowerType.BOMBER
        if (self.gunship_count / self.farm_count >= self.gf_ratio):
            tower = TowerType.SOLAR_FARM

        if rc.get_balance(rc.get_ally_team()) < tower.cost:
            return 0

        map = rc.get_map()
        maxpaths = -99999999999999999
        coords = (0, 0)
        for i in range(map.width):
            for j in range(map.height):
                if not (map.is_space(i, j) and rc.is_placeable(rc.get_ally_team(), i, j)): continue
                paths = self.paths_in_range(map, i, j, tower)
                if paths > maxpaths:
                    maxpaths = paths
                    coords = (i,j)
        x,y = coords

        if (maxpaths == -99999999999999999):
            self.stage = 2
            return 0

        rc.build_tower(tower, x, y)
        if (tower == TowerType.GUNSHIP):
            self.gunship_count += 1
        elif (tower == TowerType.BOMBER): self.bomb_count += 1
        elif (tower == TowerType.SOLAR_FARM): self.farm_count+=1
        else: self.reinforcer_count += 1
        return 1
    
    def stage2(self, rc):
        towers = rc.get_towers(rc.get_ally_team())
        map = rc.get_map()
        solar_farm_exists = False
        for tower in towers:
            x,y = tower.x, tower.y
            paths = self.paths_in_range(map,x,y,TowerType.GUNSHIP)
            if (tower.type == TowerType.SOLAR_FARM and paths > 0):
                rc.sell_tower(tower.id)
                rc.build_tower(TowerType.GUNSHIP, x, y)
                solar_farm_exists = True
        if (not solar_farm_exists):
            self.stage = 3

    def find_tower(self, rc, x, y):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            if (tower.x == x and tower.y == y):
                return tower
        return -1

    def stage3(self, rc):
        map = rc.get_map()
        for i in range(2, map.width, 2):
            for j in range(2, map.height, 2):
                if (not map.is_space(i, j)): continue
                t = self.find_tower(rc,i,j)
                if (t.type != TowerType.GUNSHIP): continue
                if (rc.get_balance(rc.get_ally_team()) < 2200): continue
                rc.sell_tower(t.id)
                rc.build_tower(TowerType.REINFORCER, i, j)

    def build_towers(self, rc: RobotController):
        map = rc.get_map()
        if (self.stage == 1):
            return self.stage1(rc)
        elif (self.stage == 2):
            # if (rc.get_balance(rc.get_ally_team()) < map.height * map.width / 4 * 2200 + self.farm_count*-600):
            #     return 0
            return self.stage2(rc)
        elif (self.stage == 3):
            return self.stage3(rc)
    
    def towers_attack(self, rc: RobotController):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            if tower.type == TowerType.GUNSHIP:
                rc.auto_snipe(tower.id, SnipePriority.FIRST)
            elif tower.type == TowerType.BOMBER:
                rc.auto_bomb(tower.id)
