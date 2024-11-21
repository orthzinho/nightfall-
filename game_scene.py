import pygame
from sys import exit
import math, random

from configs import *
import configs

pygame.init()

# Gerando a janela principal
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NightFall V" + UPDATE + ": " + UPDNAME)
clock = pygame.time.Clock()

Debuggin = False

background = pygame.image.load("backgrounds/backgroundA.png").convert()
backgroundb = pygame.image.load("backgrounds/BG_tile.png").convert()
background_upscale = pygame.transform.scale(backgroundb, (64,64))

camera = pygame.math.Vector2( 0,0 )


bossbarImage = pygame.transform.scale(pygame.image.load("UI\BossBarFrame.png"), (1272,56))

HPheart = pygame.transform.scale(pygame.image.load("UI\HP_heart.png"), (64,64))

# DEFINIÇÕES MATEMÁTICAS ========================================================================================================

def lerp(start, end, t):
    return start + t * (end - start)

def axialise(binaryValue):
    return (binaryValue+1)*2-3

def toggle(variable):
    return not variable

# DEFINIÇÕES PERSONAGENS ========================================================================================================

class Player1(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Visual_Stuffs
        self.animation = "idle"
        self.framespeed = 6
        self.curframe = 1
        self.frametimer = 0
        self.animframes = 4
        self.mirror = False
        self.isloop = 1

        # Load player image
        self.imageraw = pygame.image.load(str(f"playerCharacter/{self.animation}/{self.curframe}.png")).convert_alpha()
        self.image = self.imageraw

        # Movement_things
        self.pos = pygame.math.Vector2(X_PSTART, Y_PSTART)
        self.drawpos = pygame.math.Vector2(self.pos.x - self.image.get_width()/2 - camera.x, self.pos.y - self.image.get_height()/2 - camera.y)
    
        #Additional values to the movement
        self.appliedvector = pygame.math.Vector2( 0 , 0 )

        # PlayerVars
        self.maxspeed = 7 
        self.health = 5

        #Dashes
        self.dashPowah = 5
        self.dashPermCooldown = 90
        self.dashCooldown = 0

        # PlayerHitbox
        self.hitbox_size = pygame.math.Vector2(32,8)
        self.rect = self.image.get_rect(topleft=(self.pos.x - self.image.get_width()/2, self.pos.y - self.image.get_height()/2))

        # AttackVars
        self.state = 0
        #   0: Normal Movement
        #   1: Attacking, movement locked

        self.attackcenter = self.pos
        self.attackrad = 50
        self.attackPermCooldown = 60
        self.attackCooldown = 0

    def inputs(self):
        self.movevector = pygame.math.Vector2( 0 , 0 )

        keys = pygame.key.get_pressed()

        # MOVEMENT_KEYS =======================================

        if self.state == 0:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.movevector.y = -self.maxspeed

            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.movevector.y = self.maxspeed

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.movevector.x = -self.maxspeed
                self.mirror = False

            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.movevector.x = self.maxspeed
                self.mirror = True

            if keys[pygame.K_SPACE] or keys[pygame.K_k]:
                if self.attackCooldown == 0:
                    self.attackCooldown = self.attackPermCooldown
                    self.state = 1
                    self.attack()
            
            if keys[pygame.K_LCTRL] or keys[pygame.K_l]:
                if self.appliedvector[0] == 0 and self.appliedvector[1] == 0 and self.dashCooldown == 0:
                    self.dashCooldown = self.dashPermCooldown
                    self.dash()

        # OTHER KEY INPUTSsfsfsf =======================================
        
        if self.state == 1 and self.frametimer > self.framespeed + 5:
            self.state = 0
            self.switch_anim("idle", 4, 6, 1)
            self.curframe = 0


        # VECTOR HANDLING ================================================

        if self.dashCooldown > 0:
            self.dashCooldown -= 1

        if self.attackCooldown > 0:
            self.attackCooldown -= 1

        self.appliedvector[0] = lerp(self.appliedvector[0], 0, 0.1)
        self.appliedvector[1] = lerp(self.appliedvector[1], 0, 0.1)

        if abs(self.appliedvector[0]) < 10 and abs(self.appliedvector[1]) < 10:
            self.appliedvector[0] = 0
            self.appliedvector[1] = 0

        if self.movevector.x != 0 and self.movevector.y != 0: # moving diagonally
            self.movevector.x /= math.sqrt(2)
            self.movevector.y /= math.sqrt(2)
        
        if self.animation == "idle" and (self.movevector.x != 0 or self.movevector.y != 0) and self.state == 0:
            self.switch_anim("move", 8, 5, 1)
            self.curframe = 0

        if self.animation == "move" and (self.movevector.x == 0 and self.movevector.y == 0) and self.state == 0:
            self.switch_anim("idle", 4, 6, 1)
            self.curframe = 0
        
    def animate(self):
        self.frametimer = self.frametimer + 1

        if self.frametimer > self.framespeed and self.curframe < self.animframes:
            self.curframe = self.curframe + 1
            self.frametimer = 0

        if self.curframe == self.animframes and self.isloop == 1 and self.frametimer == self.framespeed:
            self.curframe = 0

    def upd_visual(self):
        self.imageraw = pygame.image.load(str(f"playerCharacter/{self.animation}/{self.curframe}.png")).convert_alpha()
        self.image = pygame.transform.flip(pygame.transform.scale(self.imageraw, (self.imageraw.get_width() * 4, self.imageraw.get_height() * 4)), not self.mirror, False)
        self.drawpos = pygame.math.Vector2(self.pos.x - self.image.get_width()/2 - camera.x, self.pos.y - self.image.get_height()/1.2 - camera.y )

    def switch_anim(self, name, animframes, framespeed, looping):
        self.animation = name
        self.animframes = animframes
        self.framespeed = framespeed
        self.isloop = looping

    def move(self):

        if self.state == 0:
            self.pos += self.movevector + self.appliedvector
        elif self.state == 1:
            self.pos += self.appliedvector

        # PlayerHitbox
        self.rect = pygame.Rect(self.pos.x - self.hitbox_size.x/2 , self.pos.y - self.hitbox_size.y/2, self.hitbox_size.x, self.hitbox_size.y)

        if self.mirror == True:
            self.attackcenter.x = self.pos.x + 48
        else:
            self.attackcenter.x = self.pos.x - 48

        self.attackcenter.y = self.pos.y - 24
    
    def attack(self):
        self.switch_anim("attack", 9, 1, 0)
        self.curframe = 0
    
    def dash(self):
        self.appliedvector[0] += self.movevector[0] * self.dashPowah
        self.appliedvector[1] += self.movevector[1] * self.dashPowah
    
    def scrollto(self):
        camera.x = lerp(camera.x, (self.pos.x + boss1.pos.x)/2 - WIDTH/2   , 0.05) 
        camera.y = lerp(camera.y, (self.pos.y + boss1.pos.y)/2 - HEIGHT/2  , 0.05)

    def takedamage(self, damage, knockstrength, knockangle):
        self.appliedvector[0] = math.cos(knockangle) * knockstrength
        self.appliedvector[1] = math.sin(knockangle) * knockstrength
        self.health -= damage
        
    def update(self):
        self.animate()     
        self.inputs()    
        self.move()
        self.scrollto()
        self.upd_visual()

class Boss_1(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Visual_Stuffs
        self.animation = "idle"
        self.framespeed = 12
        self.curframe = 0
        self.frametimer = 0
        self.animframes = 5
        self.isloop = True
        self.mirror = False
        targx = 0

        # Load boss image
        self.imageraw = pygame.image.load(f"boss_1/{self.animation}/{self.curframe}.png").convert_alpha()
        self.image = pygame.transform.scale(self.imageraw, (self.imageraw.get_width() * 4, self.imageraw.get_height() * 4))

        # Movement_things
        self.pos = pygame.math.Vector2(WIDTH, HEIGHT)
        self.drawpos = pygame.math.Vector2(self.pos.x - self.image.get_width()/2 - camera.x, self.pos.y - self.image.get_height() - camera.y)
        self.drawoffset = pygame.Vector2(0, 64)
        self.movevector = pygame.math.Vector2(0, 0)
        self.maxspeed = 5
        self.targ = pygame.math.Vector2(0,0)
        self.moveangle = 0
        self.orbitdist = 300
        self.movetype = "approach"
        self.orbitangle = 0

        # Hitbox Defining
        self.hitbox_size = pygame.math.Vector2(128,128)

        # HEalth Points
        self.HP = 100
        self.HP_max = 100
        self.iFrames = 30
        self.lastcombo = 0

        #Melee damage
        self.attackrad = 55
        self.attackcenteroffset = pygame.Vector2(0,0)

        #Spittin
        self.shoot_timer = 30
        self.shoot_interval = 10  # Time between shots in frames

        self.localtimer = 0
        self.switch_anim("idle", 5, 12, True)

    def animate(self):
        self.frametimer = self.frametimer + 1

        if self.isloop:
            if self.frametimer > self.framespeed:
                self.curframe = self.curframe + 1
                self.frametimer = 0

            if self.curframe > self.animframes:
                self.curframe = 0
        else:
            if self.frametimer > self.framespeed and self.curframe < self.animframes:
                self.curframe = self.curframe + 1
                self.frametimer = 0

            if self.curframe > self.animframes:
                self.curframe = 0
        
    
        self.imageraw = pygame.image.load(str(f"boss_1/{self.animation}/{self.curframe}.png")).convert_alpha()
        self.image = pygame.transform.scale(self.imageraw, (self.imageraw.get_width() * 4, self.imageraw.get_height() * 4))
    
    def switch_anim(self, name, animframes, framespeed, looping):
        self.animation = name
        self.animframes = animframes
        self.framespeed = framespeed
        self.isloop = looping

    def lookat(self):
        if self.pos.x < self.targx:
            self.mirror = False
        else:
            self.mirror = True
            
    def move(self):
        self.pos += self.movevector
        self.drawpos = pygame.math.Vector2(self.pos.x - self.image.get_width()/2 - camera.x, self.pos.y + 24 - self.image.get_height() - camera.y) + self.drawoffset
        self.rect = pygame.Rect(self.pos.x - self.hitbox_size.x/2 , self.pos.y - self.hitbox_size.y/2, self.hitbox_size.x, self.hitbox_size.y)

        if self.movetype == "lock shoot":
            self.maxspeed = (math.sqrt((self.pos.x - self.targ.x)**2 + (self.pos.y - self.targ.y)**2) - self.orbitdist) /14
            #definir velocidade de acordo com a distância de A a B
            

            self.moveangle = math.atan2(self.targ.y - self.pos.y, self.targ.x - self.pos.x)
            self.movevector = pygame.math.Vector2(math.cos(self.moveangle) * self.maxspeed, math.sin(self.moveangle) * self.maxspeed)
            self.targx = player1.pos.x
            
            self.lookat()
            self.shoot()

            self.localtimer += 1
            if self.localtimer > 180:
                self.localtimer = 0
                self.movetype = "approach"
                self.switch_anim("idle", 5, 12, True)
            
        if self.movetype == "spin shoot":
            self.maxspeed = (math.sqrt((self.pos.x - self.targ.x)**2 + (self.pos.y - self.targ.y)**2)) /14
            #definir velocidade de acordo com a distância de A a B

            self.moveangle = math.atan2(self.targ.y - self.pos.y, self.targ.x - self.pos.x)
            self.movevector = pygame.math.Vector2(math.cos(self.moveangle) * self.maxspeed, math.sin(self.moveangle) * self.maxspeed)
            self.targ = player1.pos + pygame.Vector2(math.cos(self.orbitangle),math.sin(self.orbitangle)) * self.orbitdist * 1.25
            self.orbitangle += 0.033
            
            if self.movevector.x > 0:
                self.mirror = False
            else:
                self.mirror = True
            self.shoot()

            self.localtimer += 1
            if self.localtimer > 240:
                self.localtimer = 0
                self.movetype = "approach"
                self.switch_anim("idle", 5, 12, True)

        if self.movetype == "approach":
            self.targ = player1.pos
            self.maxspeed = (math.sqrt((self.pos.x - self.targ.x)**2 + (self.pos.y - self.targ.y)**2) - self.orbitdist) /14 - 5
            #definir velocidade de acordo com a distância de A a B

            self.moveangle = math.atan2(self.targ.y - self.pos.y, self.targ.x - self.pos.x)
            self.movevector = pygame.math.Vector2(math.cos(self.moveangle) * self.maxspeed, math.sin(self.moveangle) * self.maxspeed)
            self.targx = player1.pos.x

            if self.orbitdist > 10:
                self.orbitdist -= 5

            if self.maxspeed > 1 and self.animation != "run":
                self.switch_anim("run", 5, 3, True)
            if self.maxspeed < 1 and self.animation != "idle":
                self.switch_anim("idle", 5, 12, True)
                
            
            self.lookat()
        
        if self.movetype == "bite":




            self.lookat()

    def changetype(self, newtype):
        self.movetype = newtype

        if newtype == "approach":
            self.orbitdist = 500
        
    def upd_visual(self):
        self.image = pygame.transform.flip(pygame.transform.scale(self.imageraw, (self.imageraw.get_width() * 4, self.imageraw.get_height() * 4)), not self.mirror, False)
    
    def checkfor_damage(self, damagex, damagey, damagerad):
        circle = (damagex, damagey, damagerad)
        rectangle = (self.pos.x - self.hitbox_size.x/2, self.pos.y - self.hitbox_size.y/2, self.hitbox_size.x, self.hitbox_size.y)
        if is_circle_rect_overlap(circle, rectangle):
            self.takeDamage(3)
            self.iFrames = 30
            

    def update_HP(self):
        if self.iFrames > 0:
            self.iFrames -= 1
    
    def takeDamage(self, damagetaken):
        if self.iFrames == 0:
            self.HP -= damagetaken
            self.lastcombo += 1
            if self.movetype == "approach":
                self.orbitdist = 400
                if self.lastcombo > 2:
                    self.lastcombo = 0
                    self.targ = self.pos + self.movevector*10
                    self.shoot_timer = 45
                    if self.HP < self.HP_max/2:
                        self.movetype = "spin shoot"
                        self.switch_anim("runBurst", 5, 3, True)
                    else:
                        self.movetype = "lock shoot"
                        self.switch_anim("burst", 11, 4, False)
        

    def shoot(self):
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            # Calculate projectile position and angle
            projectile_x = self.pos.x
            projectile_y = self.pos.y-96
            angle = math.atan2(player1.pos.y - projectile_y, player1.pos.x - projectile_x)
            
            # Create and add a new projectile to the projectiles group
            projectile = Proj_Spit(projectile_x, projectile_y)
            projectile.moveangle = angle + random.randrange(-20,20)/10
            projectiles.add(projectile)
            
            # Reset shoot timer
            self.shoot_timer = self.shoot_interval

    def update(self):
        self.animate()
        self.move()
        self.upd_visual()
        self.update_HP()
        
        # Handle shooting


    def pathfindTo(self, pX, pY):
        dstA = 1

class Proj_Spit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Visual stuffs
        self.image = pygame.transform.scale(pygame.image.load("spit/0.png"), (40, 24))
        
        # Movement_things
        self.pos = pygame.math.Vector2(x, y)
        self.drawpos = pygame.math.Vector2(self.pos.x - self.image.get_width()/2 - camera.x, self.pos.y - self.image.get_height() - camera.y)
        self.movevector = pygame.math.Vector2(1, 0)
        self.maxspeed = 9
        self.targ = pygame.math.Vector2(player1.pos.x, player1.pos.y)
        self.moveangle = 45

        # Hitbox Defining
        self.hitbox_size = pygame.math.Vector2(40, 24)  # Update to match the size of your image
        self.rect = pygame.Rect(self.pos.x - self.hitbox_size.x/2, self.pos.y - self.hitbox_size.y/2, self.hitbox_size.x, self.hitbox_size.y)

        #life
        self.lifetime = 0

    def move(self):
        self.movevector.x = math.cos(self.moveangle) * self.maxspeed
        self.movevector.y = math.sin(self.moveangle) * self.maxspeed
        
        self.pos += self.movevector
        self.drawpos = pygame.math.Vector2(self.pos.x - self.image.get_width()/2 - camera.x, self.pos.y - self.image.get_height() - camera.y)
        self.rect = pygame.Rect(self.pos.x - self.hitbox_size.x/2, self.pos.y - self.hitbox_size.y/2, self.hitbox_size.x, self.hitbox_size.y)

    def upd_visual(self):
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load("spit/0.png"), (40, 24)), -(self.moveangle*180/math.pi))

    def checkfor_dmg(self):
        if math.sqrt((self.pos.x-player1.attackcenter.x)**2 + (self.pos.y-player1.attackcenter.y)**2) < player1.attackrad and player1.state == 1:
            self.kill()


    def update(self):
        self.move()
        self.upd_visual()
        self.lifetime += 1
        self.checkfor_dmg()

        if self.lifetime < 90:
            self.check_target_side()
        
        if self.lifetime > 60*5:
            self.kill()


    def check_target_side(self,):
        self.targ = pygame.math.Vector2(player1.pos.x, player1.pos.y)
        direction_vector = pygame.math.Vector2(math.cos(self.moveangle), math.sin(self.moveangle))
        target_vector = pygame.math.Vector2(self.targ.x - self.pos.x, self.targ.y - self.pos.y)
        
        cross_product = direction_vector.x * target_vector.y - direction_vector.y * target_vector.x
        
        self.moveangle += cross_product/5500
        
        #print(self.moveangle)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        
        #Visual stuffs
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))  # You can change this to an image if you have one
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass

