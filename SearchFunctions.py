from game import Game
from collections import deque
from heapq import heappush, heappop

class State:
    def __init__(self, pos_player, pos_boxes, direction_from_father):
        self.pos_player = pos_player
        self.pos_boxes = pos_boxes
        self.direction_from_father = direction_from_father
        self.heuristic = 0
        self.depth = 0
    def get_player_pos(self):
        return self.pos_player
    def get_boxes_pos(self):
        return self.pos_boxes
    def get_solution(self):
        if self.father is None:
            return ""
        return self.father.get_solution() + self.direction_from_father
    def __lt__(self, other):
        return  self.sum_hurisitic_and_cost_spent < other.sum_hurisitic_and_cost_spent
    def set_depth(self, depth):
        self.depth = depth
    def get_depth(self):
        return self.depth
    def set_sum_hurisitic_and_cost_spent(self, sum_hurisitic_and_cost_spent):
        self.sum_hurisitic_and_cost_spent = sum_hurisitic_and_cost_spent
    def set_father(self, father):
        self.father = father
        
    
def get_state_id(player_pos, boxes_pos):
    return hash(str(player_pos) + str(boxes_pos))

def solver_bfs(game_map):
    game = Game(game_map)
    frontier = deque()
    explored = set()
    root = State(game.get_player_position(),game.get_box_locations(),"")
    root.set_father(None)
    frontier.append(root)
    while frontier:
        the_node = frontier.popleft()
        explored.add(get_state_id(the_node.get_player_pos(), the_node.get_boxes_pos()))
        for direction in ['U', 'D', 'R', 'L']:
            game.set_player_position(the_node.get_player_pos())
            game.set_box_positions(the_node.get_boxes_pos())
            result = game.apply_move(direction)
            if(result):
                child = State(game.get_player_position(),game.get_box_locations(),direction)
                child.set_father(the_node)
                child_state_id = get_state_id(child.get_player_pos(), child.get_boxes_pos())
                if game.is_game_won():
                    return child.get_solution(), len(explored)
                if child_state_id not in explored:
                    frontier.append(child)
                    explored.add(child_state_id)
    return None,len(explored)

def dfs(the_node, visited, game, number_states_seen):
    number_states_seen += 1
    game.set_player_position(the_node.get_player_pos())
    game.set_box_positions(the_node.get_boxes_pos())
    the_node_state_id = get_state_id(the_node.get_player_pos(), the_node.get_boxes_pos())
    visited.add(the_node_state_id)
    if game.is_game_won():
        return the_node.get_solution(), number_states_seen
    for direction in ['U', 'D', 'R', 'L']:
        game.set_player_position(the_node.get_player_pos())
        game.set_box_positions(the_node.get_boxes_pos())
        result = game.apply_move(direction)
        if result:
            child = State(game.get_player_position(), game.get_box_locations(), direction)
            child.set_father(the_node)
            child_state_id = get_state_id(child.get_player_pos(), child.get_boxes_pos()) 
            if child_state_id not in visited:
                ans, number_states_seen = dfs(child, visited, game, number_states_seen)
                if ans:
                    return ans, number_states_seen
    visited.remove(the_node_state_id)
    return None, number_states_seen

def solver_dfs(game_map):
    game = Game(game_map)
    visited = set()
    root = State(game.get_player_position(), game.get_box_locations(), "")
    root.set_father(None)
    return dfs(root, visited, game, 0)

def ids(the_node, visited, game, number_states_seen, depth_restricted):
    if the_node.get_depth() > depth_restricted:
        return None, number_states_seen
    number_states_seen += 1
    game.set_player_position(the_node.get_player_pos())
    game.set_box_positions(the_node.get_boxes_pos())
    the_node_state_id = get_state_id(the_node.get_player_pos(), the_node.get_boxes_pos())
    visited.add(the_node_state_id)
    if game.is_game_won():
        return the_node.get_solution(), number_states_seen
    for direction in ['U', 'D', 'R', 'L']:
        game.set_player_position(the_node.get_player_pos())
        game.set_box_positions(the_node.get_boxes_pos())
        result = game.apply_move(direction)
        if result:
            child = State(game.get_player_position(), game.get_box_locations(), direction)
            child.set_father(the_node)
            child.set_depth(the_node.get_depth() + 1)
            child_state_id = get_state_id(child.get_player_pos(), child.get_boxes_pos()) 
            if child_state_id not in visited:
                ans, number_states_seen = ids(child, visited, game, number_states_seen, depth_restricted)
                if ans:
                    return ans, number_states_seen
    visited.remove(the_node_state_id)
    return None, number_states_seen

