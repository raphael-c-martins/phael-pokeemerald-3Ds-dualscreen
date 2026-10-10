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

## 🚀 09/10/2026 - Milestone v3: Localização de Telas de Salvamento, Interface Touch e Eventos Iniciais
- **Branch Ativa:** `tentativa3`
- **Binário Gerado:** `dist_3ds/emerald3ds_v3.3dsx` (33.542.204 bytes) e `dist_3ds/emerald3ds.3dsx`.
- **Status do Build:** Sucesso absoluto (código de saída 0, 6.423/6.423 assets verificados e validados, ABI estável).

### 🛠️ Modificações Realizadas na v3:
1. **Engine 3DS e Interface Touch (`3ds_locale.h` e `3ds_bottom_ui.c`):**
   - Ativação da macro `CTR_TEXT` para resolução nativa de strings localizadas nos botões touch.
   - Tradução dos títulos das abas do menu de configurações inferior: `SETTINGS`, `ENHANCEMENTS`, `CHEATS` -> **`OPÇÕES`**, **`MELHORIAS`**, **`TRAPAÇAS`**.
2. **Strings de Sistema e Menus (`tools/localize_ptbr.py`):**
   - Tradução dos botões de decisão: `SIM` / `NÃO`.
   - Categorias da mochila touch: `ITENS`, `POKéBOLAS`, `TMs e HMs`, `FRUTAS`, `ITENS-CHAVE`, `FECHAR BOLSA`.
   - Identificadores do Trainer Card: `NOME: `, `DINHEIRO`, `TEMPO`, `Nº ID`, `INSÍGNIAS`.
3. **Telas e Diálogos de Salvamento (`data/text/save.inc`):**
   - Diálogos completos de gravação: *"Deseja salvar o jogo?"*, *"Já existe um arquivo salvo. Sobrescrever o arquivo?"*, *"SALVANDO… NÃO DESLIGUE O CONSOLE."* e *"{PLAYER} salvou o jogo."*.
4. **Diálogos de História e Mapas Iniciais:**
   - **Littleroot Town Externa:** Placas da cidade, do laboratório e da casa do jogador.
   - **Casa do Jogador (2F e 1F):** Diálogos do quarto (relógio parado, GameCube, caderno de notas) e do andar térreo (diálogos da mãe ao entrar, aviso do relógio, notícia de Petalburg Gym na TV e indicação do Prof. Birch).
   - **Casa do Rival (May):** Diálogos com a mãe da May e primeira conversa com a rival no quarto.
   - **Laboratório do Prof. Birch:** Diálogo do cientista explicando trabalho de campo e ausência do Birch.
   - **Rota 101:** Evento de perseguição do Zigzagoon, grito de socorro do Birch (*"S-socorro!"*, *"Na minha BOLSA! Tem uma POKéBOLA!"*), resgate e diálogo de agradecimento ao entregar o Pokémon inicial.

---

## 🏆 Resultado da Validação no Hardware Real (Old 3DS) - Milestone v3: SUCESSO E ESTABILIDADE ABSOLUTA!
- **Data da Validação:** 10/10/2026
- **Status:** **APROVADO NO CONSOLE FÍSICO COM ALTA PERFORMANCE!**
- **Evidências Arquivadas:** `# TEMPORARIO/Tentativa-v3/` (24 fotografias em alta resolução + `port.log` com 34.278 frames + `port-prev.log` + `settings.txt`).

### 🔍 Diagnóstico Técnico das Evidências da v3:
1. **Performance e Resiliência Excepcionais:**
   - O jogo executou por mais de 9,5 minutos ininterruptos (**34.278 frames**) a sólidos **59.8 ~ 59.9 FPS**.
   - Consumo de CPU médio entre **2.8 ms e 3.5 ms** (muito abaixo do teto de 16.6 ms).
   - O sistema de diagnóstico com sentinela (`debug.txt` -> `port.log`) operou perfeitamente, registrando taps na tela touch, swap de buffers e um encerramento 100% limpo (`[BOOT] clean shutdown`).
2. **Validações de Conteúdo Aprovadas:**
   - Telas de Save e confirmação de sobrescrita 100% em português.
   - Interface touch screen inferior com abas `OPÇÕES`, `MELHORIAS` e `TRAPAÇAS` e botões de decisão funcionando fluidamente.
   - Evento do Zigzagoon na Rota 101, grito de socorro do Birch e seleção do Pokémon inicial na bolsa perfeitamente funcionais.
