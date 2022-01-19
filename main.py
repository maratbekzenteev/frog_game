import pygame
import sys
import math
import os


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


def render_line(x, y, line, odd, surface, front_group):
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
                front.append((coin_deg, 2))
            else:
                back.append((coin_deg, 2))
    back.sort(key=lambda x: (-math.sin(x[0]), math.cos(x[0])))
    group = pygame.sprite.Group()
    for i in back:
        sprite = pygame.sprite.Sprite()
        if i[1] == 1:
            sprite.image = load_image('block.png')
        else:
            sprite.image = load_image('coin.png', (163, 73, 164))
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - BLOCK_R
        sprite.rect.y = y
        group.add(sprite)
        group.draw(surface)
    pygame.draw.rect(surface, (64, 49, 141), (X_AXIS - TOWER_R, y + 3, 2 * TOWER_R, BLOCK_H - 6))
    for line_n in range(24):
        line_deg = math.radians((line_n * 15 - x + 7.5 * odd) % 360)
        if math.sin(line_deg) <= 0:
            cos = X_AXIS + TOWER_R * math.cos(line_deg)
            pygame.draw.line(surface, (0, 0, 0), (cos, y), (cos, y + BLOCK_H), 6)
    front.sort(key=lambda x: (-math.sin(x[0]), math.cos(x[0])))
    for i in front:
        sprite = pygame.sprite.Sprite()
        if i[1] == 1:
            sprite.image = load_image('block.png')
        else:
            sprite.image = load_image('coin.png', (163, 73, 164))
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - BLOCK_R
        sprite.rect.y = y
        front_group.add(sprite)


def render(x, level, y, surface, front):
    surface.fill((0, 0, 0))
    for i in range(11):
        if -len(tower) <= level + 7 - i < len(tower):
            render_line(x, -y + i * BLOCK_H, tower[level + 7 - i], (level + 7 - i) % 2, surface, front)
    front.draw(surface)
    font = pygame.font.Font('Nouveau_IBM.ttf', 36)
    text = font.render(str(level) + ' ' + str(y) + ' ' + str(x), True, (85, 160, 73))
    surface.blit(text, (0, 0))


pygame.init()
size = 900, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('frog_game')


X_AXIS = 450
BLOCK_R = 36
BLOCK_H = 60
TOWER_R = 144
tower = [
    '#               ',
    ' #              ',
    '  #             ',
    '########        ',
    '   00           ',
    '   ###          ',
    '   # #          ',
    '   # #          ',
    '   ###          ',
    '                ',
    '     #          ',
    '     #          ',
    '     #          ',
    '    ##          ',
    '                ',
    '                ',
    '                ',
    '                '
]

level = 2
y = 0
# 0 <= y < 120
x = 0
# 0 <= x < 360
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[1073741906]:
        y -= 5
        level -= y // BLOCK_H
        y = y % BLOCK_H
    if keys[1073741905]:
        y += 5
        level -= y // BLOCK_H
        y = y % BLOCK_H
    if keys[1073741904]:
        x -= 2.5
        x = x % 360
    if keys[1073741903]:
        x += 2.5
        x = x % 360
    front_blocks = pygame.sprite.Group()
    render(x, level, y, screen, front_blocks)
    pygame.display.flip()
    clock.tick(30)
