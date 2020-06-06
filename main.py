import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750        # Setting the game window size                               # https://www.youtube.com/watch?v=Q-__8Xw9KTM
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASERS = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASERS = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASERS = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASERS = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT)) # Importing all the image assets to the game

class Laser: # Creates a new laser class that will create and control the movement and direction of lasers from ships, and also their drawing onto the screeen
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(img) # Creating the hit box for the laser

    def draw(self, window):
        window.blit(self.img, (self.x, self.y)) # Drawing the laser to the screen

    def move(self, vel): # Controls the direction (negative is upwards) of the laser
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >=0) # Checks whether the laser did not went off-screen

    def collision(self, obj): # Checks if the laser collides with an object
        return collide(self, obj)


class Ship:
    COOLDOWN = 30 # Half a second of cooldown that is used for the laser cooldown

    def __init__(self, x, y, health=100): # Creating an abstract class of ships. Its attributes will be used to create other ships. X and Y are coordinates for the ships.
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None    # | Acts as a placeholder for the ship images and lasers to be instantiated later
        self.laser_img = None   # |
        self.lasers = []
        self.cool_down_counter = 0 # Cooldown timer for the laser shooting to prevent laser spam

    def draw(self, window):
        # pygame.draw.rect(window, (255,0 ,0), (self.x, self.y, 50, 50)) # USED FOR TESTING - Function that draws a rectangle that acts as a ship placeholder. {window->where to draw the rectangle. color->red. position->x,y of the ship. Width/Height->50X50}
        window.blit(self.ship_img, (self.x, self.y)) # Draws the ship
        for laser in self.lasers: # Draws the lasers
            laser.draw(window)

    def move_lasers(self, vel, obj): # This function makes the lasers move and check for collisions
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT): # If the laser goes off-screen it will be removed from the lasers list
                self.lasers.remove(laser)
            elif laser.collision(obj): # If the laser collided with another object deduct 10 health from that object and remove the laser from the list
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0: # If the cooldown counter is greater than 0 and it is not passed the time limit of half a second, increment the value by 1
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0: # Checks if we are not waiting for a laser to cooldown or keeping how long until the next shot
            laser = Laser(self.x, self.y, self.laser_img) # Creates a new laser object and adding it to the lasers list
            self.lasers.append(laser)
            self.cool_down_counter = 1 # Starts the cooldown timer

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship): # The player's ship class - inherits from Ship class
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health) # Initializes the class using its parent's initializing method
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASERS
        self.mask = pygame.mask.from_surface(self.ship_img) # Creates a mask that'll define the hit box of the player's ship
        self.max_health = health # Setting the player's max health

    def move_lasers(self, vel, objs): # This function makes the lasers move and check for collisions
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT): # If the laser goes off-screen it will be removed from the lasers list
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj): # Checks if the laser has hit the other objects in the objects list and removes that object
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window) # Overrides the parent init function to draw the healthbar
        self.healthbar(window)

    def healthbar(self, window): # This function creates a health bar below a ship in order to represent its health. It draws 2 rectangles, the bottom is red and the top is green. There is a calculation that is made in order to calculate the precentage of green healthbar
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health)/self.max_health, 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASERS),
                "green": (GREEN_SPACE_SHIP, GREEN_LASERS),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASERS)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color] # Initializing the enemy ship's image and laser color
        self.mask = pygame.mask.from_surface(self.ship_img) # Creating an enemy hit box around the image

    def move(self, vel): # Defining the enemy ship movement speed downwards
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0: # Checks if we are not waiting for a laser to cooldown or keeping how long until the next shot
            laser = Laser(self.x-18, self.y, self.laser_img) # Creates a new laser object and adding it to the lasers list and shoots the laser in the middle of the enemy
            self.lasers.append(laser)
            self.cool_down_counter = 1 # Starts the cooldown timer

def collide(obj1, obj2): # This function checks for collisions. The offset is calculated by the top left hand corner of an image object
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), offset_y)) != None # Returns the collision between two masks. It returns a tuple of (x, y) which is the point of intersection between the two masks

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("courier", 50) # Initializing the variables and font used in the game
    lost_font = pygame.font.SysFont("comicsans", 60) # The font that will be used in the "lost" message

    enemies = []
    wave_length = 5
    enemy_vel = 1
    laser_vel = 5

    player_vel = 5 # Setting a player velocity. In this case the player will be able to move 5 pixels at a time

    player = Player(WIDTH / 2, 630)

    clock = pygame.time.Clock() # Creating a clock element that ticks and updates the console window

    lost = False # Setting up a boolean var that is a lost flag
    lost_count = 0 # Creates a timer that will be used to count until the game resets

    def redraw_window():
        WIN.blit(BG, (0, 0))
        #Draw Lives
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255)) # Setting the labels to be white

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) # Printing on the screen the lives to the
        # top left side and the level to the top right side using a method that decreases the width of the entire window
        # from the size of the level label and adding a 10 pixel padding.

        for enemy in enemies: # Draws the enemies to the screen
            enemy.draw(WIN)

        player.draw(WIN) # Drawing the player's ship to the screen

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255, 255, 255)) # Creates a label for the message that is white
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) # Draws the message dead-center of the window

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0: # Checks if there are no lives or health to the player and will trigger a "lost" message later on
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3: # Checking if 3 seconds has passed from the drawing of the lost message
                run = False # Quit the big while loop and the game
            else:
                continue

        if len(enemies) == 0: # Once the enemy list is empty advance 1 level
            level += 1
            wave_length += 5 # Adds 5 more enemies to the next wave
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, 100), random.choice(["red", "green", "blue"])) # Draws enemies above the screen within the range of the screen. This means 50 pixels from the x position
                enemies.append(enemy) # Adding the random enemy that was created to the enemies list

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        keys = pygame.key.get_pressed() # Returns a dictionary of the keyboard keys and whether they are pressed at the current time
        if keys[pygame.K_a] and player.x - player_vel > 0: # left + Window movement restriction so the player can't go off-screen
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player. get_height() + 15 < HEIGHT: # down and the + 15 is for the health bar clipping off screen
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]: # This for loop is responsible for making the enemies move down and if they go off-screen, to remove them from the enemies list while deducting a live
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player) # Moves the enemy lasers each frame by the laser_vel speed and checks if their laser hit the player

            if random.randrange(0, 2*60) == 1: # Takes some probability with the enemy and when it is shooting.
                enemy.shoot()

            if collide(enemy, player): # If the enenmy ship and the player ship collided deduct 10 health from the player
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT: # If the enemy went to the bottom of the screen the player loses a life
                lives -= 1
                enemies.remove(enemy)


        player.move_lasers(-laser_vel, enemies) # The negative sign is to shoot the player's laser upwards


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0)) # Draw the background
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255)) # Main menu message
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350)) # Renders the message in the middle of the screen
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN: # If in the menu the mouse is clicked the main loop is running and the game is playing, otherwise quit the game
                main()
    pygame.quit()

main_menu()
