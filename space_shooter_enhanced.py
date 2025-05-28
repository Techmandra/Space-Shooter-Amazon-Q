import pygame
import random
import math
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Game states
START_MENU = 0
GAME_ACTIVE = 1
GAME_OVER = 2
GAME_PAUSED = 3

# Create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Function to create simple ship image
def create_ship_image(filename, color, width, height):
    if not os.path.exists(filename):
        ship_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Ship body
        pygame.draw.polygon(ship_surface, color, [
            (width // 2, 0),  # Top
            (0, height),  # Bottom left
            (width, height)  # Bottom right
        ])
        
        # Cockpit
        pygame.draw.ellipse(ship_surface, (100, 100, 200), 
                          (width // 4, height // 2, width // 2, height // 3))
        
        # Engine glow
        pygame.draw.rect(ship_surface, (255, 165, 0), 
                       (width // 3, height - 5, width // 3, 5))
        
        # Save the image
        pygame.image.save(ship_surface, filename)
    
    return pygame.image.load(filename)

# Function to create simple enemy ship image
def create_enemy_image(filename, color, width, height):
    if not os.path.exists(filename):
        ship_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Ship body
        pygame.draw.polygon(ship_surface, color, [
            (width // 2, height),  # Bottom
            (0, 0),  # Top left
            (width, 0)  # Top right
        ])
        
        # Cockpit
        pygame.draw.ellipse(ship_surface, (100, 100, 200), 
                          (width // 4, height // 4, width // 2, height // 3))
        
        # Save the image
        pygame.image.save(ship_surface, filename)
    
    return pygame.image.load(filename)

# Function to create bullet image
def create_bullet_image(filename, color, width, height):
    if not os.path.exists(filename):
        bullet_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Bullet body
        pygame.draw.rect(bullet_surface, color, (0, 0, width, height))
        
        # Bullet glow
        pygame.draw.rect(bullet_surface, WHITE, (width // 4, 0, width // 2, height // 4))
        
        # Save the image
        pygame.image.save(bullet_surface, filename)
    
    return pygame.image.load(filename)

# Function to create explosion animation frames
def create_explosion_image(filename, frame, size):
    if not os.path.exists(filename):
        explosion_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different explosion shapes based on frame
        if frame == 0:
            # Small center
            pygame.draw.circle(explosion_surface, YELLOW, (size // 2, size // 2), size // 6)
        elif frame == 1:
            # Medium with rays
            pygame.draw.circle(explosion_surface, YELLOW, (size // 2, size // 2), size // 4)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = size // 2 + int(math.cos(rad) * size // 4)
                y1 = size // 2 + int(math.sin(rad) * size // 4)
                x2 = size // 2 + int(math.cos(rad) * size // 2)
                y2 = size // 2 + int(math.sin(rad) * size // 2)
                pygame.draw.line(explosion_surface, YELLOW, (x1, y1), (x2, y2), 3)
        elif frame == 2:
            # Large with rays
            pygame.draw.circle(explosion_surface, RED, (size // 2, size // 2), size // 3)
            pygame.draw.circle(explosion_surface, YELLOW, (size // 2, size // 2), size // 4)
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                x1 = size // 2 + int(math.cos(rad) * size // 3)
                y1 = size // 2 + int(math.sin(rad) * size // 3)
                x2 = size // 2 + int(math.cos(rad) * size // 1.5)
                y2 = size // 2 + int(math.sin(rad) * size // 1.5)
                pygame.draw.line(explosion_surface, RED, (x1, y1), (x2, y2), 3)
        else:
            # Fading
            alpha = 255 - (frame - 3) * 50
            if alpha < 0:
                alpha = 0
            pygame.draw.circle(explosion_surface, (RED[0], RED[1], RED[2], alpha), 
                             (size // 2, size // 2), size // 2)
        
        # Save the image
        pygame.image.save(explosion_surface, filename)
    
    return pygame.image.load(filename)

# Function to create star image for background
def create_star_image(filename, size):
    if not os.path.exists(filename):
        star_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw a simple star
        pygame.draw.circle(star_surface, WHITE, (size // 2, size // 2), size // 2)
        
        # Save the image
        pygame.image.save(star_surface, filename)
    
    return pygame.image.load(filename)

# Create and load images
player_image = create_ship_image('images/player_ship.png', GREEN, 50, 50)
enemy_image = create_enemy_image('images/enemy_ship.png', RED, 40, 40)
bullet_image = create_bullet_image('images/bullet.png', YELLOW, 4, 10)

# Create explosion animation frames
explosion_frames = []
for i in range(6):
    frame = create_explosion_image(f'images/explosion_{i}.png', i, 60)
    explosion_frames.append(frame)

# Create stars for background
star_images = []
for i in range(3):
    size = i * 2 + 1  # 1, 3, 5 pixels
    star = create_star_image(f'images/star_{i}.png', size)
    star_images.append(star)

class Star:
    def __init__(self):
        self.size = random.randint(0, 2)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = (self.size + 1) * 0.5
        self.image = star_images[self.size]
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100  # milliseconds between frames
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
        return self.frame >= len(explosion_frames)
    
    def draw(self):
        if self.frame < len(explosion_frames):
            image = explosion_frames[self.frame]
            screen.blit(image, (self.x - image.get_width() // 2, 
                              self.y - image.get_height() // 2))

class Player:
    def __init__(self):
        self.image = player_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = 5
        self.health = 100
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # frames between shots
        self.engine_flame = 0  # For engine animation
    
    def move(self, dx, dy):
        # Keep player within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x + dx))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y + dy))
    
    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            bullets.append(Bullet(self.x + self.width // 2 - 2, self.y, -10))
            self.shoot_cooldown = self.shoot_delay
            return True
        return False
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Animate engine flame
        self.engine_flame = (self.engine_flame + 1) % 6
    
    def draw(self):
        # Draw the ship
        screen.blit(self.image, (self.x, self.y))
        
        # Draw engine flame animation
        flame_height = 5 + self.engine_flame % 3
        flame_color = (255, 165, 0) if self.engine_flame < 3 else (255, 69, 0)
        pygame.draw.rect(screen, flame_color, 
                       (self.x + self.width // 3, self.y + self.height, 
                        self.width // 3, flame_height))

class Enemy:
    def __init__(self, x, y):
        self.image = enemy_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x
        self.y = y
        self.speed = random.uniform(1, 3)
    
    def update(self):
        self.y += self.speed
        return self.y > SCREEN_HEIGHT
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Bullet:
    def __init__(self, x, y, speed):
        self.image = bullet_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x
        self.y = y
        self.speed = speed
    
    def update(self):
        self.y += self.speed
        return self.y < 0 or self.y > SCREEN_HEIGHT
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Game:
    def __init__(self):
        self.state = START_MENU
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.stars = []
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60  # frames between enemy spawns
        
        # Create stars for background
        for _ in range(100):
            self.stars.append(Star())
    
    def reset(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.score = 0
        self.enemy_spawn_timer = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == START_MENU and event.key == pygame.K_RETURN:
                    self.state = GAME_ACTIVE
                    self.reset()
                elif self.state == GAME_OVER and event.key == pygame.K_RETURN:
                    self.state = START_MENU
                elif self.state == GAME_ACTIVE and event.key == pygame.K_p:
                    self.state = GAME_PAUSED
                elif self.state == GAME_PAUSED and event.key == pygame.K_p:
                    self.state = GAME_ACTIVE
    
    def update(self):
        # Always update stars for background effect
        for star in self.stars:
            star.update()
        
        if self.state != GAME_ACTIVE:
            return
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= self.player.speed
        if keys[pygame.K_RIGHT]:
            dx += self.player.speed
        if keys[pygame.K_UP]:
            dy -= self.player.speed
        if keys[pygame.K_DOWN]:
            dy += self.player.speed
        self.player.move(dx, dy)
        
        # Handle shooting
        if keys[pygame.K_SPACE]:
            self.player.shoot(self.bullets)
        
        # Update player
        self.player.update()
        
        # Spawn enemies
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            x = random.randint(0, SCREEN_WIDTH - 40)
            self.enemies.append(Enemy(x, -40))
            self.enemy_spawn_timer = 0
            # Increase spawn rate as score increases
            self.enemy_spawn_delay = max(20, 60 - self.score // 500)
        
        # Update bullets
        for bullet in self.bullets[:]:
            if bullet.update():
                self.bullets.remove(bullet)
        
        # Update enemies
        for enemy in self.enemies[:]:
            if enemy.update():
                self.enemies.remove(enemy)
                self.player.health -= 10  # Player loses health when enemy passes
                if self.player.health <= 0:
                    self.state = GAME_OVER
        
        # Update explosions
        for explosion in self.explosions[:]:
            if explosion.update():
                self.explosions.remove(explosion)
        
        # Check for collisions
        self.check_collisions()
    
    def check_collisions(self):
        # Check bullet-enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet.x < enemy.x + enemy.width and
                    bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and
                    bullet.y + bullet.height > enemy.y):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        # Create explosion at enemy position
                        self.explosions.append(Explosion(
                            enemy.x + enemy.width // 2,
                            enemy.y + enemy.height // 2
                        ))
                        self.enemies.remove(enemy)
                    self.score += 100
        
        # Check player-enemy collisions
        for enemy in self.enemies[:]:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                if enemy in self.enemies:
                    # Create explosion at collision point
                    self.explosions.append(Explosion(
                        enemy.x + enemy.width // 2,
                        enemy.y + enemy.height // 2
                    ))
                    self.enemies.remove(enemy)
                self.player.health -= 20
                if self.player.health <= 0:
                    # Create explosion at player position
                    self.explosions.append(Explosion(
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height // 2
                    ))
                    self.state = GAME_OVER
    
    def draw_stars(self):
        for star in self.stars:
            star.draw()
    
    def draw_start_menu(self):
        # Draw animated title
        title_y_offset = math.sin(pygame.time.get_ticks() / 500) * 10
        title = self.font.render("SPACE SHOOTER", True, WHITE)
        instructions = self.font.render("Press ENTER to start", True, YELLOW)
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 
                          SCREEN_HEIGHT // 2 - 50 + title_y_offset))
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 
                                SCREEN_HEIGHT // 2 + 50))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Pulsating game over text
        scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 200)
        game_over_text = self.font.render("GAME OVER", True, RED)
        scaled_text = pygame.transform.scale(
            game_over_text, 
            (int(game_over_text.get_width() * scale), 
             int(game_over_text.get_height() * scale))
        )
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press ENTER to return to menu", True, YELLOW)
        
        screen.blit(scaled_text, (SCREEN_WIDTH // 2 - scaled_text.get_width() // 2, 
                               SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 
                              SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 + 50))
    
    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        resume_text = self.font.render("Press P to resume", True, YELLOW)
        
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                              SCREEN_HEIGHT // 2 - 25))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 
                               SCREEN_HEIGHT // 2 + 25))
    
    def draw_hud(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Draw health bar
        health_width = 200
        health_height = 20
        health_x = SCREEN_WIDTH - health_width - 20
        health_y = 20
        
        # Health bar background
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        
        # Health bar fill
        health_fill_width = int(health_width * (self.player.health / 100))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_fill_width, health_height))
        
        # Health bar border
        pygame.draw.rect(screen, WHITE, (health_x, health_y, health_width, health_height), 2)
        
        # Health text
        health_text = self.small_font.render(f"Health: {self.player.health}%", True, WHITE)
        screen.blit(health_text, (health_x + 5, health_y + 2))
    
    def draw(self):
        # Draw background
        screen.fill(BLACK)
        
        # Draw stars
        self.draw_stars()
        
        if self.state == START_MENU:
            self.draw_start_menu()
        elif self.state == GAME_ACTIVE or self.state == GAME_PAUSED:
            # Draw game elements
            for bullet in self.bullets:
                bullet.draw()
            
            for enemy in self.enemies:
                enemy.draw()
            
            self.player.draw()
            
            # Draw explosions
            for explosion in self.explosions:
                explosion.draw()
            
            # Draw HUD
            self.draw_hud()
            
            if self.state == GAME_PAUSED:
                self.draw_pause_menu()
        elif self.state == GAME_OVER:
            # Draw game elements in background
            for bullet in self.bullets:
                bullet.draw()
            
            for enemy in self.enemies:
                enemy.draw()
            
            # Draw explosions
            for explosion in self.explosions:
                explosion.draw()
            
            # Draw HUD
            self.draw_hud()
            
            # Draw game over screen
            self.draw_game_over()

# Main game loop
def main():
    game = Game()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
