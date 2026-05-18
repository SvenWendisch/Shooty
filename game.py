import pygame
import math
import random

def paste_path(path):
    surf = pygame.image.load(path).convert_alpha()
    rect = surf.get_bounding_rect()
    return surf.subsurface(rect).copy()

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
        vec = pygame.Vector2(self.game.mouse_pos - self.pos)
        if  vec.length() > 0:
            self.direction = vec.normalize()
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
        screen.blit(self.game.healthbar_surf, (25,170))
    

class Enemies(pygame.sprite.Sprite):
    def __init__(self, game, config, name, pos, groups):
        super().__init__(groups)
        self.game = game
        self.image = config["surf"]
        self.rect = self.image.get_frect(center = pos)
        self.name = name
        self.pos = pygame.Vector2(self.rect.center)
        self.direction = pygame.Vector2(self.game.player.pos - self.pos).normalize()

        self.speed = config["speed"]
        self.hp = config["hp"]
        self.damage = config["damage"]

    def move_enemie(self, dt):
        self.pos += self.speed * self.direction * dt
        self.rect.center = self.pos

    def update(self, dt):
        self.move_enemie(dt)

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
    def __init__(self, game, text, color, pos, groups):
        super().__init__(groups)
        self.game = game
        self.position = pygame.Vector2(pos)
        self.text_color = color
        self.text = str(text)
        self.font = self.game.damage_font
        self.image = self.font.render(self.text, True, self.text_color)
        self.rect = self.image.get_frect(center = self.position)
        self.speed = 50
        self.direction = pygame.Vector2(0,1)
        self.alpha = 255
        self.fade_speed = 400


    def points_move(self, dt):
        self.position -= self.direction * self.speed * dt
        self.rect.center = self.position

    def update(self, dt):
        self.points_move(dt)
        self.alpha -= self.fade_speed * dt
        self.image.set_alpha(self.alpha)

        if self.alpha <= 0 :
            self.kill()
        

