# Changelog

## Unreleased

- Portuguese: the title logo reads VERSÃO ESMERALDA, VERSÃO centred over a
  wide ESMERALDA. It is drawn for this project (3ds_icons_ptbr.c, DrawLogo)
  in the palette of the player's logo, with its outline, straight;
  tools/logo_ptbr.py draws the same into a preview.
- Portuguese: the POKéDEX menu and search sheets (and the summary's titles)
  were still English on the 3DS: malloc_and_decompress decompresses a copy
  of the asset, which the port could not name. Patch 0049 now passes it the
  original asset there.
- Portuguese: the POKéNAV's graphics: the menu options (MAPA DE HOENN,
  CONDIÇÃO, CHAMADAS, FITAS, DESLIGAR, EQUIPE, BUSCAR, the five conditions,
  VOLTAR), the headers (MENU PRINCIPAL, MAPA, VISÃO GERAL, AMPLIADO…), the
  zoomed map's key (CENTRO POKéMON, GINÁSIO POKéMON, TENDA DE BATALHA,
  CONCURSO POKéMON) and the condition screen's SAIR. The labels can be
  drawn without a shadow, and an accent above a short box goes on its top
  row.
- Portuguese: the POKéDEX list's sprites: BUSCAR, NACIONAL (the T of
  NATIONAL redrawn as a C, keeping its hand-kerned letters), VISTOS and
  CAPTURADOS. The labels draw every shadow before the ink, and a text still
  too wide in the narrow font is set a pixel tighter.
- Portuguese: the POKéDEX search buttons (MODO, ORDEM, NOME, COR, TIPO,
  VOLTAR, OK, TROCAR, BUSCAR), in the game's short font. The English letters
  now take the nearest background pixel of their row.
- Portuguese: the POKéDEX menu sheet in Portuguese (ÁREA, GRITO, TAMANHO,
  VOLTAR and the START menu), written with the game's own fonts from the
  player's ROM (Port_LatinGlyph). Every graphic the game decompresses now
  passes through Port_TransformDecompressed (bios.c, patch 0049), which
  replaces the per-screen patches 0049 and 0050 of the summary and the title
  screen.
- Portuguese: the contest category icons read ESTILO, BELEZA, FOFURA,
  ESPERT. and FORÇA (3ds_icons_ptbr.c, same sheet as the type icons).
- Portuguese: the status icons read ENV, PAR, DOR, CON, QUE and DES (PKRS
  stays), in the summary and on the bottom screen, whose
  decompressed sheets now pass through Port_TransformAsset too (the bottom
  screen's type icons are Portuguese as well).
- Portuguese: APERTE START on the title screen, put together by
  3ds_icons_ptbr.c from the sheet's own letters. The logo
  (EMERALD VERSION) stays.
- Portuguese: the summary's page titles (PERFIL, HABILIDADE, GOLPES,
  DESCRIÇÃO, MEMO TREINADOR, ATRIBUTOS…), redrawn in the decompressed tiles
  before they reach VRAM.
- Portuguese: the summary's type icons too (FOGO, ÁGUA, PLANTA…), redrawn
  by 3ds_icons_ptbr.c once the summary decompresses the sheet.
  The contest categories (COOL, BEAUTY…) stay for now.
- Portuguese: the type icons in Portuguese (NORMAL, LUTADOR, ÁGUA, ELÉTR.,
  DRAGÃO…). 3ds_icons_ptbr.c redraws the player's own menu_info sheet as it
  is read from the data pack: the frames and colours stay, the English
  letters are cleared and the names written in a small font drawn for the
  project. tools/type_icons_ptbr.py renders the same into a preview.
- Portuguese: two credits pages right after the title, before the crew's
  (patch 0048): Tradução PT-BR, Carlos Mozart, AllGenWiki; Port para
  Nintendo 3DS, Daniel Cazalla.
- Portuguese: the EASY CHAT words (1008, with the abilities, types, moves
  and POKéMON from the catalogs), and their lists in alphabetical order
  again: tools/easy_chat_order.py rewrites each group's order and the ABC
  mode from the staged texts. Saves and trades keep the words' numbers.
