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
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "builder"))
sys.path.insert(0, str(ROOT / "tools"))
from emerald3ds_builder.rom import load_rom
from locales_gym1_to_gym3 import apply_gym1_to_gym3_strings

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


def check_and_apply(path: Path, replacements: dict[str, str], label: str, max_line_len: int = 34) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    applied = 0
    for old, new in replacements.items():
        if old in text:
            # Linter métrico de segurança em tempo de execução
            for m in re.finditer(r'\.string\s+"([^"]*)"', new):
                raw = m.group(1)
                for part in re.split(r'\\[nlp]', raw):
                    clean = re.sub(r'\{[^}]+\}', 'XXXX', part).replace('$', '')
                    if len(clean) > max_line_len:
                        print(f"AVISO METRICO [{label}] linha longa ({len(clean)} > {max_line_len}): '{clean}'")
            text = text.replace(old, new)
            applied += 1
        else:
            # Se já foi aplicado, tudo bem, senão avisa
            pass
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    print(f"[{label}]: {applied}/{len(replacements)} blocos traduzidos com sucesso.")
    return applied


def apply_system_strings(tree: Path) -> None:
    strings_c = tree / "src/strings.c"
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
        'const u8 gText_ShopBuy[] = _("BUY");': 'const u8 gText_ShopBuy[] = _("COMPRAR");',
        'const u8 gText_ShopSell[] = _("SELL");': 'const u8 gText_ShopSell[] = _("VENDER");',
        'const u8 gText_ShopQuit[] = _("QUIT");': 'const u8 gText_ShopQuit[] = _("SAIR");',
        'const u8 gText_InBagVar1[] = _("IN BAG: {STR_VAR_1}");': 'const u8 gText_InBagVar1[] = _("NA BOLSA: {STR_VAR_1}");',
        'const u8 gText_QuitShopping[] = _("Quit shopping.");': 'const u8 gText_QuitShopping[] = _("Sair da loja.");',
        'const u8 gText_Var1CertainlyHowMany[] = _("{STR_VAR_1}? Certainly.\\nHow many would you like?");': 'const u8 gText_Var1CertainlyHowMany[] = _("{STR_VAR_1}? Certamente.\\nQuantos você gostaria?");',
        'const u8 gText_Var1CertainlyHowMany2[] = _("{STR_VAR_1}? Certainly.\\nHow many would you like?");': 'const u8 gText_Var1CertainlyHowMany2[] = _("{STR_VAR_1}? Certamente.\\nQuantos você gostaria?");',
        'const u8 gText_Var1AndYouWantedVar2[] = _("{STR_VAR_1}? And you wanted {STR_VAR_2}?\\nThat will be ¥{STR_VAR_3}.");': 'const u8 gText_Var1AndYouWantedVar2[] = _("{STR_VAR_1}? E você quer {STR_VAR_2}?\\nIsso custará ¥{STR_VAR_3}.");',
        'const u8 gText_Var1IsItThatllBeVar2[] = _("{STR_VAR_1}, is it?\\nThat\'ll be ¥{STR_VAR_2}. Do you want it?");': 'const u8 gText_Var1IsItThatllBeVar2[] = _("{STR_VAR_1}, correto?\\nCusta ¥{STR_VAR_2}. Deseja levar?");',
        'const u8 gText_YouWantedVar1ThatllBeVar2[] = _("You wanted {STR_VAR_1}?\\nThat\'ll be ¥{STR_VAR_2}. Will that be okay?");': 'const u8 gText_YouWantedVar1ThatllBeVar2[] = _("Você quer {STR_VAR_1}?\\nCusta ¥{STR_VAR_2}. Tudo bem?");',
        'const u8 gText_HereYouGoThankYou[] = _("Here you go!\\nThank you very much.");': 'const u8 gText_HereYouGoThankYou[] = _("Aqui está!\\nMuito obrigado.");',
        'const u8 gText_YouDontHaveMoney[] = _("You don\'t have enough money.{PAUSE_UNTIL_PRESS}");': 'const u8 gText_YouDontHaveMoney[] = _("Dinheiro insuficiente.{PAUSE_UNTIL_PRESS}");',
        'const u8 gText_NoMoreRoomForThis[] = _("You have no more room for this\\nitem.{PAUSE_UNTIL_PRESS}");': 'const u8 gText_NoMoreRoomForThis[] = _("Sem espaço na bolsa\\npara este item.{PAUSE_UNTIL_PRESS}");',
        'const u8 gText_AnythingElseICanHelp[] = _("Is there anything else I can help\\nyou with?");': 'const u8 gText_AnythingElseICanHelp[] = _("Posso ajudar em algo\\nmais?");',
        'const u8 gText_CantBuyKeyItem[] = _("{STR_VAR_2}? Oh, no.\\nI can\'t buy that.{PAUSE_UNTIL_PRESS}");': 'const u8 gText_CantBuyKeyItem[] = _("{STR_VAR_2}? Ah, não.\\nNão posso comprar isso.{PAUSE_UNTIL_PRESS}");',
        'const u8 gText_HowManyToSell[] = _("{STR_VAR_2}?\\nHow many would you like to sell?");': 'const u8 gText_HowManyToSell[] = _("{STR_VAR_2}?\\nQuantos deseja vender?");',
        'const u8 gText_ICanPayVar1[] = _("I can pay ¥{STR_VAR_1}.\\nWould that be okay?");': 'const u8 gText_ICanPayVar1[] = _("Posso pagar ¥{STR_VAR_1}.\\nTudo bem?");',
        'const u8 gText_TurnedOverVar1ForVar2[] = _("Turned over the {STR_VAR_2}\\nand received ¥{STR_VAR_1}.");': 'const u8 gText_TurnedOverVar1ForVar2[] = _("Entregou {STR_VAR_2}\\ne recebeu ¥{STR_VAR_1}.");',
        'const u8 gText_Shift[] = _("SHIFT");': 'const u8 gText_Shift[] = _("TROCAR");',
        'const u8 gText_SendOut[] = _("SEND OUT");': 'const u8 gText_SendOut[] = _("ENVIAR");',
        'const u8 gText_Switch2[] = _("SWITCH");': 'const u8 gText_Switch2[] = _("MUDAR");',
        'const u8 gText_Summary5[] = _("SUMMARY");': 'const u8 gText_Summary5[] = _("DADOS");',

        # Pokédex (Modos de listagem, busca e cores)
        'const u8 gText_SearchCompleted[] = _("Search completed.");': 'const u8 gText_SearchCompleted[] = _("Busca concluída.");',
        'const u8 gText_NoMatchingPkmnWereFound[] = _("No matching POKéMON were found.");': 'const u8 gText_NoMatchingPkmnWereFound[] = _("Nenhum POKéMON encontrado.");',
        'const u8 gText_SearchForPkmnBasedOnParameters[] = _("Search for POKéMON based on\\nselected parameters.");': 'const u8 gText_SearchForPkmnBasedOnParameters[] = _("Buscar POKéMON com base nos\\nparâmetros selecionados.");',
        'const u8 gText_SwitchPokedexListings[] = _("Switch POKéDEX listings.");': 'const u8 gText_SwitchPokedexListings[] = _("Mudar listagem da POKéDEX.");',
        'const u8 gText_ReturnToPokedex[] = _("Return to the POKéDEX.");': 'const u8 gText_ReturnToPokedex[] = _("Retornar à POKéDEX.");',
        'const u8 gText_SelectPokedexMode[] = _("Select the POKéDEX mode.");': 'const u8 gText_SelectPokedexMode[] = _("Selecione o modo da POKéDEX.");',
        'const u8 gText_SelectPokedexListingMode[] = _("Select the POKéDEX listing mode.");': 'const u8 gText_SelectPokedexListingMode[] = _("Selecione a listagem da POKéDEX.");',
        'const u8 gText_ListByFirstLetter[] = _("List by the first letter in the name.\\nSpotted POKéMON only.");': 'const u8 gText_ListByFirstLetter[] = _("Listar pela primeira letra do nome.\\nPOKéMON avistados apenas.");',
        'const u8 gText_ListByBodyColor[] = _("List by body color.\\nSpotted POKéMON only.");': 'const u8 gText_ListByBodyColor[] = _("Listar pela cor do corpo.\\nPOKéMON avistados apenas.");',
        'const u8 gText_ListByType[] = _("List by type.\\nOwned POKéMON only.");': 'const u8 gText_ListByType[] = _("Listar por tipo.\\nPOKéMON capturados apenas.");',
        'const u8 gText_ExecuteSearchSwitch[] = _("Execute search/switch.");': 'const u8 gText_ExecuteSearchSwitch[] = _("Executar busca/troca.");',
        'const u8 gText_DexHoennTitle[] = _("HOENN DEX");': 'const u8 gText_DexHoennTitle[] = _("DEX DE HOENN");',
        'const u8 gText_DexNatTitle[] = _("NATIONAL DEX");': 'const u8 gText_DexNatTitle[] = _("DEX NACIONAL");',
        'const u8 gText_DexSortNumericalTitle[] = _("NUMERICAL MODE");': 'const u8 gText_DexSortNumericalTitle[] = _("MODO NUMÉRICO");',
        'const u8 gText_DexSortAtoZTitle[] = _("A TO Z MODE");': 'const u8 gText_DexSortAtoZTitle[] = _("MODO DE A A Z");',
        'const u8 gText_DexSortHeaviestTitle[] = _("HEAVIEST MODE");': 'const u8 gText_DexSortHeaviestTitle[] = _("MODO MAIS PESADO");',
        'const u8 gText_DexSortLightestTitle[] = _("LIGHTEST MODE");': 'const u8 gText_DexSortLightestTitle[] = _("MODO MAIS LEVE");',
        'const u8 gText_DexSortTallestTitle[] = _("TALLEST MODE");': 'const u8 gText_DexSortTallestTitle[] = _("MODO MAIS ALTO");',
        'const u8 gText_DexSortSmallestTitle[] = _("SMALLEST MODE");': 'const u8 gText_DexSortSmallestTitle[] = _("MODO MAIS BAIXO");',
        'const u8 gText_DexSearchColorRed[] = _("RED");': 'const u8 gText_DexSearchColorRed[] = _("VERMELHO");',
        'const u8 gText_DexSearchColorBlue[] = _("BLUE");': 'const u8 gText_DexSearchColorBlue[] = _("AZUL");',
        'const u8 gText_DexSearchColorYellow[] = _("YELLOW");': 'const u8 gText_DexSearchColorYellow[] = _("AMARELO");',
        'const u8 gText_DexSearchColorGreen[] = _("GREEN");': 'const u8 gText_DexSearchColorGreen[] = _("VERDE");',
        'const u8 gText_DexSearchColorBlack[] = _("BLACK");': 'const u8 gText_DexSearchColorBlack[] = _("PRETO");',
        'const u8 gText_DexSearchColorBrown[] = _("BROWN");': 'const u8 gText_DexSearchColorBrown[] = _("MARROM");',
        'const u8 gText_DexSearchColorPurple[] = _("PURPLE");': 'const u8 gText_DexSearchColorPurple[] = _("ROXO");',
        'const u8 gText_DexSearchColorGray[] = _("GRAY");': 'const u8 gText_DexSearchColorGray[] = _("CINZA");',
        'const u8 gText_DexSearchColorWhite[] = _("WHITE");': 'const u8 gText_DexSearchColorWhite[] = _("BRANCO");',
        'const u8 gText_DexSearchColorPink[] = _("PINK");': 'const u8 gText_DexSearchColorPink[] = _("ROSA");',
        'const u8 gText_DexHoennDescription[] = _("HOENN region\'s POKéDEX");': 'const u8 gText_DexHoennDescription[] = _("POKéDEX da região de HOENN");',
        'const u8 gText_DexNatDescription[] = _("National edition POKéDEX");': 'const u8 gText_DexNatDescription[] = _("Edição nacional da POKéDEX");',
        'const u8 gText_DexSortNumericalDescription[] = _("POKéMON are listed according to their\\nnumber.");': 'const u8 gText_DexSortNumericalDescription[] = _("Os POKéMON são listados pelo\\nseu número.");',
        'const u8 gText_DexSortAtoZDescription[] = _("Spotted and owned POKéMON are listed\\nalphabetically.");': 'const u8 gText_DexSortAtoZDescription[] = _("POKéMON avistados e obtidos são\\nlistados em ordem alfabética.");',
        'const u8 gText_DexSortHeaviestDescription[] = _("Owned POKéMON are listed from the\\nheaviest to the lightest.");': 'const u8 gText_DexSortHeaviestDescription[] = _("POKéMON obtidos são listados do\\nmais pesado ao mais leve.");',
        'const u8 gText_DexSortLightestDescription[] = _("Owned POKéMON are listed from the\\nlightest to the heaviest.");': 'const u8 gText_DexSortLightestDescription[] = _("POKéMON obtidos são listados do\\nmais leve ao mais pesado.");',
        'const u8 gText_DexSortTallestDescription[] = _("Owned POKéMON are listed from the\\ntallest to the smallest.");': 'const u8 gText_DexSortTallestDescription[] = _("POKéMON obtidos são listados do\\nmais alto ao mais baixo.");',
        'const u8 gText_DexSortSmallestDescription[] = _("Owned POKéMON are listed from the\\nsmallest to the tallest.");': 'const u8 gText_DexSortSmallestDescription[] = _("POKéMON obtidos são listados do\\nmais baixo ao mais alto.");',
        'const u8 gText_DexSearchDontSpecify[] = _("DON\'T SPECIFY.");': 'const u8 gText_DexSearchDontSpecify[] = _("NÃO ESPECIFICAR.");',
        'const u8 gText_DexSearchTypeNone[] = _("NONE");': 'const u8 gText_DexSearchTypeNone[] = _("NENHUM");',
    }
    check_and_apply(strings_c, replacements, "src/strings.c (Menus e Loja)")


def apply_save_strings(tree: Path) -> None:
    save_inc = tree / "data/text/save.inc"
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

        'gText_PlayerSavedGame::\n\t.string "{PLAYER} saved the game.$"':
        'gText_PlayerSavedGame::\n\t.string "{PLAYER} salvou o jogo.$"',

        'gText_PlayerSavedGame::\n\t.string "{PLAYER} saved the game.$"':
        'gText_PlayerSavedGame::\n\t.string "{PLAYER} salvou o jogo.$"',
    }
    check_and_apply(save_inc, replacements, "data/text/save.inc (Salvamento)")


def apply_nurse_and_mart_strings(tree: Path) -> None:
    nurse_inc = tree / "data/text/pkmn_center_nurse.inc"
    nurse_rep = {
        ('gText_WouldYouLikeToRestYourPkmn::\n'
         '\t.string "Hello, and welcome to\\n"\n'
         '\t.string "the POKéMON CENTER.\\p"\n'
         '\t.string "We restore your tired POKéMON\\n"\n'
         '\t.string "to full health.\\p"\n'
         '\t.string "Would you like to rest your POKéMON?$"'):
        ('gText_WouldYouLikeToRestYourPkmn::\n'
         '\t.string "Olá! Seja bem-vindo ao\\n"\n'
         '\t.string "CENTRO POKéMON.\\p"\n'
         '\t.string "Nós curamos os seus POKéMON\\n"\n'
         '\t.string "completamente.\\p"\n'
         '\t.string "Gostaria de descansar agora?$"'),

        ('gText_IllTakeYourPkmn::\n'
         '\t.string "Okay, I\'ll take your POKéMON\\n"\n'
         '\t.string "for a few seconds.$"'):
        ('gText_IllTakeYourPkmn::\n'
         '\t.string "Certo, cuidarei deles por\\n"\n'
         '\t.string "alguns instantes.$"'),

        ('gText_RestoredPkmnToFullHealth::\n'
         '\t.string "Thank you for waiting.\\p"\n'
         '\t.string "We\'ve restored your POKéMON\\n"\n'
         '\t.string "to full health.$"'):
        ('gText_RestoredPkmnToFullHealth::\n'
         '\t.string "Obrigada por esperar.\\p"\n'
         '\t.string "Seus POKéMON estão com a\\n"\n'
         '\t.string "saúde totalmente restaurada!$"'),

        ('gText_WeHopeToSeeYouAgain::\n'
         '\t.string "We hope to see you again!$"'):
        ('gText_WeHopeToSeeYouAgain::\n'
         '\t.string "Esperamos vê-lo de novo!$"'),

        ('gText_ThankYouForWaiting::\n'
         '\t.string "Thank you for waiting.$"'):
        ('gText_ThankYouForWaiting::\n'
         '\t.string "Obrigada por esperar.$"'),
    }
    check_and_apply(nurse_inc, nurse_rep, "data/text/pkmn_center_nurse.inc (Enfermeira Joy)")

    clerk_inc = tree / "data/text/mart_clerk.inc"
    clerk_rep = {
        ('gText_HowMayIServeYou::\n'
         '\t.string "Welcome!\\p"\n'
         '\t.string "How may I serve you?$"'):
        ('gText_HowMayIServeYou::\n'
         '\t.string "Seja bem-vindo!\\p"\n'
         '\t.string "Como posso ajudá-lo?$"'),

        ('gText_PleaseComeAgain::\n'
         '\t.string "Please come again!$"'):
        ('gText_PleaseComeAgain::\n'
         '\t.string "Volte sempre!$"'),

        ('gText_PlayerWhatCanIDoForYou::\n'
         '\t.string "{PLAYER}{STRING 5}, welcome!\\p"\n'
         '\t.string "What can I do for you?$"'):
        ('gText_PlayerWhatCanIDoForYou::\n'
         '\t.string "{PLAYER}{STRING 5}, olá!\\p"\n'
         '\t.string "Como posso ajudar você?$"'),
    }
    check_and_apply(clerk_inc, clerk_rep, "data/text/mart_clerk.inc (Balconista Mart)")


