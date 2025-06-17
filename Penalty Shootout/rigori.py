import pygame
import sys
import random
import math
from pygame import gfxdraw

pygame.init()
pygame.mixer.init()

# Costanti del gioco
WIDTH, HEIGHT = 800, 600
FPS = 60
GOAL_WIDTH = 500
GOAL_HEIGHT = 300

# Colori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
GRAY = (50, 50, 50)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 255)
CHIPS_COLORS = [(255, 50, 50), (50, 50, 255), (50, 255, 50), (255, 255, 50), (255, 50, 255)]

# Font
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)
title_font = pygame.font.SysFont("Arial", 64, bold=True)
money_font = pygame.font.SysFont("Arial", 32, bold=True)

class GameAssets:
    def __init__(self):
        self.background = self._load_image("background", (WIDTH, HEIGHT))
        self.ball = self._load_image("ball", None, 0.15)
        self.keeper = self._load_image("keeper", None, 0.6)
        self.chip = self._load_image("chip", None, 0.1)
        
        self.kick_sound = self._load_sound("kick")
        self.goal_sound = self._load_sound("goal")
        self.save_sound = self._load_sound("save")
        self.coin_sound = self._load_sound("coin")
        self.win_sound = self._load_sound("win")
        self.lose_sound = self._load_sound("lose")
        
    def _load_image(self, name, size=None, scale=None):
        try:
            img = pygame.image.load(f"{name}.png").convert_alpha()
            if scale:
                img = pygame.transform.smoothscale(img, (int(img.get_width() * scale), (int(img.get_height() * scale))))
            elif size:
                img = pygame.transform.smoothscale(img, size)
            return img
        except:
            print(f"Image {name} not found, creating placeholder")
            surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(surf, RED if name == "ball" else BLUE, (50, 50), 50)
            return surf
    
    def _load_sound(self, name):
        try:
            return pygame.mixer.Sound(f"{name}.wav")
        except:
            print(f"Sound {name} not found, using silent sound")
            return pygame.mixer.Sound(buffer=bytearray(100))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, border_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=10)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Chip:
    def __init__(self, x, y, value, color_index):
        self.x = x
        self.y = y
        self.value = value
        self.color_index = color_index
        self.radius = 30
        self.is_selected = False
        self.target_y = y
    
    def draw(self, surface, assets):
        color = CHIPS_COLORS[self.color_index % len(CHIPS_COLORS)]
        
        pygame.draw.circle(surface, (50, 50, 50), (self.x, self.y + 5), self.radius)
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.radius, 2)
        pygame.draw.circle(surface, (255, 255, 255, 100), (self.x-10, self.y-10), 10)
        
        text = font.render(str(self.value), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)
        
        if self.is_selected:
            pygame.draw.circle(surface, GOLD, (self.x, self.y), self.radius + 5, 3)
    
    def check_click(self, pos):
        distance = math.hypot(pos[0] - self.x, pos[1] - self.y)
        return distance <= self.radius