def solver_ids(game_map):
    game = Game(game_map)
    visited = set()
    root = State(game.get_player_position(),game.get_box_locations(),"")
    root.set_depth(0)
    root.set_father(None)
    for depth_restricted in range(1000):
        ans,number_states_seen = ids(root, visited, game, 0, depth_restricted)
        if ans:
            return ans,number_states_seen
    return None, number_states_seen

def manhattan_dist(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])    

def heuristic0(game):
    return 0

def heuristic1(game):
    box_positions = game.get_box_locations()
    goal_positions = game.get_goal_locations()
    heuristic = 0
    for i in range(len(box_positions)):
        dist_box_from_goal = manhattan_dist(box_positions[i], goal_positions[i])
        heuristic += dist_box_from_goal
    return heuristic

def calculate_min_dist_box_to_portal_to_goal(portal_locations, box_pos, goal_pos):
    ans = 1e9
    for j in range(len(portal_locations)):
        dist1 = manhattan_dist(box_pos, portal_locations[j][0]) + manhattan_dist(portal_locations[j][1], goal_pos)
        dist2 = manhattan_dist(box_pos, portal_locations[j][1]) + manhattan_dist(portal_locations[j][0], goal_pos)
        dist_box_from_goal_with_portals = min(dist1, dist2)
        if dist_box_from_goal_with_portals < ans:
            ans = dist_box_from_goal_with_portals
    return ans

def heuristic2(game):
    box_positions = game.get_box_locations()
    goal_positions = game.get_goal_locations()
    portal_locations = game.get_portal_locations()
    heuristic = 0
    for i in range(len(box_positions)):
        dist_box_from_goal = manhattan_dist(box_positions[i], goal_positions[i])
        dist_box_from_goal_with_portal = calculate_min_dist_box_to_portal_to_goal(portal_locations, box_positions[i], goal_positions[i])
        heuristic += min(dist_box_from_goal, dist_box_from_goal_with_portal)  
    return heuristic

def solver_astar(game_map, heuristic_func=heuristic0, weight=1):
    game = Game(game_map)
    root = State(game.get_player_position(),game.get_box_locations(),"")
    frontier = []
    explored = set()
    best_cost = {}
    root.set_depth(0)
    root_cost = weight * heuristic_func(game)
    root.set_sum_hurisitic_and_cost_spent(root_cost)
    root.set_father(None)
    heappush(frontier, root)
    best_cost[get_state_id(root.get_player_pos(), root.get_boxes_pos())] = root_cost
    while frontier:
        the_node = heappop(frontier)
        explored.add(get_state_id(the_node.get_player_pos(), the_node.get_boxes_pos()))
        game.set_player_position(the_node.get_player_pos())
        game.set_box_positions(the_node.get_boxes_pos())
        if game.is_game_won():
            return the_node.get_solution(), len(explored)
        for direction in ['U', 'D', 'R', 'L']:
            game.set_player_position(the_node.get_player_pos())
            game.set_box_positions(the_node.get_boxes_pos())
            result = game.apply_move(direction)
            if(result):
                child_state_id = get_state_id(game.get_player_position(), game.get_box_locations())
                if child_state_id not in explored:
                    child_cost = weight * heuristic_func(game) + the_node.get_depth() + 1
                    if child_state_id not in best_cost or child_cost < best_cost[child_state_id]:
                        best_cost[child_state_id] = child_cost
                        child = State(game.get_player_position(), game.get_box_locations(), direction)
                        child.set_sum_hurisitic_and_cost_spent(child_cost)
                        child.set_depth(the_node.get_depth() + 1)
                        child.set_father(the_node)
                        heappush(frontier, child)           
    return None, len(explored)
