import pygame
import random
import sys

# Constants
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
PLAYER_SPRITE = "images/fox.png"
PLAYER_SPRITE_2 = "images/fox2.png"
ENEMY_SPRITE_1 = "images/falcon.png"
ENEMY_SPRITE_2 = "images/falcon2.png"
ENEMY_SPRITE_3 = "images/falcon3.png"
ENEMY_SPRITE_4 = "images/falcon4.png"
FRIEND_SPRITE = "images/poison.png"
BACKGROUND_IMAGE = "images/R.jpg"
BACKGROUND_IMAGE_2 = "images/background2.jpg"
BACKGROUND_IMAGE_3 = "images/desert.jpg"
P_SPRITE_SCALE = 0.25
FRIENDS = 6
ENEMY_SPAWN = 400  # in milliseconds
FRIEND_SPAWN = 1250  # in milliseconds

# Initialize Pygame
pygame.init()

# Load Sounds
death_sound = pygame.mixer.Sound("sfx/lightning.wav")
pickup_sound = pygame.mixer.Sound("sfx/shortbeep.wav")
win_sound = pygame.mixer.Sound("sfx/startup.wav")

# Screen setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Content Warning")

# Load Sprites
player_image = pygame.image.load(PLAYER_SPRITE).convert_alpha()
player_image2 = pygame.image.load(PLAYER_SPRITE_2).convert_alpha()
enemy_image_1 = pygame.image.load(ENEMY_SPRITE_1).convert_alpha()
enemy_image_2 = pygame.image.load(ENEMY_SPRITE_2).convert_alpha()
enemy_image_3 = pygame.image.load(ENEMY_SPRITE_3).convert_alpha()
enemy_image_4 = pygame.image.load(ENEMY_SPRITE_4).convert_alpha()
friend_image = pygame.image.load(FRIEND_SPRITE).convert_alpha()

player_image = pygame.transform.scale(player_image, (
int(player_image.get_width() * P_SPRITE_SCALE), int(player_image.get_height() * P_SPRITE_SCALE)))
player_image2 = pygame.transform.scale(player_image2, (player_image.get_width(), player_image.get_height()))

# Load Backgrounds
background_1 = pygame.image.load(BACKGROUND_IMAGE).convert()
background_2 = pygame.image.load(BACKGROUND_IMAGE_2).convert()
background_3 = pygame.image.load(BACKGROUND_IMAGE_3).convert()

# Define sprite groups
all_sprites = pygame.sprite.Group()
enemies_list = pygame.sprite.Group()
friends_list = pygame.sprite.Group()

# Class for Flying Sprites
class FlyingSprite(pygame.sprite.Sprite):
    def __init__(self, image1, image2):
        super().__init__()
        self.image_list = [image1, image2]
        self.image_index = 0
        self.image = self.image_list[self.image_index]
        self.rect = self.image.get_rect()
        self.velocity = pygame.Vector2(0, 0)
        self.last_sprite_change = pygame.time.get_ticks()
        self.sprite_change_interval = 180

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_sprite_change > self.sprite_change_interval:
            self.image_index = (self.image_index + 1) % len(self.image_list)
            self.image = self.image_list[self.image_index]
            self.last_sprite_change = current_time

        self.rect.move_ip(self.velocity)
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH or self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()

# Class for Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_list = [player_image, player_image2]
        self.image_index = 0
        self.image = self.image_list[self.image_index]
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.velocity = pygame.Vector2(0, 0)
        self.last_sprite_change = pygame.time.get_ticks()
        self.sprite_change_interval = 500

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_sprite_change > self.sprite_change_interval:
            self.image_index = (self.image_index + 1) % len(self.image_list)
            self.image = self.image_list[self.image_index]
            self.last_sprite_change = current_time

        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = pygame.mouse.get_pos()

player = Player()
all_sprites.add(player)

# Backgrounds and enemies for each phase
backgrounds = [background_1, background_2, background_3]
enemy_images_sets = [
    [enemy_image_1, enemy_image_2],
    [enemy_image_3, enemy_image_4],
    [enemy_image_1, enemy_image_3]
]

current_phase = 0
background = backgrounds[current_phase]
enemy_images = enemy_images_sets[current_phase]

