/*
 * The Portuguese build's graphics with English words, redrawn when they are
 * read from the data pack (ReadPayload, 3ds_assets.c): the player's own
 * sheet keeps its frames and colours, its English letters are cleared and
 * the Portuguese name is written in a small capital font drawn for this
 * project. No pixel of the game is kept here.
 *
 * tools/type_icons_ptbr.py draws the same thing into a PNG, as a preview.
 */
#include <string.h>

/* Declared in compat/port_platform.h, which 3ds_assets.c includes. */
void Port_TransformAsset(const char *path, unsigned char *data, unsigned size);

#if defined(CTR_LANG_PT_BR)

/* 4bpp tiles, 16 to a row: graphics/interface/menu_info.4bpp is 128x128. */
#define SHEET_TILES_WIDE 16
#define INK 0xF
#define SHADOW 0xE

/* The sheet being drawn: menu_info is 16 tiles wide, a summary type icon
 * (a 32x16 sprite) 4. */
static int sTilesWide = SHEET_TILES_WIDE;

static unsigned SheetPixel(const unsigned char *tiles, int x, int y)
{
    const unsigned char *tile = tiles + ((y / 8) * sTilesWide + x / 8) * 32;
    unsigned char byte = tile[(y % 8) * 4 + (x % 8) / 2];
    return (x & 1) ? byte >> 4 : byte & 0xF;
}

static void SetSheetPixel(unsigned char *tiles, int x, int y, unsigned value)
{
    unsigned char *tile = tiles + ((y / 8) * sTilesWide + x / 8) * 32;
    unsigned char *byte = &tile[(y % 8) * 4 + (x % 8) / 2];
    *byte = (x & 1) ? (unsigned char)((*byte & 0x0F) | (value << 4)) : (unsigned char)((*byte & 0xF0) | value);
}

/*
 * A capital font 3 pixels wide (M 5, N 4) and 7 high, '#' for ink; the
 * accents sit on the row above. Drawn for this project.
 */
struct Glyph
{
    char ch;
    const char *rows[7];
};

static const struct Glyph sGlyphs[] = {
    {'A', {".#.", "#.#", "#.#", "###", "#.#", "#.#", "#.#"}},
    {'B', {"##.", "#.#", "#.#", "##.", "#.#", "#.#", "##."}},
    {'C', {".##", "#..", "#..", "#..", "#..", "#..", ".##"}},
    {'D', {"##.", "#.#", "#.#", "#.#", "#.#", "#.#", "##."}},
    {'E', {"###", "#..", "#..", "##.", "#..", "#..", "###"}},
    {'F', {"###", "#..", "#..", "##.", "#..", "#..", "#.."}},
    {'G', {".##", "#..", "#..", "#.#", "#.#", "#.#", ".##"}},
    {'H', {"#.#", "#.#", "#.#", "###", "#.#", "#.#", "#.#"}},
    {'I', {"###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"}},
    {'L', {"#..", "#..", "#..", "#..", "#..", "#..", "###"}},
    {'M', {"#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"}},
    {'N', {"#..#", "##.#", "##.#", "#.##", "#.##", "#..#", "#..#"}},
    {'O', {".#.", "#.#", "#.#", "#.#", "#.#", "#.#", ".#."}},
    {'P', {"##.", "#.#", "#.#", "##.", "#..", "#..", "#.."}},
    {'Q', {".#.", "#.#", "#.#", "#.#", "#.#", "##.", ".##"}},
    {'R', {"##.", "#.#", "#.#", "##.", "#.#", "#.#", "#.#"}},
    {'S', {".##", "#..", "#..", ".#.", "..#", "..#", "##."}},
    {'T', {"###", ".#.", ".#.", ".#.", ".#.", ".#.", ".#."}},
    {'U', {"#.#", "#.#", "#.#", "#.#", "#.#", "#.#", "###"}},
    {'V', {"#.#", "#.#", "#.#", "#.#", "#.#", ".#.", ".#."}},
    {'X', {"#.#", "#.#", "#.#", ".#.", "#.#", "#.#", "#.#"}},
    {' ', {"..", "..", "..", "..", "..", "..", ".."}},
    {'.', {".", ".", ".", ".", ".", ".", "#"}},
};

/* The names as byte strings: 'a' stands for Á, 'e' for É, 'i' for Í, 'c' for
 * Ç and '~' for Ã, so the table stays ASCII. */
