import pygame
import random
import time
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROAD_WIDTH = 400
LANE_WIDTH = ROAD_WIDTH // 3
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100
TRAFFIC_WIDTH = 50
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

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = PLAYER_SPEED
        self.color = RED
    
    def move(self, direction):
        if direction == "left" and self.x > (SCREEN_WIDTH - ROAD_WIDTH) // 2:
            self.x -= self.speed
        if direction == "right" and self.x < (SCREEN_WIDTH + ROAD_WIDTH) // 2 - self.width:
            self.x += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

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
        self.color = BLUE
    
    def update(self):
        self.y += self.speed
        return self.y > SCREEN_HEIGHT
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        self.state = START_MENU
        self.player = Player()
        self.traffic = []
        self.score = 0
        self.start_time = 0
        self.font = pygame.font.SysFont(None, 36)
        self.traffic_spawn_timer = 0
    
    def reset(self):
        self.player = Player()
        self.traffic = []
        self.score = 0
        self.start_time = time.time()
        self.traffic_spawn_timer = 0
    
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
        
        # Spawn traffic
        self.traffic_spawn_timer += 1
        if self.traffic_spawn_timer >= 60:  # Spawn every 60 frames (about 1 second)
            self.traffic.append(TrafficCar())
            self.traffic_spawn_timer = 0
        
        # Update traffic
        for car in self.traffic[:]:
            if car.update():
                self.traffic.remove(car)
        
        # Check for collisions
        for car in self.traffic:
            if (self.player.x < car.x + car.width and
                self.player.x + self.player.width > car.x and
                self.player.y < car.y + car.height and
                self.player.y + self.player.height > car.y):
                self.state = GAME_OVER
        
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
        
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(instructions1, (SCREEN_WIDTH // 2 - instructions1.get_width() // 2, 250))
        screen.blit(instructions2, (SCREEN_WIDTH // 2 - instructions2.get_width() // 2, 300))
        screen.blit(instructions3, (SCREEN_WIDTH // 2 - instructions3.get_width() // 2, 400))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press ENTER to return to menu", True, YELLOW)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
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
            screen.blit(score_text, (20, 20))
            
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
