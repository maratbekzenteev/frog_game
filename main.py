import pygame
import sys
import math
import os


# class for blocks. Has no differences from a regular sprite
class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image('block.png', BGCOLOR)


# class for coins. Has 2 variables, that help with deleting collected coins from the tower map
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, level):
        super(Coin, self).__init__()
        self.x = x
        self.level = level
        self.image = load_image('coin.png', BGCOLOR)


# class for froggy. Has variables like 'state' and 'acceleration',
# which are useful when defining frog's movement
class Frog(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.acceleration = 0
        self.state = 'ground'
        # states: ground - when not moving vertically
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

    # changes the frame of the frog's sprite
    def step_left(self):
        if self.direction != 0:
            self.frame = 0
            self.direction -= 1
        else:
            if not self.frame:
                self.frame = 2
            else:
                self.frame = self.frame % 8 + 1

    # changes the frame of the frog's sprite
    def step_right(self):
        if self.direction != 8:
            self.frame = 0
            self.direction += 1
        else:
            if not self.frame:
                self.frame = 2
            else:
                self.frame = self.frame % 8 + 1

    # alters the tower's position and returns it, depending on the state of the frog
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

    # updates the frog's sprite (is called after any kind of horisontal movement)
    def update_image(self):
        self.image = load_image('f' + str(self.direction) + str(self.frame) + '.png', BGCOLOR)

    # checks collisions with blocks on each side, also returns a list of collected coins
    # (a coin is considered collected if it collides with the frog on any of the sides)
    def check_collisions(self, blocks):
        down = False
        up = False
        left = False
        right = False
        collisions = pygame.sprite.spritecollide(self, blocks, False)
        collected_coins = []
        if collisions:
            for block in collisions:
                # check collisions for each of the blocks that touch the frog
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


# a function that simplifies the process of loading images for sprites and blittable surfaces
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # exit if the file is non-existent
    if not os.path.isfile(fullname):
        print(f"File '{fullname}' not found")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image.set_colorkey(colorkey)
    return image


# renders a single line, using math functions for calculating a block's horizontal position
def render_line(x, y, line, odd, surface, front_group_touchable,
                front_group_untouchable, cur_level, frog_level):
    front_touchable = []
    front_untouchable = []
    back = []
    for i in range(16):
        # 1 is for blocks, 2 is for coins
        if line[i] == '#':
            block_deg = (i * 22.5 - x) % 360
            block_rad = math.radians(block_deg)
            if math.sin(block_rad) <= 0:
                if abs(frog_level - cur_level) <= 2 and 240 < block_deg < 310:
                    front_touchable.append((block_rad, 1))
                else:
                    front_untouchable.append((block_rad, 1))
            else:
                if not (45 < block_deg < 135):
                    back.append((block_rad, 1))
        elif line[i] == '0':
            coin_deg = (i * 22.5 - x) % 360
            coin_rad = math.radians(coin_deg)
            if math.sin(coin_rad) <= 0:
                if abs(frog_level - cur_level) <= 2 and 240 < coin_deg < 310:
                    front_touchable.append((coin_rad, 2, i))
                else:
                    front_untouchable.append((coin_rad, 2, i))
            else:
                if not (45 < coin_deg < 135):
                    back.append((coin_rad, 2, i))
    # the further the block is, the earlier it is rendered,
    # so the nearest blocks are always rendered on top of others
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
    front_touchable.sort(key=lambda x: (-math.sin(x[0]), math.cos(x[0])))
    front_untouchable.sort(key=lambda x: (-math.sin(x[0]), math.cos(x[0])))
    for i in front_touchable:
        if i[1] == 1:
            sprite = Block()
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - BLOCK_R
        else:
            sprite = Coin(i[2], cur_level)
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - COIN_R
        sprite.rect.y = y - 1
        front_group_touchable.add(sprite)
    for i in front_untouchable:
        if i[1] == 1:
            sprite = Block()
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - BLOCK_R
        else:
            sprite = Coin(i[2], cur_level)
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = (TOWER_R + BLOCK_R) * math.cos(i[0]) + X_AXIS - COIN_R
        sprite.rect.y = y - 1
        front_group_untouchable.add(sprite)


# a render function for the finish sign
def render_finish(y, surface):
    finish_group = pygame.sprite.Group()
    finish = pygame.sprite.Sprite()
    finish.image = load_image('finish.png', BGCOLOR)
    finish.rect = finish.image.get_rect()
    finish.rect.x = X_AXIS - BLOCK_R
    finish.rect.y = y
    finish_group.add(finish)
    finish_group.draw(surface)


# a function that renders 1 frame of gameplay
def render(x, level, y, surface, front_touchable, front_untouchable, frog_group, coins, time, coins_all, frog_level):
    surface.fill((0, 255, 0))
    surface.blit(BACKGROUND, (int(x * BG_TO_TOWER_RATIO), 0))
    surface.blit(BACKGROUND, (int(x * BG_TO_TOWER_RATIO) - 900, 0))
    for i in range(11):
        if 0 <= level + 7 - i < len(tower):
            render_line(x, -y + i * BLOCK_H, tower[level + 7 - i],
                        (level + 7 - i) % 2, surface, front_touchable, front_untouchable, level + 7 - i, frog_level)
        elif level + 7 - i < 0:
            render_line(x, -y + i * BLOCK_H, ' ' * 16,
                        (level + 7 - i) % 2, surface, front_touchable, front_untouchable, level + 7 - i, frog_level)
        elif level + 7 - i == len(tower):
            render_finish(-y + (i - 1) * BLOCK_H, surface)
    front_untouchable.draw(surface)
    front_touchable.draw(surface)
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

    return front_touchable, front_untouchable


# initialisation:
pygame.init()
size = 900, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Froggy')

# constants:
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
record_read = open('records.txt', 'r')
records = [int(i) for i in record_read.readline().split()]
record_read.close()

# title screen
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

    # loading the world:
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

    # pre-gameplay world screen:
    while running and not world_complete:
        screen.fill((0, 0, 0))
        text = FONT.render('World ' + str(world_num), False, (255, 255, 255))
        screen.blit(text, (0, 0))
        text = FONT.render('Best time: ' + str(records[world_num - 1]), False, (255, 255, 255))
        screen.blit(text, (0, 30))
        text = FONT.render('Press any key to start', False, (255, 255, 255))
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

        # pre-gameplay variables initialisation
        level = 2
        y = 15
        # 0 <= y < 120
        x = 0
        # 0 <= x < 360
        coin_count = 0
        frames = 0
        seconds = 0
        frog = Frog()

        # gameplay:
        while running:
            front_blocks_t = pygame.sprite.Group()
            front_blocks_unt = pygame.sprite.Group()
            frog_group = pygame.sprite.Group()
            frog_group.add(frog)
            front_blocks_t, front_blocks_unt = render(x, level, y, screen, front_blocks_t, front_blocks_unt,
                                  frog_group, coin_count, seconds, coins_all, level)
            pygame.display.flip()

            down_collide, up_collide, left_collide, right_collide, collected_coins \
                = frog.check_collisions(front_blocks_t)
            coin_count += len(collected_coins)
            # removing all the collected coins from the current map
            for coin_x, coin_level in collected_coins:
                tower[coin_level][coin_x] = ' '

            # changing the state of the frog if it is incorrect
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

            # keys pressed check
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

            # level complete / death check:
            if level == -12:
                frog.state = 'dead'
            if frog.rect.y > size[1]:
                break
            if level == len(tower) and coin_count == coins_all:
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

        # post-gameplay screens:
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
            if seconds < records[world_num - 1]:
                records[world_num - 1] = seconds
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit(0)
                        if event.type == pygame.KEYDOWN:
                            running = False
                screen.fill((0, 0, 0))
                text = FONT.render('New best time: ' + str(seconds) + ' seconds!', False, (255, 255, 255))
                screen.blit(text, (0, 0))
                pygame.display.flip()
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

# updating the records
record_write = open('records.txt', 'w', encoding='utf-8')
record_write.write(' '.join([str(i) for i in records]))
record_write.close()

# ending screen:
screen_acceleration = 0
y = -size[1]
while y < 0:
    # pygame.draw.rect(screen, (0, 0, 0), (0, 0, size[0], -y))
    screen.blit(load_image('end.png'), (0, y))
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
