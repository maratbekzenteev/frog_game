import pygame
import sys
import math
import os


class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('block.png', (163, 73, 164))


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, level):
        super(Coin, self).__init__()
        self.x = x
        self.level = level
        self.image = load_image('coin.png', (163, 73, 164))


class Frog(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.acceleration = 0
        self.state = 'ground'
        # ground - when not moving vertically
        # fall - when falling, jump - when jumping

        self.direction = 8
        # 0 - fully left, 8 - fully right
        self.frame = 0
        self.image = load_image('f80.png', (163, 73, 164))
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
        return y

    def update_image(self):
        self.image = load_image('f' + str(self.direction) + str(self.frame) + '.png', (163, 73, 164))

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


def render(x, level, y, surface, front, frog_group, coins):
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
    front.draw(surface)
    frog_group.draw(surface)
    font = pygame.font.Font('Nouveau_IBM.ttf', 36)
    text = font.render(str(level) + ' ' + str(y) + ' ' + str(x) + ' ' + str(coins),
                       True, (85, 160, 73))
    surface.blit(text, (0, 0))
    return front


pygame.init()
size = 900, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('frog_game')


X_AXIS = 600  # 450
BLOCK_R = 36
BLOCK_H = 60
COIN_R = 21
TOWER_R = 144
BACKGROUND = load_image('bg.png')
BG_TO_TOWER_RATIO = 900 / 360
tower = [
    '    #           ',
    '     #          ',
    '##    #   # # ##',
    ' 0       #      ',
    '#####   #      #',
    '       #        ',
    '      #         ',
    '##  ##      ##  ',
    '                ',
    '         ##     ',
    '                ',
    '  ##  ##    ##  ',
    '   0          # ',
    '               #',
    '#               ',
    ' #              ',
    '  #     #       ',
    '     #     #    ',
    '              # ',
    '        #       ',
    '        0      #',
    '                ',
    '  #             ',
    '     #          ',
    '                '
]
tower = [list(i) for i in tower]

level = 3
y = 15
# 0 <= y < 120
x = 0
# 0 <= x < 360
coin_count = 0
running = True
clock = pygame.time.Clock()
frog = Frog()
while running:
    front_blocks = pygame.sprite.Group()
    frog_group = pygame.sprite.Group()
    frog_group.add(frog)
    front_blocks = render(x, level, y, screen, front_blocks, frog_group, coin_count)
    pygame.display.flip()

    down_collide, up_collide, left_collide, right_collide, collected_coins\
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
            running = False
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
    y = frog.update_y(y)
    level -= y // BLOCK_H
    y = y % BLOCK_H
    if frog.state == 'ground' and y:
        y = 0
    clock.tick(30)