def apply_battle_strings(tree: Path) -> None:
    battle_c = tree / "src/battle_message.c"
    replacements = {
        'const u8 gText_BattleMenu[] = _("FIGHT{CLEAR_TO 56}BAG\\nPOKéMON{CLEAR_TO 56}RUN");':
        'const u8 gText_BattleMenu[] = _("LUTAR{CLEAR_TO 56}MOCHILA\\nPOKéMON{CLEAR_TO 56}FUGIR");',

        'const u8 gText_WhatWillPkmnDo[] = _("What will\\n{B_ACTIVE_NAME_WITH_PREFIX} do?");':
        'const u8 gText_WhatWillPkmnDo[] = _("O que\\n{B_ACTIVE_NAME_WITH_PREFIX} fará?");',

        'const u8 gText_WhatWillPkmnDo2[] = _("What will\\n{B_PLAYER_NAME} do?");':
        'const u8 gText_WhatWillPkmnDo2[] = _("O que\\n{B_PLAYER_NAME} fará?");',

        'static const u8 sText_PkmnGainedEXP[] = _("{B_BUFF1} gained{B_BUFF2}\\n{B_BUFF3} EXP. Points!\\p");':
        'static const u8 sText_PkmnGainedEXP[] = _("{B_BUFF1} ganhou{B_BUFF2}\\n{B_BUFF3} pontos de EXP.!\\p");',

        'static const u8 sText_PkmnGrewToLv[] = _("{B_BUFF1} grew to\\nLV. {B_BUFF2}!{WAIT_SE}\\p");':
        'static const u8 sText_PkmnGrewToLv[] = _("{B_BUFF1} subiu para o\\nNÍVEL {B_BUFF2}!{WAIT_SE}\\p");',

        'static const u8 sText_PkmnLearnedMove[] = _("{B_BUFF1} learned\\n{B_BUFF2}!{WAIT_SE}\\p");':
        'static const u8 sText_PkmnLearnedMove[] = _("{B_BUFF1} aprendeu\\n{B_BUFF2}!{WAIT_SE}\\p");',

        'static const u8 sText_AttackerFainted[] = _("{B_ATK_NAME_WITH_PREFIX}\\nfainted!\\p");':
        'static const u8 sText_AttackerFainted[] = _("{B_ATK_NAME_WITH_PREFIX}\\ndesmaiou!\\p");',

        'static const u8 sText_TargetFainted[] = _("{B_DEF_NAME_WITH_PREFIX}\\nfainted!\\p");':
        'static const u8 sText_TargetFainted[] = _("{B_DEF_NAME_WITH_PREFIX}\\ndesmaiou!\\p");',

        'static const u8 sText_PlayerGotMoney[] = _("{B_PLAYER_NAME} got ¥{B_BUFF1}\\nfor winning!\\p");':
        'static const u8 sText_PlayerGotMoney[] = _("{B_PLAYER_NAME} ganhou ¥{B_BUFF1}\\npela vitória!\\p");',

        'static const u8 sText_CriticalHit[] = _("A critical hit!");':
        'static const u8 sText_CriticalHit[] = _("Um golpe crítico!");',

        'static const u8 sText_SuperEffective[] = _("It\'s super effective!");':
        'static const u8 sText_SuperEffective[] = _("Foi super efetivo!");',

        'static const u8 sText_NotVeryEffective[] = _("It\'s not very effective…");':
        'static const u8 sText_NotVeryEffective[] = _("Não foi muito efetivo…");',

        'static const u8 sText_GotAwaySafely[] = _("{PLAY_SE SE_FLEE}Got away safely!\\p");':
        'static const u8 sText_GotAwaySafely[] = _("{PLAY_SE SE_FLEE}Fugiu com segurança!\\p");',

        'static const u8 sText_WildPkmnAppeared[] = _("Wild {B_OPPONENT_MON1_NAME} appeared!\\p");':
        'static const u8 sText_WildPkmnAppeared[] = _("Apareceu {B_OPPONENT_MON1_NAME}\\nselvagem!\\p");',

        'static const u8 sText_Trainer1WantsToBattle[] = _("{B_TRAINER1_CLASS} {B_TRAINER1_NAME}\\nwould like to battle!\\p");':
        'static const u8 sText_Trainer1WantsToBattle[] = _("{B_TRAINER1_CLASS} {B_TRAINER1_NAME}\\nquer batalhar!\\p");',

        'static const u8 sText_Trainer1SentOutPkmn[] = _("{B_TRAINER1_CLASS} {B_TRAINER1_NAME} sent\\nout {B_OPPONENT_MON1_NAME}!");':
        'static const u8 sText_Trainer1SentOutPkmn[] = _("{B_TRAINER1_CLASS} {B_TRAINER1_NAME} enviou\\n{B_OPPONENT_MON1_NAME}!");',

        'static const u8 sText_GoPkmn[] = _("Go! {B_PLAYER_MON1_NAME}!");':
        'static const u8 sText_GoPkmn[] = _("Vai! {B_PLAYER_MON1_NAME}!");',

        'static const u8 sText_AttackerUsedX[] = _("{B_ATK_NAME_WITH_PREFIX} used\\n{B_BUFF2}");':
        'static const u8 sText_AttackerUsedX[] = _("{B_ATK_NAME_WITH_PREFIX} usou\\n{B_BUFF2}");',

        # Mensagens de batalha (v5)
        'static const u8 sText_AttackMissed[] = _("{B_ATK_NAME_WITH_PREFIX}\'s\\nattack missed!");':
        'static const u8 sText_AttackMissed[] = _("{B_ATK_NAME_WITH_PREFIX}\\nerrou o ataque!");',

        'static const u8 sText_PkmnEnergyDrained[] = _("{B_DEF_NAME_WITH_PREFIX} had its\\nenergy drained!");':
        'static const u8 sText_PkmnEnergyDrained[] = _("{B_DEF_NAME_WITH_PREFIX} teve sua\\nenergia drenada!");',

        'static const u8 sText_WildPkmnPrefix[] = _("Wild ");':
        'static const u8 sText_WildPkmnPrefix[] = _("");',

        'static const u8 sText_FoePkmnPrefix[] = _("Foe ");':
        'static const u8 sText_FoePkmnPrefix[] = _("");',

        'static const u8 sText_FoePkmnPrefix2[] = _("Foe");':
        'static const u8 sText_FoePkmnPrefix2[] = _("");',

        'static const u8 sText_FoePkmnPrefix3[] = _("Foe");':
        'static const u8 sText_FoePkmnPrefix3[] = _("");',

        'static const u8 sText_FoePkmnPrefix4[] = _("Foe");':
        'static const u8 sText_FoePkmnPrefix4[] = _("");',

        'static const u8 sText_PkmnProtectedItself[] = _("{B_DEF_NAME_WITH_PREFIX}\\nprotected itself!");':
        'static const u8 sText_PkmnProtectedItself[] = _("{B_DEF_NAME_WITH_PREFIX}\\nprotegeu-se!");',

        'static const u8 sText_AvoidedDamage[] = _("{B_DEF_NAME_WITH_PREFIX} avoided\\ndamage with {B_DEF_ABILITY}!");':
        'static const u8 sText_AvoidedDamage[] = _("{B_DEF_NAME_WITH_PREFIX} evitou\\ndano com {B_DEF_ABILITY}!");',

        'static const u8 sText_PkmnAvoidedAttack[] = _("{B_DEF_NAME_WITH_PREFIX} avoided\\nthe attack!");':
        'static const u8 sText_PkmnAvoidedAttack[] = _("{B_DEF_NAME_WITH_PREFIX} evitou\\no ataque!");',

        'static const u8 sText_ItDoesntAffect[] = _("It doesn\'t affect\\n{B_DEF_NAME_WITH_PREFIX}…");':
        'static const u8 sText_ItDoesntAffect[] = _("Não afetou\\n{B_DEF_NAME_WITH_PREFIX}…");',

        'static const u8 sText_HitXTimes[] = _("Hit {B_BUFF1} time(s)!");':
        'static const u8 sText_HitXTimes[] = _("Acertou {B_BUFF1} vez(es)!");',

        'static const u8 sText_PkmnFellAsleep[] = _("{B_EFF_NAME_WITH_PREFIX}\\nfell asleep!");':
        'static const u8 sText_PkmnFellAsleep[] = _("{B_EFF_NAME_WITH_PREFIX}\\nadormeceu!");',

        'static const u8 sText_PkmnAlreadyAsleep[] = _("{B_DEF_NAME_WITH_PREFIX} is\\nalready asleep!");':
        'static const u8 sText_PkmnAlreadyAsleep[] = _("{B_DEF_NAME_WITH_PREFIX} já\\nestá dormindo!");',

        'static const u8 sText_PkmnWasntAffected[] = _("{B_DEF_NAME_WITH_PREFIX}\\nwasn\'t affected!");':
        'static const u8 sText_PkmnWasntAffected[] = _("{B_DEF_NAME_WITH_PREFIX}\\nnão foi afetado!");',

        'static const u8 sText_PkmnWasPoisoned[] = _("{B_EFF_NAME_WITH_PREFIX}\\nwas poisoned!");':
        'static const u8 sText_PkmnWasPoisoned[] = _("{B_EFF_NAME_WITH_PREFIX}\\nfoi envenenado!");',

        'static const u8 sText_PkmnHurtByPoison[] = _("{B_ATK_NAME_WITH_PREFIX} is hurt\\nby poison!");':
        'static const u8 sText_PkmnHurtByPoison[] = _("{B_ATK_NAME_WITH_PREFIX} sofreu\\ncom o veneno!");',

        'static const u8 sText_PkmnAlreadyPoisoned[] = _("{B_DEF_NAME_WITH_PREFIX} is already\\npoisoned.");':
        'static const u8 sText_PkmnAlreadyPoisoned[] = _("{B_DEF_NAME_WITH_PREFIX} já\\nestá envenenado.");',

        'static const u8 sText_PkmnBadlyPoisoned[] = _("{B_EFF_NAME_WITH_PREFIX} is badly\\npoisoned!");':
        'static const u8 sText_PkmnBadlyPoisoned[] = _("{B_EFF_NAME_WITH_PREFIX} foi gravemente\\nenvenenado!");',

        'static const u8 sText_PkmnWasBurned[] = _("{B_EFF_NAME_WITH_PREFIX} was burned!");':
        'static const u8 sText_PkmnWasBurned[] = _("{B_EFF_NAME_WITH_PREFIX}\\nfoi queimado!");',

        'static const u8 sText_PkmnHurtByBurn[] = _("{B_ATK_NAME_WITH_PREFIX} is hurt\\nby its burn!");':
        'static const u8 sText_PkmnHurtByBurn[] = _("{B_ATK_NAME_WITH_PREFIX} sofreu com\\na queimadura!");',

        'static const u8 sText_PkmnAlreadyHasBurn[] = _("{B_DEF_NAME_WITH_PREFIX} already\\nhas a burn.");':
        'static const u8 sText_PkmnAlreadyHasBurn[] = _("{B_DEF_NAME_WITH_PREFIX} já está\\nqueimado.");',

        'static const u8 sText_PkmnWasParalyzed[] = _("{B_EFF_NAME_WITH_PREFIX} is paralyzed!\\nIt may be unable to move!");':
        'static const u8 sText_PkmnWasParalyzed[] = _("{B_EFF_NAME_WITH_PREFIX} está paralisado!\\nPode não se mover!");',

        'static const u8 sText_PkmnIsParalyzed[] = _("{B_ATK_NAME_WITH_PREFIX} is paralyzed!\\nIt can\'t move!");':
        'static const u8 sText_PkmnIsParalyzed[] = _("{B_ATK_NAME_WITH_PREFIX} está paralisado!\\nNão pode se mover!");',

        'static const u8 sText_PkmnIsConfused[] = _("{B_ATK_NAME_WITH_PREFIX} is\\nconfused!");':
        'static const u8 sText_PkmnIsConfused[] = _("{B_ATK_NAME_WITH_PREFIX} está\\nconfuso!");',

        'static const u8 sText_PkmnHealedConfusion[] = _("{B_ATK_NAME_WITH_PREFIX} snapped\\nout of confusion!");':
        'static const u8 sText_PkmnHealedConfusion[] = _("{B_ATK_NAME_WITH_PREFIX} curou-se\\nda confusão!");',

        'static const u8 sText_PkmnWasConfused[] = _("{B_EFF_NAME_WITH_PREFIX} became\\nconfused!");':
        'static const u8 sText_PkmnWasConfused[] = _("{B_EFF_NAME_WITH_PREFIX} ficou\\nconfuso!");',

        'static const u8 sText_ItHurtConfusion[] = _("It hurt itself in its\\nconfusion!");':
        'static const u8 sText_ItHurtConfusion[] = _("{B_ATK_NAME_WITH_PREFIX} feriu-se\\nna sua confusão!");',

        'static const u8 sText_PkmnFlinched[] = _("{B_ATK_NAME_WITH_PREFIX} flinched!");':
        'static const u8 sText_PkmnFlinched[] = _("{B_ATK_NAME_WITH_PREFIX} hesitou!");',

        'static const u8 sText_PkmnHitWithRecoil[] = _("{B_ATK_NAME_WITH_PREFIX} is hit\\nwith recoil!");':
        'static const u8 sText_PkmnHitWithRecoil[] = _("{B_ATK_NAME_WITH_PREFIX} sofreu dano\\nde recuo!");',

        'static const u8 sText_StatsWontIncrease[] = _("{B_ATK_NAME_WITH_PREFIX}\'s {B_BUFF1}\\nwon\'t go higher!");':
        'static const u8 sText_StatsWontIncrease[] = _("{B_BUFF1} de {B_ATK_NAME_WITH_PREFIX}\\nnão subirá mais!");',

        'static const u8 sText_StatsWontDecrease[] = _("{B_DEF_NAME_WITH_PREFIX}\'s {B_BUFF1}\\nwon\'t go lower!");':
        'static const u8 sText_StatsWontDecrease[] = _("{B_BUFF1} de {B_DEF_NAME_WITH_PREFIX}\\nnão cairá mais!");',

        'static const u8 sText_PkmnRegainedHealth[] = _("{B_DEF_NAME_WITH_PREFIX} regained\\nhealth!");':
        'static const u8 sText_PkmnRegainedHealth[] = _("{B_DEF_NAME_WITH_PREFIX} recuperou\\nsaúde!");',

        'static const u8 sText_PkmnHPFull[] = _("{B_DEF_NAME_WITH_PREFIX}\'s\\nHP is full!");':
        'static const u8 sText_PkmnHPFull[] = _("O HP de\\n{B_DEF_NAME_WITH_PREFIX} está cheio!");',

        'static const u8 sText_NoRunningFromTrainers[] = _("No! There\'s no running\\nfrom a TRAINER battle!\\p");':
        'static const u8 sText_NoRunningFromTrainers[] = _("Não! Não pode fugir\\nde batalha de TREINADOR!\\p");',

        'static const u8 sText_CantEscape[] = _("Can\'t escape!\\p");':
        'static const u8 sText_CantEscape[] = _("Não pode fugir!\\p");',

        'static const u8 sText_CantEscape2[] = _("Can\'t escape!\\p");':
        'static const u8 sText_CantEscape2[] = _("Não pode fugir!\\p");',

        'static const u8 sText_PlayerWhiteout[] = _("{B_PLAYER_NAME} is out of\\nusable POKéMON!\\p");':
        'static const u8 sText_PlayerWhiteout[] = _("{B_PLAYER_NAME} não tem mais\\nPOKéMON utilizáveis!\\p");',

        'static const u8 sText_PlayerWhiteout2[] = _("{B_PLAYER_NAME} whited out!{PAUSE_UNTIL_PRESS}");':
        'static const u8 sText_PlayerWhiteout2[] = _("{B_PLAYER_NAME} desmaiou!{PAUSE_UNTIL_PRESS}");',

        'static const u8 sText_StatSharply[] = _("sharply ");':
        'static const u8 sText_StatSharply[] = _("drasticamente ");',

        'const u8 gText_StatRose[] = _("rose!");':
        'const u8 gText_StatRose[] = _("subiu!");',

        'static const u8 sText_StatHarshly[] = _("harshly ");':
        'static const u8 sText_StatHarshly[] = _("drasticamente ");',

        'static const u8 sText_StatFell[] = _("fell!");':
        'static const u8 sText_StatFell[] = _("caiu!");',

        'static const u8 sText_AttackersStatRose[] = _("{B_ATK_NAME_WITH_PREFIX}\'s {B_BUFF1}\\n{B_BUFF2}");':
        'static const u8 sText_AttackersStatRose[] = _("{B_BUFF1} de\\n{B_ATK_NAME_WITH_PREFIX} {B_BUFF2}");',

        'const u8 gText_DefendersStatRose[] = _("{B_DEF_NAME_WITH_PREFIX}\'s {B_BUFF1}\\n{B_BUFF2}");':
        'const u8 gText_DefendersStatRose[] = _("{B_BUFF1} de\\n{B_DEF_NAME_WITH_PREFIX} {B_BUFF2}");',

        'static const u8 sText_AttackersStatFell[] = _("{B_ATK_NAME_WITH_PREFIX}\'s {B_BUFF1}\\n{B_BUFF2}");':
        'static const u8 sText_AttackersStatFell[] = _("{B_BUFF1} de\\n{B_ATK_NAME_WITH_PREFIX} {B_BUFF2}");',

        'static const u8 sText_DefendersStatFell[] = _("{B_DEF_NAME_WITH_PREFIX}\'s {B_BUFF1}\\n{B_BUFF2}");':
        'static const u8 sText_DefendersStatFell[] = _("{B_BUFF1} de\\n{B_DEF_NAME_WITH_PREFIX} {B_BUFF2}");',

        'static const u8 sText_Attack2[] = _("ATTACK");':
        'static const u8 sText_Attack2[] = _("ATAQUE");',

        'static const u8 sText_Defense2[] = _("DEFENSE");':
        'static const u8 sText_Defense2[] = _("DEFESA");',

        'static const u8 sText_Speed[] = _("SPEED");':
        'static const u8 sText_Speed[] = _("VELOCIDADE");',

        'static const u8 sText_SpAtk2[] = _("SP. ATK");':
        'static const u8 sText_SpAtk2[] = _("ATQ. ESP.");',

        'static const u8 sText_SpDef2[] = _("SP. DEF");':
        'static const u8 sText_SpDef2[] = _("DEF. ESP.");',

        'static const u8 sText_Accuracy[] = _("accuracy");':
        'static const u8 sText_Accuracy[] = _("precisão");',

        'static const u8 sText_Evasiveness[] = _("evasiveness");':
        'static const u8 sText_Evasiveness[] = _("evasão");',
    }
    check_and_apply(battle_c, replacements, "src/battle_message.c (Batalhas)")


