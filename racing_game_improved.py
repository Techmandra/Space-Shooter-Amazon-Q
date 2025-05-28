import pygame
import random
import time
import sys
import os
import json
import math

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROAD_WIDTH = 400
LANE_WIDTH = ROAD_WIDTH // 3
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 100
TRAFFIC_WIDTH = 60
TRAFFIC_HEIGHT = 100
GAME_SPEED = 5
PLAYER_SPEED = 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Racing Game")
clock = pygame.time.Clock()

# Game states
START_MENU = 0
GAME_ACTIVE = 1
GAME_OVER = 2
GAME_PAUSED = 3

# Create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Function to create placeholder car images if they don't exist
def create_car_image(filename, color, width, height):
    if not os.path.exists(filename):
        # Create a simple car image
        car_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Car body
        pygame.draw.rect(car_surface, color, (0, 0, width, height), border_radius=10)
        
        # Windows
        pygame.draw.rect(car_surface, (50, 50, 50), (5, 15, width-10, 30), border_radius=5)
        pygame.draw.rect(car_surface, (50, 50, 50), (5, height-45, width-10, 30), border_radius=5)
        
        # Wheels
        wheel_color = (30, 30, 30)
        pygame.draw.rect(car_surface, wheel_color, (0, 10, 10, 25), border_radius=3)
        pygame.draw.rect(car_surface, wheel_color, (width-10, 10, 10, 25), border_radius=3)
        pygame.draw.rect(car_surface, wheel_color, (0, height-35, 10, 25), border_radius=3)
        pygame.draw.rect(car_surface, wheel_color, (width-10, height-35, 10, 25), border_radius=3)
        
        # Save the image
        pygame.image.save(car_surface, filename)
    
    return pygame.image.load(filename)

# Create and load car images
player_image = create_car_image('images/player_car.png', RED, PLAYER_WIDTH, PLAYER_HEIGHT)
traffic_image_blue = create_car_image('images/traffic_car_blue.png', BLUE, TRAFFIC_WIDTH, TRAFFIC_HEIGHT)
traffic_image_green = create_car_image('images/traffic_car_green.png', GREEN, TRAFFIC_WIDTH, TRAFFIC_HEIGHT)
traffic_image_yellow = create_car_image('images/traffic_car_yellow.png', YELLOW, TRAFFIC_WIDTH, TRAFFIC_HEIGHT)

