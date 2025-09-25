import pygame
import random
from os.path import join

from random import randint, choice

class Player(pygame.sprite.Sprite):

    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_rect(center = (200, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        # Horn Cooldown
        self.can_honk = True
        self.horn_honk_time = 0
        self.cooldown_duration = 500

        # Lane Cooldown
        self.can_shift = True
        self.lane_shift_time = 0
        self.shift_cooldown_duration = 670

    def horn_timer(self):
        if not self.can_honk:
            current_time = pygame.time.get_ticks()
            if current_time - self.horn_honk_time >= self.cooldown_duration:
                self.can_honk = True

    def shift_timer(self):
        if not self.can_shift:
            current_time = pygame.time.get_ticks()
            if current_time - self.lane_shift_time >= self.shift_cooldown_duration:
                self.can_shift = True
                self.direction.y = 0

    def update(self, dt):
        global running
        self.rect.center += self.speed * self.direction * dt
        if self.rect.y < 100 or self.rect.y > 700:
            self.kill()
            running = False

        self.horn_timer()
        self.shift_timer()

class Car(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.direction = pygame.Vector2(-1,0)
        self.speed = choice([250, 300, 350])
        self.dangerous = False
        self.rotation_speed = 0
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.x < -200:
            self.kill()

        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

class Horn(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_rect(center = pos)
        self.direction = pygame.Vector2(1,0)
        self.speed = 400
        self.rotation_speed = -400
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.x > 400:
            self.kill()

        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = [pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2)) for frame in frames]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        self.frame_index += 100 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()

def collisions():
    global running

    player_collided_sprites = pygame.sprite.spritecollide(player, car_sprites, True, pygame.sprite.collide_mask)
    if player_collided_sprites:
        running = False

    for car in car_sprites:
        other_cars = car_sprites.copy()
        other_cars.remove(car)
        if car.dangerous:
            car_collided_sprites = pygame.sprite.spritecollide(car, other_cars, False, pygame.sprite.collide_mask)
            for collided_car in car_collided_sprites:
                collided_car.direction = car.direction
                collided_car.rotation_speed = car.rotation_speed


    for honk in honk_sprites:
        collided_sprites = pygame.sprite.spritecollide(honk, car_sprites, False, pygame.sprite.collide_mask)
        if collided_sprites:
            honk.kill()
            for car in collided_sprites:
                car.direction += (0, choice([-3,3]))
                car.dangerous = True
                car.rotation_speed = choice([-300, 300])

def display_score():
    current_time = pygame.time.get_ticks() // 3000
    text_surf = font.render('Miles Driven: ' + str(current_time), True, ('White'))
    text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, 'White', text_rect.inflate(20, 10), 5, 10)

# pygame setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 800
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Distracted Driving')
clock = pygame.time.Clock()
running = True

# Lanes
top_lane = WINDOW_HEIGHT / 2 - 200
middle_lane = WINDOW_HEIGHT / 2
bottom_lane = WINDOW_HEIGHT / 2 + 200
lane_list = [top_lane, middle_lane, bottom_lane]

# Imports
car_surf = pygame.image.load(join('images', 'car.png')).convert_alpha()
honk_surf = pygame.image.load(join('images', 'honk.png')).convert_alpha()
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

font = pygame.font.Font(join('images', 'Roboto-Regular.ttf'), 50)
font.set_bold(True)

# Audio has been disabled due to a problem with the audio system in the environment.
# This was causing the game to crash on startup.
# honk_sound_1 = pygame.mixer.Sound(join('Audio', 'honk_sound_1.mp3'))
# honk_sound_1.set_volume(0.5)
# honk_sound_2 = pygame.mixer.Sound(join('Audio', 'honk_sound_2.mp3'))
# honk_sound_2.set_volume(0.5)
# game_music = pygame.mixer.Sound(join('Audio', 'game_music.mp3'))
# game_music.set_volume(0.2)
# game_music.play(loops = -1)
# traffic_music = pygame.mixer.Sound(join('Audio', 'traffic_music.mp3'))
# traffic_music.set_volume(0.5)
# traffic_music.play(loops = -1)

# Sprites
honk_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
car_sprites = pygame.sprite.Group()

player = Player(all_sprites)

# Events
car_event = pygame.event.custom_type()
pygame.time.set_timer(car_event, randint(750, 1500))

while running:
    dt = clock.tick() / 1000

    # Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == car_event:
            x, y = WINDOW_WIDTH + 50, random.choice(lane_list)
            Car(car_surf, (x,y), (all_sprites, car_sprites))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player.can_honk:
                Horn(honk_surf, player.rect.center, (all_sprites, honk_sprites))
                player.can_honk = False
                player.horn_honk_time = pygame.time.get_ticks()
                # honk_sound_1.play()
            if event.key == pygame.K_DOWN and player.can_shift:
                player.direction.y = 1
                player.can_shift = False
                player.lane_shift_time = pygame.time.get_ticks()
            if event.key == pygame.K_UP and player.can_shift:
                player.direction.y = -1
                player.can_shift = False
                player.lane_shift_time = pygame.time.get_ticks()

    all_sprites.update(dt)
    collisions()

    # Draw the game
    display_surface.fill('darkgray')
    all_sprites.draw(display_surface)
    display_score()

    pygame.display.update()

pygame.quit()