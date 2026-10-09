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

## 🚀 08/10/2026 - Milestone v2: Blindagem ARM11, Limpeza de Menus e Executável v2 Pronto

### 1. Resumo da Entrega v2 (Branch `tentativa2`)
- **Sincronização Upstream Incorporada:** Incorporados os commits mais recentes do repositório oficial (`ZallaxDev/pokeemerald-3Ds-dualscreen`) com correções de relevo de voxels (Route 120 e Ever Grande) e o patch dos andares da Trainer Hill (`0040-trainer-hill-floors.patch`).
- **Regra Master Estabelecida:** Definida regra mandatória de verificação e sincronização diária com o upstream nos arquivos de governança do agente (`.agents/AGENTS.md` e `GEMINI.md`).
- **Blindagem do Processador ARM11:** Adicionada verificação estrita de limites (`g >= 272` e `glyph >= 272`) em todas as rotinas de desenho de texto da tela inferior (`StrWidth`, `DrawGlyph`, `DrawStr`, `GlyphInk`, `InkColumns`, além dos rasterizadores smooth e fallback em `3ds_port/src/3ds_bottom_ui.c`), eliminando a causa raiz do `prefetch abort` no Old 3DS.
- **Higienização e Localização de Menus:**
  - Telas de Continue e Menu Principal sem interferência de strings de minigames:
    - `NOVO JOGO`, `CONTINUAR`, `OPÇÕES`
    - `JOGADOR`, `TEMPO`, `POKéDEX`, `INSÍGNIAS`
  - Menu Start traduzido de forma segura: `POKéDEX`, `POKéMON`, `MOCHILA`, `SALVAR`, `OPÇÃO`, `SAIR`, `CANCELAR`.
- **Manifesto PT-BR Estável (2.176 Entradas):**
  - Mapeamento estrito com respeito absoluto aos tamanhos de buffers em C (evitando estouro de memória):
    - 355 Nomes de Golpes (100%)
    - 352 Descrições de Golpes
    - 293 Descrições de Itens
    - 276 Itens (respeitando limite de 15 caracteres)
    - 411 Nomes de Espécies
    - 78 Habilidades
    - 374 Entradas da Pokédex
    - Natures e Classes de Treinadores
- **Diálogos de Littleroot Town:** Diálogo da Mãe ao chegar na cidade e sinalização traduzidos de forma limpa.
- **Binário Gerado:** `emerald3ds_v2.3dsx` (33,54 MB) compilado com sucesso e disponibilizado em `dist_3ds/`.

---

## 🏆 Resultado da Validação no Hardware Real (Old 3DS) - Milestone v2: SUCESSO HISTÓRICO!
- **Data da Validação:** 08/10/2026
- **Status:** **APROVADO COM LOUVOR NO CONSOLE FÍSICO!**
- **Evidências Arquivadas:** `# TEMPORARIO/Tentativa-v2/` (13 fotos fotográficas do console real + `port.log` com 7.525 frames a 59.8 FPS).

### 🔍 Diagnóstico das Evidências (Fotos 1 a 13):
1. **Foto 2 (Tela de Título):** Boot limpo com Rayquaza na tela superior e assinatura da engine 3DS na tela inferior.
2. **Foto 3 (Menu Principal de Continue):** **100% Traduzido com acentuação perfeita!** Labels `CONTINUAR`, `JOGADOR Phael`, `TEMPO 0:01`, `INSÍGNIAS 0`, `NOVO JOGO`, `OPÇÕES` renderizados sem corrupção gráfica ou corte de memória.
3. **Fotos 1 e 4 (Entrada no Jogo e Touch Screen):** O save carregou perfeitamente no quarto de Brendan (`BrendansHouse_2F`) e no andar térreo (`BrendansHouse_1F`). Barra touch superior exibiu botões traduzidos (`MOCHILA`, `SALVAR`, `OPÇÃO`, `Phael`).
4. **Fotos 5 a 12 (Sub-telas do Port 3DS):** Mochila touch, Mapa, Trainer Card, Menus de Opções da engine do 3DS e janelas de confirmação de Save funcionaram 100% fluidas via toque.
5. **Fotos 1 e 13 (Diálogos de NPCs):** Os diálogos da mãe (*"MOM: Phael, how do you like your new room?"* e *"Go set the clock in your room, honey."*) ainda estão em inglês pois pertencem aos scripts de mapas de casas (`LittlerootTown_BrendansHouse_1F/2F`), foco da próxima etapa.

---

## 🎯 Próximo Passo: Milestone v3 (Branch `tentativa3`)
1. **Tradução da UI da Engine 3DS (`3ds_bottom_ui.c`):** Traduzir termos do touch (Mochila, Trainer Card, Telas de Salvar "Deseja salvar o jogo?", "Sim/Não", Opções do 3DS).
2. **Expansão de Scripts de Mapas:** Traduzir os eventos de Littleroot Town (Casa do jogador 1F/2F, Casa do rival, Laboratório do Birch e Início da Rota 101).
3. **Ambiente de Demonstração no PC:** Configurar script de execução/exibição emulada no computador para visualização direta do progresso.