def apply_item_and_berry_strings(tree: Path) -> None:
    # 1. Obter itens
    p_item = tree / "data/text/obtain_item.inc"
    rep_item = {
        ('gText_ObtainedTheItem::\n'
         '\t.string "Obtained the {STR_VAR_2}!$"'):
        ('gText_ObtainedTheItem::\n'
         '\t.string "Obteve {STR_VAR_2}!$"'),

        ('gText_TheBagIsFull::\n'
         '\t.string "The BAG is full…$"'):
        ('gText_TheBagIsFull::\n'
         '\t.string "A MOCHILA está cheia…$"'),

        ('gText_PutItemInPocket::\n'
         '\t.string "{PLAYER} put away the {STR_VAR_2}\\n"\n'
         '\t.string "in the {STR_VAR_3} POCKET.$"'):
        ('gText_PutItemInPocket::\n'
         '\t.string "{PLAYER} guardou {STR_VAR_2}\\n"\n'
         '\t.string "no BOLSO de {STR_VAR_3}.$"'),

        ('gText_PlayerFoundOneItem::\n'
         '\t.string "{PLAYER} found one {STR_VAR_2}!$"'):
        ('gText_PlayerFoundOneItem::\n'
         '\t.string "{PLAYER} encontrou {STR_VAR_2}!$"'),

        ('gText_TooBadBagIsFull::\n'
         '\t.string "Too bad!\\n"\n'
         '\t.string "The BAG is full…$"'):
        ('gText_TooBadBagIsFull::\n'
         '\t.string "Que pena!\\n"\n'
         '\t.string "A MOCHILA está cheia…$"'),

        ('gText_PlayerPutItemInBag::\n'
         '\t.string "{PLAYER} put away the {STR_VAR_2}\\n"\n'
         '\t.string "in the BAG.$"'):
        ('gText_PlayerPutItemInBag::\n'
         '\t.string "{PLAYER} guardou {STR_VAR_2}\\n"\n'
         '\t.string "na MOCHILA.$"'),

        ('gText_ObtainedTheDecor::\n'
         '\t.string "Obtained the {STR_VAR_2}!$"'):
        ('gText_ObtainedTheDecor::\n'
         '\t.string "Obteve a decoração\\n"\n'
         '\t.string "{STR_VAR_2}!$"'),

        ('gText_NoRoomLeftForAnother::\n'
         '\t.string "Too bad! There\'s no room left for\\n"\n'
         '\t.string "another {STR_VAR_2}…$"'):
        ('gText_NoRoomLeftForAnother::\n'
         '\t.string "Que pena! Sem espaço para\\n"\n'
         '\t.string "outro {STR_VAR_2}…$"'),

        ('gText_TheDecorWasTransferredToThePC::\n'
         '\t.string "The {STR_VAR_2} was transferred\\n"\n'
         '\t.string "to the PC.$"'):
        ('gText_TheDecorWasTransferredToThePC::\n'
         '\t.string "{STR_VAR_2} foi enviado\\n"\n'
         '\t.string "para o PC.$"'),
    }
    check_and_apply(p_item, rep_item, "data/text/obtain_item.inc (Obter Itens)")

    # 2. Plantio e colheita de frutas
    p_berry = tree / "data/scripts/berry_tree.inc"
    rep_berry = {
        ('BerryTree_Text_ItsSoftLoamySoil:\n'
         '\t.string "It\'s soft, loamy soil.$"'):
        ('BerryTree_Text_ItsSoftLoamySoil:\n'
         '\t.string "É uma terra macia e fértil.$"'),

        ('BerryTree_Text_WantToPlant:\n'
         '\t.string "It\'s soft, loamy soil.\\n"\n'
         '\t.string "Want to plant a BERRY?$"'):
        ('BerryTree_Text_WantToPlant:\n'
         '\t.string "É uma terra macia e fértil.\\n"\n'
         '\t.string "Quer plantar uma FRUTA?$"'),

        ('BerryTree_Text_PlantedOneBerry:\n'
         '\t.string "{PLAYER} planted one {STR_VAR_1} in\\n"\n'
         '\t.string "the soft, loamy soil.$"'):
        ('BerryTree_Text_PlantedOneBerry:\n'
         '\t.string "{PLAYER} plantou uma {STR_VAR_1}\\n"\n'
         '\t.string "na terra macia e fértil.$"'),

        ('BerryTree_Text_BerryGrowthStage1:\n'
         '\t.string "One {STR_VAR_1} was planted here.$"'):
        ('BerryTree_Text_BerryGrowthStage1:\n'
         '\t.string "Uma {STR_VAR_1} foi plantada aqui.$"'),

        ('BerryTree_Text_BerryGrowthStage2:\n'
         '\t.string "{STR_VAR_1} has sprouted.$"'):
        ('BerryTree_Text_BerryGrowthStage2:\n'
         '\t.string "{STR_VAR_1} brotou.$"'),

        ('BerryTree_Text_BerryGrowthStage3:\n'
         '\t.string "This {STR_VAR_1} plant is growing taller.$"'):
        ('BerryTree_Text_BerryGrowthStage3:\n'
         '\t.string "Esta planta de {STR_VAR_1} cresceu.$"'),

        ('BerryTree_Text_BerryGrowthStage4:\n'
         '\t.string "These {STR_VAR_1} flowers are blooming\\n"\n'
         '\t.string "{STR_VAR_2}.$"'):
        ('BerryTree_Text_BerryGrowthStage4:\n'
         '\t.string "Flores de {STR_VAR_1} estão\\n"\n'
         '\t.string "desabrochando {STR_VAR_2}.$"'),

        ('BerryTree_Text_WantToPick:\n'
         '\t.string "You found {STR_VAR_2} {STR_VAR_1}!\\p"\n'
         '\t.string "Do you want to pick the\\n"\n'
         '\t.string "{STR_VAR_1}?$"'):
        ('BerryTree_Text_WantToPick:\n'
         '\t.string "Encontrou {STR_VAR_2} {STR_VAR_1}!\\p"\n'
         '\t.string "Quer colher a\\n"\n'
         '\t.string "{STR_VAR_1}?$"'),

        ('BerryTree_Text_PickedTheBerry:\n'
         '\t.string "{PLAYER} picked the {STR_VAR_2} {STR_VAR_1}.$"'):
        ('BerryTree_Text_PickedTheBerry:\n'
         '\t.string "{PLAYER} colheu {STR_VAR_2} {STR_VAR_1}.$"'),

        ('BerryTree_Text_PutAwayBerry:\n'
         '\t.string "{PLAYER} put away the {STR_VAR_1}\\n"\n'
         '\t.string "in the BAG\'s BERRIES POCKET.\\p"\n'
         '\t.string "The soil returned to its soft and\\n"\n'
         '\t.string "loamy state.$"'):
        ('BerryTree_Text_PutAwayBerry:\n'
         '\t.string "{PLAYER} guardou {STR_VAR_1}\\n"\n'
         '\t.string "no BOLSO DE FRUTAS da MOCHILA.\\p"\n'
         '\t.string "A terra voltou ao seu estado\\n"\n'
         '\t.string "macio e fértil.$"'),

        ('BerryTree_Text_BerryPocketFull:\n'
         '\t.string "The BAG\'s BERRIES POCKET is full.\\p"\n'
         '\t.string "The {STR_VAR_1} couldn\'t be taken.$"'):
        ('BerryTree_Text_BerryPocketFull:\n'
         '\t.string "O BOLSO DE FRUTAS está cheio.\\p"\n'
         '\t.string "A {STR_VAR_1} não pôde ser pega.$"'),

        ('BerryTree_Text_BerryLeftUnpicked:\n'
         '\t.string "{PLAYER} left the {STR_VAR_1}\\n"\n'
         '\t.string "unpicked.$"'):
        ('BerryTree_Text_BerryLeftUnpicked:\n'
         '\t.string "{PLAYER} deixou a {STR_VAR_1}\\n"\n'
         '\t.string "sem colher.$"'),

        ('BerryTree_Text_WantToWater:\n'
         '\t.string "Want to water the {STR_VAR_1} with the\\n"\n'
         '\t.string "WAILMER PAIL?$"'):
        ('BerryTree_Text_WantToWater:\n'
         '\t.string "Quer regar a {STR_VAR_1} com o\\n"\n'
         '\t.string "BALDE WAILMER?$"'),

        ('BerryTree_Text_WateredTheBerry:\n'
         '\t.string "{PLAYER} watered the {STR_VAR_1}.$"'):
        ('BerryTree_Text_WateredTheBerry:\n'
         '\t.string "{PLAYER} regou a {STR_VAR_1}.$"'),

        ('BerryTree_Text_PlantIsDelighted:\n'
         '\t.string "The plant seems to be delighted.$"'):
        ('BerryTree_Text_PlantIsDelighted:\n'
         '\t.string "A planta parece contente.$"'),
    }
    check_and_apply(p_berry, rep_berry, "data/scripts/berry_tree.inc (Frutas)")


def apply_widescreen_battle_layout(tree: Path) -> None:
    p = tree / "src/battle_interface.c"
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    old_block = """void InitBattlerHealthboxCoords(u8 battler)
{
    s16 x = 0, y = 0;

    if (!IsDoubleBattle())
    {
        if (GetBattlerSide(battler) != B_SIDE_PLAYER)
            x = 44, y = 30;
        else
            x = 158, y = 88;
    }
    else
    {
        switch (GetBattlerPosition(battler))
        {
        case B_POSITION_PLAYER_LEFT:
            x = 138, y = 68;
            break;
        case B_POSITION_PLAYER_RIGHT:
            x = 159, y = 91;
            break;
        case B_POSITION_OPPONENT_LEFT:
            x = 40, y = 19;
            break;
        case B_POSITION_OPPONENT_RIGHT:
            x = 22, y = 42;
            break;
        }
    }

    UpdateSpritePos(gHealthboxSpriteIds[battler], x, y);
}"""

    new_block = """void InitBattlerHealthboxCoords(u8 battler)
{
    s16 x = 0, y = 0;

    if (!IsDoubleBattle())
    {
        if (GetBattlerSide(battler) != B_SIDE_PLAYER)
            x = 24, y = 26;
        else
            x = 180, y = 88;
    }
    else
    {
        switch (GetBattlerPosition(battler))
        {
        case B_POSITION_PLAYER_LEFT:
            x = 178, y = 76;
            break;
        case B_POSITION_PLAYER_RIGHT:
            x = 190, y = 101;
            break;
        case B_POSITION_OPPONENT_LEFT:
            x = 24, y = 19;
            break;
        case B_POSITION_OPPONENT_RIGHT:
            x = 14, y = 44;
            break;
        }
    }

    UpdateSpritePos(gHealthboxSpriteIds[battler], x, y);
}"""
    if old_block in text:
        text = text.replace(old_block, new_block)
        p.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
        print("[src/battle_interface.c]: Layout widescreen de healthboxes aplicado com sucesso.")
    elif "x = 24, y = 26;" in text:
        print("[src/battle_interface.c]: Layout widescreen de healthboxes já configurado.")