# Traffic car images list
traffic_images = [traffic_image_blue, traffic_image_green, traffic_image_yellow]

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = PLAYER_SPEED
        self.image = player_image
        self.hit = False
        self.hit_time = 0
        self.hit_animation_duration = 1.0  # seconds
    
    def move(self, direction):
        if direction == "left" and self.x > (SCREEN_WIDTH - ROAD_WIDTH) // 2:
            self.x -= self.speed
        if direction == "right" and self.x < (SCREEN_WIDTH + ROAD_WIDTH) // 2 - self.width:
            self.x += self.speed
    
    def draw(self):
        if self.hit and time.time() - self.hit_time < self.hit_animation_duration:
            # Flash the car during hit animation
            if int((time.time() - self.hit_time) * 10) % 2 == 0:
                # Create a rotated version of the car for hit animation
                angle = 5 * math.sin((time.time() - self.hit_time) * 10)
                rotated_image = pygame.transform.rotate(self.image, angle)
                screen.blit(rotated_image, (self.x - (rotated_image.get_width() - self.width) // 2, 
                                           self.y - (rotated_image.get_height() - self.height) // 2))
            else:
                screen.blit(self.image, (self.x, self.y))
        else:
            screen.blit(self.image, (self.x, self.y))
            self.hit = False

class TrafficCar:
    def __init__(self):
        self.width = TRAFFIC_WIDTH
        self.height = TRAFFIC_HEIGHT
        # Randomly choose one of the three lanes
        lane = random.randint(0, 2)
        lane_center = (SCREEN_WIDTH - ROAD_WIDTH) // 2 + LANE_WIDTH * lane + LANE_WIDTH // 2
        self.x = lane_center - self.width // 2
        self.y = -self.height
        self.speed = GAME_SPEED
        self.image = random.choice(traffic_images)
    
    def update(self):
        self.y += self.speed
        return self.y > SCREEN_HEIGHT
    
    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Game:
    def __init__(self):
        self.state = START_MENU
        self.player = Player()
        self.traffic = []
        self.score = 0
        self.high_score = self.load_high_score()
        self.start_time = 0
        self.font = pygame.font.SysFont(None, 36)
        self.traffic_spawn_timer = 0
        self.difficulty_timer = 0
        self.difficulty_increase_interval = 10  # seconds
    
    def load_high_score(self):
        try:
            if os.path.exists('racing_high_scores.json'):
                with open('racing_high_scores.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open('racing_high_scores.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def reset(self):
        self.player = Player()
        self.traffic = []
        self.score = 0
        self.start_time = time.time()
        self.traffic_spawn_timer = 0
        self.difficulty_timer = 0
    
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
        if self.state != GAME_ACTIVE:
            return
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move("left")
        if keys[pygame.K_RIGHT]:
            self.player.move("right")
        
        # Increase difficulty over time
        current_time = time.time()
        if current_time - self.start_time > self.difficulty_timer + self.difficulty_increase_interval:
            global GAME_SPEED
            GAME_SPEED += 0.5
            self.difficulty_timer += self.difficulty_increase_interval
        
        # Spawn traffic
        self.traffic_spawn_timer += 1
        spawn_rate = max(30, 60 - int((current_time - self.start_time) / 30) * 5)  # Spawn faster as time goes on
        if self.traffic_spawn_timer >= spawn_rate:
            self.traffic.append(TrafficCar())
            self.traffic_spawn_timer = 0
        
        # Update traffic
        for car in self.traffic[:]:
            if car.update():
                self.traffic.remove(car)
        
        # Check for collisions
        for car in self.traffic:
            if (self.player.x < car.x + car.width - 10 and
                self.player.x + self.player.width - 10 > car.x and
                self.player.y < car.y + car.height - 10 and
                self.player.y + self.player.height - 10 > car.y):
                self.player.hit = True
                self.player.hit_time = time.time()
                self.state = GAME_OVER
                
                # Update high score
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
        
        # Update score (based on time survived)
        self.score = int(time.time() - self.start_time)
    
    def draw_road(self):
        # Draw road
        road_x = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        pygame.draw.rect(screen, GRAY, (road_x, 0, ROAD_WIDTH, SCREEN_HEIGHT))
        
        # Draw lane markings
        lane_marking_width = 10
        for i in range(1, 3):
            lane_x = road_x + i * LANE_WIDTH - lane_marking_width // 2
            
            # Draw dashed lines
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.rect(screen, WHITE, (lane_x, y, lane_marking_width, 20))
    
    def draw_start_menu(self):
        screen.fill(BLACK)
        
        title = self.font.render("TOP-DOWN RACING GAME", True, WHITE)
        instructions1 = self.font.render("Use LEFT/RIGHT arrow keys to move", True, WHITE)
        instructions2 = self.font.render("Avoid oncoming traffic", True, WHITE)
        instructions3 = self.font.render("Press ENTER to start", True, YELLOW)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, GREEN)
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(instructions1, (SCREEN_WIDTH // 2 - instructions1.get_width() // 2, 250))
        screen.blit(instructions2, (SCREEN_WIDTH // 2 - instructions2.get_width() // 2, 300))
        screen.blit(instructions3, (SCREEN_WIDTH // 2 - instructions3.get_width() // 2, 400))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 450))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, GREEN)
        restart_text = self.font.render("Press ENTER to return to menu", True, YELLOW)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 300))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))
    
    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        resume_text = self.font.render("Press P to resume", True, YELLOW)
        
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 300))
    
    def draw(self):
        if self.state == START_MENU:
            self.draw_start_menu()
        elif self.state == GAME_ACTIVE or self.state == GAME_PAUSED:
            # Draw background
            screen.fill(BLACK)
            
            # Draw road and elements
            self.draw_road()
            
            # Draw traffic
            for car in self.traffic:
                car.draw()
            
            # Draw player
            self.player.draw()
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, GREEN)
            screen.blit(score_text, (20, 20))
            screen.blit(high_score_text, (20, 60))
            
            # Draw pause menu if paused
            if self.state == GAME_PAUSED:
                self.draw_pause_menu()
        
        elif self.state == GAME_OVER:
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
