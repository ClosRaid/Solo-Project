import pygame
import os

from random import randrange



pygame.init()
#Базовые настройки
WIDTH, HEIGHT = 1280, 720
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
#Активные персонажи
resource_path = r'C:\Users\kenue\OneDrive\Рабочий стол\дудл джамп'
player_image_path = os.path.join(resource_path, 'player.png')
player_img = pygame.image.load(player_image_path).convert_alpha()
ghost_image_path = os.path.join(resource_path,'ghost.png')
ghost_img = pygame.image.load(ghost_image_path).convert_alpha()
ghosts = pygame.sprite.Group()
ghost_spawn_chance = 15
#задний фон
background = r'C:\Users\kenue\OneDrive\Рабочий стол\дудл джамп\background.jpg'
background = pygame.image.load(background).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
bg_y = 0

running = True

#игровые настройки
PLAYER_SIZE = 30
GRAVITY = 0.5
JUMP_POWER = -20  # импульс вверх
SPEED_X = 15
PLATFORM_HEIGHT = 20
PLATFORM_WIDTH = 100
MAX_PLATFORMS = 1000 #Максимальное кол-во платформ существующих
platform_counter = 0

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img.copy()
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.vel_y = 0
        self.mass = 1

    def update(self):
        global score
        global scroll

        self.prev_rect = self.rect.copy()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rect.x -= SPEED_X
        if keys[pygame.K_d]:
            self.rect.x += SPEED_X

        # Гравитация
        self.vel_y += GRAVITY * self.mass
        self.rect.y += self.vel_y

        # Ограничение по экрану
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

        #получение очков при подьёме
        if self.vel_y < 0:
            score += scroll

        scroll = 0
        if player.rect.top < HEIGHT // 3 and player.vel_y < 0:
            scroll = -player.vel_y
            player.rect.y += scroll

        for platform in platforms:
            platform.rect.y += scroll

        for ghost in ghosts:
            ghost.rect.y += scroll


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass
        # self.rect.y += 4
        # if self.rect.top > HEIGHT:
        #     self.kill()

def generate_new_platforms():
    global last_platform_y, platform_counter
    plat_x = randrange(0, WIDTH - PLATFORM_WIDTH)
    plat_y = last_platform_y - randrange(50, 150)

    new_plat = Platform(plat_x, plat_y)
    platforms.add(new_plat)
    platform_counter += 1
    if platform_counter % 10 == 0:
        if randrange(100) < ghost_spawn_chance:
            ghost = Ghost(plat_x + PLATFORM_WIDTH // 2, plat_y - 40)
            ghosts.add(ghost)
            all_sprites.add(ghost)
    last_platform_y = plat_y

def reset_game():
    global player, platforms, last_platform_y, score, platform_counter

    player = Player()
    all_sprites.empty()
    all_sprites.add(player)

    platforms.empty()
    ghosts.empty()
    last_platform_y = HEIGHT - PLATFORM_HEIGHT
    platform_counter = 0
    for _ in range(MAX_PLATFORMS):
        generate_new_platforms()

    score = 0
class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ghost_img.copy()
        self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        pass


# Инициализация игры
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
score = 0
last_platform_y = HEIGHT - PLATFORM_HEIGHT  # глобальная переменная для генерации платформ
reset_game()

while running:
    clock.tick(FPS)
    if pygame.sprite.spritecollide(player,ghosts,False):
        reset_game()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    all_sprites.update()
    platforms.update()
    if len(platforms) < MAX_PLATFORMS:
        generate_new_platforms()
    # Отрисовка фона
    screen.blit(background, (0, 0))
    bg_y += 2
    if bg_y >= HEIGHT:
        bg_y = 0
    screen.blit(background, (0, bg_y))
    screen.blit(background, (0, bg_y - HEIGHT))
    # Проверка проигрыша и перезапуск игры
    if player.rect.top > HEIGHT:
        reset_game()

    # Физическое взаимодействие с платформами
    hit_list = pygame.sprite.spritecollide(player, platforms, False)
    for platform in hit_list:
        if player.vel_y > 0 and player.rect.bottom <= platform.rect.top + player.vel_y:
            player.rect.bottom = platform.rect.top
            player.vel_y = JUMP_POWER  # импульс вверх

    all_sprites.draw(screen)
    platforms.draw(screen)

    font = pygame.font.SysFont(None, 36)
    text_score = font.render(f'Высота: {int(score)}', True, WHITE)
    screen.blit(text_score, (10, 10))


    pygame.display.flip()

pygame.quit()