def apply_littleroot_strings(tree: Path) -> None:
    # 1. Littleroot Town externa
    p = tree / "data/maps/LittlerootTown/scripts.inc"
    rep = {
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
         '\t.string "MÃE: {PLAYER}, já chegamos!\\p"\n'
         '\t.string "Deve ter sido cansativo vir\\n"\n'
         '\t.string "no caminhão de mudança…\\p"\n'
         '\t.string "Bem, esta é a VILA RAIZ.\\p"\n'
         '\t.string "O que você achou?\\n"\n'
         '\t.string "Esta é a nossa nova casa!\\p"\n'
         '\t.string "É um lugar tão calmo e bom\\n"\n'
         '\t.string "para se viver, não acha?\\p"\n'
         '\t.string "E você terá seu próprio quarto!\\n"\n'
         '\t.string "Vamos logo entrar em casa.$"'),

        ('LittlerootTown_Text_WaitPlayer:\n'
         '\t.string "MOM: Wait, {PLAYER}!$"'):
        ('LittlerootTown_Text_WaitPlayer:\n'
         '\t.string "MÃE: Espere, {PLAYER}!$"'),

        ('LittlerootTown_Text_WearTheseRunningShoes:\n'
         '\t.string "MOM: {PLAYER}! {PLAYER}! Did you\\n"\n'
         '\t.string "introduce yourself to PROF. BIRCH?\\p"\n'
         '\t.string "Oh! What an adorable POKéMON!\\n"\n'
         '\t.string "You got it from PROF. BIRCH. How nice!\\p"\n'
         '\t.string "You\'re your father\'s child, all right.\\n"\n'
         '\t.string "You look good together with POKéMON!\\p"\n'
         '\t.string "Here, honey! If you\'re going out on an\\n"\n'
         '\t.string "adventure, wear these RUNNING SHOES.\\p"\n'
         '\t.string "They\'ll put a zip in your step!$"'):
        ('LittlerootTown_Text_WearTheseRunningShoes:\n'
         '\t.string "MÃE: {PLAYER}! Você já se\\n"\n'
         '\t.string "apresentou ao PROF. BIRCH?\\p"\n'
         '\t.string "Ah! Que POKéMON adorável!\\n"\n'
         '\t.string "Ganhou do PROF. BIRCH? Que bom!\\p"\n'
         '\t.string "Você é mesmo filho do seu pai.\\n"\n'
         '\t.string "Vocês combinam perfeitamente!\\p"\n'
         '\t.string "Tome, querido! Para a aventura,\\n"\n'
         '\t.string "use estes TÊNIS DE CORRIDA!\\p"\n'
         '\t.string "Eles darão energia aos passos!$"'),

        ('LittlerootTown_Text_SwitchShoesWithRunningShoes:\n'
         '\t.string "{PLAYER} switched shoes with the\\n"\n'
         '\t.string "RUNNING SHOES.$"'):
        ('LittlerootTown_Text_SwitchShoesWithRunningShoes:\n'
         '\t.string "{PLAYER} calçou os\\n"\n'
         '\t.string "TÊNIS DE CORRIDA.$"'),

        ('LittlerootTown_Text_ExplainRunningShoes:\n'
         '\t.string "MOM: {PLAYER}, those shoes came with\\n"\n'
         '\t.string "instructions.\\p"\n'
         '\t.string "“Press the B Button while wearing these\\n"\n'
         '\t.string "RUNNING SHOES to run extra-fast!\\p"\n'
         '\t.string "“Slip on these RUNNING SHOES and race\\n"\n'
         '\t.string "in the great outdoors!”$"'):
        ('LittlerootTown_Text_ExplainRunningShoes:\n'
         '\t.string "MÃE: {PLAYER}, os tênis vieram\\n"\n'
         '\t.string "com instruções de uso.\\p"\n'
         '\t.string "“Segure o Botão B calçando estes\\n"\n'
         '\t.string "TÊNIS DE CORRIDA para correr!\\p"\n'
         '\t.string "Calce os TÊNIS DE CORRIDA e\\n"\n'
         '\t.string "corra pelo mundo afora!”$"'),

        ('LittlerootTown_Text_ComeHomeIfAnythingHappens:\n'
         '\t.string "… … … … … … … …\\n"\n'
         '\t.string "… … … … … … … …\\p"\n'
         '\t.string "To think that you have your very own\\n"\n'
         '\t.string "POKéMON now…\\l"\n'
         '\t.string "Your father will be overjoyed.\\p"\n'
         '\t.string "…But please be careful.\\n"\n'
         '\t.string "If anything happens, you can come home.\\p"\n'
         '\t.string "Go on, go get them, honey!$"'):
        ('LittlerootTown_Text_ComeHomeIfAnythingHappens:\n'
         '\t.string "… … … … … … … …\\n"\n'
         '\t.string "… … … … … … … …\\p"\n'
         '\t.string "Pensar que tem o seu próprio\\n"\n'
         '\t.string "POKéMON agora…\\l"\n'
         '\t.string "Seu pai vai ficar radiante.\\p"\n'
         '\t.string "…Mas tome muito cuidado.\\n"\n'
         '\t.string "Se precisar,\\n"\n'
         '\t.string "pode voltar para casa.\\p"\n'
         '\t.string "Boa sorte na jornada, querido!$"'),

        ('LittlerootTown_Text_CanUsePCToStoreItems:\n'
         '\t.string "If you use a PC, you can store items\\n"\n'
         '\t.string "and POKéMON.\\p"\n'
         '\t.string "The power of science is staggering!$"'):
        ('LittlerootTown_Text_CanUsePCToStoreItems:\n'
         '\t.string "Se usar um PC, dá para guardar\\n"\n'
         '\t.string "itens e POKéMON.\\p"\n'
         '\t.string "A ciência é incrível!$"'),

        ('LittlerootTown_Text_BirchSpendsDaysInLab:\n'
         '\t.string "PROF. BIRCH spends days in his LAB\\n"\n'
         '\t.string "studying, then he\'ll suddenly go out in\\l"\n'
         '\t.string "the wild to do more research…\\p"\n'
         '\t.string "When does PROF. BIRCH spend time\\n"\n'
         '\t.string "at home?$"'):
        ('LittlerootTown_Text_BirchSpendsDaysInLab:\n'
         '\t.string "O PROF. BIRCH passa dias\\n"\n'
         '\t.string "no laboratório estudando,\\l"\n'
         '\t.string "e do nada sai a campo…\\p"\n'
         '\t.string "Quando será que ele fica em casa?$"'),

        ('LittlerootTown_Text_IfYouGoInGrassPokemonWillJumpOut:\n'
         '\t.string "Um, um, um!\\p"\n'
         '\t.string "If you go outside and go in the grass,\\n"\n'
         '\t.string "wild POKéMON will jump out!$"'):
        ('LittlerootTown_Text_IfYouGoInGrassPokemonWillJumpOut:\n'
         '\t.string "Ei, veja só!\\p"\n'
         '\t.string "Se andar na grama alta lá fora,\\n"\n'
         '\t.string "POKéMON selvagens vão pular!$"'),

        ('LittlerootTown_Text_DangerousIfYouDontHavePokemon:\n'
         '\t.string "It\'s dangerous if you don\'t have\\n"\n'
         '\t.string "your own POKéMON.$"'):
        ('LittlerootTown_Text_DangerousIfYouDontHavePokemon:\n'
         '\t.string "É muito perigoso se não tiver\\n"\n'
         '\t.string "o seu próprio POKéMON.$"'),

        ('LittlerootTown_Text_CanYouGoSeeWhatsHappening:\n'
         '\t.string "Um, hi!\\p"\n'
         '\t.string "There are scary POKéMON outside!\\n"\n'
         '\t.string "I can hear their cries!\\p"\n'
         '\t.string "I want to go see what\'s going on,\\n"\n'
         '\t.string "but I don\'t have any POKéMON…\\p"\n'
         '\t.string "Can you go see what\'s happening\\n"\n'
         '\t.string "for me?$"'):
        ('LittlerootTown_Text_CanYouGoSeeWhatsHappening:\n'
         '\t.string "Ai, socorro!\\p"\n'
         '\t.string "Tem POKéMON bravos lá fora!\\n"\n'
         '\t.string "Dá para ouvir os gritos deles!\\p"\n'
         '\t.string "Eu queria ir ver o que houve,\\n"\n'
         '\t.string "mas não tenho nenhum POKéMON…\\p"\n'
         '\t.string "Pode ir lá ver para mim?$"'),

        ('LittlerootTown_Text_YouSavedBirch:\n'
         '\t.string "You saved PROF. BIRCH!\\n"\n'
         '\t.string "I\'m so glad!$"'):
        ('LittlerootTown_Text_YouSavedBirch:\n'
         '\t.string "Você salvou o PROF. BIRCH!\\n"\n'
         '\t.string "Que grande alívio!$"'),

        ('LittlerootTown_Text_GoodLuckCatchingPokemon:\n'
         '\t.string "Are you going to catch POKéMON?\\n"\n'
         '\t.string "Good luck!$"'):
        ('LittlerootTown_Text_GoodLuckCatchingPokemon:\n'
         '\t.string "Vai capturar POKéMON?\\n"\n'
         '\t.string "Boa sorte na jornada!$"'),

        ('LittlerootTown_Text_TownSign:\n'
         '\t.string "LITTLEROOT TOWN\\n"\n'
         '\t.string "“A town that can\'t be shaded any hue.”$"'):
        ('LittlerootTown_Text_TownSign:\n'
         '\t.string "VILA RAIZ\\n"\n'
         '\t.string "“Uma vila que não se\\n"\n'
         '\t.string "prende a cores.”$"'),

        ('LittlerootTown_Text_ProfBirchsLab:\n'
         '\t.string "PROF. BIRCH\'S POKéMON LAB$"'):
        ('LittlerootTown_Text_ProfBirchsLab:\n'
         '\t.string "LABORATÓRIO DO PROF. BIRCH$"'),

        ('LittlerootTown_Text_PlayersHouse:\n'
         '\t.string "{PLAYER}\'s HOUSE$"'):
        ('LittlerootTown_Text_PlayersHouse:\n'
         '\t.string "CASA DE {PLAYER}$"'),

        ('LittlerootTown_Text_ProfBirchsHouse:\n'
         '\t.string "PROF. BIRCH\'S HOUSE$"'):
        ('LittlerootTown_Text_ProfBirchsHouse:\n'
         '\t.string "CASA DO PROF. BIRCH$"'),
    }
    check_and_apply(p, rep, "data/maps/LittlerootTown/scripts.inc")

    # 2. BrendansHouse_1F
    p_b1 = tree / "data/maps/LittlerootTown_BrendansHouse_1F/scripts.inc"
    rep_b1 = {
        ('PlayersHouse_1F_Text_GoSetTheClock:\n'
         '\t.string "MOM: {PLAYER}.\\p"\n'
         '\t.string "Go set the clock in your room, honey.$"'):
        ('PlayersHouse_1F_Text_GoSetTheClock:\n'
         '\t.string "MÃE: {PLAYER}.\\p"\n'
         '\t.string "Vá acertar o relógio no seu\\n"\n'
         '\t.string "quarto, querido.$"'),

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
         '\t.string "Os POKéMON de mudança fizeram\\n"\n'
         '\t.string "todo o trabalho pesado!\\l"\n'
         '\t.string "Isso é tão conveniente!\\p"\n'
         '\t.string "{PLAYER}, o seu quarto é lá\\n"\n'
         '\t.string "em cima. Vá dar uma olhada!\\p"\n'
         '\t.string "O PAPAI comprou um relógio novo\\n"\n'
         '\t.string "para marcar nossa mudança.\\l"\n'
         '\t.string "Não se esqueça de ajustá-lo!$"'),

        ('PlayersHouse_1F_Text_ArentYouInterestedInRoom:\n'
         '\t.string "MOM: Well, {PLAYER}?\\p"\n'
         '\t.string "Aren\'t you interested in seeing your\\n"\n'
         '\t.string "very own room?$"'):
        ('PlayersHouse_1F_Text_ArentYouInterestedInRoom:\n'
         '\t.string "MÃE: E então, {PLAYER}?\\p"\n'
         '\t.string "Você não quer ver o seu\\n"\n'
         '\t.string "próprio quarto?$"'),

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
         '\t.string "MÃE: Veja! É o GINÁSIO DE\\n"\n'
         '\t.string "PETALBURG! O PAPAI pode aparecer!$"'),

        ('PlayersHouse_1F_Text_ReportFromPetalburgGym:\n'
         '\t.string "INTERVIEWER: …We brought you this\\n"\n'
         '\t.string "report from in front of PETALBURG GYM.$"'):
        ('PlayersHouse_1F_Text_ReportFromPetalburgGym:\n'
         '\t.string "REPÓRTER: …E essa foi a nossa\\n"\n'
         '\t.string "reportagem em PETALBURG GYM.$"'),

        ('PlayersHouse_1F_Text_TheresAMovieOnTV:\n'
         '\t.string "There is a movie on TV.\\p"\n'
         '\t.string "Two men are dancing on a big piano\\n"\n'
         '\t.string "keyboard.\\p"\n'
         '\t.string "Better get going!$"'):
        ('PlayersHouse_1F_Text_TheresAMovieOnTV:\n'
         '\t.string "Está passando um filme na TV.\\p"\n'
         '\t.string "Dois homens dançam em um piano\\n"\n'
         '\t.string "gigante no chão.\\p"\n'
         '\t.string "É melhor ir andando!$"'),

        ('PlayersHouse_1F_Text_ItsOverWeMissedHim:\n'
         '\t.string "MOM: Oh… It\'s over.\\p"\n'
         '\t.string "I think DAD was on, but we missed him.\\n"\n'
         '\t.string "Too bad.$"'):
        ('PlayersHouse_1F_Text_ItsOverWeMissedHim:\n'
         '\t.string "MÃE: Ah… Já acabou.\\p"\n'
         '\t.string "Acho que o PAPAI apareceu,\\n"\n'
         '\t.string "mas nós perdemos. Que pena.$"'),

        ('PlayersHouse_1F_Text_GoIntroduceYourselfNextDoor:\n'
         '\t.string "Oh, yes.\\n"\n'
         '\t.string "One of DAD\'s friends lives in town.\\p"\n'
         '\t.string "PROF. BIRCH is his name.\\p"\n'
         '\t.string "He lives right next door, so you should\\n"\n'
         '\t.string "go over and introduce yourself.$"'):
        ('PlayersHouse_1F_Text_GoIntroduceYourselfNextDoor:\n'
         '\t.string "Ah, é verdade.\\n"\n'
         '\t.string "Um amigo do PAPAI mora na cidade.\\p"\n'
         '\t.string "O nome dele é PROF. BIRCH.\\p"\n'
         '\t.string "Ele mora bem ao lado, então você\\n"\n'
         '\t.string "deve ir lá se apresentar.$"'),

        ('PlayersHouse_1F_Text_SeeYouHoney:\n'
         '\t.string "MOM: See you, honey!$"'):
        ('PlayersHouse_1F_Text_SeeYouHoney:\n'
         '\t.string "MÃE: Até logo, querido!$"'),

        ('PlayersHouse_1F_Text_DidYouMeetProfBirch:\n'
         '\t.string "MOM: Did you introduce yourself to\\n"\n'
         '\t.string "PROF. BIRCH?$"'):
        ('PlayersHouse_1F_Text_DidYouMeetProfBirch:\n'
         '\t.string "MÃE: Você já se apresentou ao\\n"\n'
         '\t.string "PROF. BIRCH?$"'),

        ('PlayersHouse_1F_Text_YouShouldRestABit:\n'
         '\t.string "MOM: How are you doing, {PLAYER}?\\n"\n'
         '\t.string "You look a little tired.\\p"\n'
         '\t.string "I think you should rest a bit.$"'):
        ('PlayersHouse_1F_Text_YouShouldRestABit:\n'
         '\t.string "MÃE: Como você está, {PLAYER}?\\n"\n'
         '\t.string "Você parece cansado.\\p"\n'
         '\t.string "Acho que deve descansar um pouco.$"'),

        ('PlayersHouse_1F_Text_TakeCareHoney:\n'
         '\t.string "MOM: Take care, honey!$"'):
        ('PlayersHouse_1F_Text_TakeCareHoney:\n'
         '\t.string "MÃE: Se cuide, querido!$"'),
    }
    check_and_apply(p_b1, rep_b1, "data/maps/LittlerootTown_BrendansHouse_1F/scripts.inc")

    # 3. BrendansHouse_2F
    p_b2 = tree / "data/maps/LittlerootTown_BrendansHouse_2F/scripts.inc"
    rep_b2 = {
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
         '\t.string "MÃE: {PLAYER}, o que achou\\n"\n'
         '\t.string "do seu novo quarto?\\p"\n'
         '\t.string "Que bom! Tudo está arrumado!\\p"\n'
         '\t.string "Eles já terminaram lá embaixo.\\p"\n'
         '\t.string "Os POKéMON de mudança são tão\\n"\n'
         '\t.string "prestativos e rápidos!\\p"\n'
         '\t.string "Veja se está tudo certo na mesa.$"'),

        ('PlayersHouse_2F_Text_Notebook:\n'
         '\t.string "{PLAYER} flipped open the notebook.\\p"\n'
         '\t.string "ADVENTURE RULE NO. 1\\n"\n'
         '\t.string "Open the MENU with START.\\p"\n'
         '\t.string "ADVENTURE RULE NO. 2\\n"\n'
         '\t.string "Record your progress with SAVE.\\p"\n'
         '\t.string "The remaining pages are blank…$"'):
        ('PlayersHouse_2F_Text_Notebook:\n'
         '\t.string "{PLAYER} abriu o caderno.\\p"\n'
         '\t.string "REGRA DE AVENTURA Nº 1\\n"\n'
         '\t.string "Abra o MENU apertando START.\\p"\n'
         '\t.string "REGRA DE AVENTURA Nº 2\\n"\n'
         '\t.string "Grave o progresso com SALVAR.\\p"\n'
         '\t.string "O restante está em branco…$"'),

        ('PlayersHouse_2F_Text_ItsAGameCube:\n'
         '\t.string "It\'s a Nintendo GameCube.\\p"\n'
         '\t.string "A Game Boy Advance is connected to\\n"\n'
         '\t.string "serve as the Controller.$"'):
        ('PlayersHouse_2F_Text_ItsAGameCube:\n'
         '\t.string "É um Nintendo GameCube.\\p"\n'
         '\t.string "Um Game Boy Advance está conectado\\n"\n'
         '\t.string "para servir como controle.$"'),
    }
    check_and_apply(p_b2, rep_b2, "data/maps/LittlerootTown_BrendansHouse_2F/scripts.inc")

    # 4. MaysHouse_1F
    p_m1 = tree / "data/maps/LittlerootTown_MaysHouse_1F/scripts.inc"
    rep_m1 = {
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
         '\t.string "Ah, você é {PLAYER}{KUN}, nosso\\n"\n'
         '\t.string "vizinho ao lado! Olá!\\p"\n'
         '\t.string "Temos uma criança quase da\\n"\n'
         '\t.string "mesma idade que você.\\p"\n'
         '\t.string "Ela estava bem ansiosa para\\n"\n'
         '\t.string "fazer novas amizades.\\p"\n'
         '\t.string "Acho que ela está no\\n"\n'
         '\t.string "andar de cima.$"'),
    }
    check_and_apply(p_m1, rep_m1, "data/maps/LittlerootTown_MaysHouse_1F/scripts.inc")

    # 5. MaysHouse_2F
    p_m2 = tree / "data/maps/LittlerootTown_MaysHouse_2F/scripts.inc"
    rep_m2 = {
        ('RivalsHouse_2F_Text_ItsRivalsPokeBall:\n'
         '\t.string "It\'s {RIVAL}\'s POKé BALL!\\p"\n'
         '\t.string "Better leave it right where it is.$"'):
        ('RivalsHouse_2F_Text_ItsRivalsPokeBall:\n'
         '\t.string "É a POKéBOLA de {RIVAL}!\\p"\n'
         '\t.string "É melhor deixá-la exatamente\\n"\n'
         '\t.string "onde ela está.$"'),

        ('RivalsHouse_2F_Text_MayWhoAreYou:\n'
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
        ('RivalsHouse_2F_Text_MayWhoAreYou:\n'
         '\t.string "Hã?\\n"\n'
         '\t.string "Quem… Quem é você?\\p"\n'
         '\t.string "… … … … … … … …\\n"\n'
         '\t.string "… … … … … … … …\\p"\n'
         '\t.string "Ah, você é {PLAYER}{KUN}.\\n"\n'
         '\t.string "Então a mudança era hoje.\\p"\n'
         '\t.string "Hum… Eu sou a MAY.\\n"\n'
         '\t.string "Prazer em te conhecer!\\p"\n'
         '\t.string "Eu… tenho o sonho de fazer amizade\\n"\n'
         '\t.string "com POKéMON de todo o mundo.\\p"\n'
         '\t.string "Ouvi falar de você, {PLAYER}{KUN},\\n"\n'
         '\t.string "pelo meu pai, o PROF. BIRCH.\\p"\n'
         '\t.string "Esperava que fosse bem legal e\\n"\n'
         '\t.string "que fôssemos bons amigos.\\p"\n'
         '\t.string "Nossa, que bobeira falar isso, né?\\n"\n'
         '\t.string "Eu acabei de te conhecer!\\p"\n'
         '\t.string "Eheheh…\\p"\n'
         '\t.string "Ai, não! Eu esqueci!\\p"\n'
         '\t.string "Eu devia ajudar meu pai a pegar\\n"\n'
         '\t.string "alguns POKéMON selvagens!\\p"\n'
         '\t.string "{PLAYER}{KUN}, a gente se vê por aí!$"'),

        ('RivalsHouse_2F_Text_BrendanWhoAreYou:\n'
         '\t.string "Hey!\\n"\n'
         '\t.string "You…\\p"\n'
         '\t.string "Who are you?\\p"\n'
         '\t.string "Oh, you\'re {PLAYER}, aren\'t you?\\n"\n'
         '\t.string "Moved in next door, right?\\p"\n'
         '\t.string "I didn\'t know that you\'re a girl.\\p"\n'
         '\t.string "Dad, PROF. BIRCH, said that our new\\n"\n'
         '\t.string "next-door neighbor is a GYM LEADER\'s\\l"\n'
         '\t.string "kid, so I assumed you\'d be a guy.\\p"\n'
         '\t.string "My name\'s BRENDAN.\\n"\n'
         '\t.string "So, hi, neighbor!\\p"\n'
         '\t.string "Huh? Hey, {PLAYER}, don\'t you have\\n"\n'
         '\t.string "a POKéMON?\\p"\n'
         '\t.string "Do you want me to go catch you one?\\p"\n'
         '\t.string "Aw, darn, I forgot…\\p"\n'
         '\t.string "I\'m supposed to go help my dad catch\\n"\n'
         '\t.string "some wild POKéMON.\\p"\n'
         '\t.string "Some other time, okay?$"'):
        ('RivalsHouse_2F_Text_BrendanWhoAreYou:\n'
         '\t.string "Ei! Você…\\p"\n'
         '\t.string "Quem é você?\\p"\n'
         '\t.string "Ah, você é {PLAYER}, não é?\\n"\n'
         '\t.string "Mudou-se para a casa ao lado?\\p"\n'
         '\t.string "Eu não sabia que era uma garota.\\p"\n'
         '\t.string "Meu pai disse que o filho do\\n"\n'
         '\t.string "LÍDER DE GINÁSIO viria morar aqui,\\l"\n'
         '\t.string "então achei que seria um rapaz.\\p"\n'
         '\t.string "Meu nome é BRENDAN.\\n"\n'
         '\t.string "E aí, vizinha!\\p"\n'
         '\t.string "Ei, {PLAYER}, você não tem\\n"\n'
         '\t.string "um POKéMON ainda?\\p"\n'
         '\t.string "Quer que eu pegue um para você?\\p"\n'
         '\t.string "Puxa, esqueci… Tenho que ajudar\\n"\n'
         '\t.string "meu pai a capturar POKéMON.\\p"\n'
         '\t.string "Deixa para outra hora, ok?$"'),
    }
    check_and_apply(p_m2, rep_m2, "data/maps/LittlerootTown_MaysHouse_2F/scripts.inc")

    # 6. ProfessorBirchsLab
    p_lab = tree / "data/maps/LittlerootTown_ProfessorBirchsLab/scripts.inc"
    rep_lab = {
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
         '\t.string "O PROFESSOR saiu em pesquisa.\\n"\n'
         '\t.string "Portanto, ele não está aqui.\\p"\n'
         '\t.string "Pesquisa de campo é estudar as\\n"\n'
         '\t.string "coisas na natureza, ao ar livre,\\l"\n'
         '\t.string "em vez de ficar num laboratório.\\p"\n'
         '\t.string "O PROFESSOR não suporta ficar\\n"\n'
         '\t.string "preso numa mesa de escritório!$"'),

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
         '\t.string "Soube que você ainda não tinha\\n"\n'
         '\t.string "o seu próprio POKéMON.\\p"\n'
         '\t.string "Mas o jeito como você batalhou,\\n"\n'
         '\t.string "foi com coragem e maestria!\\p"\n'
         '\t.string "Parece que tem o sangue do seu pai\\n"\n'
         '\t.string "correndo nas veias, afinal!\\p"\n'
         '\t.string "Como gratidão por me salvar, quero\\n"\n'
         '\t.string "que fique com o POKéMON que usou.\\p"\n'
         '\t.string "{PLAYER} recebeu {STR_VAR_1}!$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_WhyNotGiveNicknameToMon:\n'
         '\t.string "PROF. BIRCH: While you\'re at it, why not\\n"\n'
         '\t.string "give a nickname to that {STR_VAR_1}?$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_WhyNotGiveNicknameToMon:\n'
         '\t.string "PROF. BIRCH: E já que está\\n"\n'
         '\t.string "com ele, quer dar um apelido\\l"\n'
         '\t.string "ao seu {STR_VAR_1}?$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_MightBeGoodIdeaToGoSeeRival:\n'
         '\t.string "PROF. BIRCH: If you work at POKéMON\\n"\n'
         '\t.string "and gain experience, I think you\'ll make\\l"\n'
         '\t.string "an extremely good TRAINER.\\p"\n'
         '\t.string "My kid, {RIVAL}, is also studying\\n"\n'
         '\t.string "POKéMON while helping me out.\\p"\n'
         '\t.string "{PLAYER}{KUN}, don\'t you think it might be\\n"\n'
         '\t.string "a good idea to go see {RIVAL}?$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_MightBeGoodIdeaToGoSeeRival:\n'
         '\t.string "PROF. BIRCH: Se você treinar bem\\n"\n'
         '\t.string "e ganhar experiência, será um\\l"\n'
         '\t.string "excelente TREINADOR.\\p"\n'
         '\t.string "Meu filho, {RIVAL}, também estuda\\n"\n'
         '\t.string "POKéMON enquanto me ajuda.\\p"\n'
         '\t.string "{PLAYER}{KUN}, não acha uma boa\\n"\n'
         '\t.string "ideia ir encontrar {RIVAL}?$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_GetRivalToTeachYou:\n'
         '\t.string "PROF. BIRCH: Great!\\n"\n'
         '\t.string "{RIVAL} should be happy, too.\\p"\n'
         '\t.string "Get {RIVAL} to teach you what it\\n"\n'
         '\t.string "means to be a TRAINER.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_GetRivalToTeachYou:\n'
         '\t.string "PROF. BIRCH: Ótimo!\\n"\n'
         '\t.string "{RIVAL} ficará bem contente.\\p"\n'
         '\t.string "Peça a {RIVAL} para lhe ensinar o\\n"\n'
         '\t.string "que é ser um TREINADOR!$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_DontBeThatWay:\n'
         '\t.string "PROF. BIRCH: Oh, don\'t be that way.\\n"\n'
         '\t.string "You should go meet my kid.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_DontBeThatWay:\n'
         '\t.string "PROF. BIRCH: Ora, não seja assim.\\n"\n'
         '\t.string "Você devia ir encontrar meu filho.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_BirchRivalGoneHome:\n'
         '\t.string "PROF. BIRCH: {RIVAL}?\\n"\n'
         '\t.string "Gone home, I think.\\p"\n'
         '\t.string "Or maybe that kid\'s scrabbling around\\n"\n'
         '\t.string "in tall grass again somewhere…\\p"\n'
         '\t.string "If you or your POKéMON get tired,\\n"\n'
         '\t.string "you should get some rest at home.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_BirchRivalGoneHome:\n'
         '\t.string "PROF. BIRCH: {RIVAL}?\\n"\n'
         '\t.string "Foi para casa, eu acho.\\p"\n'
         '\t.string "Ou talvez esteja na grama alta\\n"\n'
         '\t.string "procurando POKéMON de novo…\\p"\n'
         '\t.string "Se você ou seu POKéMON cansarem,\\n"\n'
         '\t.string "descanse um pouco em casa.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_HeardYouBeatRivalTakePokedex:\n'
         '\t.string "PROF. BIRCH: Oh, hi, {PLAYER}{KUN}!\\p"\n'
         '\t.string "I heard you beat {RIVAL} on\\n"\n'
         '\t.string "your first try. That\'s excellent!\\p"\n'
         '\t.string "{RIVAL}\'s been helping with my research\\n"\n'
         '\t.string "for a long time.\\p"\n'
         '\t.string "{RIVAL} has an extensive history as\\n"\n'
         '\t.string "a TRAINER already.\\p"\n'
         '\t.string "Here, {PLAYER}{KUN}, I ordered this for my\\n"\n'
         '\t.string "research, but I think you should have\\l"\n'
         '\t.string "this POKéDEX.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_HeardYouBeatRivalTakePokedex:\n'
         '\t.string "PROF. BIRCH: Olá, {PLAYER}{KUN}!\\p"\n'
         '\t.string "Soube que venceu {RIVAL} de primeira.\\n"\n'
         '\t.string "Isso é excelente!\\p"\n'
         '\t.string "{RIVAL} me ajuda há muito tempo\\n"\n'
         '\t.string "e tem bastante experiência.\\p"\n'
         '\t.string "Tome, {PLAYER}{KUN}, encomendei isto\\n"\n'
         '\t.string "para a pesquisa, mas acho que você\\l"\n'
         '\t.string "deve ficar com esta POKéDEX.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_ReceivedPokedex:\n'
         '\t.string "{PLAYER} received the POKéDEX!$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_ReceivedPokedex:\n'
         '\t.string "{PLAYER} recebeu a POKéDEX!$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_ExplainPokedex:\n'
         '\t.string "PROF. BIRCH: The POKéDEX is a high-tech\\n"\n'
         '\t.string "tool that automatically makes a record\\l"\n'
         '\t.string "of any POKéMON you meet or catch.\\p"\n'
         '\t.string "My kid, {RIVAL}, goes everywhere\\n"\n'
         '\t.string "with it.\\p"\n'
         '\t.string "Whenever my kid catches a rare POKéMON\\n"\n'
         '\t.string "and records its data in the POKéDEX,\\l"\n'
         '\t.string "why, {RIVAL} looks for me while I\'m out\\l"\n'
         '\t.string "doing fieldwork, and shows me.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_ExplainPokedex:\n'
         '\t.string "PROF. BIRCH: A POKéDEX registra\\n"\n'
         '\t.string "automaticamente qualquer POKéMON\\l"\n'
         '\t.string "que você encontrar ou capturar.\\p"\n'
         '\t.string "Meu filho a leva para toda parte.\\p"\n'
         '\t.string "Quando ele pega um POKéMON raro,\\n"\n'
         '\t.string "vem correndo me mostrar no campo.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_CountlessPokemonAwait:\n'
         '\t.string "PROF. BIRCH: Countless POKéMON\\n"\n'
         '\t.string "await you!\\p"\n'
         '\t.string "Argh, I\'m getting the itch to get out\\n"\n'
         '\t.string "and do fieldwork again!$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_CountlessPokemonAwait:\n'
         '\t.string "PROF. BIRCH: Inúmeros POKéMON\\n"\n'
         '\t.string "esperam por você!\\p"\n'
         '\t.string "Já estou com vontade de sair e\\n"\n'
         '\t.string "pesquisar na natureza de novo!$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_MayGotPokedexTooTakeThese:\n'
         '\t.string "MAY: Oh, wow, {PLAYER}{KUN}!\\n"\n'
         '\t.string "You got a POKéDEX, too!\\p"\n'
         '\t.string "That\'s great! Just like me!\\n"\n'
         '\t.string "I\'ve got something for you, too!$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_MayGotPokedexTooTakeThese:\n'
         '\t.string "MAY: Uau, {PLAYER}{KUN}!\\n"\n'
         '\t.string "Você ganhou uma POKéDEX também!\\p"\n'
         '\t.string "Que ótimo! Igual à minha!\\n"\n'
         '\t.string "Eu tenho uma coisa para você!$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_CatchCutePokemonWithPokeBalls:\n'
         '\t.string "MAY: It\'s fun if you can get a lot of\\n"\n'
         '\t.string "POKéMON!\\p"\n'
         '\t.string "I\'m going to look all over the place\\n"\n'
         '\t.string "because I want different POKéMON.\\p"\n'
         '\t.string "If I find any cute POKéMON, I\'ll catch\\n"\n'
         '\t.string "them with POKé BALLS!$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_CatchCutePokemonWithPokeBalls:\n'
         '\t.string "MAY: É muito divertido capturar um\\n"\n'
         '\t.string "montão de POKéMON!\\p"\n'
         '\t.string "Vou procurar por toda parte para\\n"\n'
         '\t.string "achar espécies diferentes.\\p"\n'
         '\t.string "Se eu achar algum bem fofo, vou\\n"\n'
         '\t.string "pegar com as POKéBOLAS!$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_BirchIsntOneForDeskWork:\n'
         '\t.string "The PROF isn\'t one for doing desk work.\\n"\n'
         '\t.string "He\'s the type of person who would\\l"\n'
         '\t.string "rather go outside and experience\\l"\n'
         '\t.string "things than read about them here.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_BirchIsntOneForDeskWork:\n'
         '\t.string "O PROFESSOR não é de ficar preso\\n"\n'
         '\t.string "ao trabalho de escritório.\\l"\n'
         '\t.string "Ele prefere sair e vivenciar\\l"\n'
         '\t.string "as coisas no campo do que\\l"\n'
         '\t.string "apenas ler sobre elas aqui.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_BirchEnjoysRivalsHelpToo:\n'
         '\t.string "PROF. BIRCH is studying the habitats\\n"\n'
         '\t.string "and distribution of POKéMON.\\p"\n'
         '\t.string "The PROF enjoys {RIVAL}\'s help, too.\\n"\n'
         '\t.string "There\'s a lot of love there.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_BirchEnjoysRivalsHelpToo:\n'
         '\t.string "O PROF. BIRCH estuda os habitats\\n"\n'
         '\t.string "e a distribuição dos POKéMON.\\p"\n'
         '\t.string "Ele adora a ajuda de {RIVAL},\\n"\n'
         '\t.string "eles são muito unidos.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_OhYourBagsFull:\n'
         '\t.string "Oh? Your BAG\'s full.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_OhYourBagsFull:\n'
         '\t.string "Ah? Sua MOCHILA está cheia.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_MayWhereShouldIGoNext:\n'
         '\t.string "MAY: I wonder where I should go look\\n"\n'
         '\t.string "for POKéMON next?$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_MayWhereShouldIGoNext:\n'
         '\t.string "MAY: Para onde devo ir procurar\\n"\n'
         '\t.string "POKéMON agora?$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_BrendanGotPokedexTooTakeThese:\n'
         '\t.string "BRENDAN: Huh…\\n"\n'
         '\t.string "So you got a POKéDEX, too.\\p"\n'
         '\t.string "Well then, here.\\n"\n'
         '\t.string "I\'ll give you these.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_BrendanGotPokedexTooTakeThese:\n'
         '\t.string "BRENDAN: Ah…\\n"\n'
         '\t.string "Você também ganhou uma POKéDEX.\\p"\n'
         '\t.string "Bem, então tome.\\n"\n'
         '\t.string "Vou lhe dar isto aqui.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_CatchCoolPokemonWithPokeBalls:\n'
         '\t.string "BRENDAN: You know it\'s more fun to\\n"\n'
         '\t.string "have a whole bunch of POKéMON.\\p"\n'
         '\t.string "I\'m going to explore all over the place\\n"\n'
         '\t.string "to find different POKéMON.\\p"\n'
         '\t.string "If I find any cool POKéMON, you bet\\n"\n'
         '\t.string "I\'ll try to get them with POKé BALLS.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_CatchCoolPokemonWithPokeBalls:\n'
         '\t.string "BRENDAN: É muito mais legal ter\\n"\n'
         '\t.string "um montão de POKéMON.\\p"\n'
         '\t.string "Vou explorar toda parte para\\n"\n'
         '\t.string "encontrar vários diferentes.\\p"\n'
         '\t.string "Se eu achar algum bem legal,\\n"\n'
         '\t.string "vou capturar com as POKéBOLAS!$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_HeyYourBagsFull:\n'
         '\t.string "Hey, your BAG\'s full.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_HeyYourBagsFull:\n'
         '\t.string "Ei, sua MOCHILA está cheia.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_BrendanWhereShouldIGoNext:\n'
         '\t.string "BRENDAN: Where should I look for\\n"\n'
         '\t.string "POKéMON next…$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_BrendanWhereShouldIGoNext:\n'
         '\t.string "BRENDAN: Onde será que eu procuro\\n"\n'
         '\t.string "POKéMON agora…$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_SeriousLookingMachine:\n'
         '\t.string "It\'s a serious-looking machine.\\n"\n'
         '\t.string "The PROF must use this for research.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_SeriousLookingMachine:\n'
         '\t.string "É uma máquina bem avançada.\\n"\n'
         '\t.string "O PROFESSOR a usa na pesquisa.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_PCUsedForResearch:\n'
         '\t.string "It\'s a PC used for research.\\n"\n'
         '\t.string "Better not mess around with it.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_PCUsedForResearch:\n'
         '\t.string "É um computador de pesquisa.\\n"\n'
         '\t.string "Melhor não mexer nele.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_CrammedWithBooksOnPokemon:\n'
         '\t.string "It\'s crammed with books on POKéMON.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_CrammedWithBooksOnPokemon:\n'
         '\t.string "Está repleto de livros de POKéMON.$"'),

        ('LittlerootTown_ProfessorBirchsLab_Text_BookTooHardToRead:\n'
         '\t.string "It\'s a book that\'s too hard to read.$"'):
        ('LittlerootTown_ProfessorBirchsLab_Text_BookTooHardToRead:\n'
         '\t.string "É um livro difícil demais de ler.$"'),
    }
    check_and_apply(p_lab, rep_lab, "data/maps/LittlerootTown_ProfessorBirchsLab/scripts.inc")


