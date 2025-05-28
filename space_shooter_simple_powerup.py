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

# Function to create power-up image
def create_powerup_image(filename, color, size):
    if not os.path.exists(filename):
        powerup_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw a glowing orb
        pygame.draw.circle(powerup_surface, color, (size // 2, size // 2), size // 2)
        pygame.draw.circle(powerup_surface, WHITE, (size // 3, size // 3), size // 6)
        
        # Save the image
        pygame.image.save(powerup_surface, filename)
    
    return pygame.image.load(filename)

# Create and load images
player_image = create_ship_image('images/player_ship.png', GREEN, 50, 50)
enemy_image = create_enemy_image('images/enemy_ship.png', RED, 40, 40)
bullet_image = create_bullet_image('images/bullet.png', YELLOW, 4, 10)
powerup_image = create_powerup_image('images/powerup.png', BLUE, 20)

class Star:
    def __init__(self):
        self.size = random.randint(1, 3)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = self.size * 0.5
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

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
        self.power_up_active = False
        self.power_up_time = 0
        self.power_up_duration = 5  # seconds
    
    def move(self, dx, dy):
        # Keep player within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x + dx))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y + dy))
    
    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            # Normal shot
            bullets.append(Bullet(self.x + self.width // 2 - 2, self.y, -10))
            
            # If power-up is active, shoot faster
            if self.power_up_active:
                self.shoot_cooldown = self.shoot_delay // 2
            else:
                self.shoot_cooldown = self.shoot_delay
            return True
        return False
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Animate engine flame
        self.engine_flame = (self.engine_flame + 1) % 6
        
        # Check if power-up has expired
        if self.power_up_active and pygame.time.get_ticks() - self.power_up_time > self.power_up_duration * 1000:
            self.power_up_active = False
    
    def activate_power_up(self):
        self.power_up_active = True
        self.power_up_time = pygame.time.get_ticks()
    
    def draw(self):
        # Draw the ship
        screen.blit(self.image, (self.x, self.y))
        
        # Draw engine flame animation
        flame_height = 5 + self.engine_flame % 3
        flame_color = (255, 165, 0) if self.engine_flame < 3 else (255, 69, 0)
        pygame.draw.rect(screen, flame_color, 
                       (self.x + self.width // 3, self.y + self.height, 
                        self.width // 3, flame_height))
        
        # Draw power-up effect if active
        if self.power_up_active:
            # Calculate time remaining
            time_left = self.power_up_duration - (pygame.time.get_ticks() - self.power_up_time) / 1000
            if time_left > 0:
                # Draw a glowing aura around the ship
                glow_size = int(self.width * 1.2)
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                alpha = int(128 * (time_left / self.power_up_duration))
                pygame.draw.circle(glow_surface, (0, 0, 255, alpha), 
                                 (glow_size // 2, glow_size // 2), glow_size // 2)
                screen.blit(glow_surface, 
                          (self.x + self.width // 2 - glow_size // 2, 
                           self.y + self.height // 2 - glow_size // 2))

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

class PowerUp:
    def __init__(self, x, y):
        self.image = powerup_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x
        self.y = y
        self.speed = 2
        self.animation_offset = 0
    
    def update(self):
        self.y += self.speed
        
        # Simple floating animation
        self.animation_offset = math.sin(pygame.time.get_ticks() / 200) * 5
        
        return self.y > SCREEN_HEIGHT
    
    def draw(self):
        # Draw with a slight horizontal oscillation for floating effect
        screen.blit(self.image, (self.x + self.animation_offset, self.y))

class Game:
    def __init__(self):
        self.state = START_MENU
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.stars = []
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60  # frames between enemy spawns
        self.powerup_spawn_timer = 0
        self.powerup_spawn_delay = 300  # frames between power-up spawns
        
        # Create stars for background
        for _ in range(100):
            self.stars.append(Star())
    
    def reset(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.score = 0
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
    
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
        
        # Spawn power-ups
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= self.powerup_spawn_delay:
            x = random.randint(0, SCREEN_WIDTH - 20)
            self.powerups.append(PowerUp(x, -20))
            self.powerup_spawn_timer = 0
        
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
        
        # Update power-ups
        for powerup in self.powerups[:]:
            if powerup.update():
                self.powerups.remove(powerup)
        
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
                        self.enemies.remove(enemy)
                    self.score += 100
        
        # Check player-enemy collisions
        for enemy in self.enemies[:]:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                self.player.health -= 20
                if self.player.health <= 0:
                    self.state = GAME_OVER
        
        # Check player-powerup collisions
        for powerup in self.powerups[:]:
            if (self.player.x < powerup.x + powerup.width and
                self.player.x + self.player.width > powerup.x and
                self.player.y < powerup.y + powerup.height and
                self.player.y + self.player.height > powerup.y):
                if powerup in self.powerups:
                    self.powerups.remove(powerup)
                self.player.activate_power_up()
                self.score += 50
    
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
        
        # Power-up indicator
        if self.player.power_up_active:
            time_left = self.player.power_up_duration - (pygame.time.get_ticks() - self.player.power_up_time) / 1000
            if time_left > 0:
                powerup_text = self.small_font.render(f"Power-Up: {time_left:.1f}s", True, BLUE)
                screen.blit(powerup_text, (20, 60))
    
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
            
            for powerup in self.powerups:
                powerup.draw()
            
            self.player.draw()
            
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
            
            for powerup in self.powerups:
                powerup.draw()
            
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
