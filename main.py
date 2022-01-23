import pygame
import sys
import math
import os


class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('block.png', BGCOLOR)


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, level):
        super(Coin, self).__init__()
        self.x = x
        self.level = level
        self.image = load_image('coin.png', BGCOLOR)


class Frog(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.acceleration = 0
        self.state = 'ground'
        # ground - when not moving vertically
        # fall - when falling, jump - when jumping, dead - when below the level

        self.direction = 8
        # 0 - fully left, 8 - fully right
        self.frame = 0
        self.image = load_image('f80.png', BGCOLOR)
        # frog sprite names:
        # 'f' for 'frog', '0' to '8' - direction, '0' to '8' - frame num
        self.rect = self.image.get_rect()
        self.rect.x = X_AXIS - BLOCK_R
        self.rect.y = 6 * BLOCK_H

    def step_left(self):
        if self.direction != 0:
            self.frame = 0
            self.direction -= 1
        else:
            if not self.frame:
                self.frame = 2
            else:
                self.frame = self.frame % 8 + 1

    def step_right(self):
        if self.direction != 8:
            self.frame = 0
            self.direction += 1
        else:
            if not self.frame:
                self.frame = 2
            else:
                self.frame = self.frame % 8 + 1

    def update_y(self, y):
        if self.state == 'ground':
            self.acceleration = 0
        elif self.state == 'jump':
            y -= self.acceleration
            self.acceleration -= 1
            if not self.acceleration:
                self.state = 'fall'
        elif self.state == 'fall':
            y += self.acceleration
            self.acceleration += 1
        elif self.state == 'dead':
            self.rect.y += self.acceleration
            self.acceleration += 1

        return y

    def update_image(self):
        self.image = load_image('f' + str(self.direction) + str(self.frame) + '.png', BGCOLOR)

    def check_collisions(self, blocks):
        down = False
        up = False
        left = False
        right = False
        collisions = pygame.sprite.spritecollide(self, blocks, False)
        collected_coins = []
        if collisions:
            for block in collisions:
                if type(block) == Block:
                    if abs(self.rect.y - block.rect.y) <= BLOCK_H / 2:
                        if self.rect.x > block.rect.x:
                            left = True
                        else:
                            right = True
                    else:
                        if self.rect.y > block.rect.y and \
                                abs(self.rect.x - block.rect.x) < 1.5 * BLOCK_R:
                            up = True
                        elif self.rect.y < block.rect.y and \
                                abs(self.rect.x - block.rect.x) < 1.5 * BLOCK_R:
                            down = True
                elif type(block) == Coin:
                    collected_coins.append([block.x, block.level])
        return down, up, left, right, collected_coins


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image.set_colorkey(colorkey)
    return image


def render_line(x, y, line, odd, surface, front_group, cur_level):
    front = []
    back = []
    for i in range(16):
        if line[i] == '#':
            block_deg = math.radians((i * 22.5 - x) % 360)
            if math.sin(block_deg) <= 0:
                front.append((block_deg, 1))
            else:
                back.append((block_deg, 1))
        elif line[i] == '0':
            coin_deg = math.radians((i * 22.5 - x) % 360)
            if math.sin(coin_deg) <= 0:
                front.append((coin_deg, 2, i))
            else:
                back.append((coin_deg, 2, i))
    back.sort(key=lambda x: (-math.sin(x[0]), math.cos(x[0])))
    group = pygame.sprite.Group()
    for i in back:
        if i[1] == 1:
            sprite = Block()
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - BLOCK_R
        else:
            sprite = Coin(i[2], cur_level)
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - COIN_R
        sprite.rect.y = y - 1
        group.add(sprite)
    group.draw(surface)
    pygame.draw.rect(surface, (0, 0, 0), (X_AXIS - TOWER_R, y, 2 * TOWER_R, BLOCK_H))
    pygame.draw.rect(surface, (64, 49, 141), (X_AXIS - TOWER_R, y + 3, 2 * TOWER_R, BLOCK_H - 6))
    for line_n in range(24):
        line_deg = math.radians((line_n * 15 - x + 7.5 * odd) % 360)
        if math.sin(line_deg) <= 0:
            cos = X_AXIS + TOWER_R * math.cos(line_deg)
            pygame.draw.line(surface, (0, 0, 0), (cos, y), (cos, y + BLOCK_H), 6)
    front.sort(key=lambda x: (-math.sin(x[0]), math.cos(x[0])))
    for i in front:
        if i[1] == 1:
            sprite = Block()
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - BLOCK_R
        else:
            sprite = Coin(i[2], cur_level)
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - COIN_R
        sprite.rect.y = y - 1
        front_group.add(sprite)


def render_finish(y, surface):
    finish_group = pygame.sprite.Group()
    finish = pygame.sprite.Sprite()
    finish.image = load_image('finish.png', BGCOLOR)
    finish.rect = finish.image.get_rect()
    finish.rect.x = X_AXIS - BLOCK_R
    finish.rect.y = y
    finish_group.add(finish)
    finish_group.draw(surface)


def render(x, level, y, surface, front, frog_group, coins, time, coins_all):
    surface.fill((0, 255, 0))
    surface.blit(BACKGROUND, (int(x * BG_TO_TOWER_RATIO), 0))
    surface.blit(BACKGROUND, (int(x * BG_TO_TOWER_RATIO) - 900, 0))
    for i in range(11):
        if 0 <= level + 7 - i < len(tower):
            render_line(x, -y + i * BLOCK_H, tower[level + 7 - i],
                        (level + 7 - i) % 2, surface, front, level + 7 - i)
        elif level + 7 - i < 0:
            render_line(x, -y + i * BLOCK_H, ' ' * 16,
                        (level + 7 - i) % 2, surface, front, level + 7 - i)
        elif level + 7 - i == len(tower):
            render_finish(-y + (i - 1) * BLOCK_H, surface)
    front.draw(surface)
    frog_group.draw(surface)

    pygame.draw.rect(surface, (0, 0, 0), (0, 0, 200, 600))

    text = FONT.render('TIME:', False, (255, 255, 255))
    surface.blit(text, (0, 0))
    text = FONT.render('0' * (5 - len(str(time))) + str(time)[-5:], False, (255, 255, 255))
    surface.blit(text, (0, 30))

    text = FONT.render('COINS:', False, (191, 206, 114))
    surface.blit(text, (0, 60))
    text = FONT.render(str(coins) + '/' + str(coins_all), False, (191, 206, 114))
    surface.blit(text, (0, 90))

    if level == len(tower) and (coins != coins_all):
        text = FONT.render('NOT ENOUGH', False, (191, 206, 114))
        surface.blit(text, (0, 120))

        text = FONT.render('COINS!', False, (191, 206, 114))
        surface.blit(text, (0, 150))

    return front


pygame.init()
size = 900, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Froggy')


X_AXIS = 600  # 450
BLOCK_R = 36
BLOCK_H = 60
COIN_R = 21
TOWER_R = 144
BACKGROUND = load_image('bg.png')
BG_TO_TOWER_RATIO = 900 / 360
BGCOLOR = (163, 73, 164)
FONT = pygame.font.Font('Nouveau_IBM.ttf', 36)
WORLDS = open('worlds.txt')
NUM_TO_CHR = {
    0: ' ',
    1: '#',
    2: '0',
    3: 'v'
}

clock = pygame.time.Clock()
running = True
screen_acceleration = 0
y = -size[1]
while y < 0:
    # pygame.draw.rect(screen, (0, 0, 0), (0, 0, size[0], -y))
    screen.blit(load_image('title.png'), (0, y))
    pygame.display.flip()
    screen_acceleration += 1
    y += screen_acceleration
    clock.tick(30)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            running = False

world_num = 0
running = True
while running:
    world_complete = False
    header = WORLDS.readline().rstrip()
    if header == '':
        break
    else:
        world_num += 1
        world = []
        n, coins_all = [int(i) for i in header.split()]
        for i in range(n):
            cur_num = int(WORLDS.readline())
            line = ''
            while cur_num:
                line += NUM_TO_CHR[cur_num % 4]
                cur_num = cur_num // 4
            line += ' ' * (16 - len(line))
            world.append(line)

    while running and not world_complete:
        screen.fill((0, 0, 0))
        text = FONT.render('World ' + str(world_num), False, (85, 160, 73))
        screen.blit(text, (0, 0))
        text = FONT.render('Press any key to start', False, (85, 160, 73))
        screen.blit(text, (0, 60))
        pygame.display.flip()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    running = False
        running = True
        tower = [list(i) for i in world]

        level = 1
        y = 15
        # 0 <= y < 120
        x = 0
        # 0 <= x < 360
        coin_count = 0
        frames = 0
        seconds = 0

        frog = Frog()
        while running:
            front_blocks = pygame.sprite.Group()
            frog_group = pygame.sprite.Group()
            frog_group.add(frog)
            front_blocks = render(x, level, y, screen, front_blocks,
                                  frog_group, coin_count, seconds, coins_all)
            pygame.display.flip()

            down_collide, up_collide, left_collide, right_collide, collected_coins \
                = frog.check_collisions(front_blocks)
            coin_count += len(collected_coins)
            for coin_x, coin_level in collected_coins:
                tower[coin_level][coin_x] = ' '
            if up_collide and frog.state == 'jump':
                frog.state = 'fall'
                frog.acceleration = 0
            if down_collide and frog.state == 'fall':
                frog.state = 'ground'
                frog.acceleration = 0
            if frog.state == 'ground' and not down_collide:
                frog.state = 'fall'
            if down_collide and y:
                y = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
            keys = pygame.key.get_pressed()
            if keys[1073741899]:
                frog.acceleration = 0
                y -= 60
                level -= y // BLOCK_H
                y = y % BLOCK_H
            if keys[1073741902]:
                frog.acceleration = 0
                y += 60
                level -= y // BLOCK_H
                y = y % BLOCK_H
            if keys[32] and frog.state == 'ground' and down_collide:
                frog.state = 'jump'
                frog.acceleration = 15
            if keys[1073741904] and not left_collide:
                frog.step_left()
                frog.update_image()
                x -= 2.5
                x = x % 360
            if keys[1073741903] and not right_collide:
                frog.step_right()
                frog.update_image()
                x += 2.5
                x = x % 360
            if not (keys[1073741904] or keys[1073741903]) or \
                    keys[1073741903] and right_collide or keys[1073741904] and left_collide:
                frog.frame = 0
                frog.update_image()
            if frog.state == 'fall' and level == -12:
                frog.state = 'dead'
            elif frog.state == 'dead' and frog.rect.y > size[1]:
                break
            elif frog.state == 'jump' and level == len(tower) and coin_count == coins_all:
                break
            y = frog.update_y(y)
            level -= y // BLOCK_H
            y = y % BLOCK_H
            if frog.state == 'ground' and y:
                y = 0
            frames += 1
            seconds += frames // 30
            frames %= 30
            clock.tick(30)
        screen_acceleration = 0
        y = -size[1]
        if level < 0:
            while y < 0:
                # pygame.draw.rect(screen, (0, 0, 0), (0, 0, size[0], -y))
                screen.blit(load_image('lose.png'), (0, y))
                pygame.display.flip()
                screen_acceleration += 1
                y += screen_acceleration
                clock.tick(30)
        else:
            while y < 0:
                # pygame.draw.rect(screen, (0, 0, 0), (0, 0, size[0], -y))
                screen.blit(load_image('win.png'), (0, y))
                pygame.display.flip()
                screen_acceleration += 1
                y += screen_acceleration
                clock.tick(30)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    running = False
        running = True
        if level > 0:
            level_complete = True
            running = False
    running = True
