import random
import math
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
        self.gb_ratio = 2

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

    def play_turn(self, rc: RobotController):
        # self.build_towers(rc)
        # self.towers_attack(rc)
        self.send(rc)

    def build_towers(self, rc: RobotController):
        tower = TowerType.GUNSHIP #what tower to build?
        if (self.gunship_count / self.bomb_count > self.gb_ratio):
            tower = TowerType.BOMBER
        if (self.gunship_count / self.farm_count >= self.gf_ratio):
            tower = TowerType.SOLAR_FARM
        if rc.get_balance(rc.get_ally_team()) < tower.cost:
            return

        map = rc.get_map()
        maxpaths = -99999999999999999
        coords = (0, 0)
        for i in range(map.height):
            for j in range(map.width):
                if not (map.is_space(i, j) and rc.is_placeable(rc.get_ally_team(), i, j)): continue
                paths = self.paths_in_range(map, i, j, tower)
                if paths > maxpaths:
                    maxpaths = paths
                    coords = (i,j)
        x,y = coords

        rc.build_tower(tower, x, y)
        if (tower == TowerType.GUNSHIP): self.gunship_count += 1
        elif (tower == TowerType.BOMBER): self.bomb_count += 1
        elif (tower == TowerType.SOLAR_FARM): self.farm_count+=1
        else: self.reinforcer_count += 1

    
    def towers_attack(self, rc: RobotController):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            if tower.type == TowerType.GUNSHIP:
                rc.auto_snipe(tower.id, SnipePriority.FIRST)
            elif tower.type == TowerType.BOMBER:
                rc.auto_bomb(tower.id)
                
    def send(self, rc: RobotController):
        bal = rc.get_balance(rc.get_ally_team())
        round_num = rc.get_turn()
        if (round_num < 350):
            rc.send_debris(3, 40)
        elif (round_num < 700):
            rc.send_debris(3, 60)
        elif (round_num < 1000):
            rc.send_debris(2, 120)
        else:
            rc.send_debris(4, 100)
            
        # rc.send_debris(bal // 10, 100)
        # rc.send_debris(100, health=bal // 5)
        # rc.send_debris(math.floor(bal / 4.0), 1)
        