def apply_route101_strings(tree: Path) -> None:
    r101 = tree / "data/maps/Route101/scripts.inc"
    rep_r101 = {
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
         '\t.string "Eu estudava na grama alta quando\\n"\n'
         '\t.string "fui atacado por este bicho.\\p"\n'
         '\t.string "Você me salvou. Muito obrigado!\\p"\n'
         '\t.string "Oh? Olá, você é {PLAYER}{KUN}!\\p"\n'
         '\t.string "Aqui não é o lugar para conversar,\\n"\n'
         '\t.string "passe no meu LABORATÓRIO\\n"\n'
         '\t.string "depois, tudo bem?$"'),

        ('Route101_Text_TakeTiredPokemonToPokeCenter:\n'
         '\t.string "If POKéMON get tired, take them to\\n"\n'
         '\t.string "a POKéMON CENTER.\\p"\n'
         '\t.string "There\'s a POKéMON CENTER in OLDALE\\n"\n'
         '\t.string "TOWN right close by.$"'):
        ('Route101_Text_TakeTiredPokemonToPokeCenter:\n'
         '\t.string "Se os POKéMON cansarem, leve-os\\n"\n'
         '\t.string "a um CENTRO POKéMON.\\p"\n'
         '\t.string "Tem um CENTRO POKéMON bem perto,\\n"\n'
         '\t.string "na CIDADE DE OLDALE.$"'),

        ('Route101_Text_WildPokemonInTallGrass:\n'
         '\t.string "Wild POKéMON will jump out at you in\\n"\n'
         '\t.string "tall grass.\\p"\n'
         '\t.string "If you want to catch POKéMON, you have\\n"\n'
         '\t.string "to go into the tall grass and search.$"'):
        ('Route101_Text_WildPokemonInTallGrass:\n'
         '\t.string "POKéMON selvagens pulam em você\\n"\n'
         '\t.string "na grama alta.\\p"\n'
         '\t.string "Se quiser pegá-los, ande na grama\\n"\n'
         '\t.string "alta e procure.$"'),

        ('Route101_Text_RouteSign:\n'
         '\t.string "ROUTE 101\\n"\n'
         '\t.string "{UP_ARROW} OLDALE TOWN$"'):
        ('Route101_Text_RouteSign:\n'
         '\t.string "ROTA 101\\n"\n'
         '\t.string "{UP_ARROW} CIDADE DE OLDALE$"'),
    }
    check_and_apply(r101, rep_r101, "data/maps/Route101/scripts.inc")


