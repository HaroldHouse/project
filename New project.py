import pygame, random
from queue import PriorityQueue
pygame.init()

#Setting the screen size and game name
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

#Defining colours with Red, Green, Blue
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#Setting a font and the size of this font for text on the screen
font = pygame.font.SysFont("arialblack", 20)
heading_font = pygame.font.SysFont("arialblack", 60)

#Load in the images for the buttons of the pause menu and death / victory menu
resume_img = pygame.image.load("Resume.png").convert_alpha()
quit_img = pygame.image.load("Quit.png").convert_alpha()
main_menu_img = pygame.image.load("Main_menu.png").convert_alpha()
main_menu_img = pygame.transform.scale(main_menu_img, (main_menu_img.get_width() // 3, main_menu_img.get_height() // 3))

#Load in the images for the buttons to alter the players stats
level_up_options_img = pygame.image.load("Level_up_options.png").convert_alpha()
level_up_options_img = pygame.transform.scale(level_up_options_img, (level_up_options_img.get_width() // 3, level_up_options_img.get_height() // 3))
alter_player_speed_img = pygame.image.load("Player_movement_speed.png").convert_alpha()
alter_player_size_img = pygame.image.load("Player_size.png").convert_alpha()
alter_bullet_size_img = pygame.image.load("Bullet_size.png").convert_alpha()
alter_bullet_speed_img = pygame.image.load("bullet_speed.png").convert_alpha()
alter_bullet_fire_rate_img = pygame.image.load("Bullet_fire_rate.png").convert_alpha()
increase_player_max_health = pygame.image.load("Max_health.png").convert_alpha()
increase_player_health = pygame.image.load("Health.png").convert_alpha()

#Set the max frames per second and define the clock for controlling the main game loop
FPS = 60
clock = pygame.time.Clock()

#Stats alteration list
alteration = ["player_size", "player_speed", "bullet_fire_rate", "bullet_size", "bullet_speed", "max_health", "health"]

#Bullet parameters
bullet_width = 10
bullet_height = 10
bullet_speed = 1

#List to store the current bullets on screen
fired_bullets = []

#List to store the obstacles on screen
obstacles = []

#List to store the enemies alive
enemies = []

class Player():
    def __init__(self, player_x: float, player_y: float, char_width: int, char_height: int, movement_speed: int, fire_rate: int, health : int, max_health: int):
        self._position = [player_x, player_y]
        self._width = char_width
        self._height = char_height
        self._speed = movement_speed
        self._fire_rate = fire_rate
        self._health = health
        self._max_health = max_health

    def draw_player(self):
        #Drawing the player and defining the position and size
        player_outline = pygame.Rect(self._position[0], self._position[1], self._width, self._height)
        pygame.draw.rect(screen,  BLUE, player_outline)

    #Method to move the player around the screen
    def player_movement(self):
        collisions = [] #List to store the results of get_collision
        for obstacle in obstacles:
            if self.get_rect().colliderect(obstacle): #If the player rectangle is colliding with the obstacle rectangle
                collisions.append(self.get_collision(obstacle)) #Append the result of the get collision method to the collisions list
        
        # Player movement controls
        user_input = pygame.key.get_pressed() #Pygame function to check if a key is being pressed
        #Move up if the user is pressing the w key and not at the top of the screen and not colliding with an obstacles above it
        if user_input[pygame.K_w] and self._position[1] > 0 and not collisions.count('up') > 0:
            self._position[1] -= self._speed #Update the y to change in the negative depending on the current speed

        #Repeats this for moving in the left, down and right direction
        if user_input[pygame.K_a] and self._position[0] > 0 and not collisions.count('left') > 0: #Move left
            self._position[0] -= self._speed
        if user_input[pygame.K_s] and self._position[1] + self._height < 800 and not collisions.count('down') > 0: #Move down
            self._position[1] += self._speed
        if user_input[pygame.K_d] and self._position[0] + self._width < 1200 and not collisions.count('right') > 0: #Move right
            self._position[0] += self._speed

        #Updating the drawn _position of the player
        self.draw_player()

    #Method to fire bullets from the player
    def fire_bullet(self):
        global last_shot
        if event.key == pygame.K_UP and last_shot >= FPS / self._fire_rate: #User must press the UP arrow key and had to have been a certain time since the last shot
            #Creates a bullet with the parameters to fire up
            bullet = Bullet(pygame.math.Vector2(self._position[0] + (self._width - bullet_width) // 2, self._position[1]), bullet_speed * pygame.math.Vector2(0, -3), bullet_width, bullet_height)
            fired_bullets.append(bullet) # Appends this bullet instance to an array
            last_shot = 0 #Resets the last shot

        #Repeats this for shooting in the left, down and right directions
        elif event.key == pygame.K_LEFT and last_shot >= FPS / self._fire_rate:
            bullet = Bullet(pygame.math.Vector2(self._position[0], self._position[1] + (self._height - bullet_height) // 2), bullet_speed * pygame.math.Vector2(-3, 0), bullet_width, bullet_height)
            fired_bullets.append(bullet)
            last_shot = 0

        elif event.key == pygame.K_DOWN and last_shot >= FPS / self._fire_rate:
            bullet = Bullet(pygame.math.Vector2(self._position[0] + (self._width - bullet_width) // 2, self._position[1] + self._height), bullet_speed * pygame.math.Vector2(0, 3), bullet_width, bullet_height)
            fired_bullets.append(bullet)
            last_shot = 0

        elif event.key == pygame.K_RIGHT and last_shot >= FPS / self._fire_rate:
            bullet = Bullet(pygame.math.Vector2(self._position[0] + self._width, self._position[1] + (self._height - bullet_height)// 2), bullet_speed * pygame.math.Vector2(3, 0), bullet_width, bullet_height)
            fired_bullets.append(bullet)
            last_shot = 0

    #method to test for collision of the player with an obstacle
    def get_collision(self, rect: pygame.Rect):
        collision_tolerance = 5 #Maximum pixels the player can move into the obstacle if its updated position had already entered it
        for node in obstacles:
            if abs(rect.top - self.get_rect().bottom) < collision_tolerance: #Calculates if the top of the obstacle is colliding with the bottom of the player
                return "down" #Returns that the down condition is true to append to the collisions list in player_movement and the player should no longer be able to move down in that direction
            
            #Repeats this for a collision on the top, left and right of the player
            if abs(rect.bottom - self.get_rect().top) < collision_tolerance: 
                return "up"
            if abs(rect.right - self.get_rect().left) < collision_tolerance: 
                return "left"
            if abs(rect.left - self.get_rect().right) < collision_tolerance: 
                return "right"

    def get_pos(self):
        return pygame.math.Vector2(self._position[0], self._position[1]) #Return the current player position as a vector
    
    def get_width(self):
        return self._width #Return the current player width
    
    def get_height(self):
        return self._height #Return the current player height
    
    def get_speed(self):
        return self._speed #Return the current player speed
    
    def get_health(self):
        return self._health #Return the current player health
    
    def get_max_health(self):
        return self._max_health #Return the current player max health
    
    def get_rect(self):
        return pygame.Rect(self._position[0], self._position[1], self._width, self._height) #Returns the current rectangle of the player to be used for collision detection
    
    def get_fire_rate(self):
        return self._fire_rate #Return the current fire rate of the player
    
    #Setters to change the values of the attributes
    def set_player_size(self, char_width: int, char_height: int):
        self._width = char_width #Set the player width to the passed in char_width value
        self._height = char_height #Set the player height to the passed in char_height value

    def set_player_speed(self, movement_speed: int):
        self._speed = movement_speed #Set the player speed to the passed in movement_speed value
    
    def set_fire_rate(self, fire_rate: int):
        self._fire_rate = fire_rate #Set the player fire rate to the passed in fire_rate value

    def increase_health(self):
        if self._health < self._max_health: #Making sure increasing the player health will not make it greater than the max health
            self._health += 1 #Increase the player health by 1

    def decrease_health(self):
        global game_over
        if self._health == 1: #If the player health is one and the method is called the player health will be zero and the game will be over
            game_over = True #Set game_over to True
        else:
            self._health -= 1 #Decreases the player health by one
    
    def increase_max_health(self):
        self._max_health += 1 #Increase the max health of the player by one

class Bullet():
    def __init__(self, position: pygame.math.Vector2 , vel: pygame.math.Vector2 , height: int, width: int):
        self._vel = vel
        self._position = position
        self._bul_width = width
        self._bul_height = height

    def draw(self):
        #Drawing the bullet and defining the position and size
        bullet_rect = pygame.Rect(self._position.x, self._position.y, self._bul_width, self._bul_height)
        pygame.draw.rect(screen, BLACK, bullet_rect)

    def get_rect(self):
        return pygame.Rect(self._position.x, self._position.y, self._bul_width, self._bul_height) #Return the rectangle of the bullet for collision detection

    def get_position(self):
        return self._position #Return the current position vector of the bullet

    def iterate_position(self):
        self._position += self._vel #Vector addition to update the bullet position 

class Enemy():
    def __init__(self, pos: pygame.math.Vector2, width: int):
        self._pos = pos
        self._width = width
        self._route = None
        self._target = pygame.Vector2(999, 999) #The last position this enemy pathfound to

    def draw_enemy(self):
        #Create and draw the enemy rectangle
        enemy = pygame.Rect(self._pos.x, self._pos.y, self._width, self._width)
        pygame.draw.rect(screen, RED, enemy)

    def get_enemy(self):
        enemy = pygame.Rect(self._pos.x, self._pos.y, self._width, self._width) #Return the rectangle of the enemy
        return enemy

    def get_pos(self):
        return self._pos #Return the position of the enemy
    
    # A* algorithm to find the route to the target
    def find_route(self, start_pos: pygame.math.Vector2, end_pos: pygame.math.Vector2, grid):
        self._target = end_pos
        #The array to pathfind through
        grid_array = grid.get_array()
        #The set of nodes and their priority
        node_set = PriorityQueue()
        start_node = grid.get_closest_node(start_pos) #Gets the closest node of the enemy
        end_node = grid.get_closest_node(end_pos) #Gets the closest node of the player
        #Using put to put in the values 0 and start_node as a tuple telling the priority queue that start node has the highest priority and so should be removed first
        node_set.put((0, start_node)) 
        #A dictionary of nodes and where they came from
        came_from = {}
        #Creating a g_score dictionary using pythons nested list comprehension to iterate through grid
        g_score = {node: float('inf') for row in grid_array for node in row}
        g_score[start_node] = 0 #The g_score in A* is the distance from the start node so initially is 0
        #Creating the same dictionairy for the f_score
        f_score = {node: float('inf') for row in grid_array for node in row}
        #The f_score in A* pathfinding is the g_score + the h_cost where the h_cost is the distance from the end position so at start g_score = 0 so f_cost = h_cost
        f_score[start_node] = self.h_cost(start_pos, end_pos) 
        
        while not node_set.empty():
            current = node_set.get()[1] #Getting the highest priority element from the priority queue
            if current == end_node: #If the algorithm has found a path to the end position
                path = [] #Array to store the path the path the enemy must take

                #Iterating through the came_from dictionary to find the route it took and what nodes it went to to get their and appending these results to the path array.
                while current in came_from:
                    #current.draw()
                    path.append(current)
                    current = came_from[current] 
                return path[::-1] #Return reversed path so the enemy knows the route they must travel to reach the end position
            
            #Iterating through all the neighbours of the node and calculating their f and g costs
            for neighbour in current.get_neighbours():
                temp_g_score = g_score[current] + 1 #g_score of the neighbour as each node has a weight of one

                if temp_g_score < g_score[neighbour]: 
                    came_from[neighbour] = current
                    g_score[neighbour] = temp_g_score
                    f_score[neighbour] = temp_g_score + self.h_cost(neighbour.get_pos(), end_pos)
                
                    if neighbour not in node_set.queue:
                        node_set.put((f_score[neighbour], neighbour)) #Lower f_score gives that neighbour higher priority
    
        return [] # If no path found
    
    # Algorithm to pathfind to a target position
    def pathfind(self, start_pos: pygame.math.Vector2, end_pos: pygame.math.Vector2, grid):
        target_displacement = self._target - end_pos #Displacement from searched position to new position
        if self._route == None: #First time running through
            self._route = self.find_route(start_pos, end_pos, grid) #Sets the self._route to the output of calling find_route
            self.pathfind(start_pos, end_pos, grid) #Recalls the method with the new self._route value
            return #Breaks out the method
        if len(self._route) == 0: #if no route currently - either no route found to get there or reached the destination
            if target_displacement.magnitude() > 20: #If the player has moved more than 20 pixels since last calling the pathfind
                self._route = self.find_route(start_pos, end_pos, grid) 
                self.pathfind(start_pos, end_pos, grid)
                return #Breaks out the method
            else:
                return #Breaks out the method
            
        #Optimisation to make it so it no longer reruns the A* star algorithm every frame
        route_displacement = (self._route[0].get_pos() - self._route[len(self._route) - 1].get_pos()) #Distance between end and start node
        if target_displacement.magnitude() > route_displacement.magnitude() / 10: #When a target moves too great a distance - moved more than 10% of route length
            if (target_displacement + route_displacement).magnitude() > route_displacement.magnitude(): #Has the distance grown
                new_route = self.find_route(self._route[len(self._route) - 1].get_pos(), end_pos, grid)  #Append new route from the end of the existing one - Following the player
                for node in new_route:
                    self._route.append(node)
            else: #Has the distance shrunk
                suggested_length_ratio = (target_displacement + route_displacement).magnitude() / route_displacement.magnitude() #Get the ratio of the lengths before and after
                new_start_index = int( (len(self._route) * suggested_length_ratio) / 3 ) #Get where we should start the new search
                del self._route[ new_start_index:len(self._route) ] #Cull the current route
                if len(self._route) > 0: #Append our new route to the head
                    new_route = self.find_route(self._route[len(self._route) - 1].get_pos(), end_pos, grid) #Rerun the a* from this new position
                    for node in new_route:
                        self._route.append(node)
                else: #If it is destroyed, remake it 
                    self._route = self.find_route(start_pos, end_pos, grid)

        #Checking if close enought to a node to remove from the route
        closest_node = self._route[0]
        difference = closest_node.get_pos() - self._pos
        if difference.magnitude() < grid.get_node_gap() / 5:
            self._route.remove(closest_node)
            return
        else:
            self._pos += difference.normalize() * 2
        
    #Heuristic of the A* algorithm
    def h_cost(self, pos1: pygame.math.Vector2, pos2: pygame.math.Vector2):
        #Returns the absolute(positive) value of subtracting the passed in pos1's x value with pos2's and addng this to the pos1's y value - pos2's
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y) 

class Grid():
    def __init__(self, side_length: int, node_gap: int):
        self._side_length = side_length #Total length of the grid
        self._node_gap = node_gap #How many pixels should be left before a new node is created
        self._total_rows = side_length // node_gap #Total nodes on each row
        self._grid = [] 
        #Create grid this is called in the init method as needs to be made as the grid is initialised
        #As it is a nested loop for each row every column will be made and appended to the grid so the grid will be in the form grid[row][column]
        for row in range(self._total_rows):
            self._grid.append([])
            for column in range(self._total_rows):
                node = Node(row, column, node_gap)
                if random.randint(0,100) == 5: #Random number generator to randomly decide when a node should become an obstacle
                    node.make_obstacle() #Makes the node an obstacle
                    obstacles.append(node.get_rect()) #Stores this node in the obstacles array
                self._grid[row].append(node) #Append the current node to the array
        #Populate neighbours of nodes
        self.__populate_neighbours()
    
    #Method to draw the obstacles on screen
    def draw_obstacles(self):
        for i in range(self._total_rows):
            for j in range(self._total_rows):
                if self._grid[i][j].is_obstacle(): #If the node in the row at that column is an obstacle
                    self._grid[i][j].draw()

    #Method to check for the existance of a node
    def __node_exists(self, row: int, column: int):
        #Exception handling to check if the node exists at that position if it does it will return True and False if it is out of range
        try:
            self._grid[row][column]
            return True
        except IndexError:
            return False

    def get_node_gap(self):
        return self._node_gap #Returns the node gap

    #Method to return the closest node to the current position of the player
    def get_closest_node(self, pos: pygame.math.Vector2):
        column = int((pos.y) // self._node_gap)
        row = int((pos.x) // self._node_gap)
        return self._grid[row][column]

    #Method to populate the grid with all valid nodes for the A* pathfinding algorithm
    def __populate_neighbours(self):
        for row in range(self._total_rows):
            for col in range(self._total_rows):
                node = self._grid[row][col]
                #Check if the node in the column below it exists and is not an obstacle
                if self.__node_exists(row, col - 1) and not node.is_obstacle():
                    node.append_neighbour(self._grid[row][col-1])

                #Repeats this for all surrounding nodes (not diagonal nodes)
                if self.__node_exists(row, col + 1) and not node.is_obstacle(): 
                    node.append_neighbour(self._grid[row][col+1])

                if self.__node_exists(row - 1, col) and not node.is_obstacle():
                    node.append_neighbour(self._grid[row-1][col])

                if self.__node_exists(row + 1, col) and not node.is_obstacle():
                    node.append_neighbour(self._grid[row+1][col])

    def get_array(self):
        return self._grid #Return the grid array


class Node():
    def __init__(self, row: int, col: int, node_gap: int):
        self._row = row
        self._col = col
        self._node_gap = node_gap
        self._x = row * node_gap #Finds the x position of the node by multiplying the node on that row by the length of each node
        self._y = col * node_gap #Finds the y position the same way
        self._colour = (0, 0, 0) #Setting the basic colour of a node to black
        self._neighbours = [] #Creating an empty neighbours array to store neighbour nodes to a node
        #Setting the f cost as unbound upper values for comparison with the pathfinding using 'inf'
        self._f_cost = float('inf') 
        self._parent = None
    
    def append_neighbour(self, node):
        self._neighbours.append(node) #Append the passed in node to the neighbours array

    def get_pos(self):
        return pygame.math.Vector2(self._x, self._y) #Return the position of the node as a vector

    def is_obstacle(self):
        return self._colour == GREEN #Checks if the node is green which is an obstacle
    
    def make_obstacle(self):
        self._colour = GREEN #Makes the node into GREEN causing it to be recognised as an obstacle

    def draw(self):
        #Drawing the obstacles, as each node is square width will be the same as the height
        pygame.draw.rect(screen, self._colour, (self._x, self._y, self._node_gap, self._node_gap))

    def get_rect(self):
        return pygame.Rect(self._x, self._y, self._node_gap, self._node_gap) #Return the rectangle of the node

    def get_neighbours(self):
        return self._neighbours #Returns the neighbours of a node

    #Comparison operator between two nodes for the priority queue
    def __lt__(self, other): #Dunder method stands for less than
        return self._f_cost < other._f_cost #Using the python dunder method to check if the f cost of one node is less than the other

class Button():
    def __init__(self, x: int, y: int, image, scale: int):
        #Getting the width and height of the image using pygames built in methods for images
        width = image.get_width() 
        height = image.get_height()
        self._image = pygame.transform.scale(image, (int(width * scale), int(height * scale))) #Transform the images to a new size
        self._rect = self._image.get_rect() #Get the rectangle argument for the image
        self._rect.topleft = (x, y) #Define the top left of the image as x,y as pygame draws from the top left position
        self._clicked = False #Has the mouse previously been clicked

    def draw(self):
        #Draw the image at the passed in position
        screen.blit(self._image, (self._rect.x, self._rect.y))

    #Method to check whether a button has been clicked
    def button_pressed(self):
        action = False
        pos = pygame.mouse.get_pos() #Getting the (x,y) position of the mouse on the screen

        if self._rect.collidepoint(pos): #If the mouse position is at any point within the buttons rectangle
            if pygame.mouse.get_pressed()[0] == 1 and self._clicked == False: #If the left click of the mouse has been pressed and the user is not currently holding down left click
                self._clicked = True
                action = True 

        #Once the player releases the left mouse button set self._clicked to False to allow the player to be able to repress the button
        if pygame.mouse.get_pressed()[0] == 0:
            self._clicked = False

        return action #Returns the outpute True or False depending on whether the user has pressed the button
    
    def set_position(self, x, y):
        self._rect.topleft = (x, y) #Allows the image to be set to a new x and y position on the screen with the passed in x and y parameters

#Function to alter the bullet size
def set_bullet_size():
    global bullet_width, bullet_height
    bullet_width = random.randint(1, 20)
    bullet_height = random.randint(1,20)

#Function to alter the bullet speed 
def set_bullet_speed():
    global bullet_speed
    bullet_speed = random.randint(1, 5)

#Bool value for the main game loop
run = True

#Create initial player instance
player = Player(50, 100, 55, 45, 2, 3, 10, 10) #x, y, width, height, speed, fire rate, health, max health

#Create button instances
resume_button = Button(350, 200, resume_img, 0.5) #x, y, image, scale
quit_button = Button(350, 400, quit_img, 0.5)

#Create the grid instance
grid = Grid(1500, 15)

# Ticks since last shot
last_shot = 0

#Ticks since last spawn of an enemy
last_spawn = 0

#Timer to activate the level up screen 
level_timer = 0

#Timer for time between enemy spawns
spawn_timer = 0

#Level counter
level = 1

#Bool value for if the level up menu is active
level_up = False
#Bool value for is a random number has been generated for the stat alteration
random_number = False
#Bool value to check if the game over screen is active
game_over = False
#Bool value to check if the game is paused
game_paused = False
#Bool value to check if an enemy has been spawned
first_spawn = False
#Bool value to check if the vicotry screen is active
victory = False

#Main game loop
while run:
    #Setting the clock to tick at a capped frame rate of the constant FPS
    clock.tick(FPS)
    #Refilling the screen white every frame as a background
    screen.fill(WHITE)
    
    if game_over == True: #Checking if the game is over and the player has lost all their health
        #Render the game over message at the top of the screen and draw the quit button
        game_over_text = heading_font.render("Game over", True, BLACK)
        screen.blit(game_over_text, (400, 10))
        quit_button.draw()
        if quit_button.button_pressed(): #Has button_pressed returned true for the quit button
            run = False #Break out the while loop and quit the game
    
    elif victory == True: #Cheking if the game has been won (the player has beat level 10)
        #Render the victory message at the top of the screen and draw the quit button
        victory_text = heading_font.render("Well done!" , True, BLACK)
        victory_message = font.render("You have completed the game", True, BLACK)
        screen.blit(victory_text, (400, 10))
        screen.blit(victory_message, (405, 100))
        quit_button.draw()
        if quit_button.button_pressed(): #Has the button_pressed returned true for the quit button
            run = False #Break out the while loop and quit the game

    elif level_up == True: #Checking to see if the level up timer has been reached
        screen.blit(level_up_options_img, (450, 50)) #Drawing the level up menu image at the top of the screen
        #Nested dictionairy containing each stat to change
        #Each stat stored as a dictionairy itself containing the corrosponding button and a lambda function to alter the players stats
        actions = {
            "player_size": {
                "button": alter_player_size_button,
                "action": lambda: player.set_player_size(random.randint(10, 100), random.randint(10, 100)) #Alter the players size with passed in random integers value between 10, 100 for the width and same for the height
            },
            "player_speed": {
                "button": alter_player_speed_button,
                "action": lambda: player.set_player_speed(random.randint(2, 4)) #Alter the player speed with a random integer between 2 and 4
            },
            "bullet_fire_rate": {
                "button": alter_bullet_fire_rate_button,
                "action": lambda: player.set_fire_rate(random.randint(2, 10)) #Alter the fire rate with a random integer between 2 and 10
            },
            "bullet_size": {
                "button": alter_bullet_size_button,
                "action": lambda: set_bullet_size() #Call the set_bullet_size function to randomly alter the bullet size
            },
            "bullet_speed": {
                "button": alter_bullet_speed_button,
                "action": lambda: set_bullet_speed() #Call the set_bullet_speed function to randomly alter the bullet speed
            },
            "max_health": {
                "button": increase_max_health_button,
                "action": lambda: player.increase_max_health() #Call the increase max health method to increase the players max health
            },
            "health": {
                "button": increase_health_button,
                "action": lambda: player.increase_health() #Call the increase health method to increase the players health if it is lower than the max health
            }
        }

        if random_number == False:
            #Generating two random numbers
            x = random.randint(0, 6)
            y = random.randint(0, 6)

            #Making y regenerate so that the same button doesn't show up twice on the level up menu
            while x == y:
                y = random.randint(0,6)

            #Setting the stat alteration equal to the string values stored with the alteration array
            first_stat = alteration[x]
            second_stat = alteration[y]

            #Making random_number True so no other numbers are generated while level_up is active
            random_number = True

        if first_stat in actions:
            #Finding the corrosponding button to first stat and that stats button
            button = actions[first_stat]["button"]
            button.draw() 
            if button.button_pressed(): #If the button pressed method returns true after being clicked
                actions[first_stat]["action"]() #Carry out the action corrosponding to the dictionairy
                level_timer = 0 #Reseting the level up timer
                level_up = False #Reseting the level up activation
                random_number = False #Reseting the random number generation

        #Repeating the same information as the first stat but moving the image further down the screen
        if second_stat in actions:
            button = actions[second_stat]["button"]
            button.set_position(350, 500)
            button.draw()
            if button.button_pressed():
                actions[second_stat]["action"]()
                level_timer = 0
                level_up = False
                random_number = False

    elif game_paused == True: #If the game paused value is true
        #Draw the main menu button at the top of the screen and then draw the resume and quit button
        screen.blit(main_menu_img, (450, 50))
        resume_button.draw()
        #If the user clicks the resume button break out the game paused menu
        if resume_button.button_pressed():
            game_paused = False
        
        quit_button.draw()
        #If the user clicks the quit button break out the game loop and quit the game
        if quit_button.button_pressed():
            run = False

    else: #If their is no menu active
        #Render the health and level text to draw on screen
        health_text = font.render("Health: " + str(player.get_health()) + "/" + str(player.get_max_health()), True, BLACK)
        level_text = font.render("Level: " + str(level), True, BLACK)

        #Create the instances of the alteration buttons (needed here to reset the position of the buttons if they were the second stat)
        alter_player_size_button = Button(350, 200, alter_player_size_img, 0.5)
        alter_player_speed_button = Button(350, 200, alter_player_speed_img, 0.5)
        alter_bullet_fire_rate_button = Button(350 ,250, alter_bullet_fire_rate_img, 0.5)
        alter_bullet_size_button = Button(350, 200, alter_bullet_size_img, 0.5)
        alter_bullet_speed_button = Button(350, 200, alter_bullet_speed_img, 0.5)
        increase_max_health_button = Button(350, 200, increase_player_max_health, 0.5)
        increase_health_button = Button(350, 200, increase_player_health, 0.5)

        player.player_movement() #Calling the player method player movement to allow the player to move on screen and update the position of the player

        #Increment the spawn_timer by the time since the last frame in ms
        spawn_timer += clock.get_time()
        if spawn_timer * (level / 2) > 3000: #As the levels increase this will be true more often allowing more frequent enemy spawns
            #Create the initial instance of the enemies at the bottom of the grid off the screen with a width and length of 15 pixels
            enemy = Enemy(pygame.math.Vector2(random.randint(0, 1300), random.randint(800, 1000)), 15)
            enemies.append(enemy) #Append this enemy instance to the enemies array
            first_spawn = True #Set that an enemy has been spawned
            spawn_timer = 0 #Reset the spawn timer
            
        
        if first_spawn == True: #If an enemy has spawned
            for enemy in enemies: 
                enemy.draw_enemy() #Calling the draw_enemy method to draw the enemy
                #Carrying out the pathfinding algorithm with the passed in values for the current enemy position, player position and the grid instance
                enemy.pathfind(enemy.get_pos(), player.get_pos(), grid) 
                if enemy.get_enemy().colliderect(player.get_rect()): #If the enemy is colliding with the player
                    enemies.remove(enemy) #Remove the enemy from the enemies array causing it to die
                    player.decrease_health() #Call the decrease health method to decrease the health by one and check if the game is over
        
        for bullet in fired_bullets:
            bullet_rect = bullet.get_rect() #Get the current rectangle of the bullet
            bullet_position = bullet.get_position() #Get the current position of the bullet
            #Check if the bullet is off the screen and remove it if it is
            if bullet_position.x < 0 or bullet_position.x > SCREEN_WIDTH or bullet_position.y < 0 or bullet_position.y > SCREEN_HEIGHT:
                fired_bullets.remove(bullet)
                
            #Update the bullet position
            bullet.iterate_position()
            for obstacle in obstacles:
                #Check for a collision between the obstacle rectangle and the bullet
                if obstacle.colliderect(bullet_rect):
                    #Check to see if the bulelt has already been removed from the array (to make sure if it collides with two obstacles it doesn't try to remove itself twice)
                    if fired_bullets.count(bullet) != 0:
                        fired_bullets.remove(bullet) #Remove the bullet from the fired_bullets array and removing that instance of the bullet
            for enemy in enemies:
                #Check for a collision between the enemy rectangle and bullet rectangle
                if enemy.get_enemy().colliderect(bullet_rect):
                    #Check to see if bullet has already been removed from the array (for the same reason)
                    if fired_bullets.count(bullet) != 0:
                        fired_bullets.remove(bullet) #Remove the bullet from the fired_bullets array and remove that instance of the bullet
                        enemies.remove(enemy) #Remove the enemy from the enemies array and that instance of the enemy
            bullet.draw() #Draw the updated bullet position 
            

        #Increment the level_timer by the time since the clock ticked last
        level_timer += clock.get_time()
        if level_timer / 30000 > 1: #If the level timer is greater than 30 seconds
            level += 1 #Increment the level counter by 1
            if level == 11: #If level 10 has been survived
                victory = True #Set victory to True the player completed the game
            else: #If the player is below level 11
                level_up = True #Activate the level up menu screen
        
        #Increment the frames since last shot by 1
        last_shot += 1

        #Drawing the obstacles on screen
        grid.draw_obstacles()

        #Drawing the health and level text on the screen as the top layer
        screen.blit(health_text, (1050, 0))
        screen.blit(level_text, (10, 0))

    pygame.display.update() #Update the display for any changes every frame
    #Using pygames event system
    for event in pygame.event.get():
        #Check to see whether the game has been closed
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
        #Check to see if a key has been pressed down    
        if event.type == pygame.KEYDOWN:
            player.fire_bullet() #Calling fire bullet to check if the key pressed was any of the arrow keys
            if event.key == pygame.K_ESCAPE and level_up == False and game_over == False and victory == False: #Check if the key pressed is escape and that the game is not on another menu
                game_paused = True #If the escape key has pressed set the game_paused value equal to true


pygame.quit() #Exit out the game