- Portuguese: the place names on the map popup, the region map and the summary:
  the towns by their own name (LITTLEROOT), ROTA 101 and the rest within 16
  characters. localize_portuguese.py stages the generated
  region_map_entries.h once `make generated` has made it.
- Portuguese: BERRIES read FRUTA ORAN and FRUTAS ORAN, with the word first as
  in Spanish (patch 0047). The game built "ORAN BERRIES" in English.
- Brazilian Portuguese, step 1: `PORT_LANG=pt_br` (`bootstrap.py
  --port-lang pt_br`) shows the port's own interface in Portuguese over the
  English game: the bottom screen's labels, the OPTIONS tabs and extras, and
  the data pack errors. The bottom screen's labels take accented letters
  (docs/PORTUGUESE.md). Not yet tested on a 3DS.
- ã, õ, Ã and Õ in every latin font (codes 0x2F-0x32, patch 0040): drawn
  when each font loads from the pack, as the letter with the tilde of the
  same font's ñ (Ñ) over it. The bottom screen's labels and the game's
  `_("...")` texts can use them.
- The game's texts in Portuguese, step 1: `tools/localize_portuguese.py`
  stages the translations of `tools/locales/pt_br/` (a label, the hash of
  the English text and the Portuguese one) into the `--port-lang pt_br`
  tree, after checking the charmap, the placeholders and every line's width.
  Translated so far: Prof. Birch's speech, the main menu, the START menu and
  YES/NO. The rest stays in English.
- Portuguese: the moving truck and all of LITTLEROOT TOWN (the town, both
  houses and PROF. BIRCH's LAB), 122 more texts.
- Portuguese: ROUTE 101 with the choice of the first POKéMON, OLDALE TOWN,
  the POKéMON CENTER nurse and the POKéMON MARTs (65 more texts, 210 in all).
- Portuguese: Brazil's official names, in tools/locales/pt_br/GLOSSARIO.md
  with their source: BOLSA (not MOCHILA), MAMÃE, POKé MART, BOLA
  PRESENTEADA and TÊNIS DE CORRER replace the earlier choices.
- Portuguese: every item's name (official Brazilian names, abbreviated to
  the game's 13 bytes where needed, such as REPELENTE MÁX) and description
  (618 texts, 828 in all). localize_portuguese.py now reads table entries
  ([MOVE_X] = _("..."), .name = _("...")) and checks fixed-size names.
- Portuguese: the BAG's menus, pockets and messages, and the messages of
  using items (59 texts, 887 in all). CANCEL becomes VOLTAR, as wide as the
  English word, since some windows fit it exactly.
- Portuguese: every move's name, Brazil's official one abbreviated to the
  game's 12 bytes where needed (GOLPE CARATÊ, REV. D'ÁGUA), and its
  two-line description (708 texts, 1595 in all).
- Portuguese: every ability's name, Brazil's official one in 12 bytes
  (ARM. BATALHA, ABS.VOLTAICA), and its description (155 texts, 1750 in
  all). localize_portuguese.py checks names and descriptions sharing a
  file apart.
- Portuguese: the battle messages, menus and the level-up box (512 texts,
  2262 in all). Patch 0041 lets a language put "wild"/"foe" after the
  POKéMON's name and the adverb after the verb of a stat change (both
  empty or unchanged in English), so the texts read naturally:
  "ZIGZAGOON selvagem usou INVESTIDA!", "ATAQUE de MUDKIP subiu muito!".
- Portuguese: the type names, whole (TERRESTRE, PSÍQUICO), and every
  POKéDEX category in 11 bytes (406 texts, 2668 in all). Patch 0042 lets a
  language put "POKéMON" before the category: POKéMON SEMENTE. Patch 0043
  makes type names 9 bytes long, widens "a FIRE move" for Portuguese as
  0034 does for Spanish, and draws a type too wide for the POKéDEX search
  boxes in the narrow font. PRECISÃO and EVASÃO in capitals.
- The OPTION menu's frame no longer runs past the bottom of its window, and
  the whole selected row is highlighted, not only its left half (patch
  0044): the 3DS shows the rows the GBA hid, and the highlight's right edge
  wrapped on the 400px screen.