class MainMenu:
    def __init__(self):
        self.title = title_font.render("Ultimate Penalty Casino", True, GOLD)
        self.title_rect = self.title.get_rect(center=(WIDTH//2, HEIGHT//4))
        
        self.subtitle = font.render("Scommetti e segna per vincere!", True, WHITE)
        self.subtitle_rect = self.subtitle.get_rect(center=(WIDTH//2, HEIGHT//4 + 70))
        
        self.play_button = Button(WIDTH//2 - 150, HEIGHT//2, 300, 60, 
                                "GIOCA", GREEN, (0, 200, 0), BLACK, GOLD)
        self.exit_button = Button(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60, 
                                 "ESCI", RED, (200, 0, 0), WHITE, GOLD)
        self.particles = []
    
    def add_particle(self):
        x = random.randint(0, WIDTH)
        y = HEIGHT
        speed = random.uniform(2, 5)
        size = random.randint(2, 5)
        color = random.choice([GOLD, RED, GREEN, BLUE, PURPLE])
        self.particles.append([x, y, speed, size, color])
    
    def update_particles(self):
        for p in self.particles[:]:
            p[1] -= p[2]
            if p[1] < 0:
                self.particles.remove(p)
        
        if random.random() < 0.1:
            self.add_particle()
    
    def draw_particles(self, surface):
        for p in self.particles:
            pygame.draw.circle(surface, p[4], (int(p[0]), int(p[1])), p[3])
    
    def draw(self, surface):
        # Sfondo con effetto gradiente
        for y in range(HEIGHT):
            color = (0, max(0, min(50, y//12)), 0)
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))
        
        self.draw_particles(surface)
        surface.blit(self.title, self.title_rect)
        surface.blit(self.subtitle, self.subtitle_rect)
        
        self.play_button.draw(surface)
        self.exit_button.draw(surface)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            mouse_pos = pygame.mouse.get_pos()
            self.play_button.check_hover(mouse_pos)
            self.exit_button.check_hover(mouse_pos)
            
            if self.play_button.is_clicked(mouse_pos, event):
                return "betting_screen"
            elif self.exit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()
        
        self.update_particles()
        return None

class BettingScreen:
    def __init__(self, balance=1600):
        self.balance = balance
        self.current_bet = 0
        self.selected_chip = None
        
        self.chips = [
            Chip(WIDTH//2 - 120, HEIGHT - 100, 10, 0),
            Chip(WIDTH//2 - 60, HEIGHT - 100, 25, 1),
            Chip(WIDTH//2, HEIGHT - 100, 50, 2),
            Chip(WIDTH//2 + 60, HEIGHT - 100, 100, 3),
            Chip(WIDTH//2 + 120, HEIGHT - 100, 500, 4)
        ]
        
        self.bet_button = Button(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50, 
                                "PUNTA", GREEN, (0, 200, 0), BLACK)
        self.back_button = Button(20, HEIGHT - 70, 100, 50, 
                                "INDIETRO", RED, (200, 0, 0))
        
        self.bet_chips = []
        self.bet_text = font.render("Scegli la tua puntata", True, WHITE)
        self.bet_text_rect = self.bet_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.confetti = []
    
    def draw_balance(self, surface):
        balance_text = money_font.render(f"BILANCIO: ${self.balance}", True, GOLD)
        balance_rect = balance_text.get_rect(topleft=(20, 20))
        
        bet_text = money_font.render(f"PUNTATA: ${self.current_bet}", True, GREEN if self.current_bet > 0 else RED)
        bet_rect = bet_text.get_rect(topright=(WIDTH - 20, 20))
        
        pygame.draw.rect(surface, BLACK, balance_rect.inflate(20, 10), border_radius=5)
        pygame.draw.rect(surface, GOLD, balance_rect.inflate(20, 10), 2, border_radius=5)
        pygame.draw.rect(surface, BLACK, bet_rect.inflate(20, 10), border_radius=5)
        pygame.draw.rect(surface, GREEN if self.current_bet > 0 else RED, bet_rect.inflate(20, 10), 2, border_radius=5)
        
        surface.blit(balance_text, balance_rect)
        surface.blit(bet_text, bet_rect)
    
    def draw(self, surface, assets):
        surface.fill(BLACK)
        self.draw_balance(surface)
        
        for chip in self.chips:
            chip.draw(surface, assets)
        
        for i, chip in enumerate(self.bet_chips):
            chip.y = HEIGHT//2 - 20 - (i * 5)
            chip.draw(surface, assets)
        
        surface.blit(self.bet_text, self.bet_text_rect)
        self.bet_button.draw(surface)
        self.back_button.draw(surface)
        
        for c in self.confetti:
            pygame.draw.rect(surface, c[2], (c[0], c[1], 5, 5))
    
    def update_confetti(self):
        for c in self.confetti[:]:
            c[0] += c[3]
            c[1] += c[4]
            c[4] += 0.1
            if c[1] > HEIGHT:
                self.confetti.remove(c)
    
    def add_confetti(self, x, y):
        for _ in range(20):
            color = random.choice([RED, GREEN, BLUE, GOLD, PURPLE, WHITE])
            self.confetti.append([x, y, color, random.uniform(-2, 2), random.uniform(-5, 0)])
    
    def handle_events(self, assets):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ("quit", 0)
            
            mouse_pos = pygame.mouse.get_pos()
            self.bet_button.check_hover(mouse_pos)
            self.back_button.check_hover(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for chip in self.chips:
                    if chip.check_click(mouse_pos):
                        if self.balance >= chip.value:
                            self.current_bet += chip.value
                            self.balance -= chip.value
                            new_chip = Chip(WIDTH//2, HEIGHT//2, chip.value, chip.color_index)
                            new_chip.is_selected = True
                            self.bet_chips.append(new_chip)
                            assets.coin_sound.play()
                        break
                
                if self.bet_button.is_clicked(mouse_pos, event) and self.current_bet > 0:
                    self.add_confetti(WIDTH//2, HEIGHT//2)
                    assets.coin_sound.play()
                    return ("start_game", self.current_bet)
                
                if self.back_button.is_clicked(mouse_pos, event):
                    self.balance += self.current_bet
                    return ("back", self.balance)
        
        self.update_confetti()
        return (None, 0)

class PenaltyGame:
    def __init__(self, assets, balance, bet_amount):
        self.assets = assets
        self.balance = balance
        self.bet_amount = bet_amount
        self.reset_game()
        
        self.target_positions = [
            (WIDTH//2 - 200, HEIGHT//2 - 120),  # Alto a sinistra
            (WIDTH//2 + 200, HEIGHT//2 - 120),  # Alto a destra
            (WIDTH//2 - 200, HEIGHT//2 + 80),   # Basso sinistra
            (WIDTH//2 + 200, HEIGHT//2 + 80)    # Basso destra
        ]
        
        # Area della porta (invisibile, usata solo per collisioni)
        self.goal_rect = pygame.Rect(
            WIDTH//2 - GOAL_WIDTH//2, 
            HEIGHT//2 - GOAL_HEIGHT//2, 
            GOAL_WIDTH, 
            GOAL_HEIGHT
        )
        
        self.goal_multiplier = 1.5  # Moltiplicatore per il gol
        self.penalty_multiplier = 5  # Moltiplicatore per la parata (perdita)
        self.particles = []
        self.win_effects = []
        self.cash_out_button = Button(WIDTH//2 - 100, HEIGHT - 70, 200, 50, 
                                     "RITIRA", GREEN, (0, 200, 0), BLACK)
        self.game_over = False
    
    def reset_game(self):
        self.ball_pos = [WIDTH//2, HEIGHT - 100]
        self.ball_target = None
        self.ball_moving = False
        self.ball_speed = 20
        
        self.keeper_rect = self.assets.keeper.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.keeper_dive_target = None
        self.keeper_moving = False
        
        self.selected_target = None
        self.result_text = ""
        self.result_details = ""
        self.game_active = True
    
    def reset_shot(self):
        self.ball_pos = [WIDTH//2, HEIGHT - 100]
        self.ball_target = None
        self.ball_moving = False
        self.result_text = ""
        self.result_details = ""
        self.keeper_rect.center = (WIDTH//2, HEIGHT//2)
        self.keeper_moving = False
    
    def reset_keeper(self):
        # 95% di probabilità che il portiere si muova, 5% che resti fermo
        if random.random() < 0.95:
            directions = ["left", "right"]
            direction = random.choice(directions)
            
            if direction == "left":
                self.keeper_dive_target = (self.keeper_rect.centerx - 150, self.keeper_rect.centery)
            else:
                self.keeper_dive_target = (self.keeper_rect.centerx + 150, self.keeper_rect.centery)
        else:
            self.keeper_dive_target = self.keeper_rect.center
        
        self.keeper_moving = True
    
    def move_keeper(self):
        if self.keeper_rect.center != self.keeper_dive_target:
            dx = self.keeper_dive_target[0] - self.keeper_rect.centerx
            dy = self.keeper_dive_target[1] - self.keeper_rect.centery
            dist = math.hypot(dx, dy)
            
            if dist > 2:
                speed = 8 if dist > 50 else 4
                self.keeper_rect.centerx += int(dx / dist * speed)
                self.keeper_rect.centery += int(dy / dist * speed)
            else:
                self.keeper_moving = False
    
    def move_ball(self):
        if self.ball_target:
            dx = self.ball_target[0] - self.ball_pos[0]
            dy = self.ball_target[1] - self.ball_pos[1]
            dist = math.hypot(dx, dy)
            
            if dist > self.ball_speed:
                self.ball_pos[0] += dx / dist * self.ball_speed
                self.ball_pos[1] += dy / dist * self.ball_speed
                
                if random.random() < 0.3:
                    self.particles.append([
                        self.ball_pos[0] + random.randint(-5, 5),
                        self.ball_pos[1] + random.randint(-5, 5),
                        random.randint(2, 5),
                        random.choice([RED, WHITE, GOLD])
                    ])
            else:
                self.ball_pos[0], self.ball_pos[1] = self.ball_target
                self.ball_moving = False
                self.check_shot_result()
    
    def update_particles(self):
        for p in self.particles[:]:
            p[1] += 2
            p[2] -= 0.1
            if p[2] <= 0:
                self.particles.remove(p)
    
    def add_win_effect(self, amount):
        x = random.randint(WIDTH//2 - 100, WIDTH//2 + 100)
        y = random.randint(HEIGHT//2 - 50, HEIGHT//2 + 50)
        self.win_effects.append({
            "text": f"+${amount}",
            "x": x,
            "y": y,
            "alpha": 255,
            "color": GOLD
        })
    
    def update_win_effects(self):
        for effect in self.win_effects[:]:
            effect["y"] -= 1
            effect["alpha"] -= 3
            if effect["alpha"] <= 0:
                self.win_effects.remove(effect)
    
    def check_shot_result(self):
        ball_rect = self.assets.ball.get_rect(center=self.ball_pos)
        keeper_catch_rect = self.keeper_rect.inflate(-30, -30)
        
        if ball_rect.colliderect(keeper_catch_rect):
            self.result_text = "PARATA!"
            penalty_amount = int(self.bet_amount * self.penalty_multiplier)
            self.result_details = f"Hai perso ${penalty_amount}!"
            self.balance -= penalty_amount
            self.assets.save_sound.play()
            self.assets.lose_sound.play()
        else:
            self.result_text = "GOOOOL!"
            win_amount = int(self.bet_amount * self.goal_multiplier)
            self.balance += win_amount
            self.result_details = f"Moltiplicatore: x{self.goal_multiplier} - Vinci ${win_amount}!"
            self.assets.goal_sound.play()
            self.assets.win_sound.play()
            self.add_win_effect(win_amount)
        
        if self.balance <= 0:
            self.game_over = True
    
    def draw_targets(self, surface):
        for i, pos in enumerate(self.target_positions):
            target_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(target_surf, (255, 255, 255, 50), (30, 30), 30)
            pygame.draw.circle(target_surf, WHITE, (30, 30), 30, 2)
            
            if self.selected_target == i:
                pygame.draw.circle(target_surf, (255, 215, 0, 150), (30, 30), 35, 5)
            
            surface.blit(target_surf, (pos[0]-30, pos[1]-30))
    
    def draw_particles(self, surface):
        for p in self.particles:
            pygame.draw.circle(surface, p[3], (int(p[0]), int(p[1])), int(p[2]))
    
    def draw_win_effects(self, surface):
        for effect in self.win_effects:
            text_surf = font.render(effect["text"], True, effect["color"])
            text_surf.set_alpha(effect["alpha"])
            surface.blit(text_surf, (effect["x"], effect["y"]))
    
    def draw(self, surface):
        surface.blit(self.assets.background, (0, 0))
        
        if not self.ball_moving and not self.result_text and self.game_active and not self.game_over:
            self.draw_targets(surface)
        
        surface.blit(self.assets.keeper, self.keeper_rect)
        surface.blit(self.assets.ball, self.assets.ball.get_rect(center=self.ball_pos))
        self.draw_particles(surface)
        
        balance_text = font.render(f"Saldo: ${self.balance}", True, GOLD)
        surface.blit(balance_text, (20, 20))
        
        bet_text = font.render(f"Puntata: ${self.bet_amount}", True, GREEN)
        surface.blit(bet_text, (20, 50))
        
        if self.result_text:
            color = GOLD if "GOOOOL" in self.result_text else RED
            result_surface = big_font.render(self.result_text, True, color)
            surface.blit(result_surface, result_surface.get_rect(center=(WIDTH//2, 50)))
            
            if self.result_details:
                details_surface = font.render(self.result_details, True, WHITE)
                surface.blit(details_surface, details_surface.get_rect(center=(WIDTH//2, 100)))
            
            if not self.game_over:
                next_shot_text = font.render("Premi un tasto per il prossimo tiro", True, WHITE)
                surface.blit(next_shot_text, next_shot_text.get_rect(center=(WIDTH//2, HEIGHT - 100)))
        
        if self.game_over:
            game_over_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            game_over_surf.fill((0, 0, 0, 200))
            surface.blit(game_over_surf, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            surface.blit(game_over_text, game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
            
            no_money_text = font.render("Non hai più soldi per giocare", True, WHITE)
            surface.blit(no_money_text, no_money_text.get_rect(center=(WIDTH//2, HEIGHT//2)))
            
            return_text = font.render("Premi un tasto per tornare al menu", True, WHITE)
            surface.blit(return_text, return_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))
        elif self.game_active:
            self.cash_out_button.draw(surface)
        
        self.draw_win_effects(surface)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            mouse_pos = pygame.mouse.get_pos()
            if not self.game_over:
                self.cash_out_button.check_hover(mouse_pos)
            
            if event.type == pygame.KEYDOWN:
                if self.result_text and not self.game_over:
                    self.reset_shot()
                    return "continue"
                elif self.game_over:
                    return "menu"
            
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if self.cash_out_button.is_clicked(mouse_pos, event) and self.game_active:
                    return "cash_out"
                
                if not self.ball_moving and not self.result_text and self.game_active:
                    for i, pos in enumerate(self.target_positions):
                        if math.hypot(event.pos[0] - pos[0], event.pos[1] - pos[1]) < 30:
                            self.selected_target = i
                            self.ball_target = pos
                            self.ball_moving = True
                            self.reset_keeper()
                            self.assets.kick_sound.play()
                            return "shot"
        
        return None
    
    def update(self):
        if self.ball_moving:
            self.move_ball()
        
        if self.keeper_moving:
            self.move_keeper()
        
        self.update_particles()
        self.update_win_effects()

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ultimate Penalty Casino")
    clock = pygame.time.Clock()
    
    assets = GameAssets()
    
    main_menu = MainMenu()
    betting_screen = None
    game = None
    
    current_screen = "main_menu"
    balance = 1600
    running = True
    
    while running:
        if current_screen == "main_menu":
            action = main_menu.handle_events()
            if action == "betting_screen":
                current_screen = "betting_screen"
                betting_screen = BettingScreen(balance)
        
        elif current_screen == "betting_screen":
            action, value = betting_screen.handle_events(assets)
            if action == "start_game":
                current_screen = "game"
                game = PenaltyGame(assets, betting_screen.balance, value)
            elif action == "back":
                current_screen = "main_menu"
            elif action == "quit":
                running = False
        
        elif current_screen == "game":
            action = game.handle_events()
            if action == "cash_out":
                balance = game.balance
                current_screen = "betting_screen"
                betting_screen = BettingScreen(balance)
            elif action == "menu":
                balance = game.balance
                current_screen = "main_menu"
            elif action == "quit":
                running = False
        
        if current_screen == "main_menu":
            main_menu.draw(screen)
        elif current_screen == "betting_screen":
            betting_screen.draw(screen, assets)
        elif current_screen == "game":
            game.update()
            game.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

main()