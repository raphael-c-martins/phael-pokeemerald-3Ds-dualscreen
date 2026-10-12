#!/usr/bin/env python3
"""Localize game graphics for Portuguese build (PT-BR).

Modifies source PNG images in build/upstream/graphics so that the decomp
tools (gbagfx) compile localized .4bpp and .4bpp.lz assets.
"""
from pathlib import Path
from PIL import Image

def get_glyph(ch):
    """3x5 pixel font for compact button labels."""
    glyphs = {
        'A': [
            ".#.",
            "#.#",
            "###",
            "#.#",
            "#.#"
        ],
        'B': [
            "##.",
            "#.#",
            "##.",
            "#.#",
            "##."
        ],
        'C': [
            ".##",
            "#..",
            "#..",
            "#..",
            ".##"
        ],
        'D': [
            "##.",
            "#.#",
            "#.#",
            "#.#",
            "##."
        ],
        'E': [
            "###",
            "#..",
            "##.",
            "#..",
            "###"
        ],
        'F': [
            "###",
            "#..",
            "##.",
            "#..",
            "#.."
        ],
        'G': [
            ".##",
            "#..",
            "#.#",
            "#.#",
            ".##"
        ],
        'H': [
            "#.#",
            "#.#",
            "###",
            "#.#",
            "#.#"
        ],
        'I': [
            "###",
            ".#.",
            ".#.",
            ".#.",
            "###"
        ],
        'L': [
            "#..",
            "#..",
            "#..",
            "#..",
            "###"
        ],
        'M': [
            "#.#",
            "###",
            "###",
            "#.#",
            "#.#"
        ],
        'N': [
            "##.",
            "#.#",
            "#.#",
            "#.#",
            "#.#"
        ],
        'O': [
            ".#.",
            "#.#",
            "#.#",
            "#.#",
            ".#."
        ],
        'R': [
            "##.",
            "#.#",
            "##.",
            "#.#",
            "#.#"
        ],
        'S': [
            ".##",
            "#..",
            ".#.",
            "..#",
            "##."
        ],
        'T': [
            "###",
            ".#.",
            ".#.",
            ".#.",
            ".#."
        ],
        'U': [
            "#.#",
            "#.#",
            "#.#",
            "#.#",
            ".##"
        ],
        'V': [
            "#.#",
            "#.#",
            "#.#",
            "#.#",
            ".#."
        ],
        'X': [
            "#.#",
            "#.#",
            ".#.",
            "#.#",
            "#.#"
        ],
        '.': [
            "...",
            "...",
            "...",
            "...",
            ".#."
        ],
        ' ': [
            "...",
            "...",
            "...",
            "...",
            "..."
        ],
        'Ã': [
            ".#.",
            "#.#",
            "###",
            "#.#",
            "#.#"
        ],
        'Í': [
            "###",
            ".#.",
            ".#.",
            ".#.",
            "###"
        ],
    }
    return glyphs.get(ch, glyphs[' '])


def draw_text_3x5(im, text, x0, y0, ink_color, shadow_color=None, bg_color=None):
    total_w = 0
    for ch in text:
        w = 1 if ch == '.' else (2 if ch == 'I' else 3)
        total_w += w + 1
    total_w -= 1

    cur_x = x0
    for ch in text:
        g = get_glyph(ch)
        w = 1 if ch == '.' else (2 if ch == 'I' else 3)
        for r, row in enumerate(g):
            for c in range(w):
                if c < len(row) and row[c] == '#':
                    if shadow_color is not None:
                        im.putpixel((cur_x + c + 1, y0 + r + 1), shadow_color)
        for r, row in enumerate(g):
            for c in range(w):
                if c < len(row) and row[c] == '#':
                    im.putpixel((cur_x + c, y0 + r), ink_color)
        cur_x += w + 1


