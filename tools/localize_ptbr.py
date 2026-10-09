#!/usr/bin/env python3
"""Stage the PT-BR localization from a user's clean PT-BR ROM.

The checked-in manifest contains source positions and ROM offsets, never game
text or graphics. Run after bootstrap applies the pinned source patches.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "builder"))
from emerald3ds_builder.rom import load_rom

PTBR_SHA1 = "18a2b0acdba046c71b8677bb58c9ee7d36f7a91f"


def encoded(data: bytes) -> str:
    return ",".join("0x%02X" % byte for byte in data)


def ensure_charmap(tree: Path) -> None:
    charmap_path = tree / "charmap.txt"
    if not charmap_path.exists():
        return
    raw = charmap_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    additions = []
    if b"'\xc3\xa3'" not in raw:
        additions.append(b"'\xc3\xa3'         = F4")
    if b"'\xc3\x83'" not in raw:
        additions.append(b"'\xc3\x83'         = F1")
    if b"'\xc3\xb5'" not in raw:
        additions.append(b"'\xc3\xb5'         = F5")
    if b"'\xc3\x95'" not in raw:
        additions.append(b"'\xc3\x95'         = F2")
    if additions:
        raw = raw + b"\n" + b"\n".join(additions) + b"\n"
    charmap_path.write_bytes(raw)
    print("Mapeamentos PT-BR ('ã', 'Ã', 'õ', 'Õ') garantidos em charmap.txt com LF.")


def apply_system_strings(tree: Path) -> None:
    strings_c = tree / "src/strings.c"
    if not strings_c.exists():
        return
    text = strings_c.read_text(encoding="utf-8")

    replacements = {
        'const u8 gText_MainMenuNewGame[] = _("NEW GAME");': 'const u8 gText_MainMenuNewGame[] = _("NOVO JOGO");',
        'const u8 gText_MainMenuContinue[] = _("CONTINUE");': 'const u8 gText_MainMenuContinue[] = _("CONTINUAR");',
        'const u8 gText_MainMenuOption[] = _("OPTION");': 'const u8 gText_MainMenuOption[] = _("OPÇÕES");',
        'const u8 gText_ContinueMenuPlayer[] = _("PLAYER");': 'const u8 gText_ContinueMenuPlayer[] = _("JOGADOR");',
        'const u8 gText_ContinueMenuTime[] = _("TIME");': 'const u8 gText_ContinueMenuTime[] = _("TEMPO");',
        'const u8 gText_ContinueMenuPokedex[] = _("POKéDEX");': 'const u8 gText_ContinueMenuPokedex[] = _("POKéDEX");',
        'const u8 gText_ContinueMenuBadges[] = _("BADGES");': 'const u8 gText_ContinueMenuBadges[] = _("INSÍGNIAS");',
        'const u8 gText_MenuPokedex[] = _("POKéDEX");': 'const u8 gText_MenuPokedex[] = _("POKéDEX");',
        'const u8 gText_MenuPokemon[] = _("POKéMON");': 'const u8 gText_MenuPokemon[] = _("POKéMON");',
        'const u8 gText_MenuBag[] = _("BAG");': 'const u8 gText_MenuBag[] = _("MOCHILA");',
        'const u8 gText_MenuSave[] = _("SAVE");': 'const u8 gText_MenuSave[] = _("SALVAR");',
        'const u8 gText_MenuOption[] = _("OPTION");': 'const u8 gText_MenuOption[] = _("OPÇÃO");',
        'const u8 gText_MenuExit[] = _("EXIT");': 'const u8 gText_MenuExit[] = _("SAIR");',
        'const u8 gText_OptionMenuCancel[] = _("CANCEL");': 'const u8 gText_OptionMenuCancel[] = _("CANCELAR");',
        'const u8 gText_Yes[] = _("YES");': 'const u8 gText_Yes[] = _("SIM");',
        'const u8 gText_No[] = _("NO");': 'const u8 gText_No[] = _("NÃO");',
        'const u8 gText_YesNo[] = _("YES\\nNO");': 'const u8 gText_YesNo[] = _("SIM\\nNÃO");',
        'const u8 gText_Yes2[] = _("YES");': 'const u8 gText_Yes2[] = _("SIM");',
        'const u8 gText_Yes3[] = _("YES");': 'const u8 gText_Yes3[] = _("SIM");',
        'const u8 gText_CloseBag[] = _("CLOSE BAG");': 'const u8 gText_CloseBag[] = _("FECHAR BOLSA");',
        'const u8 gText_ItemsPocket[] = _("ITEMS");': 'const u8 gText_ItemsPocket[] = _("ITENS");',
        'const u8 gText_PokeBallsPocket[] = _("POKé BALLS");': 'const u8 gText_PokeBallsPocket[] = _("POKéBOLAS");',
        'const u8 gText_TMHMPocket[] = _("TMs & HMs");': 'const u8 gText_TMHMPocket[] = _("TMs e HMs");',
        'const u8 gText_BerriesPocket[] = _("BERRIES");': 'const u8 gText_BerriesPocket[] = _("FRUTAS");',
        'const u8 gText_KeyItemsPocket[] = _("KEY ITEMS");': 'const u8 gText_KeyItemsPocket[] = _("ITENS-CHAVE");',
        'const u8 gText_TheField[] = _("the field");': 'const u8 gText_TheField[] = _("campo");',
        'const u8 gText_ReturnToVar1[] = _("Return to\\n{STR_VAR_1}.");': 'const u8 gText_ReturnToVar1[] = _("Voltar ao\\n{STR_VAR_1}.");',
        'const u8 gText_TrainerCardName[] = _("NAME: ");': 'const u8 gText_TrainerCardName[] = _("NOME: ");',
        'const u8 gText_TrainerCardIDNo[] = _("IDNo.");': 'const u8 gText_TrainerCardIDNo[] = _("Nº ID");',
        'const u8 gText_TrainerCardMoney[] = _("MONEY");': 'const u8 gText_TrainerCardMoney[] = _("DINHEIRO");',
        'const u8 gText_TrainerCardTime[] = _("TIME");': 'const u8 gText_TrainerCardTime[] = _("TEMPO");',
        'const u8 gText_SavingBadges[] = _("BADGES");': 'const u8 gText_SavingBadges[] = _("INSÍGNIAS");',
    }

    applied = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            applied += 1

    strings_c.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    print(f"Strings de sistema e menus: {applied}/{len(replacements)} traduzidas com sucesso em src/strings.c.")


def apply_save_strings(tree: Path) -> None:
    save_inc = tree / "data/text/save.inc"
    if not save_inc.exists():
        return
    text = save_inc.read_text(encoding="utf-8")

    replacements = {
        'gText_ConfirmSave::\n\t.string "Would you like to save the game?$"':
        'gText_ConfirmSave::\n\t.string "Deseja salvar o jogo?$"',

        ('gText_AlreadySavedFile::\n'
         '\t.string "There is already a saved file.\\n"\n'
         '\t.string "Is it okay to overwrite it?$"'):
        ('gText_AlreadySavedFile::\n'
         '\t.string "Já existe um arquivo salvo.\\n"\n'
         '\t.string "Sobrescrever o arquivo?$"'),

        ('gText_SavingDontTurnOff::\n'
         '\t.string "SAVING…\\n"\n'
         '\t.string "DON\'T TURN OFF THE POWER.$"'):
        ('gText_SavingDontTurnOff::\n'
         '\t.string "SALVANDO…\\n"\n'
         '\t.string "NÃO DESLIGUE O CONSOLE.$"'),

        'gText_PlayerSavedGame::\n\t.string "{PLAYER} saved the game control.$"':
        'gText_PlayerSavedGame::\n\t.string "{PLAYER} salvou o jogo.$"',

        'gText_PlayerSavedGame::\n\t.string "{PLAYER} saved the game.$"':
        'gText_PlayerSavedGame::\n\t.string "{PLAYER} salvou o jogo.$"',
    }

    applied = 0
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
            applied += 1

    save_inc.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    print(f"Strings de salvamento: {applied}/{len(replacements)} traduzidas em data/text/save.inc.")


def apply_map_strings(tree: Path) -> None:
    # 1. Littleroot Town externa
    littleroot = tree / "data/maps/LittlerootTown/scripts.inc"
    if littleroot.exists():
        text = littleroot.read_text(encoding="utf-8")
        replacements = {
            ('LittlerootTown_Text_OurNewHomeLetsGoInside:\n'
             '\t.string "MOM: {PLAYER}, we\'re here, honey!\\p"\n'
             '\t.string "It must be tiring riding with our things\\n"\n'
             '\t.string "in the moving truck.\\p"\n'
             '\t.string "Well, this is LITTLEROOT TOWN.\\p"\n'
             '\t.string "How do you like it?\\n"\n'
             '\t.string "This is our new home!\\p"\n'
             '\t.string "It has a quaint feel, but it seems to be\\n"\n'
             '\t.string "an easy place to live, don\'t you think?\\p"\n'
             '\t.string "And, you get your own room, {PLAYER}!\\n"\n'
             '\t.string "Let\'s go inside.$"'):
            ('LittlerootTown_Text_OurNewHomeLetsGoInside:\n'
             '\t.string "MÃE: {PLAYER}, nós já chegamos!\\p"\n'
             '\t.string "Deve ser cansativo viajar no caminhão\\n"\n'
             '\t.string "de mudança com todos os móveis…\\p"\n'
             '\t.string "Bem, esta é a bela VILA RAIZ.\\p"\n'
             '\t.string "O quê? Você gostou?\\n"\n'
             '\t.string "Este é o lugar onde vamos morar.\\p"\n'
             '\t.string "É um lugar pitoresco, mas eu acho que\\n"\n'
             '\t.string "você pode viver muito bem aqui.\\p"\n'
             '\t.string "{PLAYER}, você terá o seu próprio quarto.\\n"\n'
             '\t.string "Vamos logo entrar em casa.$"'),

            ('LittlerootTown_Text_TownSign:\n'
             '\t.string "LITTLEROOT TOWN\\n"\n'
             '\t.string "“A town that can\'t be shaded any hue.”$"'):
            ('LittlerootTown_Text_TownSign:\n'
             '\t.string "VILA RAIZ\\n"\n'
             '\t.string "“Uma vila que não se prende a cores.”$"'),

            ('LittlerootTown_Text_ProfBirchsLab:\n'
             '\t.string "PROF. BIRCH\'S POKéMON LAB$"'):
            ('LittlerootTown_Text_ProfBirchsLab:\n'
             '\t.string "LABORATÓRIO DO PROF. BIRCH$"'),

            ('LittlerootTown_Text_PlayersHouse:\n'
             '\t.string "{PLAYER}\'s HOUSE$"'):
            ('LittlerootTown_Text_PlayersHouse:\n'
             '\t.string "CASA DE {PLAYER}$"'),
        }
        applied = 0
        for old, new in replacements.items():
            if old in text:
                text = text.replace(old, new)
                applied += 1
        littleroot.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"Diálogos de Littleroot Town: {applied}/{len(replacements)} traduzidos.")

    # 2. Quarto do Brendan (2F)
    b_2f = tree / "data/maps/LittlerootTown_BrendansHouse_2F/scripts.inc"
    if b_2f.exists():
        text = b_2f.read_text(encoding="utf-8")
        replacements_2f = {
            ('PlayersHouse_2F_Text_ClockIsStopped:\n'
             '\t.string "The clock is stopped…\\p"\n'
             '\t.string "Better set it and start it!$"'):
            ('PlayersHouse_2F_Text_ClockIsStopped:\n'
             '\t.string "O relógio está parado…\\p"\n'
             '\t.string "É melhor ajustá-lo e ligá-lo!$"'),

            ('PlayersHouse_2F_Text_HowDoYouLikeYourRoom:\n'
             '\t.string "MOM: {PLAYER}, how do you like your\\n"\n'
             '\t.string "new room?\\p"\n'
             '\t.string "Good! Everything\'s put away neatly!\\p"\n'
             '\t.string "They finished moving everything in\\n"\n'
             '\t.string "downstairs, too.\\p"\n'
             '\t.string "POKéMON movers are so convenient!\\p"\n'
             '\t.string "Oh, you should make sure that\\n"\n'
             '\t.string "everything\'s all there on your desk.$"'):
            ('PlayersHouse_2F_Text_HowDoYouLikeYourRoom:\n'
             '\t.string "MÃE: {PLAYER}, o que achou do seu\\n"\n'
             '\t.string "novo quarto?\\p"\n'
             '\t.string "Que bom! Tudo está arrumado!\\p"\n'
             '\t.string "Eles já terminaram de descarregar tudo\\n"\n'
             '\t.string "no andar de baixo também.\\p"\n'
             '\t.string "Os POKéMON de mudança são tão prestativos!\\p"\n'
             '\t.string "Ah, não se esqueça de conferir se\\n"\n'
             '\t.string "está tudo certo na sua mesa.$"'),

            ('PlayersHouse_2F_Text_Notebook:\n'
             '\t.string "{PLAYER} flipped open the notebook.\\p"\n'
             '\t.string "ADVENTURE RULE NO. 1\\n"\n'
             '\t.string "Open the MENU with START.\\p"\n'
             '\t.string "ADVENTURE RULE NO. 2\\n"\n'
             '\t.string "Record your progress with SAVE.\\p"\n'
             '\t.string "The remaining pages are blank…$"'):
            ('PlayersHouse_2F_Text_Notebook:\n'
             '\t.string "{PLAYER} abriu o caderno de notas.\\p"\n'
             '\t.string "REGRA DE AVENTURA Nº 1\\n"\n'
             '\t.string "Abra o MENU apertando START.\\p"\n'
             '\t.string "REGRA DE AVENTURA Nº 2\\n"\n'
             '\t.string "Salve seu progresso com SALVAR.\\p"\n'
             '\t.string "As páginas restantes estão em branco…$"'),

            ('PlayersHouse_2F_Text_ItsAGameCube:\n'
             '\t.string "It\'s a Nintendo GameCube.\\p"\n'
             '\t.string "A Game Boy Advance is connected to\\n"\n'
             '\t.string "serve as the Controller.$"'):
            ('PlayersHouse_2F_Text_ItsAGameCube:\n'
             '\t.string "É um Nintendo GameCube.\\p"\n'
             '\t.string "Um Game Boy Advance está conectado\\n"\n'
             '\t.string "para servir como controle.$"'),
        }
        applied = 0
        for old, new in replacements_2f.items():
            if old in text:
                text = text.replace(old, new)
                applied += 1
        b_2f.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"Diálogos de BrendansHouse_2F: {applied}/{len(replacements_2f)} traduzidos.")

    # 3. Térreo do Brendan (1F)
    b_1f = tree / "data/maps/LittlerootTown_BrendansHouse_1F/scripts.inc"
    if b_1f.exists():
        text = b_1f.read_text(encoding="utf-8")
        replacements_1f = {
            ('PlayersHouse_1F_Text_GoSetTheClock:\n'
             '\t.string "MOM: {PLAYER}.\\p"\n'
             '\t.string "Go set the clock in your room, honey.$"'):
            ('PlayersHouse_1F_Text_GoSetTheClock:\n'
             '\t.string "MÃE: {PLAYER}.\\p"\n'
             '\t.string "Vá acertar o relógio no seu quarto, querido.$"'),

            ('PlayersHouse_1F_Text_MoversPokemonGoSetClock:\n'
             '\t.string "The mover\'s POKéMON do all the work\\n"\n'
             '\t.string "of moving us in and cleaning up after.\\l"\n'
             '\t.string "This is so convenient!\\p"\n'
             '\t.string "{PLAYER}, your room is upstairs.\\n"\n'
             '\t.string "Go check it out, dear!\\p"\n'
             '\t.string "DAD bought you a new clock to mark\\n"\n'
             '\t.string "our move here.\\l"\n'
             '\t.string "Don\'t forget to set it!$"'):
            ('PlayersHouse_1F_Text_MoversPokemonGoSetClock:\n'
             '\t.string "Os POKéMON de mudança fizeram todo o trabalho\\n"\n'
             '\t.string "pesado e ainda limparam tudo depois.\\l"\n'
             '\t.string "Isso é tão conveniente!\\p"\n'
             '\t.string "{PLAYER}, o seu quarto fica lá em cima.\\n"\n'
             '\t.string "Vá dar uma olhada, querido!\\p"\n'
             '\t.string "O PAPAI comprou um relógio novo para marcar\\n"\n'
             '\t.string "nossa mudança para cá.\\l"\n'
             '\t.string "Não se esqueça de ajustá-lo!$"'),

            ('PlayersHouse_1F_Text_ArentYouInterestedInRoom:\n'
             '\t.string "MOM: Well, {PLAYER}?\\p"\n'
             '\t.string "Aren\'t you interested in seeing your\\n"\n'
             '\t.string "very own room?$"'):
            ('PlayersHouse_1F_Text_ArentYouInterestedInRoom:\n'
             '\t.string "MÃE: E então, {PLAYER}?\\p"\n'
             '\t.string "Você não quer ver o seu próprio quarto?$"'),

            ('PlayersHouse_1F_Text_OhComeQuickly:\n'
             '\t.string "MOM: Oh! {PLAYER}, {PLAYER}!\\n"\n'
             '\t.string "Quick! Come quickly!$"'):
            ('PlayersHouse_1F_Text_OhComeQuickly:\n'
             '\t.string "MÃE: Ah! {PLAYER}, {PLAYER}!\\n"\n'
             '\t.string "Rápido! Venha depressa!$"'),

            ('PlayersHouse_1F_Text_MaybeDadWillBeOn:\n'
             '\t.string "MOM: Look! It\'s PETALBURG GYM!\\n"\n'
             '\t.string "Maybe DAD will be on!$"'):
            ('PlayersHouse_1F_Text_MaybeDadWillBeOn:\n'
             '\t.string "MÃE: Veja! É o GINÁSIO DE PETALBURG!\\n"\n'
             '\t.string "Talvez o PAPAI vá aparecer!$"'),

            ('PlayersHouse_1F_Text_ItsOverWeMissedHim:\n'
             '\t.string "MOM: Oh… It\'s over.\\p"\n'
             '\t.string "I think DAD was on, but we missed him.\\n"\n'
             '\t.string "Too bad.$"'):
            ('PlayersHouse_1F_Text_ItsOverWeMissedHim:\n'
             '\t.string "MÃE: Ah… Já acabou.\\p"\n'
             '\t.string "Acho que o PAPAI apareceu, mas perdemos.\\n"\n'
             '\t.string "Que pena.$"'),

            ('PlayersHouse_1F_Text_GoIntroduceYourselfNextDoor:\n'
             '\t.string "Oh, yes.\\n"\n'
             '\t.string "One of DAD\'s friends lives in town.\\p"\n'
             '\t.string "PROF. BIRCH is his name.\\p"\n'
             '\t.string "He lives right next door, so you should\\n"\n'
             '\t.string "go over and introduce yourself.$"'):
            ('PlayersHouse_1F_Text_GoIntroduceYourselfNextDoor:\n'
             '\t.string "Ah, é verdade.\\n"\n'
             '\t.string "Um dos amigos do PAPAI mora nesta cidade.\\p"\n'
             '\t.string "O nome dele é PROF. BIRCH.\\p"\n'
             '\t.string "Ele mora bem na casa ao lado, então você deve\\n"\n'
             '\t.string "ir até lá e se apresentar.$"'),

            ('PlayersHouse_1F_Text_IsntItNiceInHere:\n'
             '\t.string "MOM: See, {PLAYER}?\\n"\n'
             '\t.string "Isn\'t it nice in here, too?$"'):
            ('PlayersHouse_1F_Text_IsntItNiceInHere:\n'
             '\t.string "MÃE: Viu só, {PLAYER}?\\n"\n'
             '\t.string "Não é uma gracinha aqui dentro também?$"'),

            ('PlayersHouse_1F_Text_SeeYouHoney:\n'
             '\t.string "MOM: See you, honey!$"'):
            ('PlayersHouse_1F_Text_SeeYouHoney:\n'
             '\t.string "MÃE: Até mais, querido!$"'),

            ('PlayersHouse_1F_Text_DidYouMeetProfBirch:\n'
             '\t.string "MOM: Did you introduce yourself to\\n"\n'
             '\t.string "PROF. BIRCH?$"'):
            ('PlayersHouse_1F_Text_DidYouMeetProfBirch:\n'
             '\t.string "MÃE: Já se apresentou ao\\n"\n'
             '\t.string "PROF. BIRCH?$"'),
        }
        applied = 0
        for old, new in replacements_1f.items():
            if old in text:
                text = text.replace(old, new)
                applied += 1
        b_1f.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"Diálogos de BrendansHouse_1F: {applied}/{len(replacements_1f)} traduzidos.")

    # 4. Casa do Rival / May (1F)
    m_1f = tree / "data/maps/LittlerootTown_MaysHouse_1F/scripts.inc"
    if m_1f.exists():
        text = m_1f.read_text(encoding="utf-8")
        replacements_m1f = {
            ('RivalsHouse_1F_Text_OhYoureTheNewNeighbor:\n'
             '\t.string "Oh, hello. And you are?\\p"\n'
             '\t.string "… … … … … … … … …\\n"\n'
             '\t.string "… … … … … … … … …\\p"\n'
             '\t.string "Oh, you\'re {PLAYER}{KUN}, our new next-door\\n"\n'
             '\t.string "neighbor! Hi!\\p"\n'
             '\t.string "We have a {STR_VAR_1} about the same\\n"\n'
             '\t.string "age as you.\\p"\n'
             '\t.string "Our {STR_VAR_1} was excited about making\\n"\n'
             '\t.string "a new friend.\\p"\n'
             '\t.string "Our {STR_VAR_1} is upstairs, I think.$"'):
            ('RivalsHouse_1F_Text_OhYoureTheNewNeighbor:\n'
             '\t.string "Olá! E quem é você?\\p"\n'
             '\t.string "… … … … … … … … …\\n"\n'
             '\t.string "… … … … … … … … …\\p"\n'
             '\t.string "Ah, você é {PLAYER}{KUN}, nosso vizinho\\n"\n'
             '\t.string "novo ao lado! Olá!\\p"\n'
             '\t.string "Temos uma criança quase da mesma\\n"\n'
             '\t.string "idade que você.\\p"\n'
             '\t.string "Ela estava ansiosa para fazer novas\\n"\n'
             '\t.string "amizades.\\p"\n'
             '\t.string "Acho que ela está no andar de cima.$"'),

            ('RivalsHouse_1F_Text_MayWhoAreYou:\n'
             '\t.string "Huh?\\n"\n'
             '\t.string "Who… Who are you?\\p"\n'
             '\t.string "… … … … … … … …\\n"\n'
             '\t.string "… … … … … … … …\\p"\n'
             '\t.string "Oh, you\'re {PLAYER}{KUN}.\\n"\n'
             '\t.string "So your move was today.\\p"\n'
             '\t.string "Um… I\'m MAY.\\n"\n'
             '\t.string "Glad to meet you!\\p"\n'
             '\t.string "I…\\n"\n'
             '\t.string "I have this dream of becoming friends\\l"\n'
             '\t.string "with POKéMON all over the world.\\p"\n'
             '\t.string "I… I heard about you, {PLAYER}{KUN}, from\\n"\n'
             '\t.string "my dad, PROF. BIRCH.\\p"\n'
             '\t.string "I was hoping that you would be nice,\\n"\n'
             '\t.string "{PLAYER}{KUN}, and that we could be friends.\\p"\n'
             '\t.string "Oh, this is silly, isn\'t it?\\n"\n'
             '\t.string "I… I\'ve just met you, {PLAYER}{KUN}.\\p"\n'
             '\t.string "Eheheh…\\p"\n'
             '\t.string "Oh, no! I forgot!\\p"\n'
             '\t.string "I was supposed to go help Dad catch\\n"\n'
             '\t.string "some wild POKéMON!\\p"\n'
             '\t.string "{PLAYER}{KUN}, I\'ll catch you later!$"'):
            ('RivalsHouse_1F_Text_MayWhoAreYou:\n'
             '\t.string "Hã?\\n"\n'
             '\t.string "Quem… Quem é você?\\p"\n'
             '\t.string "… … … … … … … …\\n"\n'
             '\t.string "… … … … … … … …\\p"\n'
             '\t.string "Ah, você é {PLAYER}{KUN}.\\n"\n'
             '\t.string "Então a mudança era hoje.\\p"\n'
             '\t.string "Hum… Eu sou a MAY.\\n"\n'
             '\t.string "Prazer em te conhecer!\\p"\n'
             '\t.string "Eu…\\n"\n'
             '\t.string "Eu tenho o sonho de fazer amizade\\l"\n'
             '\t.string "com POKéMON do mundo inteiro.\\p"\n'
             '\t.string "Ouvi falar de você, {PLAYER}{KUN}, pelo\\n"\n'
             '\t.string "meu pai, o PROF. BIRCH.\\p"\n'
             '\t.string "Esperava que você fosse legal,\\n"\n'
             '\t.string "{PLAYER}{KUN}, e que seríamos amigos.\\p"\n'
             '\t.string "Nossa, que bobeira falar isso, né?\\n"\n'
             '\t.string "Eu acabei de te conhecer, {PLAYER}{KUN}.\\p"\n'
             '\t.string "Eheheh…\\p"\n'
             '\t.string "Ai, não! Eu esqueci!\\p"\n'
             '\t.string "Eu tinha que ajudar meu pai a pegar\\n"\n'
             '\t.string "alguns POKéMON selvagens!\\p"\n'
             '\t.string "{PLAYER}{KUN}, a gente se vê por aí!$"'),
        }
        applied = 0
        for old, new in replacements_m1f.items():
            if old in text:
                text = text.replace(old, new)
                applied += 1
        m_1f.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"Diálogos de MaysHouse_1F: {applied}/{len(replacements_m1f)} traduzidos.")

    # 5. Laboratório do Prof. Birch
    lab = tree / "data/maps/LittlerootTown_ProfessorBirchsLab/scripts.inc"
    if lab.exists():
        text = lab.read_text(encoding="utf-8")
        replacements_lab = {
            ('LittlerootTown_ProfessorBirchsLab_Text_BirchAwayOnFieldwork:\n'
             '\t.string "Hunh? PROF. BIRCH?\\p"\n'
             '\t.string "The PROF\'s away on fieldwork.\\n"\n'
             '\t.string "Ergo, he isn\'t here.\\p"\n'
             '\t.string "Oh, let me explain what fieldwork is.\\p"\n'
             '\t.string "It is to study things in the natural\\n"\n'
             '\t.string "environment, like fields and mountains,\\l"\n'
             '\t.string "instead of a laboratory.\\p"\n'
             '\t.string "The PROF isn\'t one for doing desk work.\\n"\n'
             '\t.string "He\'s the type of person who would\\l"\n'
             '\t.string "rather go outside and experience\\l"\n'
             '\t.string "things than read about them here.$"'):
            ('LittlerootTown_ProfessorBirchsLab_Text_BirchAwayOnFieldwork:\n'
             '\t.string "Hã? PROF. BIRCH?\\p"\n'
             '\t.string "O PROFESSOR saiu em trabalho de campo.\\n"\n'
             '\t.string "Portanto, ele não está aqui.\\p"\n'
             '\t.string "Ah, deixe-me explicar o que é isso.\\p"\n'
             '\t.string "É estudar as coisas no ambiente natural,\\n"\n'
             '\t.string "como campos e montanhas, em vez de\\l"\n'
             '\t.string "ficar trancado num laboratório.\\p"\n'
             '\t.string "O PROFESSOR não é de ficar em escritório.\\n"\n'
             '\t.string "Ele prefere sair e viver experiências\\l"\n'
             '\t.string "a apenas ler sobre elas aqui dentro.$"'),

            ('LittlerootTown_ProfessorBirchsLab_Text_LikeYouToHavePokemon:\n'
             '\t.string "PROF. BIRCH: So, {PLAYER}{KUN}.\\p"\n'
             '\t.string "I\'ve heard so much about you from\\n"\n'
             '\t.string "your father.\\p"\n'
             '\t.string "I\'ve heard that you don\'t have your\\n"\n'
             '\t.string "own POKéMON yet.\\p"\n'
             '\t.string "But the way you battled earlier,\\n"\n'
             '\t.string "you pulled it off with aplomb!\\p"\n'
             '\t.string "I guess you have your father\'s blood\\n"\n'
             '\t.string "in your veins after all!\\p"\n'
             '\t.string "Oh, yes. As thanks for rescuing me,\\n"\n'
             '\t.string "I\'d like you to have the POKéMON you\\l"\n'
             '\t.string "used earlier.\\p"\n'
             '\t.string "{PLAYER} received the {STR_VAR_1}!$"'):
            ('LittlerootTown_ProfessorBirchsLab_Text_LikeYouToHavePokemon:\n'
             '\t.string "PROF. BIRCH: Então, {PLAYER}{KUN}.\\p"\n'
             '\t.string "Ouvi muito a seu respeito através\\n"\n'
             '\t.string "do seu pai.\\p"\n'
             '\t.string "Fiquei sabendo que você ainda não tem\\n"\n'
             '\t.string "um POKéMON próprio.\\p"\n'
             '\t.string "Mas o jeito como você batalhou antes,\\n"\n'
             '\t.string "foi com grande coragem e maestria!\\p"\n'
             '\t.string "Parece que você tem o sangue do seu pai\\n"\n'
             '\t.string "correndo nas veias, afinal!\\p"\n'
             '\t.string "Ah, sim. Em gratidão por me salvar,\\n"\n'
             '\t.string "gostaria que ficasse com o POKéMON que\\l"\n'
             '\t.string "você usou na batalha.\\p"\n'
             '\t.string "{PLAYER} recebeu {STR_VAR_1}!$"'),

            ('LittlerootTown_ProfessorBirchsLab_Text_WhyNotGiveNicknameToMon:\n'
             '\t.string "PROF. BIRCH: While you\'re at it, why not\\n"\n'
             '\t.string "give a nickname to that {STR_VAR_1}?$"'):
            ('LittlerootTown_ProfessorBirchsLab_Text_WhyNotGiveNicknameToMon:\n'
             '\t.string "PROF. BIRCH: Aproveitando o momento, por que\\n"\n'
             '\t.string "não dá um apelido ao seu {STR_VAR_1}?$"'),
        }
        applied = 0
        for old, new in replacements_lab.items():
            if old in text:
                text = text.replace(old, new)
                applied += 1
        lab.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"Diálogos de ProfessorBirchsLab: {applied}/{len(replacements_lab)} traduzidos.")

    # 6. Rota 101
    r101 = tree / "data/maps/Route101/scripts.inc"
    if r101.exists():
        text = r101.read_text(encoding="utf-8")
        replacements_r101 = {
            ('Route101_Text_HelpMe:\n'
             '\t.string "H-help me!$"'):
            ('Route101_Text_HelpMe:\n'
             '\t.string "S-socorro!$"'),

            ('Route101_Text_PleaseHelp:\n'
             '\t.string "Hello! You over there!\\n"\n'
             '\t.string "Please! Help!\\p"\n'
             '\t.string "In my BAG!\\n"\n'
             '\t.string "There\'s a POKé BALL!$"'):
            ('Route101_Text_PleaseHelp:\n'
             '\t.string "Ei! Você aí!\\n"\n'
             '\t.string "Por favor! Socorro!\\p"\n'
             '\t.string "Na minha BOLSA!\\n"\n'
             '\t.string "Tem uma POKéBOLA!$"'),

            ('Route101_Text_DontLeaveMe:\n'
             '\t.string "Wh-Where are you going?!\\n"\n'
             '\t.string "Don\'t leave me like this!$"'):
            ('Route101_Text_DontLeaveMe:\n'
             '\t.string "O-onde você vai?!\\n"\n'
             '\t.string "Não me deixe aqui sozinho!$"'),

            ('Route101_Text_YouSavedMe:\n'
             '\t.string "PROF. BIRCH: Whew…\\p"\n'
             '\t.string "I was in the tall grass studying wild\\n"\n'
             '\t.string "POKéMON when I was jumped.\\p"\n'
             '\t.string "You saved me.\\n"\n'
             '\t.string "Thanks a lot!\\p"\n'
             '\t.string "Oh?\\p"\n'
             '\t.string "Hi, you\'re {PLAYER}{KUN}!\\p"\n'
             '\t.string "This is not the place to chat, so come\\n"\n'
             '\t.string "by my POKéMON LAB later, okay?$"'):
            ('Route101_Text_YouSavedMe:\n'
             '\t.string "PROF. BIRCH: Ufa…\\p"\n'
             '\t.string "Eu estava na grama alta estudando\\n"\n'
             '\t.string "POKéMON selvagens quando fui atacado.\\p"\n'
             '\t.string "Você me salvou.\\n"\n'
             '\t.string "Muito obrigado!\\p"\n'
             '\t.string "Oh?\\p"\n'
             '\t.string "Olá, você é {PLAYER}{KUN}!\\p"\n'
             '\t.string "Este não é o melhor lugar para conversar,\\n"\n'
             '\t.string "então passe no meu LABORATÓRIO depois, ok?$"'),

            ('Route101_Text_TakeTiredPokemonToPokeCenter:\n'
             '\t.string "If POKéMON get tired, take them to\\n"\n'
             '\t.string "a POKéMON CENTER.\\p"\n'
             '\t.string "There\'s a POKéMON CENTER in OLDALE\\n"\n'
             '\t.string "TOWN right close by.$"'):
            ('Route101_Text_TakeTiredPokemonToPokeCenter:\n'
             '\t.string "Se seus POKéMON ficarem cansados,\\n"\n'
             '\t.string "leve-os a um CENTRO POKéMON.\\p"\n'
             '\t.string "Tem um CENTRO POKéMON bem pertinho,\\n"\n'
             '\t.string "na CIDADE DE OLDALE.$"'),

            ('Route101_Text_WildPokemonInTallGrass:\n'
             '\t.string "Wild POKéMON will jump out at you in\\n"\n'
             '\t.string "tall grass.\\p"\n'
             '\t.string "If you want to catch POKéMON, you have\\n"\n'
             '\t.string "to go into the tall grass and search.$"'):
            ('Route101_Text_WildPokemonInTallGrass:\n'
             '\t.string "POKéMON selvagens pulam em você na\\n"\n'
             '\t.string "grama alta.\\p"\n'
             '\t.string "Se quiser pegar POKéMON, você precisa\\n"\n'
             '\t.string "ir até a grama alta e procurar.$"'),

            ('Route101_Text_RouteSign:\n'
             '\t.string "ROUTE 101\\n"\n'
             '\t.string "{UP_ARROW} OLDALE TOWN$"'):
            ('Route101_Text_RouteSign:\n'
             '\t.string "ROTA 101\\n"\n'
             '\t.string "{UP_ARROW} CIDADE DE OLDALE$"'),
        }
        applied = 0
        for old, new in replacements_r101.items():
            if old in text:
                text = text.replace(old, new)
                applied += 1
        r101.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print(f"Diálogos de Route101: {applied}/{len(replacements_r101)} traduzidos.")


def stage(tree: Path, rom_path: Path) -> None:
    manifest_path = ROOT / "tools/locales/ptbr.json.gz"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    manifest = json.loads(gzip.decompress(manifest_path.read_bytes()))
    rom = load_rom(rom_path, supported=(PTBR_SHA1,))
    source = rom.data

    writes: dict[Path, bytes] = {}
    print(f"Applying PT-BR text localizations to {len(manifest['files'])} files...")

    applied_files = 0
    applied_edits = 0

    for relative, file in manifest["files"].items():
        path = tree / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if hashlib.sha256(text.encode()).hexdigest() != file["sha256"]:
            continue

        previous_end = 0
        valid_edits = []
        for start, end, offset, size, kind in sorted(file["edits"]):
            if previous_end <= start < end <= len(text) and 0 <= offset < offset + size <= len(source):
                valid_edits.append((start, end, offset, size, kind))
                previous_end = end

        for start, end, offset, size, kind in sorted(valid_edits, reverse=True):
            data = source[offset:offset + size]
            if kind == "c":
                replacement = "{" + encoded(data) + "}"
            elif kind == "asm":
                replacement = "\n\t.byte " + encoded(data) + "\n"
            elif kind == "u32":
                replacement = str(struct.unpack("<I", data)[0])
            elif kind == "u16s":
                replacement = ",".join("0x%04X" % n for n in struct.unpack("<6H", data))
            elif kind == "u16array":
                replacement = ",".join("0x%04X" % n for n in struct.unpack("<%dH" % (size // 2), data))
            else:
                replacement = "{" + encoded(data) + "}"

            text = text[:start] + replacement + text[end:]
            applied_edits += 1

        writes[path] = text.replace("\r\n", "\n").encode("utf-8")
        applied_files += 1

    for path, data in writes.items():
        path.write_bytes(data)

    ensure_charmap(tree)
    apply_system_strings(tree)
    apply_save_strings(tree)
    apply_map_strings(tree)

    (tree / ".emerald3ds-locale").write_bytes(b"PTBR stable v3\n")
    print(f"PT-BR staging complete! {applied_edits} edits applied across {applied_files} source files.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    args = parser.parse_args()
    stage(args.tree.resolve(), args.rom)


if __name__ == "__main__":
    main()