def apply_oldale_strings(tree: Path) -> None:
    # 1. OldaleTown externa
    p_old = tree / "data/maps/OldaleTown/scripts.inc"
    rep_old = {
        ('OldaleTown_Text_SavingMyProgress:\n'
         '\t.string "I want to take a rest, so I\'m saving my\\n"\n'
         '\t.string "progress.$"'):
        ('OldaleTown_Text_SavingMyProgress:\n'
         '\t.string "Quero descansar, por isso estou\\n"\n'
         '\t.string "salvando o meu progresso.$"'),

        ('OldaleTown_Text_IWorkAtPokemonMart:\n'
         '\t.string "Hi!\\n"\n'
         '\t.string "I work at a POKéMON MART.\\p"\n'
         '\t.string "Can I get you to come with me?$"'):
        ('OldaleTown_Text_IWorkAtPokemonMart:\n'
         '\t.string "Olá!\\n"\n'
         '\t.string "Trabalho em um POKéMON MART.\\p"\n'
         '\t.string "Pode vir comigo até a loja?$"'),

        ('OldaleTown_Text_ThisIsAPokemonMart:\n'
         '\t.string "This is a POKéMON MART.\\n"\n'
         '\t.string "Just look for our blue roof.\\p"\n'
         '\t.string "We sell a variety of goods including\\n"\n'
         '\t.string "POKé BALLS for catching POKéMON.\\p"\n'
         '\t.string "Here, I\'d like you to have this as\\n"\n'
         '\t.string "a promotional item.$"'):
        ('OldaleTown_Text_ThisIsAPokemonMart:\n'
         '\t.string "Este é um POKéMON MART.\\n"\n'
         '\t.string "É só procurar pelo teto azul.\\p"\n'
         '\t.string "Vendemos itens úteis e POKéBOLAS\\n"\n'
         '\t.string "para pegar POKéMON.\\p"\n'
         '\t.string "Tome, pegue isto como brinde!$"'),

        ('OldaleTown_Text_PotionExplanation:\n'
         '\t.string "A POTION can be used anytime, so it\'s\\n"\n'
         '\t.string "even more useful than a POKéMON CENTER\\l"\n'
         '\t.string "in certain situations.$"'):
        ('OldaleTown_Text_PotionExplanation:\n'
         '\t.string "Uma POÇÃO pode ser usada na hora,\\n"\n'
         '\t.string "sendo ótima em emergências!$"'),

        ('OldaleTown_Text_WaitDontComeInHere:\n'
         '\t.string "Aaaaah! Wait!\\n"\n'
         '\t.string "Please don\'t come in here.\\p"\n'
         '\t.string "I just discovered the footprints of\\n"\n'
         '\t.string "a rare POKéMON!\\p"\n'
         '\t.string "Wait until I finish sketching\\n"\n'
         '\t.string "them, okay?$"'):
        ('OldaleTown_Text_WaitDontComeInHere:\n'
         '\t.string "Aaaaah! Espere!\\n"\n'
         '\t.string "Não pise aqui, por favor!\\p"\n'
         '\t.string "Achei pegadas de um POKéMON raro!\\p"\n'
         '\t.string "Espere eu terminar de desenhar,$"'),

        ('OldaleTown_Text_DiscoveredFootprints:\n'
         '\t.string "I just discovered the footprints of\\n"\n'
         '\t.string "a rare POKéMON!\\p"\n'
         '\t.string "Wait until I finish sketching\\n"\n'
         '\t.string "them, okay?$"'):
        ('OldaleTown_Text_DiscoveredFootprints:\n'
         '\t.string "Achei pegadas de um POKéMON raro!\\p"\n'
         '\t.string "Espere eu terminar de desenhar,$"'),

        ('OldaleTown_Text_FinishedSketchingFootprints:\n'
         '\t.string "I finished sketching the footprints of\\n"\n'
         '\t.string "a rare POKéMON.\\p"\n'
         '\t.string "But it turns out they were only my\\n"\n'
         '\t.string "own footprints…$"'):
        ('OldaleTown_Text_FinishedSketchingFootprints:\n'
         '\t.string "Terminei de desenhar as pegadas…\\p"\n'
         '\t.string "Mas eram apenas as minhas próprias\\n"\n'
         '\t.string "pegadas no chão… que vergonha.$"'),

        ('OldaleTown_Text_MayLetsGoBack:\n'
         '\t.string "MAY: {PLAYER}{KUN}!\\n"\n'
         '\t.string "Over here!\\l"\n'
         '\t.string "Let\'s hurry home!$"'):
        ('OldaleTown_Text_MayLetsGoBack:\n'
         '\t.string "MAY: {PLAYER}{KUN}!\\n"\n'
         '\t.string "Por aqui!\\l"\n'
         '\t.string "Vamos logo para casa!$"'),

        ('OldaleTown_Text_BrendanLetsGoBack:\n'
         '\t.string "BRENDAN: I\'m heading back to my dad\'s\\n"\n'
         '\t.string "LAB now.\\l"\n'
         '\t.string "{PLAYER}, you should hustle back, too.$"'):
        ('OldaleTown_Text_BrendanLetsGoBack:\n'
         '\t.string "BRENDAN: Vou voltar ao laboratório\\n"\n'
         '\t.string "do meu pai agora.\\l"\n'
         '\t.string "{PLAYER}, apresse-se também!$"'),

        ('OldaleTown_Text_TownSign:\n'
         '\t.string "OLDALE TOWN\\n"\n'
         '\t.string "“Where things start off scarce.”$"'):
        ('OldaleTown_Text_TownSign:\n'
         '\t.string "CIDADE DE OLDALE\\n"\n'
         '\t.string "“Onde as coisas começam\\n"\n'
         '\t.string "aos poucos.”$"'),
    }
    check_and_apply(p_old, rep_old, "data/maps/OldaleTown/scripts.inc")

    # 2. Oldale House1
    p_h1 = tree / "data/maps/OldaleTown_House1/scripts.inc"
    rep_h1 = {
        ('OldaleTown_House1_Text_LeftPokemonGoesOutFirst:\n'
         '\t.string "When a POKéMON battle starts, the one\\n"\n'
         '\t.string "at the left of the list goes out first.\\p"\n'
         '\t.string "So, when you get more POKéMON in your\\n"\n'
         '\t.string "party, try switching around the order\\l"\n'
         '\t.string "of your POKéMON.\\p"\n'
         '\t.string "It could give you an advantage.$"'):
        ('OldaleTown_House1_Text_LeftPokemonGoesOutFirst:\n'
         '\t.string "Na batalha, o primeiro POKéMON\\n"\n'
         '\t.string "da equipe é quem luta primeiro.\\p"\n'
         '\t.string "Tente mudar a ordem do seu grupo\\n"\n'
         '\t.string "para ter vantagem nas lutas!$"'),
    }
    check_and_apply(p_h1, rep_h1, "data/maps/OldaleTown_House1/scripts.inc")

    # 3. Oldale House2
    p_h2 = tree / "data/maps/OldaleTown_House2/scripts.inc"
    rep_h2 = {
        ('OldaleTown_House2_Text_PokemonLevelUp:\n'
         '\t.string "When POKéMON battle, they eventually\\n"\n'
         '\t.string "level up and become stronger.$"'):
        ('OldaleTown_House2_Text_PokemonLevelUp:\n'
         '\t.string "Nas batalhas, os POKéMON sobem\\n"\n'
         '\t.string "de nível e ficam mais fortes.$"'),

        ('OldaleTown_House2_Text_YoullGoFurtherWithStrongPokemon:\n'
         '\t.string "If the POKéMON with you become\\n"\n'
         '\t.string "stronger, you\'ll be able to go farther\\l"\n'
         '\t.string "away from here.$"'):
        ('OldaleTown_House2_Text_YoullGoFurtherWithStrongPokemon:\n'
         '\t.string "Com POKéMON mais fortes, você\\n"\n'
         '\t.string "poderá viajar para muito longe!$"'),
    }
    check_and_apply(p_h2, rep_h2, "data/maps/OldaleTown_House2/scripts.inc")

    # 4. Oldale Mart
    p_om = tree / "data/maps/OldaleTown_Mart/scripts.inc"
    rep_om = {
        ('OldaleTown_Mart_Text_PokeBallsAreSoldOut:\n'
         '\t.string "The clerk says they\'re all sold out.\\n"\n'
         '\t.string "I can\'t buy any POKé BALLS.$"'):
        ('OldaleTown_Mart_Text_PokeBallsAreSoldOut:\n'
         '\t.string "O atendente disse que esgotou.\\n"\n'
         '\t.string "Não posso comprar POKéBOLAS agora.$"'),

        ('OldaleTown_Mart_Text_ImGoingToBuyPokeBalls:\n'
         '\t.string "I\'m going to buy a bunch of POKé BALLS\\n"\n'
         '\t.string "and catch a bunch of POKéMON!$"'):
        ('OldaleTown_Mart_Text_ImGoingToBuyPokeBalls:\n'
         '\t.string "Vou comprar várias POKéBOLAS\\n"\n'
         '\t.string "e pegar um monte de POKéMON!$"'),

        ('OldaleTown_Mart_Text_RestoreHPWithPotion:\n'
         '\t.string "If a POKéMON gets hurt and loses its HP\\n"\n'
         '\t.string "and faints, it won\'t be able to battle.\\p"\n'
         '\t.string "To prevent your POKéMON from fainting,\\n"\n'
         '\t.string "restore its HP with a POTION.$"'):
        ('OldaleTown_Mart_Text_RestoreHPWithPotion:\n'
         '\t.string "Se o POKéMON perder o HP, ele\\n"\n'
         '\t.string "desmaia e não consegue lutar.\\p"\n'
         '\t.string "Para evitar isso, recupere o HP\\n"\n'
         '\t.string "dele com uma POÇÃO.$"'),
    }
    check_and_apply(p_om, rep_om, "data/maps/OldaleTown_Mart/scripts.inc")

    # 5. Oldale PokemonCenter_1F
    p_oc = tree / "data/maps/OldaleTown_PokemonCenter_1F/scripts.inc"
    rep_oc = {
        ('OldaleTown_PokemonCenter_1F_Text_TrainersCanUsePC:\n'
         '\t.string "That PC in the corner there is\\n"\n'
         '\t.string "for any POKéMON TRAINER to use.\\p"\n'
         '\t.string "Naturally, that means you\'re welcome\\n"\n'
         '\t.string "to use it, too.$"'):
        ('OldaleTown_PokemonCenter_1F_Text_TrainersCanUsePC:\n'
         '\t.string "Aquele PC no canto é livre para\\n"\n'
         '\t.string "qualquer TREINADOR usar.\\p"\n'
         '\t.string "Você também pode usá-lo à vontade.$"'),

        ('OldaleTown_PokemonCenter_1F_Text_PokemonCentersAreGreat:\n'
         '\t.string "POKéMON CENTERS are great!\\p"\n'
         '\t.string "You can use their services as much\\n"\n'
         '\t.string "as you like, and it\'s all for free.\\l"\n'
         '\t.string "You never have to worry!$"'):
        ('OldaleTown_PokemonCenter_1F_Text_PokemonCentersAreGreat:\n'
         '\t.string "Os CENTROS POKéMON são ótimos!\\p"\n'
         '\t.string "Você pode usá-los à vontade e\\n"\n'
         '\t.string "é tudo de graça! Sem preocupações!$"'),

        ('OldaleTown_PokemonCenter_1F_Text_WirelessClubNotAvailable:\n'
         '\t.string "The POKéMON WIRELESS CLUB on\\n"\n'
         '\t.string "the second floor was built recently.\\p"\n'
         '\t.string "But they say they\'re still making\\n"\n'
         '\t.string "adjustments.$"'):
        ('OldaleTown_PokemonCenter_1F_Text_WirelessClubNotAvailable:\n'
         '\t.string "O CLUBE SEM FIO no segundo andar\\n"\n'
         '\t.string "foi inaugurado recentemente.\\p"\n'
         '\t.string "Mas ainda estão fazendo ajustes.$"'),
    }
    check_and_apply(p_oc, rep_oc, "data/maps/OldaleTown_PokemonCenter_1F/scripts.inc")


def apply_route103_strings(tree: Path) -> None:
    r103 = tree / "data/maps/Route103/scripts.inc"
    rep_r103 = {
        ('Route103_Text_MayRoute103Pokemon:\n'
         '\t.string "MAY: Let\'s see… The POKéMON found\\n"\n'
         '\t.string "on ROUTE 103 include…$"'):
        ('Route103_Text_MayRoute103Pokemon:\n'
         '\t.string "MAY: Vejamos… Os POKéMON desta\\n"\n'
         '\t.string "ROTA 103 incluem…$"'),

        ('Route103_Text_MayLetsBattle:\n'
         '\t.string "Oh, hi, {PLAYER}{KUN}!\\p"\n'
         '\t.string "…Oh, I see, my dad gave you\\n"\n'
         '\t.string "a POKéMON as a gift.\\p"\n'
         '\t.string "Since we\'re here, let\'s have a quick\\n"\n'
         '\t.string "battle!\\p"\n'
         '\t.string "I\'ll give you a taste of what being\\n"\n'
         '\t.string "a TRAINER is like.$"'):
        ('Route103_Text_MayLetsBattle:\n'
         '\t.string "Ah, olá, {PLAYER}{KUN}!\\p"\n'
         '\t.string "…Ah, meu pai te deu um POKéMON\\n"\n'
         '\t.string "de presente! Que legal!\\p"\n'
         '\t.string "Já que estamos aqui, vamos ter\\n"\n'
         '\t.string "uma batalha rápida!\\p"\n'
         '\t.string "Vou lhe mostrar um pouco do que\\n"\n'
         '\t.string "é ser uma TREINADORA!$"'),

        ('Route103_Text_MayDefeated:\n'
         '\t.string "Wow! That\'s great!\\n"\n'
         '\t.string "{PLAYER}{KUN}, you\'re pretty good!$"'):
        ('Route103_Text_MayDefeated:\n'
         '\t.string "Uau! Incrível!\\n"\n'
         '\t.string "{PLAYER}{KUN}, você luta muito bem!$"'),

        ('Route103_Text_MayTimeToHeadBack:\n'
         '\t.string "MAY: I think I know why my dad has\\n"\n'
         '\t.string "an eye out for you now.\\p"\n'
         '\t.string "I mean, you just got that POKéMON,\\n"\n'
         '\t.string "but it already likes you.\\p"\n'
         '\t.string "You might be able to befriend any\\n"\n'
         '\t.string "kind of POKéMON easily.\\p"\n'
         '\t.string "Well, it\'s time to head back to\\n"\n'
         '\t.string "the LAB.$"'):
        ('Route103_Text_MayTimeToHeadBack:\n'
         '\t.string "MAY: Acho que entendi por que\\n"\n'
         '\t.string "meu pai gostou tanto de você.\\p"\n'
         '\t.string "Você acabou de pegar esse POKéMON\\n"\n'
         '\t.string "e ele já confia em você!\\p"\n'
         '\t.string "Você deve fazer amizade fácil com\\n"\n'
         '\t.string "qualquer tipo de POKéMON.\\p"\n'
         '\t.string "Bem, é hora de voltar\\n"\n'
         '\t.string "ao LABORATÓRIO.$"'),

        ('Route103_Text_BrendanRoute103Pokemon:\n'
         '\t.string "BRENDAN: Okay, so it\'s this one and\\n"\n'
         '\t.string "that one that live on ROUTE 103…$"'):
        ('Route103_Text_BrendanRoute103Pokemon:\n'
         '\t.string "BRENDAN: Certo, então são estes\\n"\n'
         '\t.string "que vivem na ROTA 103…$"'),

        ('Route103_Text_BrendanLetsBattle:\n'
         '\t.string "Hey, it\'s {PLAYER}!\\p"\n'
         '\t.string "…Oh, yeah, Dad gave you a POKéMON.\\p"\n'
         '\t.string "Since we\'re here, how about a little\\n"\n'
         '\t.string "battle?\\p"\n'
         '\t.string "I\'ll teach you what being a TRAINER\'s\\n"\n'
         '\t.string "about!$"'):
        ('Route103_Text_BrendanLetsBattle:\n'
         '\t.string "Ei, {PLAYER}!\\p"\n'
         '\t.string "…Ah, meu pai te deu um POKéMON!\\p"\n'
         '\t.string "Já que estamos aqui,\\n"\n'
         '\t.string "que tal batalhar?\\p"\n'
         '\t.string "Vou te ensinar o que é ser um\\n"\n'
         '\t.string "TREINADOR de verdade!$"'),

        ('Route103_Text_BrendanDefeated:\n'
         '\t.string "Huh, {PLAYER}, you\'re not too shabby.$"'):
        ('Route103_Text_BrendanDefeated:\n'
         '\t.string "Uau, {PLAYER}, você é muito forte.$"'),

        ('Route103_Text_BrendanTimeToHeadBack:\n'
         '\t.string "BRENDAN: I think I get it.\\n"\n'
         '\t.string "I think I know why my dad has his eye\\l"\n'
         '\t.string "out for you now.\\p"\n'
         '\t.string "Look, your POKéMON already likes you,\\n"\n'
         '\t.string "even though you just got it.\\p"\n'
         '\t.string "{PLAYER}, I get the feeling that you\\n"\n'
         '\t.string "could befriend any POKéMON with ease.\\p"\n'
         '\t.string "We should head back to the LAB.$"'):
        ('Route103_Text_BrendanTimeToHeadBack:\n'
         '\t.string "BRENDAN: Acho que entendi.\\n"\n'
         '\t.string "Seu POKéMON já gosta de você,\\n"\n'
         '\t.string "mesmo tendo acabado de recebê-lo.\\p"\n'
         '\t.string "Você tem talento com POKéMON.\\p"\n'
         '\t.string "Vamos voltar para o LABORATÓRIO.$"'),

        ('Route103_Text_ShouldHaveBroughtPotion:\n'
         '\t.string "My POKéMON is staggeringly tired…\\n"\n'
         '\t.string "I should have brought a POTION…$"'):
        ('Route103_Text_ShouldHaveBroughtPotion:\n'
         '\t.string "Meu POKéMON está muito cansado…\\n"\n'
         '\t.string "Eu devia ter trazido uma POÇÃO…$"'),

        ('Route103_Text_ShortcutToOldale:\n'
         '\t.string "If you cross the sea from here,\\n"\n'
         '\t.string "it\'ll be a shortcut to OLDALE TOWN.\\p"\n'
         '\t.string "Fufufu, that\'s useful, isn\'t it?$"'):
        ('Route103_Text_ShortcutToOldale:\n'
         '\t.string "Cruzando o mar daqui, é um atalho\\n"\n'
         '\t.string "para a CIDADE DE OLDALE!$"'),

        ('Route103_Text_RouteSign:\n'
         '\t.string "ROUTE 103\\n"\n'
         '\t.string "{DOWN_ARROW} OLDALE TOWN$"'):
        ('Route103_Text_RouteSign:\n'
         '\t.string "ROTA 103\\n"\n'
         '\t.string "{DOWN_ARROW} CIDADE DE OLDALE$"'),
    }
    check_and_apply(r103, rep_r103, "data/maps/Route103/scripts.inc")


