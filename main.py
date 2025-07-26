# main.py - Full 800+ line web-ready version
import pygame
import random
import json
import math
import asyncio
from pygame import gfxdraw
try:
    import js
    js.window.loadingManager.complete()
except:
    pass

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.75
JUMP_FORCE = -18
PLAYER_SPEED = 5
SCROLL_THRESH = 400
MAX_PLATFORMS = 15
MIN_PLATFORM_DIST = 100
MAX_PLATFORM_DIST = 200
PLATFORM_WIDTH_RANGE = (80, 180)
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

# Colors
SKY_COLOR = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)

# Trail types
TRAIL_TYPES = {
    "none": {"price": 0, "color": None, "effect": None},
    "sparkle": {"price": 150, "color": (255, 255, 200), "effect": "sparkle"},
    "fire": {"price": 200, "color": (255, 100, 0), "effect": "fire"},
    "shadow": {"price": 100, "color": (50, 50, 50, 150), "effect": "fade"},
    "rainbow": {"price": 250, "color": None, "effect": "rainbow"}
}

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Don't Look Down")
clock = pygame.time.Clock()

def create_platform_texture(width, platform_type):
    texture = pygame.Surface((width, 20), pygame.SRCALPHA)
    
    if platform_type == "wood":
        plank_width = 20
        for i in range(0, width, plank_width):
            shade = random.randint(150, 200)
            pygame.draw.rect(texture, (139, 69, 19), (i, 0, plank_width, 20))
            pygame.draw.rect(texture, (shade, shade//2, shade//4), (i, 0, plank_width, 2))
            pygame.draw.line(texture, (100, 50, 0), (i, 0), (i, 20), 1)
    
    elif platform_type == "grass":
        pygame.draw.rect(texture, (101, 67, 33), (0, 5, width, 15))
        pygame.draw.rect(texture, (34, 139, 34), (0, 0, width, 5))
        for i in range(0, width, 5):
            height = random.randint(1, 3)
            pygame.draw.rect(texture, (random.randint(50, 150), random.randint(150, 200), random.randint(50, 100)), 
                           (i, 0, 2, height))
    
    elif platform_type == "stone":
        pygame.draw.rect(texture, (150, 150, 150), (0, 0, width, 20))
        for _ in range(width//5):
            x, y = random.randint(0, width-5), random.randint(0, 15)
            shade = random.randint(100, 200)
            pygame.draw.rect(texture, (shade, shade, shade), (x, y, 5, 5))
    
    return texture

def create_player_skin(color, style="default"):
    surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
    
    if style == "default":
        pygame.draw.ellipse(surf, color, (5, 10, PLAYER_WIDTH-10, PLAYER_HEIGHT-15))
        pygame.draw.ellipse(surf, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)), 
                          (7, 12, PLAYER_WIDTH-14, PLAYER_HEIGHT-19), 2)
        pygame.draw.circle(surf, color, (PLAYER_WIDTH//2, 10), 10)
        pygame.draw.circle(surf, WHITE, (PLAYER_WIDTH//2-5, 8), 3)
        pygame.draw.circle(surf, WHITE, (PLAYER_WIDTH//2+5, 8), 3)
        pygame.draw.circle(surf, BLACK, (PLAYER_WIDTH//2-5, 8), 1)
        pygame.draw.circle(surf, BLACK, (PLAYER_WIDTH//2+5, 8), 1)
        pygame.draw.arc(surf, BLACK, (PLAYER_WIDTH//2-5, 10, 10, 6), 0.2, 2.9, 1)
        pygame.draw.line(surf, color, (5, 20), (0, 25), 3)
        pygame.draw.line(surf, color, (PLAYER_WIDTH-5, 20), (PLAYER_WIDTH, 25), 3)
    
    elif style == "ninja":
        pygame.draw.ellipse(surf, BLACK, (5, 10, PLAYER_WIDTH-10, PLAYER_HEIGHT-15))
        pygame.draw.ellipse(surf, (50, 50, 50), (10, 5, PLAYER_WIDTH-20, 15))
        pygame.draw.line(surf, (100, 100, 100), (10, 10), (PLAYER_WIDTH-10, 10), 2)
        pygame.draw.rect(surf, RED, (PLAYER_WIDTH//2-8, 10, 5, 2))
        pygame.draw.rect(surf, RED, (PLAYER_WIDTH//2+3, 10, 5, 2))
        pygame.draw.rect(surf, (100, 0, 0), (5, 30, PLAYER_WIDTH-10, 3))
        pygame.draw.line(surf, (150, 150, 150), (5, 20), (10, 25), 2)
        pygame.draw.line(surf, (150, 150, 150), (10, 20), (5, 25), 2)
    
    elif style == "robot":
        for i in range(5, PLAYER_HEIGHT, 5):
            shade = 150 + (i % 10)
            pygame.draw.rect(surf, (shade, shade, shade), (5, i, PLAYER_WIDTH-10, 3))
        pygame.draw.rect(surf, (200, 200, 200), (10, 5, PLAYER_WIDTH-20, 10))
        pygame.draw.line(surf, (200, 200, 200), (PLAYER_WIDTH//2, 0), (PLAYER_WIDTH//2, 5), 2)
        pygame.draw.circle(surf, RED, (PLAYER_WIDTH//2, 0), 3)
        pygame.draw.rect(surf, BLUE, (PLAYER_WIDTH//2-7, 8, 4, 4))
        pygame.draw.rect(surf, BLUE, (PLAYER_WIDTH//2+3, 8, 4, 4))
        pygame.draw.rect(surf, (100, 100, 100), (PLAYER_WIDTH//2-5, 12, 10, 2))
        pygame.draw.line(surf, GREEN, (PLAYER_WIDTH//2-4, 13), (PLAYER_WIDTH//2-2, 13), 1)
        pygame.draw.line(surf, GREEN, (PLAYER_WIDTH//2+2, 13), (PLAYER_WIDTH//2+4, 13), 1)
        pygame.draw.circle(surf, (100, 100, 100), (0, 20), 4)
        pygame.draw.circle(surf, (100, 100, 100), (PLAYER_WIDTH, 20), 4)
    
    elif style == "classic":
        pygame.draw.rect(surf, color, (0, 0, PLAYER_WIDTH, PLAYER_HEIGHT))
        pygame.draw.rect(surf, WHITE, (PLAYER_WIDTH//4, PLAYER_HEIGHT//4, PLAYER_WIDTH//2, PLAYER_HEIGHT//2))
        pygame.draw.rect(surf, BLACK, (PLAYER_WIDTH//3, PLAYER_HEIGHT//3, 5, 5))
        pygame.draw.rect(surf, BLACK, (2*PLAYER_WIDTH//3-5, PLAYER_HEIGHT//3, 5, 5))
        pygame.draw.rect(surf, BLACK, (PLAYER_WIDTH//3, 2*PLAYER_HEIGHT//3, PLAYER_WIDTH//3, 3))
        pygame.draw.rect(surf, color, (0, PLAYER_HEIGHT//3, PLAYER_WIDTH//4, 5))
        pygame.draw.rect(surf, color, (3*PLAYER_WIDTH//4, PLAYER_HEIGHT//3, PLAYER_WIDTH//4, 5))
    
    elif style == "bach":
        pygame.draw.ellipse(surf, (50, 50, 150), (5, 10, PLAYER_WIDTH-10, PLAYER_HEIGHT-15))
        pygame.draw.ellipse(surf, (200, 200, 200), (8, 15, PLAYER_WIDTH-16, PLAYER_HEIGHT-25))
        pygame.draw.circle(surf, (200, 180, 150), (PLAYER_WIDTH//2, 10), 10)
        pygame.draw.ellipse(surf, (220, 220, 220), (PLAYER_WIDTH//2-12, 0, 24, 15))
        pygame.draw.arc(surf, BLACK, (PLAYER_WIDTH//2-5, 5, 10, 10), 0.2, 2.9, 2)
        pygame.draw.line(surf, BLACK, (PLAYER_WIDTH//2-3, 12), (PLAYER_WIDTH//2+3, 12), 1)
        pygame.draw.polygon(surf, (200, 200, 200), 
                          [(PLAYER_WIDTH//2, 15), (PLAYER_WIDTH//2-5, 20), (PLAYER_WIDTH//2+5, 20)])
        pygame.draw.circle(surf, (200, 180, 150), (0, 25), 4)
        pygame.draw.circle(surf, (200, 180, 150), (PLAYER_WIDTH, 25), 4)
        pygame.draw.rect(surf, (240, 240, 200), (0, 20, 5, 10))
        pygame.draw.rect(surf, (240, 240, 200), (PLAYER_WIDTH-5, 20, 5, 10))
        pygame.draw.line(surf, BLACK, (0, 22), (5, 22), 1)
        pygame.draw.line(surf, BLACK, (PLAYER_WIDTH-5, 22), (PLAYER_WIDTH, 22), 1)
    
    elif style == "wizard":
        pygame.draw.ellipse(surf, (100, 50, 150), (5, 10, PLAYER_WIDTH-10, PLAYER_HEIGHT-15))
        pygame.draw.rect(surf, (150, 100, 50), (10, 25, PLAYER_WIDTH-20, 3))
        pygame.draw.circle(surf, (200, 180, 150), (PLAYER_WIDTH//2, 10), 10)
        pygame.draw.ellipse(surf, (200, 200, 200), (PLAYER_WIDTH//2-8, 12, 16, 10))
        pygame.draw.polygon(surf, (50, 50, 100), 
                          [(PLAYER_WIDTH//2, 0), (PLAYER_WIDTH//2-15, 10), (PLAYER_WIDTH//2+15, 10)])
        pygame.draw.circle(surf, BLUE, (PLAYER_WIDTH//2-3, 8), 2)
        pygame.draw.circle(surf, BLUE, (PLAYER_WIDTH//2+3, 8), 2)
        pygame.draw.line(surf, (150, 100, 50), (PLAYER_WIDTH, 15), (PLAYER_WIDTH+5, 5), 3)
        pygame.draw.circle(surf, (255, 200, 0), (PLAYER_WIDTH+5, 5), 4)
    
    return surf

class TrailParticle:
    def __init__(self, x, y, trail_type):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.trail_type = trail_type
        
        if trail_type == "sparkle":
            self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(100, 200)
        elif trail_type == "fire":
            self.color = (255, random.randint(50, 150), 0)
        elif trail_type == "shadow":
            self.color = (50, 50, 50, random.randint(100, 200))
        elif trail_type == "rainbow":
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        if trail_type in ["sparkle", "rainbow"]:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
        else:
            self.vx = 0
            self.vy = 0
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.trail_type == "fire":
            self.y -= random.uniform(0.5, 1.5)
        return self.life > 0
    
    def draw(self, surface, scroll):
        alpha = min(255, int(255 * (self.life / self.max_life)))
        
        if self.trail_type == "shadow":
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - scroll[0] - self.size, self.y - scroll[1] - self.size))
        else:
            color = self.color
            if self.trail_type == "fire" and self.life < self.max_life//2:
                color = (255, random.randint(150, 255), 0)
            
            if len(color) == 4:
                s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (self.size, self.size), self.size)
                surface.blit(s, (self.x - scroll[0] - self.size, self.y - scroll[1] - self.size))
            else:
                pygame.draw.circle(surface, color, 
                                 (int(self.x - scroll[0]), int(self.y - scroll[1])), 
                                 self.size)

class Cloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.2, 0.5)
        self.size = random.randint(50, 150)
        self.parts = []
        for _ in range(random.randint(3, 6)):
            part_size = random.randint(self.size//3, self.size//2)
            offset_x = random.randint(-self.size//2, self.size//2)
            offset_y = random.randint(-self.size//4, self.size//4)
            self.parts.append((offset_x, offset_y, part_size))
    
    def update(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH + self.size:
            self.x = -self.size
            self.y = random.randint(50, SCREEN_HEIGHT//3)
    
    def draw(self, surface, scroll):
        for offset_x, offset_y, part_size in self.parts:
            pos_x = self.x + offset_x - scroll[0] * 0.2
            pos_y = self.y + offset_y - scroll[1] * 0.1
            pygame.draw.circle(surface, (240, 240, 255, 200), 
                             (int(pos_x), int(pos_y)), part_size)
            pygame.draw.circle(surface, (255, 255, 255, 200), 
                             (int(pos_x)-5, int(pos_y)-5), part_size-5)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", 30)
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class Player:
    def __init__(self, x, y):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_y = 0
        self.vel_x = 0
        self.jumping = True
        self.flip = False
        self.current_skin = "bach"
        self.current_trail = "none"
        self.skins = self.load_skins()
        self.image = self.skins[self.current_skin]
        self.on_moving_platform = None
        self.trail_particles = []
        self.trail_timer = 0
    
    def load_skins(self):
        return {
            "bach": create_player_skin((50, 50, 150), "bach"),
            "default": create_player_skin((200, 100, 50), "default"),
            "classic": create_player_skin((200, 100, 50), "classic"),
            "ninja": create_player_skin(BLACK, "ninja"),
            "robot": create_player_skin((150, 150, 150), "robot"),
            "wizard": create_player_skin((100, 50, 150), "wizard")
        }
    
    def set_skin(self, skin_name):
        if skin_name in self.skins:
            self.current_skin = skin_name
            self.image = self.skins[skin_name]
    
    def set_trail(self, trail_type):
        if trail_type in TRAIL_TYPES:
            self.current_trail = trail_type
            self.trail_particles = []
    
    def add_trail_particle(self):
        if self.current_trail != "none":
            x = self.rect.centerx + random.randint(-5, 5)
            y = self.rect.centery + random.randint(-5, 5)
            self.trail_particles.append(TrailParticle(x, y, self.current_trail))
    
    def update_trail(self):
        self.trail_timer += 1
        if self.trail_timer >= 3:
            self.add_trail_particle()
            self.trail_timer = 0
        
        self.trail_particles = [p for p in self.trail_particles if p.update()]
    
    def move(self, dx, platforms):
        self.vel_x = dx * PLAYER_SPEED
        if dx != 0:
            self.flip = dx < 0
        
        self.rect.x += self.vel_x
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.rect.left = platform.rect.right
        
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
    
    def jump(self):
        if not self.jumping:
            self.vel_y = JUMP_FORCE
            self.jumping = True
            self.on_moving_platform = None
    
    def apply_gravity(self, platforms, scroll):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        self.jumping = True
        self.on_moving_platform = None
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y >= 0 and self.rect.bottom <= platform.rect.centery:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.jumping = False
                    if platform.is_moving:
                        self.on_moving_platform = platform
                
                elif self.vel_y < 0 and self.rect.top >= platform.rect.centery:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        if self.on_moving_platform:
            self.rect.x += self.on_moving_platform.speed * self.on_moving_platform.move_dir
        
        if self.rect.top > SCREEN_HEIGHT + scroll[1]:
            return True
        return False
    
    def draw(self, surface, scroll):
        for particle in self.trail_particles:
            particle.draw(surface, scroll)
        
        if self.flip:
            flipped = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        else:
            surface.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

class Platform:
    def __init__(self, x, y, width, is_moving=False):
        self.rect = pygame.Rect(x, y, width, 20)
        self.type = random.choice(["wood", "grass", "stone"])
        self.texture = create_platform_texture(width, self.type)
        self.is_moving = is_moving
        if is_moving:
            self.move_dir = random.choice([-1, 1])
            self.speed = random.uniform(1, 2)
            self.move_dist = random.randint(50, 150)
            self.start_x = x
    
    def update(self):
        if self.is_moving:
            prev_x = self.rect.x
            self.rect.x += self.speed * self.move_dir
            if abs(self.rect.x - self.start_x) > self.move_dist:
                self.move_dir *= -1
    
    def draw(self, surface, scroll):
        shadow = pygame.Rect(
            self.rect.x - scroll[0] + 3,
            self.rect.y - scroll[1] + 3,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow, border_radius=5)
        
        platform_pos = (self.rect.x - scroll[0], self.rect.y - scroll[1])
        surface.blit(self.texture, platform_pos)
        
        if self.type == "grass":
            for i in range(0, self.rect.width, 5):
                if random.random() < 0.3:
                    grass_height = random.randint(3, 7)
                    grass_x = self.rect.x - scroll[0] + i
                    grass_y = self.rect.y - scroll[1] - grass_height + 3
                    pygame.draw.line(surface, (random.randint(50, 150), random.randint(150, 200), 50),
                                   (grass_x, grass_y), (grass_x, grass_y + grass_height), 2)

class ShopItem:
    def __init__(self, name, price, x, y, item_type="skin"):
        self.name = name
        self.price = price
        self.rect = pygame.Rect(x, y, 100, 150)
        self.owned = False
        self.equipped = False
        self.item_type = item_type
    
    def draw(self, surface, player_skins=None):
        color = (200, 200, 200) if not self.owned else (100, 200, 100)
        if self.equipped:
            color = (100, 100, 200)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        font = pygame.font.SysFont("Arial", 20)
        
        if self.item_type == "skin":
            preview_img = pygame.transform.scale(player_skins[self.name], (60, 90))
            surface.blit(preview_img, (self.rect.centerx - 30, self.rect.y + 10))
            
            name_text = font.render(self.name.capitalize(), True, BLACK)
            surface.blit(name_text, (self.rect.centerx - name_text.get_width()//2, self.rect.y + 105))
        else:
            if self.name == "none":
                name_text = font.render("No Trail", True, BLACK)
                surface.blit(name_text, (self.rect.centerx - name_text.get_width()//2, self.rect.y + 60))
            else:
                if self.name == "sparkle":
                    for _ in range(10):
                        x = random.randint(self.rect.left + 10, self.rect.right - 10)
                        y = random.randint(self.rect.top + 10, self.rect.bottom - 10)
                        pygame.draw.circle(surface, (random.randint(200, 255), random.randint(200, 255), random.randint(100, 200)), 
                                         (x, y), random.randint(2, 4))
                elif self.name == "fire":
                    pygame.draw.circle(surface, (255, 100, 0), (self.rect.centerx, self.rect.centery), 15)
                    pygame.draw.circle(surface, (255, 200, 0), (self.rect.centerx, self.rect.centery), 10)
                elif self.name == "shadow":
                    s = pygame.Surface((80, 80), pygame.SRCALPHA)
                    pygame.draw.circle(s, (50, 50, 50, 150), (40, 40), 20)
                    surface.blit(s, (self.rect.centerx - 40, self.rect.centery - 40))
                elif self.name == "rainbow":
                    for i in range(5):
                        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        pygame.draw.circle(surface, color, 
                                         (self.rect.centerx - 20 + i*10, self.rect.centery), 
                                         random.randint(3, 5))
            
            name_text = font.render(self.name.capitalize(), True, BLACK)
            surface.blit(name_text, (self.rect.centerx - name_text.get_width()//2, self.rect.y + 125))
        
        if not self.owned:
            price_text = font.render(f"{self.price} coins", True, BLACK)
            surface.blit(price_text, (self.rect.centerx - price_text.get_width()//2, self.rect.y + 145))

class Game:
    def __init__(self):
        self.reset()
        self.state = "menu"
        self.total_coins = 0
        self.setup_menu()
        self.setup_shop()
        self.clouds = [Cloud(random.randint(0, SCREEN_WIDTH), random.randint(50, SCREEN_HEIGHT//3)) for _ in range(5)]
        self.load_player_prefs()
    
    def reset(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.platforms = []
        self.coins = []
        self.scroll = [0, 0]
        self.score = 0
        self.difficulty = 0
        
        self.generate_platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100)
        for _ in range(MAX_PLATFORMS - 1):
            self.generate_random_platform()
        
        self.player.rect.bottom = self.platforms[0].rect.top
        self.player.rect.centerx = self.platforms[0].rect.centerx
        
        self.load_player_prefs()
    
    def setup_menu(self):
        button_width = 300
        button_height = 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.play_button = Button(
            center_x, 250, button_width, button_height,
            "PLAY", GREEN, (100, 255, 100))
        self.shop_button = Button(
            center_x, 350, button_width, button_height,
            "SHOP", BLUE, (100, 100, 255))
        self.quit_button = Button(
            center_x, 450, button_width, button_height,
            "QUIT", RED, (255, 100, 100))
    
    def setup_shop(self):
        self.shop_items = [
            ShopItem("bach", 0, 150, 150),
            ShopItem("default", 100, 300, 150),
            ShopItem("classic", 200, 450, 150),
            ShopItem("ninja", 300, 600, 150),
            ShopItem("robot", 400, 750, 150),
            ShopItem("wizard", 500, 900, 150),
            
            ShopItem("none", 0, 150, 350, "trail"),
            ShopItem("sparkle", 150, 300, 350, "trail"),
            ShopItem("fire", 200, 450, 350, "trail"),
            ShopItem("shadow", 100, 600, 350, "trail"),
            ShopItem("rainbow", 250, 750, 350, "trail")
        ]
        
        self.load_player_prefs()
        
        self.save_button = Button(
            SCREEN_WIDTH // 2 - 150, 450, 300, 60,
            "SAVE SELECTIONS", (150, 200, 150), (200, 255, 200))
        
        self.back_button = Button(
            SCREEN_WIDTH // 2 - 150, 520, 300, 60,
            "BACK TO MENU", (150, 150, 150), (200, 200, 200))
    
    def save_player_prefs(self):
        prefs = {
            'skin': self.player.current_skin,
            'trail': self.player.current_trail,
            'coins': self.total_coins,
            'owned_skins': [item.name for item in self.shop_items 
                           if item.owned and item.item_type == "skin"],
            'owned_trails': [item.name for item in self.shop_items 
                            if item.owned and item.item_type == "trail"]
        }
        
        try:
            # Web version uses localStorage
            if '__window__' in globals():
                __window__.localStorage.setItem('dontlookdown_prefs', json.dumps(prefs))
                return True
            # Fallback for testing locally
            with open('player_prefs.json', 'w') as f:
                json.dump(prefs, f)
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False
    
    def load_player_prefs(self):
        try:
            # Web version
            if '__window__' in globals():
                prefs_str = __window__.localStorage.getItem('dontlookdown_prefs')
                if prefs_str:
                    prefs = json.loads(prefs_str)
                else:
                    return False
            else:
                # Local testing
                if os.path.exists('player_prefs.json'):
                    with open('player_prefs.json', 'r') as f:
                        prefs = json.load(f)
                else:
                    return False
            
            if 'coins' in prefs:
                self.total_coins = prefs['coins']
            
            if 'skin' in prefs:
                self.player.set_skin(prefs['skin'])
                for item in self.shop_items:
                    if item.item_type == "skin":
                        item.owned = item.name in prefs.get('owned_skins', [])
                        item.equipped = (item.name == prefs['skin'])
            
            if 'trail' in prefs:
                self.player.set_trail(prefs['trail'])
                for item in self.shop_items:
                    if item.item_type == "trail":
                        item.owned = item.name in prefs.get('owned_trails', [])
                        item.equipped = (item.name == prefs['trail'])
            
            return True
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return False
    
    def generate_platform(self, x, y, width, is_moving=False):
        self.platforms.append(Platform(x, y, width, is_moving))
    
    def generate_random_platform(self):
        if not self.platforms:
            self.generate_platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100)
            return
        
        highest = min(self.platforms, key=lambda p: p.rect.y)
        
        min_x = max(0, highest.rect.x - 200)
        max_x = min(SCREEN_WIDTH - 100, highest.rect.x + 200)
        x = random.randint(int(min_x), int(max_x))
        
        y = highest.rect.y - random.randint(MIN_PLATFORM_DIST, MAX_PLATFORM_DIST)
        width = random.randint(*PLATFORM_WIDTH_RANGE)
        is_moving = random.random() < 0.2
        
        self.generate_platform(x, y, width, is_moving)
        
        if random.random() < 0.3:
            self.coins.append({
                'rect': pygame.Rect(x + random.randint(20, width - 20), y - 30, 20, 20),
                'collected': False
            })
    
    def update(self):
        if self.state != "playing":
            return
        
        for cloud in self.clouds:
            cloud.update()
        
        self.player.update_trail()
        
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        
        self.player.move(dx, self.platforms)
        
        if self.player.apply_gravity(self.platforms, self.scroll):
            self.state = "game_over"
            self.total_coins += self.score // 10
            self.save_player_prefs()
        
        for platform in self.platforms:
            platform.update()
        
        self.platforms = [p for p in self.platforms if p.rect.y - self.scroll[1] < SCREEN_HEIGHT + 200]
        self.coins = [c for c in self.coins if not c['collected'] and c['rect'].y - self.scroll[1] < SCREEN_HEIGHT + 100]
        
        while len(self.platforms) < MAX_PLATFORMS:
            self.generate_random_platform()
        
        if self.player.rect.top < SCROLL_THRESH + self.scroll[1]:
            self.scroll[1] = self.player.rect.top - SCROLL_THRESH
        
        self.score = int(self.scroll[1] / 10)
        
        for coin in self.coins[:]:
            if not coin['collected'] and self.player.rect.colliderect(coin['rect']):
                coin['collected'] = True
                self.total_coins += 1
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_click = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.state == "playing":
                    self.player.jump()
                if event.key == pygame.K_RETURN and self.state == "game_over":
                    self.reset()
                    self.state = "playing"
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                    elif self.state == "shop":
                        self.state = "menu"
        
        if self.state == "menu":
            self.play_button.check_hover(mouse_pos)
            self.shop_button.check_hover(mouse_pos)
            self.quit_button.check_hover(mouse_pos)
            
            if self.play_button.is_clicked(mouse_pos, mouse_click):
                self.reset()
                self.state = "playing"
            elif self.shop_button.is_clicked(mouse_pos, mouse_click):
                self.state = "shop"
            elif self.quit_button.is_clicked(mouse_pos, mouse_click):
                return False
        
        elif self.state == "shop":
            self.back_button.check_hover(mouse_pos)
            self.save_button.check_hover(mouse_pos)
            
            for item in self.shop_items:
                if item.rect.collidepoint(mouse_pos) and mouse_click:
                    if item.owned:
                        if item.item_type == "skin":
                            for i in self.shop_items:
                                if i.item_type == "skin":
                                    i.equipped = False
                            item.equipped = True
                            self.player.set_skin(item.name)
                        else:
                            for i in self.shop_items:
                                if i.item_type == "trail":
                                    i.equipped = False
                            item.equipped = True
                            self.player.set_trail(item.name)
                    elif self.total_coins >= item.price:
                        item.owned = True
                        self.total_coins -= item.price
                        if item.item_type == "skin":
                            for i in self.shop_items:
                                if i.item_type == "skin":
                                    i.equipped = False
                            item.equipped = True
                            self.player.set_skin(item.name)
                        else:
                            for i in self.shop_items:
                                if i.item_type == "trail":
                                    i.equipped = False
                            item.equipped = True
                            self.player.set_trail(item.name)
            
            if self.save_button.is_clicked(mouse_pos, mouse_click):
                if self.save_player_prefs():
                    self.show_saved_message = True
                    self.saved_message_timer = pygame.time.get_ticks()
            
            if self.back_button.is_clicked(mouse_pos, mouse_click):
                self.state = "menu"
        
        elif self.state == "game_over":
            if mouse_click:
                self.reset()
                self.state = "playing"
        
        return True
    
    def draw(self):
        for y in range(SCREEN_HEIGHT):
            shade = min(255, 135 + y // 4)
            pygame.draw.line(screen, (shade, min(255, 206 + y // 8), min(255, 235 + y // 12)), 
                           (0, y), (SCREEN_WIDTH, y))
        
        if self.state == "playing":
            for cloud in self.clouds:
                cloud.draw(screen, self.scroll)
            
            for platform in self.platforms:
                platform.draw(screen, self.scroll)
            
            for coin in self.coins:
                if not coin['collected']:
                    pos_x = coin['rect'].centerx - self.scroll[0]
                    pos_y = coin['rect'].centery - self.scroll[1]
                    
                    angle = (pygame.time.get_ticks() // 10) % 360
                    rad_angle = math.radians(angle)
                    shine_x = pos_x + 15 * math.cos(rad_angle)
                    shine_y = pos_y + 15 * math.sin(rad_angle)
                    
                    pygame.draw.circle(screen, GOLD, (int(pos_x), int(pos_y)), 10)
                    pygame.draw.circle(screen, (255, 255, 0), (int(pos_x), int(pos_y)), 8)
                    pygame.draw.circle(screen, (255, 255, 200, 100), (int(shine_x), int(shine_y)), 5)
            
            self.player.draw(screen, self.scroll)
            
            font = pygame.font.SysFont("Arial", 30, bold=True)
            score_text = font.render(f"Score: {self.score}", True, BLACK)
            pygame.draw.rect(screen, (255, 255, 255, 150), (15, 15, score_text.get_width() + 10, score_text.get_height() + 10), border_radius=5)
            screen.blit(score_text, (20, 20))
            
            coins_text = font.render(f"Coins: {self.total_coins}", True, GOLD)
            pygame.draw.rect(screen, (255, 255, 255, 150), (15, 55, coins_text.get_width() + 10, coins_text.get_height() + 10), border_radius=5)
            screen.blit(coins_text, (20, 60))
        
        elif self.state == "menu":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            screen.blit(overlay, (0, 0))
            
            for cloud in self.clouds:
                cloud.draw(screen, (0, 0))
            
            title_font = pygame.font.SysFont("Arial", 60, bold=True)
            title_text = title_font.render("DON'T LOOK DOWN", True, BLACK)
            shadow_text = title_font.render("DON'T LOOK DOWN", True, (100, 100, 100, 150))
            screen.blit(shadow_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 3, 103))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
            
            self.play_button.draw(screen)
            self.shop_button.draw(screen)
            self.quit_button.draw(screen)
            
            instr_font = pygame.font.SysFont("Arial", 24)
            instructions = [
                "Climb as high as you can!",
                "Use LEFT/RIGHT or A/D to move",
                "Press SPACE to jump",
                "Collect coins to buy skins & trails",
                "Don't fall off the screen!"
            ]
            
            pygame.draw.rect(screen, (255, 255, 255, 180), 
                           (SCREEN_WIDTH // 2 - 200, 520, 400, len(instructions) * 30 + 10), 
                           border_radius=10)
            
            for i, line in enumerate(instructions):
                text = instr_font.render(line, True, BLACK)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 530 + i * 30))
        
        elif self.state == "shop":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 220, 255, 200))
            screen.blit(overlay, (0, 0))
            
            title_font = pygame.font.SysFont("Arial", 60, bold=True)
            title_text = title_font.render("SKIN SHOP", True, (50, 50, 150))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
            
            coins_font = pygame.font.SysFont("Arial", 40)
            coins_text = coins_font.render(f"Coins: {self.total_coins}", True, GOLD)
            pygame.draw.circle(screen, GOLD, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2 - 30, 140), 15)
            screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 120))
            
            font = pygame.font.SysFont("Arial", 30, bold=True)
            skins_label = font.render("SKINS", True, (50, 50, 150))
            screen.blit(skins_label, (150, 120))
            
            trails_label = font.render("TRAILS", True, (50, 50, 150))
            screen.blit(trails_label, (150, 320))
            
            pygame.draw.rect(screen, (255, 255, 255, 150), (100, 150, 800, 150), border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255, 150), (100, 350, 800, 150), border_radius=15)
            
            for item in self.shop_items:
                item.draw(screen, self.player.skins)
            
            self.save_button.draw(screen)
            self.back_button.draw(screen)
            
            if hasattr(self, 'show_saved_message') and self.show_saved_message:
                current_time = pygame.time.get_ticks()
                if current_time - self.saved_message_timer < 2000:
                    font = pygame.font.SysFont("Arial", 30, bold=True)
                    saved_text = font.render("Saved!", True, GREEN)
                    screen.blit(saved_text, (SCREEN_WIDTH // 2 - saved_text.get_width() // 2, 520))
                else:
                    self.show_saved_message = False
        
        elif self.state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.SysFont("Arial", 80, bold=True)
            game_over_text = game_over_font.render("GAME OVER", True, (255, 100, 100))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
            
            score_font = pygame.font.SysFont("Arial", 50)
            score_text = score_font.render(f"Score: {self.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            coins_text = score_font.render(f"Total Coins: {self.total_coins}", True, GOLD)
            screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            
            restart_font = pygame.font.SysFont("Arial", 30)
            restart_text = restart_font.render("Click or press ENTER to restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))

async def main():
    game = Game()
    running = True
    
    while running:
        clock.tick(FPS)
        
        running = game.handle_events()
        game.update()
        game.draw()
        
        pygame.display.flip()
        await asyncio.sleep(0)

# Web entry point
if __name__ == "__main__":
    asyncio.run(main())