class Game():
    def __init__(self):
        pygame.init()
        self.state = "menu"
        self.WINDOW_W, self.WINDOW_H = 1400, 750
        self.screen = pygame.display.set_mode((self.WINDOW_W, self.WINDOW_H))
        pygame.display.set_caption("SHOOTY")
        self.clock = pygame.time.Clock()
        self.running, self.playing = True, False

        self.mouse_pos = pygame.Vector2(0,0)

        # color management
        self.start_time = pygame.time.get_ticks()
        self.colors = [[87,14,0], [35,87,0], [0,83,87], [0,1,87], [87,0,78], [0,0,0], [50,50,50]]

        self.from_color = (0,0,0)
        self.to_color = (30,30,30)
        self.duration = 5.0

        # fonts
        self.header_font = pygame.font.Font("Sprites/Pixeltype.ttf",200)
        self.text_font = pygame.font.Font("Sprites/Pixeltype.ttf",50)
        self.damage_font = pygame.font.Font("Sprites/Pixeltype.ttf", 35)

        self.enemie_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemie_event, 500)

        self.score_points = 0

        # assets
        self.player_surf = paste_path("Sprites/shooty.png")
        self.laser_surf = paste_path("Sprites/shooty_laser_l.png")
    
        self.healthbar_surf = paste_path("Sprites/health_bar.png")

        self.health_more = paste_path("Sprites/health_more.png")
        self.health_regen = paste_path("Sprites/health_regen.png")
        self.piercing_shot = paste_path("Sprites/piercing_shot.png")
        self.damage_up = paste_path("Sprites/damage_up.png")
        self.rapid_fire = paste_path("Sprites/rapid_fire.png")

        self.cute_surf = paste_path("Sprites/enemie_cute.png")
        self.terminator_surf = paste_path("Sprites/enemie_terminator.png")
        self.alien_surf = paste_path("Sprites/enemie_alien.png")
        self.devil_surf = paste_path("Sprites/enemie_devil.png")
        self.marimon_surf = paste_path("Sprites/enemie_marimon.png")
        self.scream_surf = paste_path("Sprites/enemie_scream.png")
        self.poison_surf = paste_path("Sprites/enemie_poison.png")
        self.doheoni_surf = paste_path("Sprites/enemie_dohoeni.png")


        self.ITEM_DROPS = ["health_more", "health_regen", "piercing_shot", "rapid_fire", "damage_up"]
        


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
                "surf" : self.doheoni_surf, "speed" : 20, "hp" : 130, "damage" : 50, "weigth" : 1,
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

    def run(self):
        while self.running:
            self.now = pygame.time.get_ticks()
            self.dt = self.clock.tick() / 1000
            self.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

            if self.state == "menu":
                self.menu_loop()
            
            if self.state == "playing":
                self.game_loop()
            
            if self.state == "game_over":
                self.game_over_loop()
            
            pygame.display.update()

  
    def draw_text(self, text, font, text_color, x, y):
        self.img = font.render(text, True, text_color)
        self.screen.blit(self.img, (x, y))

    def menu_loop(self):
        pygame.display.set_caption("SHOOTY - Menu")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = "playing"

        self.screen.fill("black")
        self.menu_mouse_pos = pygame.mouse.get_pos()
        self.draw_text("SHOOTY", self.header_font, (255, 255, 255), 100, 100)
        self.draw_text("press 'SPACE' to play and to shoot", self.text_font, "white", 100, 300)
        

    
    def game_over_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed() [0]:
                    self.reset_game()
                    self.state = "menu"

        self.screen.fill("black")
        self.draw_text("You are dead", self.header_font, "white", 100 , 100)
        self.draw_text("left-click to start a new game", self.text_font, "white", 100 , 300)

    def reset_game(self):
        self.all_sprites.empty()
        self.laser_sprites.empty()
        self.enemie_sprites.empty()
        self.point_sprites.empty()
        self.score_points = 0

        self.player = Player(self, self.all_sprites, self.player_surf)
        self.healthbar = Healthbar(self, self.player)

        self.start_time = pygame.time.get_ticks()
        self.from_color = (0, 0, 0)
        self.to_color = (30, 30, 30)


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

            if event.type == self.enemie_event:
                x, y = random_spawn(self.WINDOW_W, self.WINDOW_H, 140)
                enemie_type = random.choice(list(self.ENEMIES.keys()))
                config = self.ENEMIES[enemie_type]
                Enemies(self, config, enemie_type, (x, y), (self.all_sprites, self.enemie_sprites))

    def drop_item(self):
        self.random_number = random.randint(0,100)
        if 0 <= self.random_number < 25 :
            self.item = random.choice(self.ITEM_DROPS)
            if self.item == "health_more":

            

    def collisions(self):
        self.hits = pygame.sprite.groupcollide(self.laser_sprites, self.enemie_sprites, True, False)

        for laser, enemies in self.hits.items():
            for enemie in enemies:
                enemie.hp -= laser.damage

                if enemie.hp <= 0:
                    enemie.kill()
                    self.score_points += 25
                    self.drop_item()
            
            Points(self, f"-{laser.damage}", "red", enemie.rect.center, self.all_sprites)
        
        self.attacking_enemie = pygame.sprite.spritecollide(self.player, self.enemie_sprites, True)

        for enemie in self.attacking_enemie:
            self.player.get_damage(enemie.damage)
            

            if self.player.current_health <= 0:
                self.state = "game_over"

            if enemie.name == "cute":
                self.player.get_health(25)
                Points(self, "+ 25", "green", self.player.rect.center, self.all_sprites)
            


    def game_loop(self):
        self.change_color()
        self.get_events()
        self.all_sprites.update(self.dt)
        self.collisions()
        self.screen.fill((self.current_color))
        self.all_sprites.draw(self.screen)
        self.healthbar.draw_healthbar(self.screen)
        self.draw_text(str(self.score_points), self.text_font, "white", 650, 50)