def solver_astar2(game_map, heuristic_func=heuristic1, weight=1):
    game = Game(game_map)
    root = State(game.get_player_position(),game.get_box_locations(),"")
    frontier = []
    explored = set()
    best_cost = {}
    root.set_depth(0)
    root_cost = weight * heuristic_func(game)
    root.set_sum_hurisitic_and_cost_spent(root_cost)
    root.set_father(None)
    heappush(frontier, root)
    best_cost[get_state_id(root.get_player_pos(), root.get_boxes_pos())] = root_cost
    while frontier:
        the_node = heappop(frontier)
        explored.add(get_state_id(the_node.get_player_pos(), the_node.get_boxes_pos()))
        game.set_player_position(the_node.get_player_pos())
        game.set_box_positions(the_node.get_boxes_pos())
        if game.is_game_won():
            return the_node.get_solution(), len(explored)
        for direction in ['U', 'D', 'R', 'L']:
            game.set_player_position(the_node.get_player_pos())
            game.set_box_positions(the_node.get_boxes_pos())
            result = game.apply_move(direction)
            if(result):
                child_state_id = get_state_id(game.get_player_position(), game.get_box_locations())
                if child_state_id not in explored:
                    child_cost = weight * heuristic_func(game) + the_node.get_depth() + 1
                    if child_state_id not in best_cost or child_cost < best_cost[child_state_id]:
                        best_cost[child_state_id] = child_cost
                        child = State(game.get_player_position(), game.get_box_locations(), direction)
                        child.set_sum_hurisitic_and_cost_spent(child_cost)
                        child.set_depth(the_node.get_depth() + 1)
                        child.set_father(the_node)
                        heappush(frontier, child)           
    return None, len(explored)
def solver_astar3(game_map, heuristic_func=heuristic2, weight=1):
    game = Game(game_map)
    root = State(game.get_player_position(),game.get_box_locations(),"")
    frontier = []
    explored = set()
    best_cost = {}
    root.set_depth(0)
    root_cost = weight * heuristic_func(game)
    root.set_sum_hurisitic_and_cost_spent(root_cost)
    root.set_father(None)
    heappush(frontier, root)
    best_cost[get_state_id(root.get_player_pos(), root.get_boxes_pos())] = root_cost
    while frontier:
        the_node = heappop(frontier)
        explored.add(get_state_id(the_node.get_player_pos(), the_node.get_boxes_pos()))
        game.set_player_position(the_node.get_player_pos())
        game.set_box_positions(the_node.get_boxes_pos())
        if game.is_game_won():
            return the_node.get_solution(), len(explored)
        for direction in ['U', 'D', 'R', 'L']:
            game.set_player_position(the_node.get_player_pos())
            game.set_box_positions(the_node.get_boxes_pos())
            result = game.apply_move(direction)
            if(result):
                child_state_id = get_state_id(game.get_player_position(), game.get_box_locations())
                if child_state_id not in explored:
                    child_cost = weight * heuristic_func(game) + the_node.get_depth() + 1
                    if child_state_id not in best_cost or child_cost < best_cost[child_state_id]:
                        best_cost[child_state_id] = child_cost
                        child = State(game.get_player_position(), game.get_box_locations(), direction)
                        child.set_sum_hurisitic_and_cost_spent(child_cost)
                        child.set_depth(the_node.get_depth() + 1)
                        child.set_father(the_node)
                        heappush(frontier, child)           
    return None, len(explored)
def solver_astar4(game_map, heuristic_func=heuristic2, weight= 2.5):
    game = Game(game_map)
    root = State(game.get_player_position(),game.get_box_locations(),"")
    frontier = []
    explored = set()
    best_cost = {}
    root.set_depth(0)
    root_cost = weight * heuristic_func(game)
    root.set_sum_hurisitic_and_cost_spent(root_cost)
    root.set_father(None)
    heappush(frontier, root)
    best_cost[get_state_id(root.get_player_pos(), root.get_boxes_pos())] = root_cost
    while frontier:
        the_node = heappop(frontier)
        explored.add(get_state_id(the_node.get_player_pos(), the_node.get_boxes_pos()))
        game.set_player_position(the_node.get_player_pos())
        game.set_box_positions(the_node.get_boxes_pos())
        if game.is_game_won():
            return the_node.get_solution(), len(explored)
        for direction in ['U', 'D', 'R', 'L']:
            game.set_player_position(the_node.get_player_pos())
            game.set_box_positions(the_node.get_boxes_pos())
            result = game.apply_move(direction)
            if(result):
                child_state_id = get_state_id(game.get_player_position(), game.get_box_locations())
                if child_state_id not in explored:
                    child_cost = weight * heuristic_func(game) + the_node.get_depth() + 1
                    if child_state_id not in best_cost or child_cost < best_cost[child_state_id]:
                        best_cost[child_state_id] = child_cost
                        child = State(game.get_player_position(), game.get_box_locations(), direction)
                        child.set_sum_hurisitic_and_cost_spent(child_cost)
                        child.set_depth(the_node.get_depth() + 1)
                        child.set_father(the_node)
                        heappush(frontier, child)           
    return None, len(explored)