static const struct
{
    unsigned short tile;
    const char *name;
} sTypeNames[] = {
    {0x20, "NORMAL"}, {0x64, "LUTADOR"}, {0x60, "VOADOR"}, {0x80, "VENENO"}, {0x48, "TERRA"},
    {0x44, "PEDRA"}, {0x6C, "INSETO"}, {0x68, "FANTAS"}, {0x88, "AcO"}, {0x24, "FOGO"},
    {0x28, "aGUA"}, {0x2C, "PLANTA"}, {0x40, "ELeTR."}, {0x84, "PSiQ."}, {0x4C, "GELO"},
    {0xA0, "DRAG~O"}, {0x8C, "SOMBR."},
};

/* Ink of letter ch on row r (-1 the accent row, 0-6 the letter, 7 the
 * cedilla's tail) at column c; its width in *width. */
static int GlyphInk(char ch, int r, int c, int *width)
{
    char base = ch;
    unsigned i;

    switch (ch)
    {
    case 'a': case '~': base = 'A'; break;
    case 'e': base = 'E'; break;
    case 'i': base = 'I'; break;
    case 'c': base = 'C'; break;
    }
    for (i = 0; i < sizeof(sGlyphs) / sizeof(sGlyphs[0]); i++)
    {
        if (sGlyphs[i].ch != base)
            continue;
        *width = (int)strlen(sGlyphs[i].rows[0]);
        if (r == -1)
        {
            if (ch == 'a' || ch == 'e' || ch == 'i')
                return c == 1;
            if (ch == '~')
                return 1;
            return 0;
        }
        if (r == 7)
            return ch == 'c' && c == 1;
        return sGlyphs[i].rows[r][c] == '#';
    }
    *width = 0;
    return 0;
}

/* The icon's letters sit on rows top to top + 6 (the accents on top - 1);
 * rows first to last - 1 are cleared. */
static void DrawTypeNameAt(unsigned char *tiles, int x0, int y0, int first, int last, int top, const char *name)
{
    unsigned rowBg[16];
    int total = -1, x, y;
    const char *p;

    /* Some icons fade to a second colour at the bottom: each row is
     * cleared with its own background, read at the icon's right edge. */
    for (y = 0; y < 16; y++)
        rowBg[y] = 0;
    for (y = first; y < last; y++)
    {
        for (x = 31; x > 0; x--)
        {
            unsigned v = SheetPixel(tiles, x0 + x, y0 + y);
            if (v != INK && v != SHADOW && v != 0)
            {
                rowBg[y] = v;
                break;
            }
        }
        for (x = 0; x < 32; x++)
        {
            unsigned v = SheetPixel(tiles, x0 + x, y0 + y);
            if (v == INK || v == SHADOW)
                SetSheetPixel(tiles, x0 + x, y0 + y, rowBg[y]);
        }
    }
    for (p = name; *p; p++)
    {
        int w;
        GlyphInk(*p, 0, 0, &w);
        total += w + 1;
    }
    x = x0 + (31 - total) / 2;
    for (p = name; *p; p++)
    {
        int w, r, c;
        GlyphInk(*p, 0, 0, &w);
        for (r = -1; r <= 7; r++)
        {
            for (c = 0; c < w; c++)
            {
                int dx, dy, ink;
                int dummy;
                ink = GlyphInk(*p, r, c, &dummy);
                if (!ink)
                    continue;
                y = y0 + top + r;
                SetSheetPixel(tiles, x + c, y, INK);
                for (dy = 0; dy <= 1; dy++)
                    for (dx = 0; dx <= 1; dx++)
                    {
                        int sy = y + dy - y0;
                        if ((dx || dy) && sy < last && SheetPixel(tiles, x + c + dx, y + dy) == rowBg[sy])
                            SetSheetPixel(tiles, x + c + dx, y + dy, SHADOW);
                    }
            }
        }
        x += w + 1;
    }
}

static void DrawTypeName(unsigned char *tiles, unsigned tile, const char *name)
{
    /* Rows 0-11 cleared, the letter on rows 2-8. */
    DrawTypeNameAt(tiles, (int)(tile % SHEET_TILES_WIDE) * 8, (int)(tile / SHEET_TILES_WIDE) * 8, 0, 12, 2, name);
}

/* The summary's type icons (graphics/types/move_types.4bpp), one 32x16
 * sprite of 8 tiles (256 bytes) per type, in the order of TYPE_*; ??? and
 * the contest categories stay. */
