import pygame
import math
import random

def paste_path(path):
    return pygame.image.load(path).convert_alpha()

def lerp_color(c1, c2, t):
        return([int(pygame.math.lerp(a, b, t)) for a, b in zip(c1, c2)])

def random_spawn(w, h, margin,):
    sides = random.choice(("up", "left", "right", "down"))

    if sides == "up":
        return (random.randint(0,w),- margin)
    if sides == "left":
        return (-margin, random.randint(0,h))
    if sides == "right":
        return (w + margin, random.randint(0,h))
    if sides == "down":
        return (random.randint(0,w), h + margin)
    

class Player(pygame.sprite.Sprite):
    def __init__(self, game, groups, surf):
        super().__init__(groups)
        self.game = game
        mid_w, mid_h = self.game.WINDOW_W/2, self.game.WINDOW_H/2
        self.image = surf
        self.rect = self.image.get_frect(center = (mid_w, mid_h))
        self.pos = pygame.Vector2((mid_w, mid_h))
        self.master = self.image

        self.max_health = 300
        self.current_health = 300

    def get_damage(self, amount):
        if self.current_health > 0 :
            self.current_health -= amount
        if self.current_health <= 0 : 
            self.current_health = 0
    
    def get_health(self, amount):
        if self.current_health > 0 :
            self.current_health += amount
        if self.current_health >= self.max_health :
            self.current_health = self.max_health
    
    def rotate_turret(self,dt):
        self.direction = pygame.Vector2(self.game.mouse_pos - self.pos).normalize()
        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
        self.image = pygame.transform.rotozoom(self.master, self.angle, 1)
        self.rect = self.image.get_frect(center = self.pos)
    
    def update(self, dt):
        self.rotate_turret(dt)

class Healthbar():
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.health_bar_length = 400
        self.health_ratio = self.health_bar_length / self.player.max_health

    def draw_healthbar(self, screen):
        pygame.draw.rect(screen, "green", (30, self.game.WINDOW_H / 2 - 200 + (self.player.max_health * self.health_ratio) - (self.player.current_health * self.health_ratio),30,self.player.current_health * self.health_ratio))
        pygame.draw.rect(screen, "white", (30, self.game.WINDOW_H / 2 - 200, 30, self.health_bar_length), width=1)
    

# class Enemies(pygame.sprite.Sprite):
#     def __init__(self, config, pos, groups):
#         super().__init__(groups)
#         self.image = config["surf"]
#         self.rect = self.image.get_ferct(center = pos)
#         self.pos = pygame.Vector2(self.rect.center)
#         self.direction = pygame.Vector2(self.player.pos - self.pos).normalize()

#         self.speed = config["speed"]
#         self.hp = config["hp"]

#     def move_enemie(self, dt):
#         self.pos += self.speed * self.direction
#         self.rect.center = self.pos

#     def update(self, dt):
#         self.move_enemie(dt)

class Laser(pygame.sprite.Sprite):
    def __init__(self, game, surf, pos, player_pos, groups):
        super().__init__(groups)
        self.game = game
        self.position = pygame.Vector2(pos)
        self.image = surf
        self.rect = self.image.get_frect(center = self.position)  
        self.speed = 300
        self.direction = pygame.Vector2(self.game.mouse_pos - player_pos).normalize()
        self.angle = math.degrees(math.atan2(-self.direction.y, self.direction.x)) - 90
        self.image = pygame.transform.rotozoom(self.image, self.angle, 1)
        self.rect = self.image.get_frect(center=self.position)
        self.damage = 35
        


    def update(self, dt):
        self.position += self.direction * self.speed * dt
        self.rect.center = self.position


        if self.position.x < 0 or self.position.x > self.game.WINDOW_W or self.position.y < 0 or self.position.y > self.game.WINDOW_H:
            self.kill()



