def load_enemy_assets():
    import pyxel

    # Helper to draw sprite from string list
    # u, v: positions in image bank 1
    # data: list of 16 strings (16 chars each)
    # color_map: dict mapping char to color index
    def draw_sprite(u, v, data, color_map):
        for y, line in enumerate(data):
            for x, char in enumerate(line):
                if x < 16 and y < 16:
                    col = color_map.get(char, 0)
                    if col != 0: # Only draw non-transparent pixels
                        pyxel.image(1).pset(u + x, v + y, col)

    # 1. Slime (Blue: 12) u=0, v=0
    slime = [
        "................",
        "................",
        "......XXXX......",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "..XXXXXXXXXXXX..",
        "..X.XX.XX.XX.X..",
        "..X.XX.XX.XX.X..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        "................",
        "................",
        "................",
        "................",
    ]
    draw_sprite(0, 0, slime, {'X': 12, '.': 0})

    # 2. Bat (Purple: 2) u=16, v=0
    bat = [
        "................",
        "X..............X",
        "XX............XX",
        ".XX..........XX.",
        ".XXX........XXX.",
        "..XXX..XX..XXX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        ".....XXXXXX.....",
        "....XX.XX.XX....",
        "....X..XX..X....",
        ".......XX.......",
        "................",
        "................",
        "................",
        "................",
    ]
    draw_sprite(16, 0, bat, {'X': 2, '.': 0})

    # 3. Spider (Black/DarkGray: 1/13? Let's use 13 for visibility on black bg? No, bg is black. Use 5 (Dark Blue) or 13 (Gray))
    # Using 13 (Gray) for body, 8 (Red) for eyes
    spider = [
        "................",
        "................",
        "X..X........X..X",
        ".XX..........XX.",
        "..XX..XXXX..XX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        "...X.RR..RR.X...",
        "..X..RR..RR..X..",
        ".X...XXXXXX...X.",
        "X.....XXXX.....X",
        "......X..X......",
        ".....X....X.....",
        "....X......X....",
        "................",
        "................",
    ]
    draw_sprite(32, 0, spider, {'X': 13, 'R': 8, '.': 0})

    # 4. Snake (Green: 11 / 3) u=48, v=0
    snake = [
        "................",
        "................",
        "......XXXX......",
        ".....XXXXXX.....",
        "....XX.XX.XX....",
        "....XXXXXXXX....",
        ".....XXXXXXX....",
        "......XXXX......",
        ".......XX.......",
        ".......XX.......",
        "......XXXX......",
        ".....XXXXXX.....",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "..XXXXXXXXXXXX..",
        "................",
    ]
    draw_sprite(48, 0, snake, {'X': 11, '.': 0})

    # 5. Scorpion (Red: 8) u=0, v=16
    scorpion = [
        "................",
        "X......XX......X",
        "XX....XXXX....XX",
        ".XX..XXXXXX..XX.",
        "..XXXXXXXXXXXX..",
        "...XXXXXXXXXX...",
        "....XXXXXXXX....",
        "....XXXXXXXX....",
        ".....XXXXXX.....",
        "......XXXX......",
        "......XXXX......",
        ".......XX.......",
        ".......XX.......",
        "...XX..XX..XX...",
        "..XX...XX...XX..",
        "................",
    ]
    draw_sprite(0, 16, scorpion, {'X': 8, '.': 0})

    # 6. Wolf (Gray: 13) u=16, v=16
    wolf = [
        "................",
        ".......X...X....",
        "......XX...XX...",
        ".....XXXXXXXX...",
        "....XXXXXXXXXX..",
        "...XXXXXXXXXXXX.",
        "..XXXXXXXXXXXXX.",
        "..XXX.XXXXX.XXX.",
        "..XXXXXXXXXXXXX.",
        "..XXXXXXXXXXXXX.",
        "...XXXXXXXXXXXX.",
        "....XX.....XX...",
        "....XX.....XX...",
        "....XX.....XX...",
        "................",
        "................",
    ]
    draw_sprite(16, 16, wolf, {'X': 13, '.': 0})

    # 7. Skeleton (White: 7) u=32, v=16
    skeleton = [
        "................",
        "......XXXX......",
        ".....XXXXXX.....",
        ".....X.XX.X.....",
        ".....XXXXXX.....",
        "......XXXX......",
        ".......XX.......",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "...XX..XX..XX...",
        "...XX..XX..XX...",
        ".......XX.......",
        "......XXXX......",
        ".....XX..XX.....",
        ".....XX..XX.....",
        "................",
    ]
    draw_sprite(32, 16, skeleton, {'X': 7, '.': 0})
    
    # 8. Ghost (White/LightBlue: 6) u=48, v=16
    ghost = [
        "................",
        "......XXXX......",
        "....XXXXXXXX....",
        "...XXXXXXXXXX...",
        "..XXXXXXXXXXXX..",
        "..XX.XX..XX.XX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "..XXXXXXXXXXXX..",
        "...X..X..X..X...",
        "...X..X..X..X...",
        "................",
        "................",
    ]
    draw_sprite(48, 16, ghost, {'X': 6, '.': 0})

    print("[EnemyAssets] Loaded enemy sprites into Bank 1")