static const char *const sSummaryTypeNames[] = {
    "NORMAL", "LUTADOR", "VOADOR", "VENENO", "TERRA", "PEDRA", "INSETO", "FANTAS", "AcO", NULL,
    "FOGO", "aGUA", "PLANTA", "ELeTR.", "PSiQ.", "GELO", "DRAG~O", "SOMBR.",
};

/* The move window's labels, 42x12: white letters outlined in the colour of
 * the bar they sit on (rows 4-8). '~' stands for Ã. */
static const struct
{
    unsigned short tile;
    const char *name;
} sLabels[] = {
    {0xA8, "TIPO"}, {0xC0, "PODER"}, {0xC8, "PRECIS~O"}, {0xE0, "PP"}, {0xE8, "EFEITO"},
};

#define LABEL_W 42
#define LABEL_H 12

static void DrawLabel(unsigned char *tiles, unsigned tile, const char *name)
{
    int x0 = (int)(tile % SHEET_TILES_WIDE) * 8, y0 = (int)(tile / SHEET_TILES_WIDE) * 8;
    unsigned char inked[LABEL_H][LABEL_W];
    int total = -1, x, y;
    const char *p;

    /* The bar back without its letters, and nothing above or below it. */
    for (y = 0; y < LABEL_H; y++)
        for (x = 0; x < LABEL_W; x++)
        {
            if (y >= 4 && y <= 8)
            {
                if (SheetPixel(tiles, x0 + x, y0 + y) != 0)
                    SetSheetPixel(tiles, x0 + x, y0 + y, SHADOW);
            }
            else
            {
                SetSheetPixel(tiles, x0 + x, y0 + y, 0);
            }
        }
    memset(inked, 0, sizeof(inked));
    for (p = name; *p; p++)
    {
        int w;
        GlyphInk(*p, 0, 0, &w);
        total += w + 1;
    }
    x = (LABEL_W - 1 - total) / 2;
    for (p = name; *p; p++)
    {
        int w, r, c, dummy;
        GlyphInk(*p, 0, 0, &w);
        for (r = -1; r <= 7; r++)
            for (c = 0; c < w; c++)
            {
                int ly = 3 + r; /* row -1 on the label's row 2, the letter on rows 3-9 */
                if (GlyphInk(*p, r, c, &dummy) && ly >= 0 && ly < LABEL_H && x + c < LABEL_W)
                    inked[ly][x + c] = 1;
            }
        x += w + 1;
    }
    for (y = 0; y < LABEL_H; y++)
        for (x = 0; x < LABEL_W; x++)
        {
            int dx, dy;
            if (!inked[y][x])
                continue;
            for (dy = -1; dy <= 1; dy++)
                for (dx = -1; dx <= 1; dx++)
                {
                    int nx = x + dx, ny = y + dy;
                    if (nx >= 0 && ny >= 0 && nx < LABEL_W && ny < LABEL_H && !inked[ny][nx])
                        SetSheetPixel(tiles, x0 + nx, y0 + ny, SHADOW);
                }
        }
    for (y = 0; y < LABEL_H; y++)
        for (x = 0; x < LABEL_W; x++)
            if (inked[y][x])
                SetSheetPixel(tiles, x0 + x, y0 + y, INK);
}

/*
 * The summary's page titles (graphics/summary_screen/tiles.4bpp, 16 tiles to
 * a row): one 8-pixel row of tiles each, the letters in colour 2 with the
 * shadow 6 below and to the right, on the strip's colour. The font loses its
 * third row there, so the accents fit on the tile's row 0 and the cedilla on
 * row 7.
 */
#define TITLE_INK 0x2
#define TITLE_SHADOW 0x6

static const struct
{
    unsigned short tile;
    unsigned char tiles;
    const char *name;
} sSummaryTitles[] = {
    {128, 8, "PERFIL"}, {144, 9, "HABILIDADE"}, {176, 9, "ESTADO"}, {224, 9, "MEMO TREINADOR"},
    {192, 8, "GOLPES"}, {202, 6, "EFEITO"}, {208, 10, "DESCRIc~O"},
    {137, 7, "ITEM"}, {153, 7, "FITAS"}, {169, 7, "ATRIBUTOS"}, {185, 7, "EXP."},
};