# Function to start a new phase
def start_new_phase():
    global current_phase, background, enemy_images, friends_left, start_time
    current_phase += 1
    if current_phase >= len(backgrounds):
        current_phase = len(backgrounds) - 1
    background = backgrounds[current_phase]
    enemy_images = enemy_images_sets[current_phase]
    friends_left = FRIENDS
    for sprite in enemies_list:
        sprite.kill()
    for sprite in friends_list:
        sprite.kill()
    pygame.time.set_timer(pygame.USEREVENT + 1, ENEMY_SPAWN)
    pygame.time.set_timer(pygame.USEREVENT + 2, FRIEND_SPAWN)
    start_time = pygame.time.get_ticks()

# Add enemy and friend functions
def add_enemy():
    enemy = FlyingSprite(enemy_images[0], enemy_images[1])
    placement = random.randint(1, 4)
    if placement == 1:
        enemy.rect.left = WINDOW_WIDTH
        enemy.rect.top = random.randint(0, WINDOW_HEIGHT - enemy.rect.height)
        enemy.velocity = pygame.Vector2(random.randint(-8, -1), 0)
    elif placement == 2:
        enemy.rect.right = 0
        enemy.rect.top = random.randint(0, WINDOW_HEIGHT - enemy.rect.height)
        enemy.velocity = pygame.Vector2(random.randint(1, 8), 0)
    elif placement == 3:
        enemy.rect.left = random.randint(0, WINDOW_WIDTH - enemy.rect.width)
        enemy.rect.bottom = WINDOW_HEIGHT
        enemy.velocity = pygame.Vector2(0, random.randint(-8, -1))
    else:
        enemy.rect.left = random.randint(0, WINDOW_WIDTH - enemy.rect.width)
        enemy.rect.top = 0
        enemy.velocity = pygame.Vector2(0, random.randint(1, 8))
    enemies_list.add(enemy)
    all_sprites.add(enemy)

def add_friend():
    friend = FlyingSprite(friend_image, friend_image)
    placement = random.randint(1, 4)
    if placement == 1:
        friend.rect.left = WINDOW_WIDTH
        friend.rect.top = random.randint(0, WINDOW_HEIGHT - friend.rect.height)
        friend.velocity = pygame.Vector2(random.randint(-8, -1), 0)
    elif placement == 2:
        friend.rect.right = 0
        friend.rect.top = random.randint(0, WINDOW_HEIGHT - friend.rect.height)
        friend.velocity = pygame.Vector2(random.randint(1, 8), 0)
    elif placement == 3:
        friend.rect.left = random.randint(0, WINDOW_WIDTH - friend.rect.width)
        friend.rect.bottom = WINDOW_HEIGHT
        friend.velocity = pygame.Vector2(0, random.randint(-8, -1))
    else:
        friend.rect.left = random.randint(0, WINDOW_WIDTH - friend.rect.width)
        friend.rect.top = 0
        friend.velocity = pygame.Vector2(0, random.randint(1, 8))
    friends_list.add(friend)
    all_sprites.add(friend)

# Timers
pygame.time.set_timer(pygame.USEREVENT + 1, ENEMY_SPAWN)
pygame.time.set_timer(pygame.USEREVENT + 2, FRIEND_SPAWN)

# Game variables
paused = False
player_down = False
success = False
friends_left = FRIENDS
total_score = 0
start_time = pygame.time.get_ticks()

# Main game loop
clock = pygame.time.Clock()
running = True

# Menu variables
menu_active = True
play_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 25, 100, 50)

