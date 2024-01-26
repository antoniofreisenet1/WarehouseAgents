#Test of a warehouse model using mesa agents. The model is based on the paper "A Multi-Agent Architecture for Warehouse Management" by M. G. Villalobos et al.

import mesa
import numpy as np

class Box(mesa.Agent):
    def __init__(self, unique_id, model, position):
        super().__init__(unique_id, model)
        self.position = position


class Stack(mesa.Agent):
    def __init__(self, unique_id, model, position):
        super().__init__(unique_id, model)
        self.position = position
        self.boxes = []

    def add_box(self, box):
        self.boxes.append(box)

    def is_full(self):
        return len(self.boxes) == self.model.num_boxes_per_stack



class Warehouse(mesa.Model):
    #A warehouse will have m x n spaces
    def __init__(self, width, height, num_robots, num_boxes):
        #Conditions to check: num_boxes_per_stack <= 5
        #num_boxes <= m*n*5
        super().__init__()
        self.grid = mesa.space.MultiGrid(width, height, torus=False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.datacollector = mesa.datacollection.DataCollector(model_reporters={"Grid":get_grid})
        self.next_stack_id = 0
        self.boxes_location = set()
        self.stacks = {}
        self.num_boxes_per_stack = 5

        self.initialize_boxes(num_boxes)
        self.initialize_robots(num_robots)

    def initialize_boxes(self, num_boxes):
        #check preconditions:
        if(num_boxes > self.grid.width*self.grid.height):
            print("Too many boxes for the warehouse")
            return

        #Initialize boxes in random locations
        for i in range(num_boxes):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            while((x,y) in self.boxes_location):
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
            self.boxes_location.add((x,y))
            box = Box(self.next_id(), (x,y), self)
            self.grid.place_agent(box, (x,y))
            self.schedule.add(box)
        print("Boxes initialized at: ", self.boxes_location)
    
    def initialize_robots(self, num_robots):

        for i in range(num_robots):

            while(True):
                x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
                if((x,y) not in self.boxes_location): #to be replaced with a function that checks if the space is valid (empty)
                    id_robot = "Robot " + str(i)
                    robot = Robot(id_robot, (x,y), self)
                    self.grid.place_agent(robot, (x,y))
                    self.schedule.add(robot)
                    break

    def all_boxes_stacked(self):
        return all(stack.is_full() for stack in self.stacks.values()) and not self.boxes
    
    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        if(self.all_boxes_stacked()):
            self.running = False
    
# class State:
#     def __init__(self, spaces):
#         #We have a warehouse of mxn spaces
#         self.spaces = spaces
#     def is_valid(self, currentSpace):
#         #Check if the current space is valid
#         if currentSpace in self.spaces:
#             for space in currentSpace:
#                 # Do something with the space variable
#                 for position in space:
#                     if(position > 5 or position < 0):
#                         return False
#                     else:
#                         return True
                    

class Robot(mesa.Agent):

    #The robot will have beliefs, desires and intentions
    def __init__(self, unique_id, position, model):
        super().__init__(unique_id, model)
        self.position = position
        self.holding_box = False


    def find_nearest_incomplete_stack(self):
        #Find the nearest incomplete stack
        #If there are no incomplete stacks, return None
        #If there are incomplete stacks, return the nearest one
        incomplete_stacks = [stack for stack in self.model.stacks if not stack.is_full()]
        if not incomplete_stacks:
            # nearest_stack = None
            return None

        closest_stack = min(incomplete_stacks, key=lambda stack: self.distance_to(stack))
        return closest_stack
    
    def distance_to(self, position):
        x1, y1 = self.position
        x2, y2 = position
        return abs(x1-x2) + abs(y1-y2) #Can be changed for a manhattan distance/euclidean distance calculation
    
    def distance_to_target(self, position, target_position):
        x1, y1 = position
        x2, y2 = target_position
        return abs(x1-x2) + abs(y1-y2)
    
    def move_to(self, position):
        #Examines the best way to reach a certain position and then moves towards it

        possible_steps = self.model.grid.get_neighborhood(self.position, moore=False, include_center=False)
        best_step = min(possible_steps, key=lambda step: self.distance_to_target(step, position))
        self.model.grid.move_agent(self, best_step)

    def move(self):
        #Moves the agent. If the agent is holding a box, it will move to the nearest incomplete stack. If not, move randomly.
        if self.holding_box:
            stack = self.find_nearest_incomplete_stack()
            if stack:
                self.move_to(stack.position)
        else:
            possible_steps = self.model.grid.get_neighborhood(self.position, moore=False, include_center=False)
            possible_steps = [step for step in possible_steps if step not in self.model.boxes_location]
        if possible_steps:
            self.move_to(self.random.choice(possible_steps))

    def pick_up_box(self):
        #pick up box from an adjacent cell if there is one
        if not self.holding_box:
            neighbors = self.model.grid.get_neighbors(self.position, moore=False, include_center=False)
            for neighbor_position in neighbors:
                box = next(self.model.grid.iter_cell_list_contents(neighbor_position)) #(box for box in self.model.boxes if box.pos == neighbor_pos), None
                if box:
                    self.model.grid.remove_agent(box)
                    self.holding_box = True
                    break

    def stack_box(self):
        #Stack a box in an adjacent incomplete stack. If there is none, it creates a new one if possible, or it moves to another stack.

        if self.holding_box:
            nearest_stack = self.find_nearest_incomplete_stack()

            if(nearest_stack and self.distance_to(nearest_stack.position) <=1 and not nearest_stack.is_full()):
                nearest_stack.add_box(self.holding_box)
                self.holding_box = True
            elif not nearest_stack:
                id = "Stack " + str(self.model.next_stack_id)
                new_stack = Stack(id, self.position, self.model)
                new_stack.add_box(self.holding_box)
                self.model.stacks.append(new_stack)
                self.model.grid.place_agent(new_stack, self.position)
                self.holding_box = None

    def step(self):
        self.move()
        self.pick_up_box()
        self.stack_box() 
        

def get_grid(model):
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        if cell_content:
            grid[x][y] = 1
    return grid