def apply_route102_strings(tree: Path) -> None:
    r102 = tree / "data/maps/Route102/scripts.inc"
    rep_r102 = {
        ('Route102_Text_WatchMeCatchPokemon:\n'
         '\t.string "WALLY: {PLAYER}…\\n"\n'
         '\t.string "POKéMON hide in tall grass like this,\\l"\n'
         '\t.string "don\'t they?\\p"\n'
         '\t.string "Please watch me and see if I can\\n"\n'
         '\t.string "catch one properly.\\p"\n'
         '\t.string "…Whoa!$"'):
        ('Route102_Text_WatchMeCatchPokemon:\n'
         '\t.string "WALLY: {PLAYER}…\\n"\n'
         '\t.string "Eles se escondem na grama alta\\n"\n'
         '\t.string "assim, não é?\\p"\n'
         '\t.string "Por favor, me observe para ver se\\n"\n'
         '\t.string "eu consigo pegar um direitinho.\\p"\n'
         '\t.string "…Uau!$"'),

        ('Route102_Text_WallyIDidIt:\n'
         '\t.string "WALLY: I did it… It\'s my…\\n"\n'
         '\t.string "My POKéMON!$"'):
        ('Route102_Text_WallyIDidIt:\n'
         '\t.string "WALLY: Eu consegui… É o meu…\\n"\n'
         '\t.string "O meu próprio POKéMON!$"'),

        ('Route102_Text_LetsGoBack:\n'
         '\t.string "{PLAYER}, thank you!\\n"\n'
         '\t.string "Let\'s go back to the GYM!$"'):
        ('Route102_Text_LetsGoBack:\n'
         '\t.string "{PLAYER}, muito obrigado!\\n"\n'
         '\t.string "Vamos voltar para o GINÁSIO!$"'),

        ('Route102_Text_ImNotVeryTall:\n'
         '\t.string "I\'m…not very tall, so I sink right\\n"\n'
         '\t.string "into tall grass.\\p"\n'
         '\t.string "The grass goes up my nose and…\\n"\n'
         '\t.string "Fwafwafwafwafwa…\\p"\n'
         '\t.string "Fwatchoo!$"'):
        ('Route102_Text_ImNotVeryTall:\n'
         '\t.string "Eu sou baixinho, então afundo\\n"\n'
         '\t.string "todo na grama alta.\\p"\n'
         '\t.string "A grama entra no meu nariz e…\\n"\n'
         '\t.string "Atchim!$"'),

        ('Route102_Text_CatchWholeBunchOfPokemon:\n'
         '\t.string "I\'m going to catch a whole bunch of\\n"\n'
         '\t.string "POKéMON!$"'):
        ('Route102_Text_CatchWholeBunchOfPokemon:\n'
         '\t.string "Eu vou pegar um montão de\\n"\n'
         '\t.string "POKéMON bem legais!$"'),

        ('Route102_Text_RouteSignOldale:\n'
         '\t.string "ROUTE 102\\n"\n'
         '\t.string "{RIGHT_ARROW} OLDALE TOWN$"'):
        ('Route102_Text_RouteSignOldale:\n'
         '\t.string "ROTA 102\\n"\n'
         '\t.string "{RIGHT_ARROW} CIDADE DE OLDALE$"'),

        ('Route102_Text_RouteSignPetalburg:\n'
         '\t.string "ROUTE 102\\n"\n'
         '\t.string "{LEFT_ARROW} PETALBURG CITY$"'):
        ('Route102_Text_RouteSignPetalburg:\n'
         '\t.string "ROTA 102\\n"\n'
         '\t.string "{LEFT_ARROW} CIDADE DE PETALBURG$"'),
    }
    check_and_apply(r102, rep_r102, "data/maps/Route102/scripts.inc")


def apply_trainers_strings(tree: Path) -> None:
    tr = tree / "data/text/trainers.inc"
    rep_tr = {
        ('Route102_Text_CalvinIntro:\n'
         '\t.string "If you have POKéMON with you, then\\n"\n'
         '\t.string "you\'re an official POKéMON TRAINER!\\l"\n'
         '\t.string "You can\'t say no to my challenge!$"'):
        ('Route102_Text_CalvinIntro:\n'
         '\t.string "Se você carrega POKéMON, é um\\n"\n'
         '\t.string "TREINADOR oficial!\\l"\n'
         '\t.string "Não pode recusar meu desafio!$"'),

        ('Route102_Text_CalvinDefeated:\n'
         '\t.string "Arrgh, I lost…\\n"\n'
         '\t.string "I should have trained mine more…$"'):
        ('Route102_Text_CalvinDefeated:\n'
         '\t.string "Aargh, eu perdi…\\n"\n'
         '\t.string "Devia ter treinado muito mais…$"'),

        ('Route102_Text_CalvinPostBattle:\n'
         '\t.string "Listen, you. If you\'re strong,\\n"\n'
         '\t.string "you should have told me before!$"'):
        ('Route102_Text_CalvinPostBattle:\n'
         '\t.string "Se você era tão forte assim,\\n"\n'
         '\t.string "devia ter me avisado antes!$"'),

        ('Route102_Text_AllenIntro:\n'
         '\t.string "Did you just become a TRAINER?\\n"\n'
         '\t.string "We\'re both beginners!$"'):
        ('Route102_Text_AllenIntro:\n'
         '\t.string "Acabou de virar TREINADOR?\\n"\n'
         '\t.string "Nós dois somos novatos!$"'),

        ('Route102_Text_AllenDefeated:\n'
         '\t.string "I called you because I thought\\n"\n'
         '\t.string "I could beat you…$"'):
        ('Route102_Text_AllenDefeated:\n'
         '\t.string "Eu te chamei achando que podia\\n"\n'
         '\t.string "vencer você… que pena!$"'),

        ('Route102_Text_AllenPostBattle:\n'
         '\t.string "I haven\'t won once yet…\\n"\n'
         '\t.string "I wish I would win soon…$"'):
        ('Route102_Text_AllenPostBattle:\n'
         '\t.string "Ainda não venci nenhuma vez…\\n"\n'
         '\t.string "Queria tanto ganhar uma luta…$"'),

        ('Route102_Text_RickIntro:\n'
         '\t.string "Hahah! Our eyes met!\\n"\n'
         '\t.string "I\'ll take you on with my BUG POKéMON!$"'):
        ('Route102_Text_RickIntro:\n'
         '\t.string "Hahaha! Nossos olhares\\n"\n'
         '\t.string "se cruzaram! Lutarei com meus\\n"\n'
         '\t.string "POKéMON INSETO!$"'),

        ('Route102_Text_RickDefeated:\n'
         '\t.string "Ow! Down and out!$"'):
        ('Route102_Text_RickDefeated:\n'
         '\t.string "Ai! Fui totalmente derrotado!$"'),

        ('Route102_Text_RickPostBattle:\n'
         '\t.string "If you lock eyes with a TRAINER,\\n"\n'
         '\t.string "you have to challenge! It\'s a rule!$"'):
        ('Route102_Text_RickPostBattle:\n'
         '\t.string "Se cruzar os olhos com alguém,\\n"\n'
         '\t.string "tem que batalhar! É a regra!$"'),

        ('Route102_Text_TianaIntro:\n'
         '\t.string "I\'m going to keep winning and aim\\n"\n'
         '\t.string "to be the best TRAINER.\\p"\n'
         '\t.string "Help me further my career!$"'):
        ('Route102_Text_TianaIntro:\n'
         '\t.string "Vou continuar vencendo para ser\\n"\n'
         '\t.string "a melhor TREINADORA de todas!\\p"\n'
         '\t.string "Batalhe comigo agora!$"'),

        ('Route102_Text_TianaDefeated:\n'
         '\t.string "I ended up furthering your career…$"'):
        ('Route102_Text_TianaDefeated:\n'
         '\t.string "Acabei ajudando na sua carreira…$"'),

        ('Route102_Text_TianaPostBattle:\n'
         '\t.string "To keep winning my way up, I see that\\n"\n'
         '\t.string "I have to catch more POKéMON.$"'):
        ('Route102_Text_TianaPostBattle:\n'
         '\t.string "Para vencer, vejo que preciso\\n"\n'
         '\t.string "capturar mais POKéMON.$"'),
    }
    check_and_apply(tr, rep_tr, "data/text/trainers.inc (Treinadores)")