# Menu loop
while menu_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Check if the play button was clicked
                if play_button_rect.collidepoint(event.pos):
                    menu_active = False
                    break

    # Carregar a imagem do menu
    menu_image = pygame.image.load("images/menu_image.jpg").convert_alpha()
    menu_image_rect = menu_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    # Clear the screen
    screen.fill((0, 0,0))

    # Draw the menu image
    screen.blit(menu_image, menu_image_rect)

    # Draw the menu elements
    font = pygame.font.SysFont("Kenny Pixel", 48)
    text_surface = font.render("Content Rescue", True, (255, 255, 255))

    text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))

    screen.blit(text_surface, text_rect)

    # No loop do menu
    font = pygame.font.SysFont("Kenny Pixel", 24)

    # Mensagem do parágrafo
    paragraph_text = [
        "Bem-vindo ao jogo Content rescue!",
        "Este é um jogo simples onde você controla um personagem",
        "e deve coletar os resíduos tóxicos enquanto evita os inimigos.",
        "Use o mouse para mover o personagem e pressione P para pausar o jogo.",
        "Clique no botão Play para começar!",
        "divirta-se!"
    ]

    # Coordenadas para o primeiro linha do parágrafo
    paragraph_x = WINDOW_WIDTH // 2
    paragraph_y = WINDOW_HEIGHT // 2+55

    # Espaçamento entre as linhas
    line_spacing = 30

    # Desenhe o parágrafo
    for line in paragraph_text:
        text_surface = font.render(line, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(paragraph_x, paragraph_y))
        screen.blit(text_surface, text_rect)
        paragraph_y += line_spacing

    pygame.draw.rect(screen, (255, 255, 255), play_button_rect)
    play_button_text = font.render("Play", True, (0, 0, 0))
    play_button_text_rect = play_button_text.get_rect(center=play_button_rect.center)
    screen.blit(play_button_text, play_button_text_rect)

    # Update the display
    pygame.display.flip()

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_p:
                paused = not paused
                if paused:
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                else:
                    pygame.time.set_timer(pygame.USEREVENT + 1, ENEMY_SPAWN)
                    pygame.time.set_timer(pygame.USEREVENT + 2, FRIEND_SPAWN)
            elif event.key == pygame.K_SPACE:  # Verificação para a tecla de espaço
                # Reinicie todas as variáveis do jogo para seus valores iniciais
                paused = False
                player_down = False
                success = False
                friends_left = FRIENDS
                total_score = 0
                start_time = pygame.time.get_ticks()
                current_phase = 0
                background = backgrounds[current_phase]
                enemy_images = enemy_images_sets[current_phase]
                all_sprites.empty()
                enemies_list.empty()
                friends_list.empty()
                player = Player()
                all_sprites.add(player)
                pygame.time.set_timer(pygame.USEREVENT + 1, ENEMY_SPAWN)
                pygame.time.set_timer(pygame.USEREVENT + 2, FRIEND_SPAWN)
        elif event.type == pygame.USEREVENT + 1:
            add_enemy()
        elif event.type == pygame.USEREVENT + 2:
            add_friend()
        elif event.type == pygame.MOUSEMOTION:
            player.rect.center = event.pos

    if not paused and not player_down:
        all_sprites.update()

        if pygame.sprite.spritecollideany(player, enemies_list):
            player_down = True
            player.kill()
            pygame.mixer.Sound.play(death_sound)

        friends_hit_list = pygame.sprite.spritecollide(player, friends_list, True)
        for _ in friends_hit_list:
            friends_left -= 1
            if friends_left < 0:
                friends_left = 0
            pygame.mixer.Sound.play(pickup_sound)

            if friends_left == 0 and not success:
                success = True
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                pygame.mixer.Sound.play(win_sound)
                end_time = pygame.time.get_ticks()
                elapsed_time_seconds = (end_time - start_time) / 1000
                total_score += 10 * elapsed_time_seconds

                if current_phase < len(backgrounds) - 1:
                    pygame.time.set_timer(pygame.USEREVENT + 3, 2000)  # Timer to start the next phase

        if success and current_phase < len(backgrounds) - 1:
            success = False
            start_new_phase()

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the background
    screen.blit(background, (0, 0))

    # Draw all sprites
    all_sprites.draw(screen)

    # Draw remaining friends count
    font = pygame.font.SysFont("Kenny Pixel", 18)
    text_surface = font.render(f"Residuos Toxicos restantes: {friends_left}", True, (255, 255, 255))
    screen.blit(text_surface, (30, 30))

    # Draw success message if applicable
    if success:
        font = pygame.font.SysFont("Kenny Pixel", 24)
        win_text_surface = font.render("Os resíduos foram expelidos bom trabalho!!", True, (0, 255, 0))
        win_text_rect = win_text_surface.get_rect(center=(WINDOW_WIDTH // 2, int(WINDOW_HEIGHT / 2 * 1.25)))
        screen.blit(win_text_surface, win_text_rect)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

    if player_down:
        running = False

# Calculate final score
if not success:
    end_time = pygame.time.get_ticks()
    elapsed_time_seconds = (end_time - start_time) / 1000
    total_score += 10 * elapsed_time_seconds

# Display final score
final_score_display = True
while final_score_display:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            final_score_display = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            final_score_display = False

    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("Kenny Pixel", 48)
    score_surface = font.render(f"Pontuação Final: {int(total_score)}", True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(score_surface, score_rect)
    pygame.display.flip()

pygame.quit()
sys.exit()

