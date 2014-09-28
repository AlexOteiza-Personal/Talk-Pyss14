import os
import pygame
from pygame.locals import *
from pygame.surface import Surface
from pygame.sprite import Sprite
import random

main_dir = os.path.split(os.path.abspath("__file__"))[0]
MAX_ENEMIES = 40

def load_image(filename):
    f = os.path.join(main_dir, 'data', filename)
    try:
        surface = pygame.image.load(f)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(filename, pygame.get_error()))
    return surface

def load_images(image_names):
    images = []
    for name in image_names:
        images.append(load_image(name))
    return images

class Game():
    screen_rect = Rect(0, 0, 640, 480)
    score = 0
    player_group = pygame.sprite.Group()
    player_shots = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    score_text = pygame.sprite.Group()
    explosions = pygame.sprite.Group()


class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('white')
        self.score = 1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self):
        self.image = self.font.render("Score %i" % Game.score, 0, self.color)
    
class PlayerShot(pygame.sprite.Sprite):
    vspeed = -4
    images = load_images(['shot.png'])
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.move_ip(x-self.rect.centerx,y)

    def update(self):
        self.rect.move_ip(0, self.vspeed)
        if self.rect.y > Game.screen_rect.height:
            self.kill()
        for i in Game.enemy_group:
            if pygame.sprite.collide_rect(self, i):
                i.explode()
                self.kill()

class Player(pygame.sprite.Sprite):
    images = load_images(['player.png'])
    speed = 4
    reloading = 0
    reload_time = 8
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.move_ip(x,y)
        
    def update(self):
        keystate = pygame.key.get_pressed()
        hdirection = keystate[K_RIGHT] - keystate[K_LEFT]
        vdirection = keystate[K_DOWN] -  keystate[K_UP]
        self.rect.move_ip(hdirection*self.speed, vdirection*self.speed)
        self.rect = self.rect.clamp(Game.screen_rect)
        if self.reloading > 0:
            self.reloading -= 1
        if keystate[K_SPACE] and not self.reloading:
            shot = PlayerShot(self.rect.centerx, self.rect.y-16)
            Game.player_shots.add(shot)
            self.reloading = self.reload_time
        for i in Game.enemy_group:
            if pygame.sprite.collide_rect(self,i):
                self.explode()
                i.explode()
                
    def explode(self):
        # BOOM
        explosion = Explosion(self.rect.x, self.rect.y)
        Game.explosions.add(explosion)
        self.kill()

class Enemy(pygame.sprite.Sprite):
    images = load_images(['enemy.png'])
    vspeed = 4
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.move_ip(x,y)

    def update(self):
        self.rect.move_ip(0, self.vspeed)
        if self.rect.y > Game.screen_rect.height:
            self.kill()

    def explode(self):
        explosion = Explosion(self.rect.x, self.rect.y)
        Game.explosions.add(explosion)
        Game.score += 100
        self.kill()

class Explosion(pygame.sprite.Sprite):
    images = load_images(['explosion_1.png','explosion_2.png',
                          'explosion_3.png','explosion_4.png','explosion_5.png'])
    anim_speed = 0.15
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image_index = 0.0
        self.image = self.images[int(self.image_index)]
        self.rect = self.image.get_rect()
        self.rect.move_ip(x,y)
        
    def update(self):
        self.image = self.images[int(self.image_index)]
        self.image_index += self.anim_speed
        if self.image_index >= len(self.images):
            self.kill()

def main(winstyle = 0):
    pygame.init()
    screen = pygame.display.set_mode(Game.screen_rect.size)
    pygame.display.set_caption('PyFighter')
    background_tile = load_image('bg.png')
    background_speed = 2
    background_y = 0
    player = Player(Game.screen_rect.width/2, Game.screen_rect.height-64)
    Game.player_group.add(player)
    score = Score()
    Game.score_text.add(score)
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    running = False
        screen.fill((255,255,255))

        screen.blit(background_tile, (0, background_y))
        screen.blit(background_tile, (0, background_y - background_tile.get_height()))
        background_y = (background_y + background_speed) % (background_tile.get_height())
        
        Game.enemy_group.update()
        Game.player_shots.update()
        Game.player_group.update()
        Game.score_text.update()
        Game.explosions.update()
        
        Game.player_group.draw(screen)
        Game.enemy_group.draw(screen)
        Game.player_shots.draw(screen)
        Game.score_text.draw(screen)
        Game.explosions.draw(screen)

        if len(Game.enemy_group) < MAX_ENEMIES:
            if int(random.random()*1000)%10 == 1:
                rand_x = int(random.random()*(Game.screen_rect.width-32))
                new_enemy = Enemy(rand_x, -32)
                Game.enemy_group.add(new_enemy)

        if not player.alive():
            running = False
        pygame.display.flip()
        clock.tick(60)
            
    pygame.quit()

main()