3. **Anomalias Reportadas e Diagnóstico de Causa Raiz:**
   - **Estouro de Texto na Caixa de Diálogo:** Frases com mais de 34 caracteres por linha vazaram para fora da borda direita da caixa de diálogo clássica do GBA.
   - **Transição de Idioma no Prof. Birch:** Diálogos do Birch no laboratório pós-resgate (`MightBeGoodIdeaToGoSeeRival` e `GetRivalToTeachYou`) ainda estavam no texto original em inglês.
   - **Falas de TV:** Falas da reportagem do pai na TV (`ReportFromPetalburgGym` e `TheresAMovieOnTV`) pendentes de localização.
   - **Rival e Batalha na Rota 103:** Encontro com a May/Brendan na Rota 103 e batalha ainda em inglês.

---

## 🚀 10/10/2026 - Milestone v4: Ajuste Fino de Layout, Rota 103, Oldale Town, Petalburg Gym e Citra QA
- **Branch Ativa:** `tentativa4`
- **Binário Gerado:** `dist_3ds/emerald3ds_v4.3dsx` (33.540.476 bytes) e `dist_3ds/emerald3ds.3dsx`.
- **Status da Compilação:** **SUCESSO ABSOLUTO** (Código de saída 0, ABI `b9c6e212`, 6.423/6.423 assets empacotados e validados).

### 🛠️ Modificações Realizadas na v4:
1. **Eliminação do Estouro de Texto (Auditoria Métrica Estrita):**
   - Desenvolvida verificação com limites em tempo de execução garantindo que todas as falas respeitem o limite de **<= 32 a 33 caracteres por linha**.
   - Ajustadas todas as quebras de linha com caracteres de controle nativos do GBA (`\n`, `\l`, `\p`), impedindo que textos vazem da moldura do balão na tela real do console.
   - 219 de 219 blocos validados com 100% de match contra a árvore original do pokeemerald.
2. **Localização em Massa de Áreas Iniciais:**
   - **Littleroot Town Completa:** Falas da Mãe (chegada e descanso), quarto de Brendan/May (relógio, GameCube, caderno), TV da sala (notícia de Petalburg Gym e filme), Laboratório do Prof. Birch (falas pós-resgate, conselho de encontrar o rival e entrega da Pokédex oficial).
   - **Rota 101:** Resgate do Prof. Birch, perseguição do Zigzagoon e NPCs de dicas.
   - **Oldale Town Completa:** Todas as casas, Centro Pokémon (Enfermeira Joy), Poké Mart (balconista, mensagens de compra/venda, clientes no balcão) e placas informativas.
   - **Rota 103:** Diálogo com a rival May/Brendan, desafio pré-batalha, derrota e convite para voltar ao laboratório.
   - **Rota 102:** Todos os NPCs do caminho e treinadores de rota (Calvin, Allen, Rick, Tiana).
   - **Petalburg City & Ginásio:** Casas 1 e 2, Centro Pokémon, Poké Mart (3 NPCs), primeiro encontro com o pai Norman no Ginásio de Petalburg e evento completo do Wally pedindo ajuda para capturar o Zigzagoon.
3. **Módulo de Automação e QA com Citra (`tools/citra_runner.py`):**
   - Criação da ferramenta de automação CLI que localiza e lança o emulador Citra (`citra-qt.exe` / `citra.exe`) apontando direto para o `.3dsx` compilado.
   - Suporte a injeção automática de saves (`--save`) no SDMC virtual para testes instantâneos de rotas avançadas.
   - Ativação do modo sentinela (`debug.txt`) para capturar e auditar telemetria de `port.log` e `citra_log.txt` sem necessidade de hardware físico.
   - Criação da skill do agente em `.agents/skills/citra-qa-agent/SKILL.md` e workflow `/citra-debug`.

4. **Incorporação do Upstream Oficial Release v0.3.1:**
   - Incorporada a nova funcionalidade de compras do Poké Mart (`BUY`) renderizada nativamente na tela touch inferior com suporte a toque.
   - Hotfixes oficiais de estabilidade contra travamentos na Mirage Tower e no golpe *Hyper Beam*.
   - Atualizados banner e ícone oficiais para o HOME Menu do Nintendo 3DS.
5. **Introdução do Professor Birch em PT-BR (`data/text/birch_speech.inc`):**
   - Diálogos completos de abertura do jogo ("Bem-vindo ao mundo POKéMON!", escolha de menino/menina e nome) traduzidos com métrica estrita de no máximo 31 caracteres por linha, garantindo que o "Novo Jogo" inicie 100% em português desde o primeiro frame.

### 🎮 Validação no Emulador Citra com Save Limpo:
- **Telemetria em Execução:** Mais de 10.200 frames renderizados a **59.8 FPS** contínuos.
- **Consumo de Hardware:** CPU em **3.44 ms** (orçamento de 16.6 ms) e mixagem de áudio em **0.59 ms**.
- **Assets e Memória:** 6.424/6.424 assets verificados e carregados sem erros, confirmando estabilidade do binário v4 antes do hardware real.