class Points(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.position = pygame.Vector2(pos)
        self.image = surf
        self.rect = self.image.get_frect(center = self.position)
        self.speed = 30
        self.direction = pygame.Vector2(0,1)

    def points_move(self, dt):
        self.position -= self.direction * self.speed * dt
        self.rect.center = self.position
    
   # def points_fade(self):


    def update(self, dt):
        self.points_move(dt)

class Game():
    def __init__(self):
        pygame.init()
        self.WINDOW_W, self.WINDOW_H = 1400, 750
        self.screen = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H))
        pygame.display.set_caption("SHOOTY")
        self.clock = pygame.time.Clock()
        self.running, self.playing = True, False

        self.mouse_pos = pygame.Vector2(0,0)

        self.start_time = pygame.time.get_ticks()
        self.colors = [[87,14,0], [35,87,0], [0,83,87], [0,1,87], [87,0,78], [0,0,0], [50,50,50]]

        self.from_color = (0,0,0)
        self.to_color = (30,30,30)
        self.duration = 5.0

        # assets
        self.player_surf = paste_path("C:/Users/User/Projekte/Sprites/shooty.png")
        self.laser_surf = paste_path("C:/Users/User/Projekte/Sprites/shooty_laser_l.png")
        self.points_surf = paste_path("C:/Users/User/Projekte/Sprites/shooty_laser_l.png")

        self.cute_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_cute.png")
        self.terminator_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_terminator.png")
        self.alien_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_alien.png")
        self.devil_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_devil.png")
        self.marimon_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_marimon.png")
        self.scream_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_scream.png")
        self.poison_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_poison.png")
        self.doheoni_surf = paste_path("C:/Users/User/Projekte/Sprites/enemie_dohoeni.png")


        # config

        self.ENEMIES = {
    "cute": {
        "surf" : self.cute_surf, "speed" : 200, "hp" : 25, "damage" : 0, "weigth" : 1,
    },
    "alien": {
        "surf" : self.alien_surf, "speed" : 70, "hp" : 80, "damage" : 25, "weigth" : 1,
    },
    "scream": {
        "surf" : self.scream_surf, "speed" : 100, "hp" : 150, "damage" : 25, "weigth" : 1,
    },
    "poison": {
        "surf" : self.poison_surf, "speed" : 100, "hp" : 100, "damage" : 25, "weigth" : 1,
    },
    "devil": {
        "surf" : self.devil_surf, "speed" : 100, "hp" : 100, "damage" : 25, "weigth" : 1,
    },
    "terminator": {
        "surf" : self.terminator_surf, "speed" : 130, "hp" : 100, "damage" : 50, "weigth" : 1,
    },
    "dohoeni": {
        "surf" : self.doheoni_surf, "speed" : 20, "hp" : 4000, "damage" : 50, "weigth" : 1,
    },
    "marimon": {
        "surf" : self.marimon_surf, "speed" : 100, "hp" : 100, "damage" : 100, "weigth" : 1,
    },
}

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()
        self.enemie_sprites = pygame.sprite.Group()
        self.point_sprites = pygame.sprite.Group()

        self.player = Player(self, self.all_sprites, self.player_surf)
        
        self.healthbar = Healthbar(self, self.player)

    def change_color(self):
        self.elapsed = (self.now - self.start_time)/1000
        self.t = pygame.math.clamp(self.elapsed/self.duration, 0, 1)
        self.current_color = lerp_color(self.from_color, self.to_color, self.t)

        if self.t >= 1:
            self.from_color = self.to_color
            self.to_color = random.choice(self.colors)
            self.start_time = self.now


    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.offset = 40
                self.start_pos = self.player.pos + self.player.direction * self.offset
                Laser(self, self.laser_surf, self.start_pos, self.player.pos, (self.all_sprites, self.laser_sprites))
            

    def game_loop(self):
        while self.playing:
            self.now = pygame.time.get_ticks()
            self.dt = self.clock.tick() / 1000
            self.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            self.change_color()
            self.get_events()
            self.all_sprites.update(self.dt)
            self.screen.fill((self.current_color))
            self.healthbar.draw_healthbar(self.screen)
            self.all_sprites.draw(self.screen)
            self.screen.blit(self.ENEMIES["cute"]["surf"], (100, 100))
            
            pygame.display.update()