class Ground_Deco(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()

        #Visual stuffs
        self.image = pygame.transform.scale(pygame.image.load(f"grndDeco/deco_{type}.png"), (64,64))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.drawpos = pygame.math.Vector2( x,y+8 )

    def update_visual(self):
        # Adjust the draw position based on the camera position
        self.drawpos.x = self.rect.x - camera.x
        self.drawpos.y = self.rect.y - camera.y

    def update(self):
        self.update_visual()


# DEFINIÇÕES DE GAMEPLAY ========================================================================================================

# Check Ccollision, exists to serve Hanle_collision
def check_collision(sprite, sprite2):
    return pygame.sprite.spritecollide(sprite, sprite2, False, pygame.sprite.collide_rect)

def handle_collision(sprite, obstacles):
    collisions = check_collision(sprite, obstacles)
    
    if not collisions:
        return  # Exit the function if no collisions

    for sprite2 in collisions:
        # Calculate the collision vector

        #Difference from the center of both colliding parties ( x and y )

        dx = sprite.rect.centerx - sprite2.rect.centerx
        dy = sprite.rect.centery - sprite2.rect.centery

        #Calculate the overlap between bot collidin parties. Positive values equal no collisions, while negative mean collision.

        overlap_x = sprite.rect.width / 2 + sprite2.rect.width / 2 - abs(dx)
        overlap_y = sprite.rect.height / 2 + sprite2.rect.height / 2 - abs(dy)
        
        #SE a sobreposição em X for maior que a sobreposição em Y, quer dizer que o personagem
        #está colidindo para x. usando mais um SE, pode-se inferir se é para direita ou esquerda.

        if overlap_x < overlap_y:
            if dx < 0:
                sprite.rect.right = sprite2.rect.left
            else:
                sprite.rect.left = sprite2.rect.right
        #caso o inverso sesja verdade, logo, ele colide para y.
        else:
            if dy < 0:
                sprite.rect.bottom = sprite2.rect.top
            else:
                sprite.rect.top = sprite2.rect.bottom

        # Adjust player position
        sprite.pos = pygame.math.Vector2(sprite.rect.centerx, sprite.rect.centery)

def is_circle_rect_overlap(circle, rect):
    # Circle properties
    C_x, C_y, r = circle  # Circle center (x, y) and radius

    # Rectangle properties
    rect_x, rect_y, rect_width, rect_height = rect  # Rect properties
    rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

    # Find the closest point on the rectangle to the circle's center
    closest_x = max(rect.left, min(C_x, rect.right))
    closest_y = max(rect.top, min(C_y, rect.bottom))

    # Calculate the distance from the closest point to the circle's center
    distance_x = C_x - closest_x
    distance_y = C_y - closest_y

    # Calculate the square of the distance (to avoid square root)
    distance_squared = distance_x**2 + distance_y**2

    # Check if the distance is less than or equal to the radius squared
    return distance_squared <= r**2


# DORGANIZE OS SPRITESS ========================================================================================================

def sort_sprites_by_y(sprites):
    return sorted(sprites, key=lambda sprite: sprite.rect.centery, reverse=False)

# GERANDO DECORAÇÃO ============================================================================================================

def generate_decorations(num_decorations, width, height):
    decorations = pygame.sprite.Group()
    for _ in range(num_decorations):
        # Randomly choose a type (you can adjust this if you have more decoration types)
        deco_type = random.randint(1, 9)  # Adjust the range based on the number of types you have

        # Randomly choose a position within the screen boundaries
        x = random.randint(0, width - 64)  - width/2  # 64 is the width of the decoration image
        y = random.randint(0, height - 64) - height/2 # 64 is the height of the decoration image

        # Create and add the decoration to the group
        deco = Ground_Deco(x, y, deco_type)
        decorations.add(deco)

    return decorations

# INSTANCIANDO AQUILO QUE PODE SER INSTANCIADO! =================================================================================

player1 = Player1()
 
boss1 = Boss_1()

camera = camera

obstacles = pygame.sprite.Group()
decorations = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

# Create obstacles
obstacle1 = Obstacle(100, 100, 50, 50)
obstacle2 = Obstacle(300, 200, 122, 70)

# Create Decorations
decorations = generate_decorations(500, WIDTH*5, HEIGHT*5)


# Add obstacles to the group
obstacles.add(obstacle1, obstacle2)
enemies.add(boss1)
projectiles.add()



font = pygame.font.Font(None, 36)

# O QUE É UM SPRITE? EIS A QUESTÃO. ============================================================================================
print("")
print("")
print("CONTROLES:")
print("Para controlar seu personagem, use as teclas W,A,S,D. Para dar uma investida na direção do movimento, use a tecla CTRL, para atacar, use o botão SPACEBAR.")
print("")
print("")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    

    if player1.health <= 0:
        player1.pos = pygame.math.Vector2(X_PSTART, Y_PSTART)  # Reset position to start
        player1.health = 5  # Reset health
        player1.dashCooldown = 0  # Reset dash cooldown
        player1.attackCooldown = 0  # Reset attack cooldown
        player1.state = 0  # Set the player state back to normal movement
        player1.animation = "idle"  # Reset animation state
        player1.curframe = 0  # Reset animation frame
        player1.frametimer = 0  # Reset animation timer
        player1.movevector = pygame.math.Vector2(0, 0)  # Reset movement vector
        player1.appliedvector = pygame.math.Vector2(0, 0)  # Reset applied vector for momentum
        player1.mirror = False  # Reset mirrored state
        boss1.pos = pygame.math.Vector2(WIDTH, HEIGHT)  # Reset position
        boss1.HP = boss1.HP_max  # Reset health
        boss1.iFrames = 0  # Reset invincibility frames
        boss1.movetype = "approach"  # Reset movement type to default
        boss1.orbitdist = 300  # Reset orbit distance
        boss1.localtimer = 0  # Reset internal timers
        boss1.lastcombo = 0  # Reset combo counter
        boss1.targ = player1.pos  # Set boss target back to player
        boss1.shoot_timer = 0  # Reset shooting timer
        boss1.animation = "idle"  # Reset animation state
        boss1.curframe = 0  # Reset animation frame
        boss1.frametimer = 0  # Reset animation timer
        projectiles.empty()  # Clear all projectiles from the group

        #Reset other game variables (like score, timer, etc.)
        score = 0  # Reset score
        timer = 0  # Reset timer
        camera.x = 0  # Reset camera position
        camera.y = 0



    keys = pygame.key.get_pressed()
    if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                Debuggin = True
    if event.type == pygame.KEYUP:
            if event.key == pygame.K_TAB:
                Debuggin = False

    screen.blit(background, (-camera.x, -camera.y))
    

    # Get the dimensions of the background 
    tile_width, tile_height = background_upscale.get_size()


    # Calculate the number of tiles needed to cover the screen width and height
    num_tiles_x = math.ceil(WIDTH / tile_width) + 2
    num_tiles_y = math.ceil(HEIGHT / tile_height) + 2


    # Draw the tiled background
    for x in range(num_tiles_x):
        for y in range(num_tiles_y):
            # Calculate the position for each tile
            tile_x = -camera.x + (x * tile_width) +  round(camera.x/tile_width)*tile_width   - tile_width
            tile_y = -camera.y + (y * tile_height) + round(camera.y/tile_height)*tile_height - tile_height
            screen.blit(background_upscale, (tile_x, tile_y))


    player1.update()
    boss1.update()
    decorations.update()
    projectiles.update()


    #detectar se o boss tomo dano
    if player1.state == 1:
        boss1.checkfor_damage(player1.attackcenter.x, player1.attackcenter.y, player1.attackrad)


    # Handle collisions
    handle_collision(player1, obstacles)
    handle_collision(boss1, obstacles)

    collided_projectiles = check_collision(player1, projectiles)

    # Remove collided projectiles
    for projectile in collided_projectiles:
        projectile.kill()
        player1.takedamage(1,20,projectile.moveangle)



    # Draw everything
    # Collect all sprites to draw
    all_sprites = [player1] + list(obstacles) + list(enemies) + list(decorations) 


    # Sort sprites by their Y position (in descending order)
    sorted_sprites = sort_sprites_by_y(all_sprites)


    # Draw everything
    for sprite in sorted_sprites:
        if isinstance(sprite, Obstacle):
            screen.blit(sprite.image, (sprite.rect.x - camera.x, sprite.rect.y - camera.y))
        else:
            screen.blit(sprite.image, sprite.drawpos)


    

    for projectile in projectiles:
        screen.blit(projectile.image, projectile.drawpos)

    if Debuggin == True:
        pygame.draw.rect(screen, (255, 0, 0), (player1.rect.x - camera.x, player1.rect.y - camera.y, player1.rect.width, player1.rect.height), 2)
        pygame.draw.rect(screen, (255, 0, 0), (boss1.rect.x - camera.x, boss1.rect.y - camera.y, boss1.rect.width, boss1.rect.height), 2)
        pygame.draw.rect(screen, (255, 0, 0), (player1.pos.x - camera.x - 4, player1.pos.y -4  - camera.y, 8, 8))
        pygame.draw.rect(screen, (255, 0, 0), (boss1.pos.x - camera.x - 4, boss1.pos.y -4  - camera.y, 8, 8))
        print("FPS: ", clock.get_fps(), (boss1.pos), player1.state, boss1.HP)
        if player1.state == 1:
            pygame.draw.circle(screen, (0, 255, 0), (player1.attackcenter.x - camera.x, player1.attackcenter.y - camera.y), player1.attackrad, 2)
        
    pygame.draw.rect(screen, (255, 0, 255), ((player1.pos.x - player1.dashCooldown/2) - camera.x, (player1.pos.y + 8)  - camera.y, player1.dashCooldown, 8))
    pygame.draw.rect(screen, (0, 255, 255), ((player1.pos.x - player1.attackCooldown/2) - camera.x, (player1.pos.y + 20)  - camera.y, player1.attackCooldown, 8))


    pygame.draw.rect(screen, (186, 50, 33), (32, 32, boss1.HP * (WIDTH-64)/boss1.HP_max , 28))
    screen.blit(bossbarImage, (4,16))

    if player1.health > 0:
        screen.blit(HPheart, (WIDTH-64-32, HEIGHT-64-32))
    
    if player1.health > 1:
        screen.blit(HPheart, (WIDTH-128-32, HEIGHT-64-32))
    
    if player1.health > 2:
        screen.blit(HPheart, (WIDTH-192-32, HEIGHT-64-32))
    
    if player1.health > 3:
        screen.blit(HPheart, (WIDTH-256-32, HEIGHT-64-32))
    
    if player1.health > 4:
        screen.blit(HPheart, (WIDTH-320-32, HEIGHT-64-32))
    
    if boss1.HP <= 0:
        boss1.kill()
    
    

    pygame.display.update()
    clock.tick(60)  # Limit to 60 frames per second