- Portuguese: the OPTION menu (VEL. DO TEXTO, LENTA MÉDIA RÁPIDA,
  ANIMAÇÕES, ESTILO BATALHA…), the CONTINUE menu and the save file
  messages at start. Patch 0045 widens the OPTION menu's choices column for
  Portuguese (x=96..204 instead of 104..198); English is unchanged.
- Portuguese: the player's PC (ITENS GUARDADOS, CARTAS, DECORAÇÃO), the
  POKéMON STORAGE SYSTEM's menus, wallpapers and messages, and the START
  menu's save and SAFARI BALLS windows (2805 texts in all).
- Portuguese: the POKéMON summary (INFO POKéMON, ATRIBUTOS, GOLPES DE
  LUTA, the nature and where it was met, the EGG notes) and the party
  menu's messages (healing, items, MAIL, learning moves).
- Portuguese: the POKéDEX screens: DEX HOENN and DEX NACIONAL, the search
  (colors, NENHUM, QUALQUER) and its listing modes (MODO NUMÉRICO, MODO A A
  Z, MAIS PESADOS…), ALT. and PESO, GRITO DE and TAMANHO COMPARADO A.
- Portuguese: the POKéDEX shows meters and kilograms with the decimal comma
  (0,7 m, 6,9 kg), reusing the Spanish metric code of patch 0035 (patch
  0046); English keeps feet and pounds.
- Portuguese: SIM/NÃO in the scripts' yes/no box (the nickname question
  stayed YES/NO) and in the BATTLE FACTORY; the POKéNAV's menus, help bar,
  CONDIÇÃO, FITAS and the CHAMADAS with the trainers' titles.
