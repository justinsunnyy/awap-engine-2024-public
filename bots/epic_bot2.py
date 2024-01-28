import random
from src.game_constants import SnipePriority, TowerType
from src.robot_controller import RobotController
from src.player import Player
from src.map import Map
from src.game_constants import Tile, TowerType

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map

    def paths_in_range(self, map: Map, x: int, y: int):
        res = 0
        for (xp,yp) in map.path:
            if (x - xp)**2 + (y-yp)**2 <= TowerType.GUNSHIP.range:
                res+=1
        return res

    def play_turn(self, rc: RobotController):
        self.build_towers(rc)
        self.towers_attack(rc)

    def build_towers(self, rc: RobotController):
        print(rc.get_balance(rc.get_ally_team()), TowerType.GUNSHIP.cost)
        if rc.get_balance(rc.get_ally_team()) < TowerType.GUNSHIP.cost:
            return
        
        map = rc.get_map()
        maxpaths = -1
        coords = (0, 0)
        for i in range(map.height):
            for j in range(map.width):
                if not (map.is_space(i, j) and rc.is_placeable(rc.get_ally_team(), i, j)): continue
                paths = self.paths_in_range(map, i, j)
                if paths > maxpaths:
                    maxpaths = paths
                    coords = (i,j)
        x,y = coords
        rc.build_tower(TowerType.GUNSHIP, x, y)
    
    def towers_attack(self, rc: RobotController):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            if tower.type == TowerType.GUNSHIP:
                rc.auto_snipe(tower.id, SnipePriority.FIRST)
            elif tower.type == TowerType.BOMBER:
                rc.auto_bomb(tower.id)
