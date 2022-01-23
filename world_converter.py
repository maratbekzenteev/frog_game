n, coins = [int(i) for i in input().split()]
world = []
CHR_SET = {
    ' ': 0,
    '#': 1,
    '0': 2,
    'v': 3
}
for i in range(n):
    line = input()
    line = line + ' ' * (16 - len(line))
    cur_num = 0
    for j in range(len(line)):
        cur_num += CHR_SET[line[(j + 8) % 16]] * (4**j)
    world.append(cur_num)
print(n, coins)
for i in world:
    print(i)