- Portuguese: all 386 POKéDEX descriptions (and the unknown species'),
  translated from the Emerald's own texts in 4 lines and up to 224 px, with
  metric units.

## 0.3.1 — 2026-10-10

New and improved:

- A new icon and banner on the HOME Menu, for the forwarder CIA and the
  3DSX.

Fixed:

- Taking a fossil in the Mirage Tower crashed the game when the tower
  started to shake (the tower's graphics overran their buffer).
- Hyper Beam could crash a battle (an original game bug that picks an orb
  animation that does not exist; harmless on the GBA, a crash on the 3DS).
- Shops: the BUY screen showed a black background and sat in the top-left
  corner of the screen. It is on the bottom screen now, on the same green as
  the bag you sell from, and works by touch: tap an item to pick it and again
  to buy it, drag the list to scroll it, drag to change how many, tap YES or
  NO. The top screen keeps the world, in 2D and in voxel mode.
- Battles: the stats box shown on a level up was hidden behind the text box
  and ran off the bottom of the screen; it is drawn over the text box again,
  whole.
- Graphics and data the 3DS read from the wrong place (the same cause as the
  Mirage Tower crash): Sootopolis's drought weather no longer fades the
  screen to black; Trainer Hill floors have their maps and walls (by
  @Trukitro, pull request #25); Spinda has
  its spots; the evolution background, the Pokéball, mugshot, Rayquaza and
  grid battle transitions, the PP colours, Pokédex footprints and area glow,
  the contest applause meter, turn numbers and results window, the Secret
  Base decoration preview, the Match Call frame, the underwater map name
  frame, the Pokénav condition cancel icon, the Battle Factory screens, the
  Trainer Hill records, the Battle Pyramid floor colours and the slots' Reel
  Time window are drawn as on the GBA.

## 0.3.0 — 2026-10-08

New and improved:

- Spanish: the game in Spanish from your own Pokémon Esmeralda (Spain) ROM.
  The web and Windows builders accept it and pick the language from the ROM;
  every release carries both languages (`Emerald3DS-es.3dsx` is the Spanish
  executable for Quick Update). The texts, graphics, braille, credits and
  Trainer Hill come from your ROM; the touch screen has Spanish labels and
  the Pokédex shows metres and kilograms. Translation work by Jesus Oliva
  (@jesus0m, pull request #6).
- OPTIONS has tabs: SETTINGS (as before), ENHANCEMENTS and CHEATS, all off
  by default, by @papacult (pull request #11). ENHANCEMENTS: SPEED 1x-4x
  fast-forward (also ZR/ZL on New 3DS, music and sound at normal speed),
  visible wild Pokémon that wander the grass, caves and water instead of
  random encounters, EXP for catching, the modern Exp Share, trade
  evolutions at Lv. 40, field HMs with the badge alone. CHEATS: wild
  encounter rate, shiny odds, every Poké Ball catches, instant victory, fast
  egg hatching, infinite money, Pokédex (Hoenn full, National on or full)
  and GIVE ITEMS.
- Quick ball in wild battles, by @papacult (pull request #11): a button
  beside FIGHT (or R) throws the last ball used without opening the bag.
- Soft reset (A+B+START+SELECT) restarts the game as on the GBA instead of
  crashing, by @papacult (pull request #12).
- A visible wild shiny sparkles more often, so it can be told apart, by
  @Trukitro (pull request #20).
- Bottom screen redrawn: an emerald button column with the game's icons, a
  Y button for the registered item (the console's Y is now SELECT) and a
  RUN toggle that makes running the default (B walks); X puts a focus ring
  on the column for the D-pad; the options in a 2x6 grid, the map in a
  recessed frame with its area name, and one light green background behind
  the game's own screens.
- Battle bottom screen redrawn: plates in the DS/3DS style over a teal
  backdrop, FIGHT with Rayquaza's silhouette, the quick ball, the party's
  six balls, moves in their type's colour with PP in the game's warning
  colours; the screen fades in as a battle starts, and the menus no longer
  drop frames.
- Battles in 3D with the 3D slider: the scenery behind the screen, each
  side's Pokémon at its own depth and the text box at the screen, in 2D
  battles and in 3D BATTLE.
- 3D BATTLE: the camera's flight from the field to the battle is a
  cinematic entrance (crane, dolly zoom, landing with a short quake, speed
  lines, flash and cinema bars).
- Flash: caves that need it (and the Battle Pyramid) now show their
  darkness and the circle of light around the player: the GBA's own circle
  in 2D, a soft, flickering pool of light in voxel.
- The title screen shows the developer's logo and the game's version under
  it.
- Voxel (experimental): mountains on Routes 104, 105, 106 and 116 rebuilt
  level by level on the tile grid, and Route 106 joined to Dewford.
- Voxel: sliding doors (Pokémon Centers, Marts, gyms) open as you walk
  through them, by @Trukitro (pull request #17).
- Voxel: more rooms modelled, by @Trukitro (pull request #19): the house
  with a bed, Mr. Briney's house, the Pretty Petal flower shop; the walls of
  21 rooms of the general indoor tileset and Rustboro's school; doorways for
  the stairs of Rustboro's flats, the Devon Corporation, Lilycove's motel,
  the Fossil Maniac's house and the Trick House; Petalburg's gym walls and
  Dewford's gym maze. No furniture is guessed from tile ids any more.
- Voxel: a ledge jump is drawn as an arc, by @Trukitro (pull request #16).
- Voxel: the surf mon lies on the water under the rider, bobbing, with
  shadows; Dewford's small tree is modelled.
- Much less stalling on Old 3DS: a fixed-point sound mixer, faster copies
  and decompression, a performance pass over the voxel field, 3D battles
  and the bottom screen, and the furniture checks of towns done once
  instead of every frame.
- Builder: the scenery generation takes about half as long, with the same
  pack.
- Building from source: `tools/bootstrap.py --make --spanish-rom` builds the
  Spanish game, and a clean tree now builds in one go (from pull request #6,
  Jesus Oliva).

Fixes:

- Stat changes in battle showed no animation, only their sound (2D and
  3D BATTLE).
- Drums played about three times too fast and too high; cymbals, triangles
  and bells now sound as on the GBA.
- The evolution scene showed half a Pokémon on a black screen, by
  @Trukitro (pull request #16).
- The poison step's flash on the field was not drawn; a violet veil stands
  in for it in 2D and voxel, by @Trukitro (pull request #16).
- Voxel: walkers were hidden by furniture against the back wall, by
  @Deunnis (pull request #9, issue #4), and by the Pokémon Center's PC, by
  @Trukitro (pull request #16).
- Voxel: rug borders and wall tops stood up as television sets, beds and
  mats in some rooms, by @Trukitro (pull request #19).
- Voxel: leaving a 3D BATTLE could fall back to 2D.
- The bag's item icon was drawn off its box, under the list.

## 0.2.0 — 2026-10-04

New and improved:

- The game's own menus on the bottom screen, by touch: the party menu (with
  the summary's move screens), the bag, the Pokédex and the PC boxes are the
  original screens, built as a centred picture with the background carried
  to the edges; every action of the originals is reachable by tapping, and
  they run at 60 fps on Old 3DS.
- 3D BATTLE option (off by default, needs VOXEL 3D): battles are drawn in
  front of the voxel world, on level ground found near the player, with the
  camera gliding in from the field's.
- The FPS counter is now the SHOW FPS option of the bottom screen's OPTION
  list: off by default, turn it on there (it used to be always shown).
- Voxel (experimental, still full of errors and under active work): HD-2D look - tilt-shift blur at the top and bottom of the screen
  (3D BLUR option), bloom, sunlit dust, natural sunlight with richer colour,
  sun rays, soft sun dapples that stay on the ground across map crossings,
  lighter tree crowns and softer shadows.
- Voxel: mountains in their true tile shapes, with cut tiles, rock edges that
  follow the rock and flanks that rise across their drawn run; sea rocks and
  boulders modelled once wherever they repeat; Jagged Pass, Mt Chimney and
  Lavaridge read as mountains; Route 106's ledge apart from its plateau.
- Voxel: fog banks lying over the ground and thinning into the distance, and
  a cold, dim light with a dark ring in caves; in 2D the fog covers the whole
  screen and is see-through.
- Voxel: water lies flush with the ground (no line along the shores), tall
  grass rustles on its own tile, the surf mon, grass, "!" icons and splashes
  are drawn, and sprites stand in front of stairs.
- Much less stalling on the console: assets read ahead by a background
  worker, the sound mixer on another core, unchanged layers not walked, New
  3DS at 804 MHz with L2; the voxel frame scheduling, frustum view and chunk
  builds reworked for Old 3DS, draft chunks filling holes at once, animated
  tiles uploading only what changed.
- Builder about 2.5x faster (a full build takes about 6.5 minutes instead of
  15-17) with a byte-identical pack.
- Releases also carry `Emerald3DS.3dsx` and `Emerald3DS.smdh` on their own
  (quick update) and `Emerald3DS-WebPayload.zip` with `web-manifest.json` for
  the web builder; the builder can run the voxel generators in-process (used
  by the web builder), and the Windows ZIP's `LICENSES/` folder again
  includes `LICENSE-PORT.md`, `NOTICE.md` and `AI_DISCLOSURE.md`.
- Optional HOME Menu forwarder, `Emerald3DS-Forwarder.cia`: installed once
  with FBI, it starts the game's 3DSX through Luma3DS without needing the
  Homebrew Launcher title, so updates only replace the 3DSX. The game's own
  icon is the new project icon.
- The SD log is only written when `sdmc:/3ds/emerald3ds/debug.txt` exists;
  `port.log` holds the current session and `port-prev.log` the previous one.

Fixes:

- Voxel: the overworld crashed on the console as soon as the sun dapples
  drew (a null texture unbind that the emulator let pass).
- Voxel: freezes after battles, chunks that stopped loading near Mauville and
  the overworld falling back to 2D on Old 3DS; each option tap froze the game
  for about a second (settings are now saved by their own thread).
- Voxel: sun dapples jumped at every map crossing.
- Voxel: grass floated between tufts and walkers hopped in it.
- Voxel: black gaps at the edges of the view after a crossing.
- 2D: the Surf, Fly and field-move banner left the rest of the field black.
- 2D: Match Call turned the map to garbage while a call lasted.
- 2D: the map name popup peeked in at the bottom of the screen as it slid
  away.
- Items shown by the PC and the like fell outside their frame, and the
  healing machine's balls were not on the machine.
- Graphics that were read past their stubs and never showed: PC wallpapers,
  party menu and summary tilemaps, Deoxys's form icon.
- The starter choice screen was drawn at the top-left of the top screen with
  a teal backdrop beyond the meadow; it is now centred 1:1 with the meadow
  carried to every edge, and the left starter's label (Treecko) keeps its
  darkened box.
- The forwarder hung on a black screen.

## 0.1.2 — 2026-09-30

New and improved:

- PokéNav on the bottom screen, driven by touch: laid out as header, body
  and help bar, a tap moves the cursor straight to the option or entry, and
  the Hoenn map scrolls smoothly.
- 3D slider: the intro and the title screen now have stereo depth, and 2D
  screens keep blended sprites and text windows at their own depth.
- Battle transitions now play in both the classic 2D field and the voxel
  overworld, at full speed on Old 3DS.
- Voxel: the world fades with the screen on warps and battle starts.
- Voxel: characters are drawn at their proper proportions, stand on their
  feet and meet their shadow; the walking bob is kept.
- Voxel: walls and mountain sides facing away from the sun are in shade,
  lit by the same sun as the cast shadows.
- Voxel: newly modelled Rustboro's gym (its statues stand in all eight gyms),
  Oldale's two houses, Mr Briney's cottage and the Pretty Petal flower shop.
- Voxel: every mountain of the general tileset is drawn; Route 116's
  mountain is built from straight faces and one-level steps; stairs, lamps
  and Rustboro's railings stand again.
- Voxel: Route 104's beach and sea are a level below the route, and Routes
  105 and 106 follow them down.
- Intro, title and menus: the margins around the 240x160 picture are made
  from each screen's own art (Rayquaza stands on the bottom edge under a lit
  sky, the Professor's sky reaches the top), and menu screens are centred.
- Title screen and palette fades much smoother on Old 3DS: layer textures
  are redrawn only where they change, and fades are drawn as a tint.
- Installation guide in `docs/INSTALLATION.md`, and bug report and feature
  request forms on GitHub.

Fixes:

- PokéNav tiles and palettes were wrong.
- With the 3D slider up, black screens came out blue and the save selection
  lost its backdrop; the intro's leaves scene slowed down.
- Voxel: sprites went black on their own during warps and battle starts.
- Voxel: cast shadows striped and came apart from the feet.
- Voxel: black gaps along the shores of recessed water (now a rim).
- Voxel: ledges were sunk into a toothed trench; they now sit on the ground
  as on Route 101, and side ledges are no longer striped by the lighting.
- Voxel: Rustboro's lamps against walls did not stand.

## 0.1.1 — 2026-09-27

- The voxel overworld is now off by default. It is switched on from the new
  **VOXEL 3D** row of the bottom-screen OPTION screen.
- While it is on, **3D ANGLE** (34-46 degrees, default 40) and **3D ZOOM**
  (90-120%, default 100%) adjust its camera.
- These settings are kept in `/3ds/emerald3ds/settings.txt` and apply at once,
  without saving the game.
- Classic 2D field: text boxes, prompts and the map name are centred as in
  the voxel view.
- Classic 2D field: much faster on Old 3DS; the backgrounds are kept in
  textures and only the cells that change are redrawn.
- Classic 2D field: sprites just below the view are no longer drawn at the
  top of the screen.

## 0.1 — 2026-09-26 — first public version

- Native ARM11 port of pokeemerald for Nintendo 3DS: GPU compositor at
  native 400x240, NDSP audio, touch and Circle Pad input, SD saves.
- Bottom-screen interface replacing the START menu (map, party, bag, trainer
  card, Pokédex, PokéNav, save, options) and touch battle menus.
- Optional voxel overworld with buildings, trees, signposts and terrain relief
  modelled from each map's own art, fixed-sun lighting and cast shadows.
  The modelled part is still limited: most of the map and nearly all
  interiors are shown flat for now.
- Game data outside the executable: embedded (development), loose files or a
  single `emerald3ds.pak` with ABI and integrity checks.
- Pokémon Emerald 3Ds Dual Screen Builder: generates the data pack from the player's own ROM and
  installs the game on an SD card, with no toolchain or Python required on
  Windows.