def apply_petalburg_strings(tree: Path) -> None:
    # 1. PetalburgCity externa
    p_pet = tree / "data/maps/PetalburgCity/scripts.inc"
    rep_pet = {
        ('PetalburgCity_Text_WhereIsWally:\n'
         '\t.string "Where has our WALLY gone?\\p"\n'
         '\t.string "We have to leave for VERDANTURF TOWN\\n"\n'
         '\t.string "very soon…$"'):
        ('PetalburgCity_Text_WhereIsWally:\n'
         '\t.string "Aonde será que o WALLY foi?\\p"\n'
         '\t.string "Temos que ir para a CIDADE DE\\n"\n'
         '\t.string "VERDANTURF em breve…$"'),

        ('PetalburgCity_Text_AreYouRookieTrainer:\n'
         '\t.string "Hiya! Are you maybe…\\n"\n'
         '\t.string "A rookie TRAINER?\\p"\n'
         '\t.string "Do you know what POKéMON TRAINERS\\n"\n'
         '\t.string "do when they reach a new town?\\p"\n'
         '\t.string "They first check what kind of GYM\\n"\n'
         '\t.string "is in the town.$"'):
        ('PetalburgCity_Text_AreYouRookieTrainer:\n'
         '\t.string "Olá! Você por acaso é novato?\\p"\n'
         '\t.string "Sabe o que TREINADORES fazem ao\\n"\n'
         '\t.string "chegar numa cidade nova?\\p"\n'
         '\t.string "Eles vão direto ao GINÁSIO!$"'),

        ('PetalburgCity_Text_ThisIsPetalburgGym:\n'
         '\t.string "See? This is PETALBURG CITY\'s GYM.$"'):
        ('PetalburgCity_Text_ThisIsPetalburgGym:\n'
         '\t.string "Viu? É o GINÁSIO DE PETALBURG.$"'),

        ('PetalburgCity_Text_ThisIsGymSign:\n'
         '\t.string "This is the GYM\'s sign. Look for it\\n"\n'
         '\t.string "whenever you\'re looking for a GYM.$"'):
        ('PetalburgCity_Text_ThisIsGymSign:\n'
         '\t.string "Esta é a placa do GINÁSIO.\\n"\n'
         '\t.string "Procure por ela nas cidades!$"'),

        ('PetalburgCity_Text_WaterReflection:\n'
         '\t.string "My face is reflected in the water.\\p"\n'
         '\t.string "It\'s a shining grin full of hope…\\p"\n'
         '\t.string "Or it could be a look of somber silence\\n"\n'
         '\t.string "struggling with fear…\\p"\n'
         '\t.string "What do you see reflected in your face?$"'):
        ('PetalburgCity_Text_WaterReflection:\n'
         '\t.string "Meu rosto reflete na água.\\p"\n'
         '\t.string "É um sorriso cheio de esperança…\\p"\n'
         '\t.string "O que você vê refletido no seu?$"'),

        ('PetalburgCity_Text_GymSign:\n'
         '\t.string "PETALBURG CITY POKéMON GYM\\n"\n'
         '\t.string "LEADER: NORMAN\\l"\n'
         '\t.string "“A man in pursuit of power!”$"'):
        ('PetalburgCity_Text_GymSign:\n'
         '\t.string "GINÁSIO POKéMON DE PETALBURG\\n"\n'
         '\t.string "LÍDER: NORMAN\\l"\n'
         '\t.string "“Um homem em busca de poder!”$"'),

        ('PetalburgCity_Text_CitySign:\n'
         '\t.string "PETALBURG CITY\\n"\n'
         '\t.string "“Where people mingle with nature.”$"'):
        ('PetalburgCity_Text_CitySign:\n'
         '\t.string "CIDADE DE PETALBURG\\n"\n'
         '\t.string "“Onde pessoas convivem\\n"\n'
         '\t.string "com a natureza.”$"'),

        ('PetalburgCity_Text_WallyHouseSign:\n'
         '\t.string "WALLY\'S HOUSE$"'):
        ('PetalburgCity_Text_WallyHouseSign:\n'
         '\t.string "CASA DO WALLY$"'),

        ('PetalburgCity_Text_ImLookingForTalentedTrainers:\n'
         '\t.string "I\'m roaming the land in search of\\n"\n'
         '\t.string "talented TRAINERS.\\p"\n'
         '\t.string "I\'m sorry to have taken your time.$"'):
        ('PetalburgCity_Text_ImLookingForTalentedTrainers:\n'
         '\t.string "Viajo pelo mundo buscando grandes\\n"\n'
         '\t.string "TREINADORES de talento.\\p"\n'
         '\t.string "Desculpe tomar o seu tempo!$"'),
    }
    check_and_apply(p_pet, rep_pet, "data/maps/PetalburgCity/scripts.inc")

    # 2. PetalburgCity_Gym
    p_gym = tree / "data/maps/PetalburgCity_Gym/scripts.inc"
    rep_gym = {
        ('PetalburgCity_Gym_Text_DadYoureHereWithYourPokemon:\n'
         '\t.string "DAD: Hm?\\p"\n'
         '\t.string "Well, if it isn\'t {PLAYER}!\\n"\n'
         '\t.string "So you\'re all finished moving in?\\p"\n'
         '\t.string "I\'m surprised that you managed to\\n"\n'
         '\t.string "get here by yourself.\\p"\n'
         '\t.string "Oh, I see.\\n"\n'
         '\t.string "You\'re with your POKéMON.\\p"\n'
         '\t.string "Hm… Then I guess you\'re going to\\n"\n'
         '\t.string "become a TRAINER like me, {PLAYER}.\\p"\n'
         '\t.string "That\'s great news!\\n"\n'
         '\t.string "I\'ll be looking forward to it!$"'):
        ('PetalburgCity_Gym_Text_DadYoureHereWithYourPokemon:\n'
         '\t.string "PAPAI: Hum?\\p"\n'
         '\t.string "Ora, se não é {PLAYER}!\\n"\n'
         '\t.string "Terminaram toda a mudança?\\p"\n'
         '\t.string "Estou surpreso que tenha vindo\\n"\n'
         '\t.string "até aqui sozinho!\\p"\n'
         '\t.string "Ah, compreendo.\\n"\n'
         '\t.string "Você está com o seu POKéMON.\\p"\n'
         '\t.string "Hum… Então vai se tornar um grande\\n"\n'
         '\t.string "TREINADOR como eu, {PLAYER}.\\p"\n'
         '\t.string "Que ótima notícia! Fico ansioso!$"'),

        ('PetalburgCity_Gym_Text_WallyIdLikeAPokemon:\n'
         '\t.string "Um… I…\\n"\n'
         '\t.string "I\'d like to get a POKéMON, please…$"'):
        ('PetalburgCity_Gym_Text_WallyIdLikeAPokemon:\n'
         '\t.string "Com licença… Eu…\\n"\n'
         '\t.string "Gostaria de um POKéMON, por favor…$"'),

        ('PetalburgCity_Gym_Text_DadOhYoureWallyRight:\n'
         '\t.string "DAD: Hm? You\'re… Uh… Oh, right.\\n"\n'
         '\t.string "You\'re WALLY, right?$"'):
        ('PetalburgCity_Gym_Text_DadOhYoureWallyRight:\n'
         '\t.string "PAPAI: Hum? Você é… Ah, certo.\\n"\n'
         '\t.string "Você é o WALLY, não é?$"'),

        ('PetalburgCity_Gym_Text_WallyIveNeverCaughtAPokemon:\n'
         '\t.string "WALLY: I\'m going to go stay with my\\n"\n'
         '\t.string "relatives in VERDANTURF TOWN.\\p"\n'
         '\t.string "I thought I would be lonely by myself,\\n"\n'
         '\t.string "so I wanted to take a POKéMON along.\\p"\n'
         '\t.string "But I\'ve never caught a POKéMON before.\\n"\n'
         '\t.string "I don\'t know how…$"'):
        ('PetalburgCity_Gym_Text_WallyIveNeverCaughtAPokemon:\n'
         '\t.string "WALLY: Vou ficar com parentes na\\n"\n'
         '\t.string "CIDADE DE VERDANTURF.\\p"\n'
         '\t.string "Ficarei solitário sozinho, então\\n"\n'
         '\t.string "queria levar um POKéMON comigo.\\p"\n'
         '\t.string "Mas nunca peguei um POKéMON antes.\\n"\n'
         '\t.string "Eu não sei como fazer…$"'),

        ('PetalburgCity_Gym_Text_DadHmISee:\n'
         '\t.string "DAD: Hm. I see.$"'):
        ('PetalburgCity_Gym_Text_DadHmISee:\n'
         '\t.string "PAPAI: Hum. Compreendo.$"'),

        ('PetalburgCity_Gym_Text_DadPlayerGoWithWally:\n'
         '\t.string "DAD: {PLAYER}, you heard that,\\n"\n'
         '\t.string "right?\\p"\n'
         '\t.string "Go with WALLY and make sure that he\\n"\n'
         '\t.string "safely catches a POKéMON.$"'):
        ('PetalburgCity_Gym_Text_DadPlayerGoWithWally:\n'
         '\t.string "PAPAI: {PLAYER}, você ouviu isso?\\p"\n'
         '\t.string "Vá com WALLY e garanta que ele\\n"\n'
         '\t.string "pegue um POKéMON com segurança.$"'),

        ('PetalburgCity_Gym_Text_IllLoanYouMyZigzagoon:\n'
         '\t.string "WALLY, here, I\'ll loan you my POKéMON.\\p"\n'
         '\t.string "WALLY received a ZIGZAGOON!$"'):
        ('PetalburgCity_Gym_Text_IllLoanYouMyZigzagoon:\n'
         '\t.string "WALLY, tome, vou emprestar\\n"\n'
         '\t.string "um POKéMON para você.\\p"\n'
         '\t.string "WALLY recebeu um ZIGZAGOON!$"'),

        ('PetalburgCity_Gym_Text_WallyThankYouAndDadGivesPokeBall:\n'
         '\t.string "WALLY: Oh, wow!\\n"\n'
         '\t.string "A POKéMON!\\p"\n'
         '\t.string "DAD: Hm. I\'ll give you a POKé BALL, too.\\n"\n'
         '\t.string "Go for it!\\p"\n'
         '\t.string "WALLY received a POKé BALL!$"'):
        ('PetalburgCity_Gym_Text_WallyThankYouAndDadGivesPokeBall:\n'
         '\t.string "WALLY: Uau! Um POKéMON!\\p"\n'
         '\t.string "PAPAI: Tome também uma POKéBOLA.\\n"\n'
         '\t.string "Vá em frente!\\p"\n'
         '\t.string "WALLY recebeu uma POKéBOLA!$"'),

        ('PetalburgCity_Gym_Text_WallyOhWowThankYou:\n'
         '\t.string "WALLY: Oh, wow!\\n"\n'
         '\t.string "Thank you!$"'):
        ('PetalburgCity_Gym_Text_WallyOhWowThankYou:\n'
         '\t.string "WALLY: Puxa vida! Muito obrigado!$"'),

        ('PetalburgCity_Gym_Text_WouldYouReallyComeWithMe:\n'
         '\t.string "{PLAYER}… Would you really come\\n"\n'
         '\t.string "with me?$"'):
        ('PetalburgCity_Gym_Text_WouldYouReallyComeWithMe:\n'
         '\t.string "{PLAYER}… Você realmente vem comigo?$"'),

        ('PetalburgCity_Gym_Text_DadSoDidItWorkOut:\n'
         '\t.string "DAD: So, did it work out?$"'):
        ('PetalburgCity_Gym_Text_DadSoDidItWorkOut:\n'
         '\t.string "PAPAI: E então, deu tudo certo?$"'),

        ('PetalburgCity_Gym_Text_WallyThankYouBye:\n'
         '\t.string "WALLY: Thank you, yes, it did.\\n"\n'
         '\t.string "Here\'s your POKéMON back.\\p"\n'
         '\t.string "{PLAYER}, thank you for coming along\\n"\n'
         '\t.string "with me.\\p"\n'
         '\t.string "You two are why I was able to catch\\n"\n'
         '\t.string "my POKéMON.\\p"\n'
         '\t.string "I promise I\'ll take really good\\n"\n'
         '\t.string "care of it.\\p"\n'
         '\t.string "Oh! My mom\'s waiting for me,\\n"\n'
         '\t.string "so I have to go!\\p"\n'
         '\t.string "Bye, {PLAYER}!$"'):
        ('PetalburgCity_Gym_Text_WallyThankYouBye:\n'
         '\t.string "WALLY: Muito obrigado, sim, deu!\\n"\n'
         '\t.string "Aqui está seu POKéMON de volta.\\p"\n'
         '\t.string "{PLAYER}, obrigado por vir comigo.\\p"\n'
         '\t.string "Graças a vocês consegui o meu!\\p"\n'
         '\t.string "Vou cuidar muito bem dele.\\p"\n'
         '\t.string "Minha mãe está esperando lá fora!\\p"\n'
         '\t.string "Até logo, {PLAYER}!$"'),

        ('PetalburgCity_Gym_Text_DadGoCollectBadges:\n'
         '\t.string "DAD: Now…\\p"\n'
         '\t.string "{PLAYER}, if you want to become a\\n"\n'
         '\t.string "strong TRAINER, here\'s my advice.\\p"\n'
         '\t.string "Head for RUSTBORO CITY beyond this\\n"\n'
         '\t.string "town.\\p"\n'
         '\t.string "There, you should challenge\\n"\n'
         '\t.string "the GYM LEADER, ROXANNE.\\p"\n'
         '\t.string "After her, go on to other POKéMON\\n"\n'
         '\t.string "GYMS and defeat their LEADERS.\\p"\n'
         '\t.string "Collect BADGES from them,\\n"\n'
         '\t.string "understood?\\p"\n'
         '\t.string "Of course, I\'m a GYM LEADER, too.\\n"\n'
         '\t.string "We\'ll battle one day, {PLAYER}.\\p"\n'
         '\t.string "But that\'s only after you become\\n"\n'
         '\t.string "stronger.$"'):
        ('PetalburgCity_Gym_Text_DadGoCollectBadges:\n'
         '\t.string "PAPAI: Agora… {PLAYER}, para ser\\n"\n'
         '\t.string "um TREINADOR forte,\\n"\n'
         '\t.string "ouça o meu conselho.\\p"\n'
         '\t.string "Siga para a CIDADE DE RUSTBORO.\\p"\n'
         '\t.string "Lá, você deve desafiar a\\n"\n'
         '\t.string "LÍDER DE GINÁSIO, ROXANNE.\\p"\n'
         '\t.string "Depois, enfrente outros\\n"\n'
         '\t.string "GINÁSIOS da região\\n"\n'
         '\t.string "e junte as INSÍGNIAS, entendeu?\\p"\n'
         '\t.string "Eu também sou um LÍDER.\\n"\n'
         '\t.string "Nós vamos lutar um dia, {PLAYER}.\\p"\n'
         '\t.string "Mas só quando estiver mais forte!$"'),
    }
    check_and_apply(p_gym, rep_gym, "data/maps/PetalburgCity_Gym/scripts.inc")

    # 3. Petalburg Houses, Center, Mart
    p_h1 = tree / "data/maps/PetalburgCity_House1/scripts.inc"
    rep_h1 = {
        ('PetalburgCity_House1_Text_TravelingIsWonderful:\n'
         '\t.string "Traveling is wonderful!\\p"\n'
         '\t.string "When I was young, I roamed the seas\\n"\n'
         '\t.string "and the mountains!$"'):
        ('PetalburgCity_House1_Text_TravelingIsWonderful:\n'
         '\t.string "Viajar é maravilhoso!\\p"\n'
         '\t.string "Quando jovem, explorei os mares\\n"\n'
         '\t.string "e as mais belas montanhas!$"'),
    }
    check_and_apply(p_h1, rep_h1, "data/maps/PetalburgCity_House1/scripts.inc")

    p_h2 = tree / "data/maps/PetalburgCity_House2/scripts.inc"
    rep_h2 = {
        ('PetalburgCity_House2_Text_NormanBecameGymLeader:\n'
         '\t.string "NORMAN became our town\'s new\\n"\n'
         '\t.string "GYM LEADER.\\p"\n'
         '\t.string "I think he called his family over from\\n"\n'
         '\t.string "somewhere far away.$"'):
        ('PetalburgCity_House2_Text_NormanBecameGymLeader:\n'
         '\t.string "NORMAN virou o novo LÍDER.\\p"\n'
         '\t.string "Acho que chamou a família de longe\\n"\n'
         '\t.string "para morar aqui na cidade.$"'),
    }
    check_and_apply(p_h2, rep_h2, "data/maps/PetalburgCity_House2/scripts.inc")

    p_pc = tree / "data/maps/PetalburgCity_PokemonCenter_1F/scripts.inc"
    rep_pc = {
        ('PetalburgCity_PokemonCenter_1F_Text_PCStorageSystem:\n'
         '\t.string "That PC-based POKéMON Storage\\n"\n'
         '\t.string "System…\\p"\n'
         '\t.string "Whoever made it must be some kind\\n"\n'
         '\t.string "of a scientific wizard!$"'):
        ('PetalburgCity_PokemonCenter_1F_Text_PCStorageSystem:\n'
         '\t.string "O sistema de caixas no PC…\\p"\n'
         '\t.string "Quem criou deve ser um verdadeiro\\n"\n'
         '\t.string "gênio da informática!$"'),
    }
    check_and_apply(p_pc, rep_pc, "data/maps/PetalburgCity_PokemonCenter_1F/scripts.inc")

    p_pm = tree / "data/maps/PetalburgCity_Mart/scripts.inc"
    rep_pm = {
        ('PetalburgCity_Mart_Text_WeakWillGrowStronger:\n'
         '\t.string "Even if a POKéMON is weak now,\\n"\n'
         '\t.string "it will grow stronger.\\p"\n'
         '\t.string "The most important thing is love!\\n"\n'
         '\t.string "Love for your POKéMON!$"'):
        ('PetalburgCity_Mart_Text_WeakWillGrowStronger:\n'
         '\t.string "Mesmo fraco agora, o POKéMON\\n"\n'
         '\t.string "vai se tornar mais forte.\\p"\n'
         '\t.string "O mais importante é o amor!\\n"\n'
         '\t.string "Amor pelo seu POKéMON!$"'),

        ('PetalburgCity_Mart_Text_RepelIsUseful:\n'
         '\t.string "Do you use REPEL?\\n"\n'
         '\t.string "It keeps POKéMON away, so it\'s\\l"\n'
         '\t.string "useful when you\'re in a hurry.$"'):
        ('PetalburgCity_Mart_Text_RepelIsUseful:\n'
         '\t.string "Você usa REPEL?\\n"\n'
         '\t.string "Ele afasta POKéMON selvagens,\\l"\n'
         '\t.string "ótimo quando você tem pressa!$"'),

        ('PetalburgCity_Mart_Text_TakeSomeAntidotesWithYou:\n'
         '\t.string "Do you have any ANTIDOTES with\\n"\n'
         '\t.string "you?\\p"\n'
         '\t.string "If you walk around with a poisoned\\n"\n'
         '\t.string "POKéMON, it will lose HP until it faints.\\l"\n'
         '\t.string "Take some ANTIDOTES with you.$"'):
        ('PetalburgCity_Mart_Text_TakeSomeAntidotesWithYou:\n'
         '\t.string "Você tem ANTÍDOTOS na bolsa?\\p"\n'
         '\t.string "Se andar com um POKéMON\\n"\n'
         '\t.string "envenenado, ele perderá HP até\\l"\n'
         '\t.string "desmaiar. Leve ANTÍDOTOS!$"'),
    }
    check_and_apply(p_pm, rep_pm, "data/maps/PetalburgCity_Mart/scripts.inc")


def apply_birch_speech_strings(tree: Path) -> None:
    p = tree / "data/text/birch_speech.inc"
    replacements = {
        ('gText_Birch_Welcome::\n'
         '\t.string "Hi! Sorry to keep you waiting!\\p"\n'
         '\t.string "Welcome to the world of POKéMON!\\p"\n'
         '\t.string "My name is BIRCH.\\p"\n'
         '\t.string "But everyone calls me the POKéMON\\n"\n'
         '\t.string "PROFESSOR.\\p"\n'
         '\t.string "$"'):
        ('gText_Birch_Welcome::\n'
         '\t.string "Olá! Desculpe a demora!\\p"\n'
         '\t.string "Bem-vindo ao mundo POKéMON!\\p"\n'
         '\t.string "Meu nome é BIRCH.\\p"\n'
         '\t.string "Mas todos me chamam de\\n"\n'
         '\t.string "PROFESSOR POKéMON.\\p"\n'
         '\t.string "$"'),

        ('gText_Birch_Pokemon::\n'
         '\t.string "This is what we call a “POKéMON.”\\p"\n'
         '\t.string "\\n"\n'
         '\t.string "$"'):
        ('gText_Birch_Pokemon::\n'
         '\t.string "Isto é o que chamamos\\n"\n'
         '\t.string "de “POKéMON.”\\p"\n'
         '\t.string "\\n"\n'
         '\t.string "$"'),

        ('gText_Birch_MainSpeech::\n'
         '\t.string "This world is widely inhabited by\\n"\n'
         '\t.string "creatures known as POKéMON.\\p"\n'
         '\t.string "We humans live alongside POKéMON,\\n"\n'
         '\t.string "at times as friendly playmates, and\\l"\n'
         '\t.string "at times as cooperative workmates.\\p"\n'
         '\t.string "And sometimes, we band together\\n"\n'
         '\t.string "and battle others like us.\\p"\n'
         '\t.string "But despite our closeness, we don\'t\\n"\n'
         '\t.string "know everything about POKéMON.\\p"\n'
         '\t.string "In fact, there are many, many\\n"\n'
         '\t.string "secrets surrounding POKéMON.\\p"\n'
         '\t.string "To unravel POKéMON mysteries,\\n"\n'
         '\t.string "I\'ve been undertaking research.\\l"\n'
         '\t.string "That\'s what I do.\\p"\n'
         '\t.string "$"'):
        ('gText_Birch_MainSpeech::\n'
         '\t.string "Este mundo é habitado por\\n"\n'
         '\t.string "criaturas chamadas POKéMON.\\p"\n'
         '\t.string "Nós convivemos com os POKéMON,\\n"\n'
         '\t.string "às vezes como bons amigos,\\l"\n'
         '\t.string "e às vezes trabalhando juntos.\\p"\n'
         '\t.string "E em certos momentos, nós\\n"\n'
         '\t.string "batalhamos entre nós.\\p"\n'
         '\t.string "Mas apesar de tão próximos,\\n"\n'
         '\t.string "não sabemos tudo sobre eles.\\p"\n'
         '\t.string "Na verdade, ainda existem muitos\\n"\n'
         '\t.string "mistérios sobre os POKéMON.\\p"\n'
         '\t.string "Para desvendar esses mistérios,\\n"\n'
         '\t.string "eu faço pesquisas de campo.\\l"\n'
         '\t.string "Essa é a minha vida.\\p"\n'
         '\t.string "$"'),

        ('gText_Birch_AndYouAre::\n'
         '\t.string "And you are?$"'):
        ('gText_Birch_AndYouAre::\n'
         '\t.string "E quem é você?$"'),

        ('gText_Birch_BoyOrGirl::\n'
         '\t.string "Are you a boy?\\n"\n'
         '\t.string "Or are you a girl?$"'):
        ('gText_Birch_BoyOrGirl::\n'
         '\t.string "Você é um menino?\\n"\n'
         '\t.string "Ou é uma menina?$"'),

        ('gText_Birch_WhatsYourName::\n'
         '\t.string "All right.\\n"\n'
         '\t.string "What\'s your name?$"'):
        ('gText_Birch_WhatsYourName::\n'
         '\t.string "Muito bem.\\n"\n'
         '\t.string "Qual é o seu nome?$"'),

        ('gText_Birch_SoItsPlayer::\n'
         '\t.string "So it\'s {PLAYER}{KUN}?$"'):
        ('gText_Birch_SoItsPlayer::\n'
         '\t.string "Então é {PLAYER}{KUN}?$"'),

        ('gText_Birch_YourePlayer::\n'
         '\t.string "Ah, okay!\\p"\n'
         '\t.string "You\'re {PLAYER}{KUN} who\'s moving to my\\n"\n'
         '\t.string "hometown of LITTLEROOT.\\l"\n'
         '\t.string "I get it now!\\p"\n'
         '\t.string "$"'):
        ('gText_Birch_YourePlayer::\n'
         '\t.string "Ah, sim!\\p"\n'
         '\t.string "Você é {PLAYER}{KUN}, que vai morar\\n"\n'
         '\t.string "na minha cidade, VILA RAIZ.\\l"\n'
         '\t.string "Agora tudo faz sentido!\\p"\n'
         '\t.string "$"'),

        ('gText_Birch_AreYouReady::\n'
         '\t.string "All right, are you ready?\\p"\n'
         '\t.string "Your very own adventure is about\\n"\n'
         '\t.string "to unfold.\\p"\n'
         '\t.string "Take courage, and leap into the\\n"\n'
         '\t.string "world of POKéMON where dreams,\\l"\n'
         '\t.string "adventure, and friendships await!\\p"\n'
         '\t.string "Well, I\'ll be expecting you later.\\n"\n'
         '\t.string "Come see me in my POKéMON LAB.\\p"\n'
         '\t.string "$"'):
        ('gText_Birch_AreYouReady::\n'
         '\t.string "Muito bem, está pronto?\\p"\n'
         '\t.string "Sua grande jornada está\\n"\n'
         '\t.string "prestes a começar.\\p"\n'
         '\t.string "Tenha coragem e entre no mundo\\n"\n'
         '\t.string "dos POKéMON, onde sonhos e\\l"\n'
         '\t.string "grandes amizades o aguardam!\\p"\n'
         '\t.string "Estarei esperando por você.\\n"\n'
         '\t.string "Venha ao meu LABORATÓRIO.\\p"\n'
         '\t.string "$"'),
    }
    check_and_apply(p, replacements, "data/text/birch_speech.inc (Introdução Birch)")


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
    apply_birch_speech_strings(tree)
    apply_nurse_and_mart_strings(tree)
    apply_battle_strings(tree)
    apply_item_and_berry_strings(tree)
    apply_widescreen_battle_layout(tree)
    apply_trainers_strings(tree)
    apply_littleroot_strings(tree)
    apply_route101_strings(tree)
    apply_oldale_strings(tree)
    apply_route103_strings(tree)
    apply_route102_strings(tree)
    apply_petalburg_strings(tree)
    apply_gym1_to_gym3_strings(tree)

    (tree / ".emerald3ds-locale").write_bytes(b"PTBR stable v5\n")
    print(f"PT-BR staging v5 complete! {applied_edits} edits applied across {applied_files} source files.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    args = parser.parse_args()
    stage(args.tree.resolve(), args.rom)


if __name__ == "__main__":
    main()