def localize_money(tree: Path):
    path = tree / "graphics/shop/money.png"
    if not path.exists():
        return
    im = Image.open(path)
    # Background: 0, Outline: 6, Highlight: 0xE, Main: 0xC, Shadow: 0xD / 2
    # Clear the text area: x=3..29, y=3..9
    for y in range(3, 10):
        for x in range(3, 29):
            im.putpixel((x, y), 0)
    
    # Text SALDO in 5 characters
    # S, A, L, D, O custom 5x7 with outline
    chars = {
        'S': [
            ".####.",
            "#EEEE#",
            "#E####",
            ".#CCC#",
            "###CC#",
            "#DDDD#",
            ".####."
        ],
        'A': [
            ".####.",
            "#EEEE#",
            "#E##E#",
            "#CCCC#",
            "#C##C#",
            "#D##D#",
            ".####."
        ],
        'L': [
            "####..",
            "#EE#..",
            "#EE#..",
            "#CC#..",
            "#CC##.",
            "#DDDD#",
            "######"
        ],
        'D': [
            "#####.",
            "#EEE##",
            "#E##E#",
            "#C##C#",
            "#C##C#",
            "#DDD##",
            "#####."
        ],
        'O': [
            ".####.",
            "#EEEE#",
            "#E##E#",
            "#C##C#",
            "#C##C#",
            "#DDDD#",
            ".####."
        ]
    }
    text = "SALDO"
    cur_x = 3
    col_map = {
        '.': 0,
        '#': 6,
        'E': 0xE,
        'C': 0xC,
        'D': 0xD
    }
    for ch in text:
        grid = chars[ch]
        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                color = col_map.get(val, 0)
                if color != 0:
                    im.putpixel((cur_x + c, 3 + r), color)
        cur_x += len(grid[0]) - 1
    im.save(path)
    print("Localized graphics/shop/money.png -> SALDO")


def localize_trainer_card(tree: Path):
    path = tree / "graphics/trainer_card/tiles.png"
    if not path.exists():
        return
    im = Image.open(path)
    
    # 1. TRAINER CARD -> CARTAO TREINADOR at y=67..75, x=16..100
    # Clear background color 0xD
    for y in range(67, 76):
        for x in range(16, 96):
            im.putpixel((x, y), 0xD)
            
    # Draw CARTAO TREINADOR
    # Ink 0xF, Shadow 0x8
    text1 = "CARTAO TREINADOR"
    # Using 3x5 font at y=69, ink 0xF, shadow 0x8
    # Center text in 80px width
    total_w = sum(1 if ch == '.' else (2 if ch == 'I' else 3) for ch in text1) + len(text1) - 1
    start_x = 16 + (80 - total_w) // 2
    draw_text_3x5(im, text1, start_x, 69, ink_color=0xF, shadow_color=0x8)
    # Add tilde on A in CARTAO
    # The A is index 4: C(3), A(3), R(3), T(3), A(3) -> x around start_x + 16
    tilde_x = start_x + 17
    im.putpixel((tilde_x, 68), 0xF)
    im.putpixel((tilde_x + 1, 67), 0xF)
    im.putpixel((tilde_x + 2, 68), 0xF)
    
    # 2. BADGES -> INSIGNIAS at y=1..6, x=48..96
    # Clear background color 0xA
    for y in range(1, 7):
        for x in range(48, 96):
            im.putpixel((x, y), 0xA)
    text2 = "INSIGNIAS"
    total_w2 = sum(1 if ch == '.' else (2 if ch == 'I' else 3) for ch in text2) + len(text2) - 1
    start_x2 = 48 + (48 - total_w2) // 2
    draw_text_3x5(im, text2, start_x2, 1, ink_color=0x1, shadow_color=0xB)
    
    im.save(path)
    print("Localized graphics/trainer_card/tiles.png -> CARTÃO TREINADOR & INSÍGNIAS")


