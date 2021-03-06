# program template for Spaceship
import simpleguitk as simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
shoot = False
rock_group = set([])
missile_group = set([])
rock_group_size = 0 
disgard_missile = False
points = 0

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2013.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 35)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrusters = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrusters == True:
            canvas.draw_image(self.image, (self.image_center[0]+90,self.image_center[1]), self.image_size, self.pos, self.image_size, self.angle)
        else:    
            canvas.draw_image(self.image, (self.image_center), self.image_size, self.pos, self.image_size, self.angle)
    
    def increase_ang_vel(self):
        self.angle_vel += .2
    def decrease_ang_vel(self):
        self.angle_vel -= .2
    def keyup_ang_vel(self):
        self.angle_vel = 0
    
    def thrust(self):
        self.thrusters = True
        ship_thrust_sound.play()

    def no_thrust(self):    
        self.thrusters = False
        ship_thrust_sound.rewind()
        
    def update(self):
        self.pos[0] = (self.pos[0] + self.vel[0]) % 800
        self.pos[1] = (self.pos[1] + self.vel[1]) % 600
        
        self.angle += self.angle_vel
        
        self.vel[0] *= (1 -.05)
        self.vel[1] *= (1 -.05) 
        
        if self.thrusters == True:
            forward = angle_to_vector(self.angle)
            self.vel[0] += forward[0]  * .7
            self.vel[1] += forward[1]  * .7	 
        
    def shoot(self):
        global missile_group, a_missile
        forward = angle_to_vector(self.angle)
        vel = [self.radius * forward[0]* .3 + self.vel[0]    * .5,
            self.radius * forward[1] * .3 + self.vel[1] * .5]
        
        a_missile = Sprite([self.pos[0] + self.radius * forward[0],
                            self.pos[1] + self.radius * forward[1]], 
                           vel, self.angle, self.angle_vel, missile_image, missile_info, missile_sound)
   
        missile_group.add(a_missile)

        
    def get_pos(self):
        return self.pos
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, (self.image_center), self.image_size, self.pos, self.image_size, self.angle)
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % 800
        self.pos[1] = (self.pos[1] + self.vel[1]) % 600
        self.age += 1
        
        if self.age < self.lifespan:
            return False
        else:
            return True
        
    def collision(self, other_object):
       '''Checks if objects are colliding, if yes returns true if no returns false'''
       if self.radius + other_object.radius > distance(self.get_pos(), other_object.get_pos()):
            return True
       else:
            return False
            
    def get_pos(self):
        return self.pos
           
def draw(canvas):
    global time, lives, rock_group, missile_group, score
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)

    

    # update ship and sprites
    my_ship.update()

    
    #draws rocks on canvas
    process_sprite_group(rock_group,canvas)
    process_sprite_group(missile_group,canvas)
    
    
    # draws score and lives
    canvas.draw_text("Score: " +str(score), (WIDTH - 130,43), 30, "Green")
    canvas.draw_text("Lives: " +str(lives), (30,43), 30, "Green")

    # Removes rocks from canvas if ship & rock collide and removes a live if there is a collision	
    game_lives = group_collide(rock_group, my_ship) 
    if game_lives == True:
        lives -= 1

    game_score = group_group_collide(missile_group, rock_group)    
    score = game_score * 10        
# timer handler that spawns a rock    
def rock_spawner():
    '''creates the rock sprite at a random position, velocity and ang_vel. 
    Also adds the rock sprite to rock_group set and limits the set to 12 values'''
    global rock_group
    asteroid_pos = [0,0]
    asteroid_pos[0] = random.randrange(0,801)
    asteroid_pos[1] = random.randrange(0,601)
    asteroid_vel = [0,0]
    asteroid_vel[0] = random.randrange(-2,3)
    asteroid_vel[1] = random.randrange(-2,3)
    
    flag = random.choice( [True,False])
    if flag == True:
        angle_vel = - random.random()/10.0
    else:
        angle_vel = random.random()/10.0   
    
    rock = Sprite([asteroid_pos[0], asteroid_pos[1]], [asteroid_vel[0],asteroid_vel[1]], 0, angle_vel, asteroid_image, asteroid_info)
    
    if len(rock_group) < 12:
        rock_group.add(rock)
   
    

    
def process_sprite_group(set,canvas):
    '''Helper function that calls the draws & updates 
    methods for all sprites in a set'''
    for sprite in set:
        sprite.update()
        sprite.draw(canvas)
   
    for sprite in list(set):
        if sprite.update() == True:
            set.remove(sprite)
        
        
        
def distance(object1, object2):
    '''Helper function that finds the distance between two objects'''
    dist = math.sqrt((object1[0] - object2[0]) ** 2 + (object1[1] - object2[1]) ** 2) 
    return dist

def group_collide(group, other_object):
    '''Removes the the rock that just collided with a rocket or ship and minuses a life after collision'''
    value = False
    for object in set(group):
        if object.collision(other_object) == True:
            group.remove(object)
            value = True        
    return value   


def group_group_collide(group1, group2):
    global points
    for objects in set(group1):
        var = group_collide(group2, objects)
        if var == True:
            group1.discard(objects)
            points += 1
    return points        
                

      
        
            



#Keyboard Handler
def key_handler1(key):
    global shoot
    if key == simplegui.KEY_MAP['right']:
        my_ship.increase_ang_vel()
    elif key == simplegui.KEY_MAP['left']:
        my_ship.decrease_ang_vel()

    if key == simplegui.KEY_MAP['up']:
        my_ship.thrust()
    
    if key == simplegui.KEY_MAP['space']:
        my_ship.shoot()


def key_handler2(key):
    global shoot
    if key == simplegui.KEY_MAP['right']:
         my_ship.keyup_ang_vel() 
    elif key == simplegui.KEY_MAP['left']:
        my_ship.keyup_ang_vel()
        
    if key == simplegui.KEY_MAP['up']:
        my_ship.no_thrust() 
        



# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
#a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [0,0], 0, 0, missile_image, missile_info, missile_sound)


# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_handler1)
frame.set_keyup_handler(key_handler2)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