static void DrawSummaryTitle(unsigned char *tiles, unsigned tile, int width, const char *name)
{
    int x0 = (int)(tile % SHEET_TILES_WIDE) * 8, y0 = (int)(tile / SHEET_TILES_WIDE) * 8;
    unsigned char inked[8][80];
    int x, y;
    const char *p;

    for (y = 0; y < 8; y++)
    {
        /* The strip's colour: the commonest one besides the letters' (the
         * right end may have a border). */
        unsigned count[16] = {0}, bg = 0;
        for (x = 0; x < width; x++)
            count[SheetPixel(tiles, x0 + x, y0 + y)]++;
        count[TITLE_INK] = count[TITLE_SHADOW] = 0;
        for (x = 1; x < 16; x++)
            if (count[x] > count[bg])
                bg = (unsigned)x;
        for (x = 0; x < width; x++)
        {
            unsigned v = SheetPixel(tiles, x0 + x, y0 + y);
            if (v == TITLE_INK || v == TITLE_SHADOW)
                SetSheetPixel(tiles, x0 + x, y0 + y, bg);
        }
    }
    memset(inked, 0, sizeof(inked));
    x = 2;
    for (p = name; *p; p++)
    {
        int w, t, c, dummy;
        GlyphInk(*p, 0, 0, &w);
        for (t = 0; t < 8; t++)
        {
            /* Tile row 0 the accent, 1-6 the letter without its row 2, 7 the cedilla. */
            int r = t == 0 ? -1 : t == 7 ? 7 : t < 3 ? t - 1 : t;
            for (c = 0; c < w; c++)
                if (x + c < width - 1 && GlyphInk(*p, r, c, &dummy))
                    inked[t][x + c] = 1;
        }
        x += w + 1;
    }
    for (y = 0; y < 8; y++)
        for (x = 0; x < width; x++)
        {
            int dx, dy;
            if (!inked[y][x])
                continue;
            for (dy = 0; dy <= 1; dy++)
                for (dx = 0; dx <= 1; dx++)
                    if ((dx || dy) && y + dy < 8 && x + dx < width && !inked[y + dy][x + dx])
                        SetSheetPixel(tiles, x0 + x + dx, y0 + y + dy, TITLE_SHADOW);
            SetSheetPixel(tiles, x0 + x, y0 + y, TITLE_INK);
        }
}

/*
 * PRESS START on the title screen (graphics/title_screen/press_start.4bpp,
 * 16 tiles to a row): five 32x8 sprites from tile 1, 160 pixels in a line.
 * APERTE START is put together from the sheet's own letters, each cut from
 * its left outline to its right one (the next letter shares that column).
 */
static const struct
{
    char ch;
    unsigned char from, to;
} sStartCells[] = {
    {'P', 35, 43}, {'R', 43, 51}, {'E', 51, 59}, {'T', 91, 100}, {'A', 100, 107}, {'*', 83, 124}, /* '*' the word START */
};

static int StartLinear(int l, int y, int *sx, int *sy)
{
    int tile = 1 + l / 8;
    *sx = (tile % SHEET_TILES_WIDE) * 8 + l % 8;
    *sy = (tile / SHEET_TILES_WIDE) * 8 + y;
    return tile <= 20;
}

static void DrawPressStart(unsigned char *tiles)
{
    static const char sText[] = "APERTE *";
    unsigned char source[8][128], line[8][160];
    int l = 23, x, y, sx, sy;
    const char *p;
    unsigned i;

    for (y = 0; y < 8; y++)
        for (x = 0; x < 128; x++)
            source[y][x] = (unsigned char)SheetPixel(tiles, x, y);
    memset(line, 0, sizeof(line));
    for (p = sText; *p; p++)
    {
        if (*p == ' ')
        {
            l += 7;
            continue;
        }
        for (i = 0; i < sizeof(sStartCells) / sizeof(sStartCells[0]); i++)
        {
            if (sStartCells[i].ch != *p)
                continue;
            for (x = sStartCells[i].from; x <= sStartCells[i].to; x++)
                for (y = 0; y < 8; y++)
                {
                    unsigned v = source[y][x];
                    int at = l + x - sStartCells[i].from;
                    /* The A's column 100 above its apex is the T's bar. */
                    if (*p == 'A' && x == 100 && y <= 3)
                        v = 0;
                    /* An outline (1) gives way to a letter's colours. */
                    if (v != 0 && at < 160 && (line[y][at] == 0 || line[y][at] == 1))
                        line[y][at] = (unsigned char)v;
                }
            l += sStartCells[i].to - sStartCells[i].from;
            break;
        }
    }
    for (l = 0; l < 160; l++)
        for (y = 0; y < 8; y++)
            if (StartLinear(l, y, &sx, &sy))
                SetSheetPixel(tiles, sx, sy, line[y][l]);
}

