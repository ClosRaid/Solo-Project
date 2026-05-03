from collections import deque
import cv2
import pygame
import os
import threading
from random import randrange
from pygame import surfarray
import time

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
video_path = r'C:\Users\kenue\OneDrive\Рабочий стол\дудл джамп\background_score_1500.mp4'
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise FileNotFoundError(f"Не удалось открыть видео: {video_path}")
show_video = True
frame_queue = deque(maxlen=2)
stop_thread = False
def video_reader():
    target_fps = 30
    delay = 1 / target_fps
    while not stop_thread:
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
        # Преобразование и изменение размера
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame_queue.append(frame)
        if len(frame_queue) < frame_queue.maxlen:
            frame_queue.append(frame)
        elapsed = time.time() - start_time
        if elapsed < delay:
            time.sleep(delay-elapsed)

thread = threading.Thread(target=video_reader, daemon=True)
thread.start()
running = True


PLAYER_SIZE = 30
GRAVITY = 0.5
JUMP_POWER = -15  # импульс вверх
SPEED_X = 15
PLATFORM_HEIGHT = 20
PLATFORM_WIDTH = 100
MAX_PLATFORMS = 1000 #Максимальное кол-во платформ существующих

def Video_reader():
    while not stop_thread:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame_queue.append(frame)

        time.sleep(1/30)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img.copy()
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.vel_y = 0
        self.mass = 1

    def update(self):
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

        if player.rect.top < HEIGHT // 3 and player.vel_y < 0:
            scroll = -player.vel_y
            player.rect.y += scroll
        for platform in platforms:
            platform.rect.y +- scroll

        for ghost in ghosts:
            ghost.rect.y += scroll
        score += scroll

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass
        # self.rect.y += 4
        # if self.rect.top > HEIGHT:
        #     self.kill()

def generate_new_platforms():
    global last_platform_y
    plat_x = randrange(0, WIDTH - PLATFORM_WIDTH)
    plat_y = last_platform_y - randrange(50, 150)

    new_plat = Platform(plat_x, plat_y)
    platforms.add(new_plat)

    last_platform_y = plat_y

def reset_game():
    global player, platforms, last_platform_y, score

    player = Player()
    all_sprites.empty()
    all_sprites.add(player)

    platforms.empty()
    last_platform_y = HEIGHT - PLATFORM_HEIGHT
    for _ in range(MAX_PLATFORMS):
        generate_new_platforms()

    score = 0

# Инициализация игры
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
score = 0
last_platform_y = HEIGHT - PLATFORM_HEIGHT  # глобальная переменная для генерации платформ
reset_game()

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    all_sprites.update()
    platforms.update()
    if len(platforms) < MAX_PLATFORMS:
        generate_new_platforms()
        # Отрисовка видео или обычного фона
    if show_video and score < 1500:
        if frame_queue:
            frame = frame_queue.popleft()
            frame_surface = surfarray.make_surface(frame.swapaxes(0,1))
            screen.blit(frame_surface, (0, 0))
    else:
        screen.fill(WHITE)  # или другой фон

    # Проверка проигрыша и перезапуск игры
    if player.rect.top > HEIGHT:
        reset_game()

    # Физическое взаимодействие с платформами
    hit_list = pygame.sprite.spritecollide(player, platforms, False)
    for platform in hit_list:
        if player.vel_y > 0 and player.rect.bottom - player.vel_y <= platform.rect.top:
            player.rect.bottom = platform.rect.top
            player.vel_y = JUMP_POWER  # импульс вверх

    all_sprites.draw(screen)
    platforms.draw(screen)

    font = pygame.font.SysFont(None, 36)
    text_score = font.render(f'Высота: {int(score)}', True, BLACK)
    screen.blit(text_score, (10, 10))

    score += 1

    pygame.display.flip()
cap.release()
pygame.quit()