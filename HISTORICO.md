# Diário de Bordo e Histórico Arquitetural - Pokémon Emerald 3DS (PT-BR)

## 🛡️ Diretrizes Mandatórias de Preservação de Dados
> **Atenção:** Em qualquer manutenção, compilação ou evolução deste projeto, é expressamente proibido apagar, resetar ou sobrescrever arquivos de save (`.sav`), pastas de logs persistentes (`/logs/` ou `port.log`) e os arquivos brutos da pasta `# TEMPORARIO`. Todas as alterações estruturais devem ser rastreáveis, seguras e reversíveis.

---

## 📝 08/10/2026 - Milestone v1 e Diagnóstico da Primeira Execução no Hardware Real

### 1. Resumo da Entrega v1
- **Toolchain Operacional:** MSYS2 configurado com `devkitARM r68`, `libctru 2.7.0`, `citro2d 1.7.0`, `citro3d 1.7.1` e ambiente Python local para montagem de assets.
- **Primeiro Executável Gerado:** `emerald3ds.3dsx` (33,68 MB) com Engine ABI `0x89793437`.
- **Mapeamento de Conteúdo:** 355 nomes de golpes (ex.: *Bater*, *Cortar*, *Voar*, *Soco Fogo*), descrições de itens e nomes de espécies aplicados via tabelas em C com charmap GBA nativo.

---

### 2. Relatório de Execução no Console (Old 3DS)

O teste foi realizado em um Nintendo 3DS da família Old com o save do jogador (`Phael`, no início da jornada):

#### ✅ Pontos Fortes e Validações Positivas
- **Performance de Alto Nível:** O Old 3DS rodou a sólidos **59.8 FPS**, com consumo de CPU de apenas **3.94 ms** (num orçamento de 16.6 ms por frame) e tempo de mixagem de áudio de **1.3 ms**. Sem aquecimento, sem perda de frames e com áudio estéreo cristalino.
- **Boot e Compatibilidade:** O jogo passou a abertura, carregou os 6.391 assets e leu o save de 128 KB (`emerald3ds.sav`) com sucesso.

#### ⚠️ Anomalias Detectadas na Tela
1. **Menu de Continue Poluído:** A tela de informações do save exibiu textos misturados (*"tempo de bônus, você receberá moedas extras..."* e *"extras. S... us, você receb..."*) no lugar das informações normais de tempo e insígnias.
2. **Crash ao Entrar no Jogo:** Ao selecionar "CONTINUE", o console gerou uma tela de exceção do Luma3DS (`prefetch abort` no processador ARM11 no endereço `0x00381510`).

---

### 3. Diagnóstico e Causa Raiz (RCA)

A telemetria do `port.log` e a análise do crash dump (`crash_dump_00000005.dmp`) revelaram com precisão a causa raiz:
1. **Desalinhamento de Strings de Sistema:** Na primeira extração de textos, o gerador de locale aplicou substituições baseando-se estritamente nas posições de memória da ROM americana. Porém, na ROM PT-BR da comunidade, os tradutores moveram várias frases curtas e colocaram diálogos longos de minigames nos offsets antigos.
2. **Estouro de Textos no Menu:** Variáveis como `gText_ContinueMenuTime` (que em inglês continham apenas a palavra `"TIME"`) foram preenchidas acidentalmente com textos longos de diálogo contendo comandos de formatação e quebras de linha (`\n`, `\p`).
3. **Exceção de Renderização da Tela Inferior:** Ao carregar o mapa, a função `InkColumns` do motor do 3DS (`3ds_bottom_ui.c:1292`) tentou calcular a largura de caracteres dessas strings corrompidas. Ao encontrar bytes fora da tabela padrão de símbolos suportados, o ponteiro tentou acessar um endereço de memória inexistente, acionando o bloqueio de segurança do ARM11.

---

### 4. Plano de Ação para a Versão v2
1. **Isolamento de Strings de Interface:** Restaurar as variáveis de interface e labels de sistema em `src/strings.c` e `src/main_menu.c` para suas versões originais estáveis ou traduzidas manualmente de forma enxuta e segura (*ex.: "TEMPO", "INSÍGNIAS", "POKéDEX"*).
2. **Proteção Defensiva em `3ds_bottom_ui.c`:** Adicionar uma verificação de limites (*bounds checking*) nas funções de medição de fontes da tela inferior para garantir que nenhum caractere anômalo trave o processador.
3. **Pipeline Limpo de Compilação:** Garantir que o diretório `build/upstream` seja limpo antes da nova compilação para que apenas as alterações revisadas da v2 entrem no binário final.

---

## 🎯 Roteiro de Retomada Imediata (Próximos Passos para a v2)

Quando esta sessão for retomada, o agente/desenvolvedor deve seguir rigorosamente os seguintes passos para entregar a versão v2 estável:

1. **Passo 1: Higienização da Árvore de Compilação (`build/upstream`)**
   - Executar `git -C build/upstream checkout .` e `git -C build/upstream clean -fd` para remover as alterações residuais da tentativa v1.
   - Garantir que `src/strings.c` volte ao estado padrão antes de qualquer novo patch.

2. **Passo 2: Blindagem Defensiva na Tela Inferior (`3ds_bottom_ui.c`)**
   - Em `3ds_port/src/3ds_bottom_ui.c`, na função `InkColumns` e `DrawStr`, adicionar uma checagem de limites:
     ```c
     if (g >= 272) continue; // Impede leitura fora de gFontNormalLatinGlyphWidths
     ```
   - Isso elimina 100% da possibilidade de um `prefetch abort` no processador ARM11 por causa de caracteres inesperados.

3. **Passo 3: Localização Limpa e Segura do Menu Principal (`src/strings.c`)**
   - Traduzir manualmente apenas as labels curtas de sistema que o menu de continue exige:
     - `gText_ContinueMenuPlayer` -> `"JOGADOR"`
     - `gText_ContinueMenuTime` -> `"TEMPO"`
     - `gText_ContinueMenuPokedex` -> `"POKéDEX"`
     - `gText_ContinueMenuBadges` -> `"INSÍGNIAS"`
   - Não permitir injeção automática cega por offset em `src/strings.c`.

4. **Passo 4: Pipeline de Repointing para Diálogos de Mapas (v2)**
   - Utilizar o algoritmo já prototipado e validado em `scratch/decode_dialog_9c0f28.py` que busca os ponteiros originais da ROM USA (`0x08xxxxxx`), localiza o novo ponteiro repontado na ROM PT-BR (`0x089cxxxx+`) e decodifica o texto em português respeitando o charmap ocidental do pokeemerald.
   - Atualizar os arquivos de script correspondentes em `data/maps/.../scripts.inc`.

5. **Passo 5: Recompilação e Validação**
   - Executar `python tools/bootstrap.py --clean --ptbr-rom <caminho> --make -j8`.
   - Copiar o novo `emerald3ds.3dsx` para `dist_3ds/`.
   - Testar o save no Old 3DS: confirmar que o menu de continue carrega com layout limpo e que o jogo entra no mapa sem crash.