/*
 * The status icons (graphics/interface/status_icons.4bpp, 4 tiles to a row):
 * one 32x8 icon per row in the order of the summary (PSN, PAR, SLP, FRZ,
 * BRN, PKRS, FNT), the letters in colour 2 on rows 1-6, no shadow. The font
 * loses its third row, as in the summary's titles; PKRS stays.
 */
static const char *const sStatusNames[] = {"ENV", "PAR", "DOR", "CON", "QUE", NULL, "DES"};

static void DrawStatusIcon(unsigned char *tiles, int y0, const char *name)
{
    int total = -1, x, y;
    const char *p;

    for (y = 1; y <= 6; y++)
    {
        unsigned bg = SheetPixel(tiles, 8, y0 + y); /* left of the letters */
        for (x = 0; x < 32; x++)
            if (SheetPixel(tiles, x, y0 + y) == TITLE_INK)
                SetSheetPixel(tiles, x, y0 + y, bg);
    }
    for (p = name; *p; p++)
    {
        int w;
        GlyphInk(*p, 0, 0, &w);
        total += w + 1;
    }
    x = (32 - total) / 2;
    for (p = name; *p; p++)
    {
        int w, t, c, dummy;
        GlyphInk(*p, 0, 0, &w);
        for (t = 1; t <= 6; t++)
        {
            int r = t < 3 ? t - 1 : t;
            for (c = 0; c < w; c++)
                if (GlyphInk(*p, r, c, &dummy))
                    SetSheetPixel(tiles, x + c, y0 + t, TITLE_INK);
        }
        x += w + 1;
    }
}

static int EndsWith(const char *path, const char *suffix)
{
    size_t n = strlen(path), m = strlen(suffix);
    return n >= m && strcmp(path + n - m, suffix) == 0;
}

void Port_TransformAsset(const char *path, unsigned char *data, unsigned size)
{
    unsigned i;

    if (EndsWith(path, "interface/menu_info.4bpp") && size >= 128 * 128 / 2)
    {
        for (i = 0; i < sizeof(sTypeNames) / sizeof(sTypeNames[0]); i++)
            DrawTypeName(data, sTypeNames[i].tile, sTypeNames[i].name);
        for (i = 0; i < sizeof(sLabels) / sizeof(sLabels[0]); i++)
            DrawLabel(data, sLabels[i].tile, sLabels[i].name);
    }
    else if (EndsWith(path, "summary_screen/tiles.4bpp") && size >= 128 * 120 / 2)
    {
        for (i = 0; i < sizeof(sSummaryTitles) / sizeof(sSummaryTitles[0]); i++)
            DrawSummaryTitle(data, sSummaryTitles[i].tile, sSummaryTitles[i].tiles * 8, sSummaryTitles[i].name);
    }
    else if (EndsWith(path, "title_screen/press_start.4bpp") && size >= 21 * 32)
    {
        DrawPressStart(data);
    }
    else if (EndsWith(path, "interface/status_icons.4bpp") && size >= 7 * 4 * 32)
    {
        sTilesWide = 4;
        for (i = 0; i < sizeof(sStatusNames) / sizeof(sStatusNames[0]); i++)
            if (sStatusNames[i] != NULL)
                DrawStatusIcon(data, (int)i * 8, sStatusNames[i]);
        sTilesWide = SHEET_TILES_WIDE;
    }
    else if (EndsWith(path, "types/move_types.4bpp") && size >= sizeof(sSummaryTypeNames) / sizeof(sSummaryTypeNames[0]) * 256)
    {
        sTilesWide = 4;
        for (i = 0; i < sizeof(sSummaryTypeNames) / sizeof(sSummaryTypeNames[0]); i++)
            if (sSummaryTypeNames[i] != NULL)
                /* Rows 3-12 cleared, the letter on rows 4-10. */
                DrawTypeNameAt(data + i * 256, 0, 0, 3, 13, 4, sSummaryTypeNames[i]);
        sTilesWide = SHEET_TILES_WIDE;
    }
}

#else

void Port_TransformAsset(const char *path, unsigned char *data, unsigned size)
{
    (void)path;
    (void)data;
    (void)size;
}

#endif
