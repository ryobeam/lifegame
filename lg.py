import sys
import random
import csv

import pygame
from pygame.locals import *

# CELL変数
WIDTH = 100
HEIGHT = 100
SIZE = 10
TX = 10
TY = 10
SET_RANDOM = 0.15
COLOR_CELL_NONE = (0,0,0)
COLOR_CELL_NONE_2 = (0,50,0)
COLOR_CELL_LIVE = (0,100,0)
COLOR_CELL_BORN = (100,255,100)
COLOR_CELL_DEAD = (100,0,0)
COLOR_CELL_STAR = (255,255,255)
RUN_WAIT = 100

# PANEL変数
PANEL_X = TX
PANEL_Y = HEIGHT * SIZE + 5 + TY
PANEL_HEIGHT = 30
PANEL_WIDTH = WIDTH * SIZE

#
cell  = [[0 for i in range(WIDTH)] for j in range(HEIGHT)] # フィールド
cell_old  = [[0 for i in range(WIDTH)] for j in range(HEIGHT)] # ひとつ前のフィールド 
screen = None # pygame screen

gen = 1
live = 0
live_old = 0

def restart():
    global gen, live, live_old

    gen = 1
    live = count_live()
    live_old = live

def count_live():
    live = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if cell[y][x] == 1:
                live += 1
    return live

def next():
    global cell, cell_old
    global gen, live, live_old

    cell_next = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

    # 周りのセルの生存数を計算 (0～8) ＊自身は除く
    def _check_cell(x, y):
        count = 0
        for yy in range(-1, 2):
            for xx in range(-1, 2):
                iy = y + yy
                ix = x + xx
                if ix < 0 or ix >= WIDTH or iy < 0 or iy >= HEIGHT:
                    p = 0
                else:
                    p = cell[iy][ix]
                count += p
        count -= cell[y][x]
        return count

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # 生存チェック
            p = _check_cell(x, y)
            cell_next[y][x] = 0
            if cell[y][x] == 0:
                if p == 3: # 誕生
                    cell_next[y][x] = 1
            else:
                if p == 2 or p == 3: # キープ
                    cell_next[y][x] = 1
    
    cell_old = cell # ひとつ前のフィールドを保存
    cell = cell_next # 現在のフィールドを更新

    gen += 1
    live_old = live
    live = count_live()

def set_cell_random():
    global cell, cell_old

    for y in range(HEIGHT):
        for x in range(WIDTH):
            r = random.random()
            if r < SET_RANDOM:
                cell[y][x] = 1
            else:
                cell[y][x] = 0
    
    cell_old = cell

    #with open('a.txt', 'w') as f:
    #    for y in range(HEIGHT):
    #        s = ''
    #        for x in range(WIDTH):
    #            s += f'{cell[y][x]},'
    #        f.write(s[:-1])

    # 初期状態をファイルへ出力          
    with open('data.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(cell)   

def set_cell_p2():
    global cell, cell_old

    def hline(x, y, width):
        for i in range(width):
            cell[y][x + i] = 1
    def vline(x, y, height):
        for i in range(height):
            cell[y + i][x] = 1

    for y in range(HEIGHT):
        for x in range(WIDTH):
            cell[y][x] = 0

    hline(0, 15, 100)
    hline(0, 17, 100)
    hline(0, 19, 100)

    hline(0, 80, 100)
    hline(0, 82, 100)
    hline(0, 84, 100)

    vline(15, 0, 100)
    vline(17, 0, 100)
    vline(19, 0, 100)

    vline(80, 0, 100)
    vline(82, 0, 100)
    vline(84, 0, 100)

    cell_old = cell

#
# GUI
#
def init_screen():
    pygame.init()
    pygame.display.set_caption("lifegame")
    screen = pygame.display.set_mode((WIDTH * SIZE + TX * 2, HEIGHT * SIZE + TY * 2 + PANEL_HEIGHT))
    screen.fill((50,50,50))
    pygame.display.update()

    return screen

def draw(offset_x, offset_y):
    def _pos(x, y):
        return _pos_x(x), _pos_y(y)

    def _pos_x(x):
        return x * SIZE + TX

    def _pos_y(y):
        yy = y + offset_y
        if yy >= HEIGHT:
            yy -= HEIGHT
        return yy * SIZE + TY

    def _draw_cell(x, y, color):
        pygame.draw.rect(screen, color, _pos(x, y) + (SIZE, SIZE))

    def _draw_box(x, y):
        _draw_cell(x, y, COLOR_CELL_NONE)
        pygame.draw.line(screen, COLOR_CELL_NONE_2, _pos(x, y), (_pos_x(x) + SIZE, _pos_y(y)), 1)
        pygame.draw.line(screen, COLOR_CELL_NONE_2, _pos(x, y), (_pos_x(x), _pos_y(y) + SIZE), 1)

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if cell[y][x] == 1: # 生存
                color = COLOR_CELL_LIVE
                if cell_old[y][x] == 0: # 誕生
                    color = COLOR_CELL_BORN
                    if random.random() < 0.05: color = COLOR_CELL_STAR # 誕生(STAR)
                _draw_cell(x, y, color)
            else: # 空間
                if cell_old[y][x] == 1: # 死亡
                    _draw_cell(x, y, COLOR_CELL_DEAD)
                else: # 空間
                    _draw_box(x, y)

    draw_panel()
    pygame.display.update()

def draw_panel():
    global gen, live

    def _print(x, y, text):
        screen.blit(text, (PANEL_X + x,PANEL_Y + y))
        
    pygame.draw.rect(screen, (0,50,0), (PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT))

    font = pygame.font.SysFont(None, 30)

    text1 = font.render('LIFEGAME', True, (200,200,200))
    text2 = font.render(f'Generation {gen:,}', True, (200,200,200))
    text3 = font.render(f'Live {live:,} ({(live_old - live):+,})', True, (200,200,200))
    
    _print(6,6,text1)
    _print(200,6,text2)
    _print(400,6,text3)

#
# Main Loop
#
def main():
    global screen, live
    ##is_run = False
    step = 0 # step の数だけ更新 0の時は停止
    dy = 0

    screen = init_screen()
    set_cell_random()
    restart()
    draw(0,0)

    while True:
        if step == 0:
            is_run = False
        else:
            is_run = True
            step -= 1

        if is_run:
            next()

            draw(0, 0)
            dy += 1
            if dy >= HEIGHT:
                dy = 0

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_SPACE:
                    if step > 0:
                        step = 0
                    else:
                        step = 10000
                    ## is_run = not is_run
                elif event.key == K_RIGHT or event.key == K_DOWN:
                    step = 1
                elif event.key == K_1:
                    step = 0
                    set_cell_random()
                    restart()
                    draw(0,0)
                elif event.key == K_2:
                    step = 0
                    set_cell_p2()
                    restart()
                    draw(0,0)

        pygame.time.wait(RUN_WAIT)


if __name__ == '__main__':
    main()