def localize_pokemon_storage(tree: Path):
    path = tree / "graphics/pokemon_storage/menu.png"
    if not path.exists():
        return
    im = Image.open(path)
    
    # 1. CLOSE BOX -> FECHAR at lines 60..68, x=1..35
    # Clear with background 0x8
    for y in range(60, 69):
        for x in range(1, 35):
            im.putpixel((x, y), 0x8)
    text1 = "FECHAR"
    total_w1 = sum(1 if ch == '.' else (2 if ch == 'I' else 3) for ch in text1) + len(text1) - 1
    start_x1 = 1 + (34 - total_w1) // 2
    draw_text_3x5(im, text1, start_x1, 62, ink_color=0xE, shadow_color=0xB)
    
    # 2. CANCEL -> VOLTAR at lines 60..68, x=43..85
    for y in range(60, 69):
        for x in range(43, 85):
            im.putpixel((x, y), 0x8)
    text2 = "VOLTAR"
    total_w2 = sum(1 if ch == '.' else (2 if ch == 'I' else 3) for ch in text2) + len(text2) - 1
    start_x2 = 43 + (42 - total_w2) // 2
    draw_text_3x5(im, text2, start_x2, 62, ink_color=0x9, shadow_color=0x2)
    
    im.save(path)
    print("Localized graphics/pokemon_storage/menu.png -> FECHAR & VOLTAR")


def localize_naming_screen(tree: Path):
    # 1. back_button.png: BACK -> VOLTAR at lines 16..22, x=8..32
    path_back = tree / "graphics/naming_screen/back_button.png"
    if path_back.exists():
        im = Image.open(path_back)
        for y in range(16, 23):
            for x in range(8, 34):
                im.putpixel((x, y), 0x4)
        text = "VOLTAR"
        total_w = sum(1 if ch == '.' else (2 if ch == 'I' else 3) for ch in text) + len(text) - 1
        start_x = (40 - total_w) // 2
        draw_text_3x5(im, text, start_x, 17, ink_color=0x1, shadow_color=0x3)
        im.save(path_back)
        print("Localized graphics/naming_screen/back_button.png -> VOLTAR")
        
    # 2. page_swap_lower.png: lower -> minúsc.
    path_lower = tree / "graphics/naming_screen/page_swap_lower.png"
    if path_lower.exists():
        im = Image.open(path_lower)
        for y in range(1, 7):
            for x in range(3, 24):
                im.putpixel((x, y), 0x9)
        text = "MINUS."
        draw_text_3x5(im, text, 4, 1, ink_color=0x1, shadow_color=0x8)
        im.save(path_lower)
        print("Localized graphics/naming_screen/page_swap_lower.png -> MINUS.")

    # 3. page_swap_upper.png: UPPER -> MAIUS.
    path_upper = tree / "graphics/naming_screen/page_swap_upper.png"
    if path_upper.exists():
        im = Image.open(path_upper)
        for y in range(1, 7):
            for x in range(3, 24):
                im.putpixel((x, y), 0x6)
        text = "MAIUS."
        draw_text_3x5(im, text, 4, 1, ink_color=0x1, shadow_color=0x7)
        im.save(path_upper)
        print("Localized graphics/naming_screen/page_swap_upper.png -> MAIUS.")

    # 4. page_swap_others.png: others -> OUTROS
    path_others = tree / "graphics/naming_screen/page_swap_others.png"
    if path_others.exists():
        im = Image.open(path_others)
        for y in range(1, 7):
            for x in range(3, 25):
                im.putpixel((x, y), 0x6)
        text = "OUTROS"
        draw_text_3x5(im, text, 3, 1, ink_color=0x1, shadow_color=0x7)
        im.save(path_others)
        print("Localized graphics/naming_screen/page_swap_others.png -> OUTROS")


def main(tree: Path):
    localize_money(tree)
    localize_trainer_card(tree)
    localize_pokemon_storage(tree)
    localize_naming_screen(tree)

if __name__ == "__main__":
    import sys
    tree_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("build/upstream")
    main(tree_path)
