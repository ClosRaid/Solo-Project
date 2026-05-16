import pygame
import os
from random import randrange
import pydroid



pygame.init()
#Базовые настройки
WIDTH, HEIGHT = 1280, 720
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
#Активные персонажи
resource_path = "/storage/emulated/0/Download/doodle_jump"
player_image_path = os.path.join(resource_path, "player.png")
ghost_image_path = os.path.join(resource_path, "ghost.png")
player_img = pygame.image.load(player_image_path).convert_alpha()
ghost_img = pygame.image.load(ghost_image_path).convert_alpha()
ghosts = pygame.sprite.Group()
ghost_spawn_chance = 15
#задний фон
background = os.path.join(resource_path, "background.jpg")
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
MAX_PLATFORMS = 10000 #Максимальное кол-во платформ существующих
platform_counter = 0
non_active_chance = 10

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img.copy()
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, 50))
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
        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = WIDTH

        #получение очков при подьёме
        if self.vel_y < 0:
            score += scroll

        scroll = 0
        if player.rect.top < HEIGHT // 3 and player.vel_y < 0:
            scroll = -player.vel_y
            player.rect.y += scroll

        for platform1 in platforms:
            platform1.rect.y += scroll

        for platform1 in platforms:
            if platform1.rect.top > HEIGHT:
                platform1.kill()

        for ghost in ghosts:
            ghost.rect.y += scroll


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_type="normal"):
        super().__init__()

        self.platform_type = platform_type
        self.used = False
        self.break_timer = 15
        self.is_active = True
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.update_color()

    def update_color(self):
        if self.platform_type == "normal":
            color = (0, 255, 0)

        elif self.platform_type == "break":
            color = (255, 165, 0)

        elif self.platform_type == "one_jump":
            color = (255, 0, 0)

        self.image.fill(color)
        pygame.draw.rect(self.image, (0, 0, 0), self.image.get_rect(), 2)

    def update(self):
        if self.platform_type == "break" and self.used:
            self.break_timer -= 1

            self.rect.y += 8

            if self.break_timer <= 0:
                self.kill()

def generate_new_platforms():
    global last_platform_y, platform_counter

    plat_x = randrange(5, WIDTH - PLATFORM_WIDTH)
    plat_y = last_platform_y - randrange(50, 150)

    chance = randrange(100)

    if chance < 15:
        platform_type = "break"

    elif chance < 30:
        platform_type = "one_jump"

    else:
        platform_type = "normal"

    new_plat = Platform(plat_x, plat_y, platform_type)

    platforms.add(new_plat)
    all_sprites.add(new_plat)

    platform_counter += 1

    # Случайное появление призраков
    if randrange(100) < 8: #шанс появления призрака

        ghost_x = randrange(100, WIDTH - 100)
        ghost_y = plat_y - randrange(50, 150)

        ghost = Ghost(ghost_x, ghost_y)

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

        self.speed_x = randrange(-3, 4)

        if self.speed_x == 0:
            self.speed_x = 2

    def update(self):

        self.rect.x += self.speed_x

        # Отскок от стен
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x *= -1


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
    # перезапуск игры после проигрыша
    if player.rect.top > HEIGHT:
        reset_game()

    # Физическое взаимодействие с платформами
    hit_list = pygame.sprite.spritecollide(player, platforms, False)

    for platform in hit_list:

        if (
                player.vel_y > 0
                and player.prev_rect.bottom <= platform.rect.top
        ):

            # Одноразовая платформа уже использована
            if platform.platform_type == "one_jump" and platform.used:
                continue

            player.rect.bottom = platform.rect.top
            player.vel_y = JUMP_POWER

            # Разваливающаяся платформа
            if platform.platform_type == "break":
                platform.used = True

            # Одноразовая платформа
            elif platform.platform_type == "one_jump":
                platform.used = True
                platform.image.set_alpha(120)
                platform.is_active = False
    #рисуем игрока
    screen.blit(player.image, player.rect)
    if player.rect.right > WIDTH:
        wrap_rect = player.rect.copy()
        wrap_rect.x -= WIDTH
        screen.blit(player.image,wrap_rect)
    if player.rect.left < 0:
        wrap_rect = player.rect.copy()
        wrap_rect.x += WIDTH
        screen.blit(player.image,wrap_rect)
    platforms.draw(screen)
    ghosts.draw(screen)
    font = pygame.font.SysFont(None, 36)
    text_score = font.render(f'Высота: {int(score)}', True, WHITE)
    screen.blit(text_score, (10, 10))


    pygame.display.flip()

pygame.quit()