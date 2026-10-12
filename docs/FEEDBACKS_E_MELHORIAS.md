# 📋 Registro de Feedbacks, Relatórios e Melhorias (Ciclo pós-v10)

Este documento registra detalhadamente todos os apontamentos, impressões de teste no console e emulador, e ideias de melhorias arquiteturais levantadas pelo usuário para serem planejadas e implementadas em lote (*batch*) nas próximas versões.

---

## ✅ 1. Validações Aprovadas no Hardware Real e Emulador (Milestone v10)

1. **Logo da Tela de Título ("VERSÃO ESMERALDA"):**
   - **Status:** **Aprovado com sucesso.**
   - O logotipo alinhado em linha reta com a paleta oficial em português foi validado no Nintendo 3DS e no emulador.

2. **Velocidade Inteligente de Abertura / Boot (Fast-Forward Seguro):**
   - **Status:** **Aprovado com sucesso.**
   - O jogo inicia estritamente a **1x** (velocidade normal, sem acelerar músicas ou menus da abertura). Ao carregar o save e entrar no mundo ativo (*in-game*), o motor ativa dinamicamente a taxa acelerada configurada pelo usuário (ex.: **4x**).

3. **Menu de Inspeção e Resumo de Golpes (Pokémon Summary Screen):**
   - **Status:** **Aprovado com sucesso.**
   - Telas de resumo de Pokémon testadas e validadas: cabeçalhos (*GOLPES DE LUTA*, *EFEITO*, *DESCRIÇÃO*), atributos (*PODER*, *PRECISÃO*, *PP*), botões (*TROCAR*, *VOLTAR*) e textos de golpes e descrições com 100% de acentuação e alinhamento visual perfeito.

4. **Colheita de Frutas (Overworld Berry Picking):**
   - **Status:** **Aprovado com sucesso.**
   - Textos e diálogos de interação com arbustos de frutas testados e homologados: strings como *"Phael colheu 2 FRUTAS ORAN."* com nomes, concordância gramatical, numerais e acentuação 100% corretos e caixas centralizadas em widescreen.

5. **Diálogos de NPCs até a Rota 104 (Littleroot, Oldale, Rota 102, Petalburg e Rota 104):**
   - **Status:** **Aprovado com sucesso.**
   - Todos os NPCs abordados pelo jogador no overworld ao longo do percurso inicial (vilas, cidades, casas e rotas) exibiram falas com localização impecável em Português do Brasil, sem cortes de caracteres, com acentuação e pontuação corretas e sem estouro de balão.

---

## 🎯 2. Novos Apontamentos e Demandas para o Próximo Ciclo

### 📊 Item A: Posição das Healthboxes (Caixas de Vida em Batalha)
- **Cenário Atual (v10):**
  - Oponente: `x = 38, y = 20`
  - Jogador: `x = 160, y = 88`
- **Diagnóstico do Usuário:**
  - A caixa do Pokémon do jogador está em uma posição adequada/aceitável.
  - A caixa do Pokémon adversário ainda não está no ponto ideal desejado. Pelo print com a marcação em vermelho (`media_1791818705946.png`), o usuário deseja a caixa mais à esquerda e no alto do céu (aproximadamente `x ≈ 12~16, y ≈ 8~12`).
- **💡 Ideia Arquitetural Proposta pelo Usuário:**
  - Adicionar uma opção de configuração dentro do menu de **MELHORIAS** (na tela inferior touch) para permitir que o jogador escolha o posicionamento das Healthboxes.
  - **Mapeamento Técnico de Implementação:**
    - Em `3ds_port/src/3ds_extras.c`, na lista `CTR_EXTRAS_ENHANCEMENTS`:
      - Adicionar entrada configurável (ex.: `HEALTHBOX POS` com opções `PADRÃO (CÉU)`, `CLÁSSICO GBA`, `WIDESCREEN`).
      - Persistência automática no arquivo de configurações do SD (`emerald3ds.cfg`).
      - Em `src/battle_interface.c`, ler a variável de estado e aplicar os offsets correspondentes dinamicamente.

---

### 🎒 Item B: Interface da Mochila em Batalha (Battle Bag no Touch Screen)
- **Cenário Atual (v10):**
  - Ao selecionar "BOLSA" no menu de batalha da tela inferior, a mochila é renderizada em uma janela reduzida de **240x160** pixels centralizada na tela de **320x240** (com 40px de borda ociosa em cima/baixo e 40px nas laterais).
- **Diagnóstico do Usuário:**
  - A mochila ocupa um espaço muito reduzido em relação à área útil da tela inferior do 3DS (`media_1791818793628.png`), dificultando a visualização e ergonomia do toque.
- **Mapeamento Técnico de Implementação:**
  - A renderização da mochila em batalha é tratada no compositing de `3ds_port/src/3ds_video.c` (`CTR_CENTRED_BAG_WHOLE`).
  - **Caminhos de Melhoria Arquitetural:**
    1. Aplicar escala proporcional ou filtro bilinear na renderização do buffer da bolsa para preencher a tela de 320x240 (escala de 1.5x na vertical/horizontal).
    2. Recalibrar o mapeamento de toques em `3ds_bottom_ui.c` (`CtrBag_Touch`, offsets `ox` e `oy`) para acompanhar a nova resolução ampliada sem gerar perda de precisão no clique.

---

### 🏪 Item C: Quebra em Menus do Canto Superior Esquerdo (Poké Mart, PC de Pokémon e Diálogos Multichoice)
- **Cenário Atual (v10):**
  - **Poké Mart (`media_1791818973379.png`):** Ao interagir com o atendente, o menu de opções (`COMPRAR`, `VENDER`, `SAIR`) é cortado na horizontal e vertical: o topo fica em `x = 0` e o comando `SAIR` salta 80 pixels para a direita.
  - **Menu Principal do PC (`media_1791824000000.png`):** Ao acessar o PC, `PC DE ALGUÉM`, `PC de Phael`, `DESLIGAR` sofre deformação idêntica (opção `DESLIGAR` partida e jogada 80px para a direita).
  - **Menu de Itens do PC (`media_1791825000000.png`):** Como a string `ITENS GUARDADOS` tem mais de 104px de largura, o menu ultrapassa `splitX = 104`: a metade direita é jogada 80px para a frente, deixando um **buraco negro retangular no meio do menu** e fatiando o box em 4 pedaços!
  - **Submenus de Armazenamento e Caixas:**
    - `RETIRAR ITEM`, `GUARDAR ITEM`, `DESCARTAR`, `VOLTAR` (fatiado verticalmente no `DESCARTAR`).
    - `RETIRAR`, `DEPOSITAR`, `MOVER POKÉMON`, `MOVER ITENS`, `ATÉ MAIS!` (fatiado e duplicado na tela).
- **Mapeamento Preventivo Completo das Telas Afetadas:**
  Como observado pelo usuário, **todos os menus e escolhas que abrem no canto superior esquerdo do campo usam o mesmo sistema de janelas do GBA (`tilemapLeft = 2, tilemapTop = 1` no `BG0`)**:
  1. 💻 **Menu do PC e Submenus:** Itens guardados, cartas, caixas de Pokémon (Bill/Lanette), mover itens e desligar.
  2. 🏪 **Menu do Poké Mart:** Comprar, Vender, Sair.
  3. 🏢 **Menu de Elevadores (ex.: Loja de Departamentos de Lilycove):** Seleção de andares (1º, 2º, 3º, 4º, 5º, Cobertura, Sair).
  4. 🚠 **Menu do Teleférico (Mt. Chimney):** Escolha de subida/descida.
  5. ⛵ **Menu de Balsa / Barco do Mr. Briney:** Destinos de viagem (Dewford, Slateport).
  6. 🎰 **Menu do Cassino / Game Corner:** Troca de fichas e prêmios.
  7. ❓ **Menus de Perguntas e Quizzes:** Casa dos Desafios (Trick House), entrevistas da TV e NPCs de charadas.
  8. ⚔️ **Battle Frontier (Recepção das 7 Facilidades):** Seleção de categorias (Single, Double, Multi, Aluguel, etc.).
- **Diagnóstico da Causa Raiz (RCA Cirúrgico):**
  - Em `3ds_port/src/3ds_video.c` (linhas 1234 a 1238 e linhas 2885 a 2925), existe uma divisão estática baseada em coordenadas:
    - Qualquer tile com `px < 104 && py < 48` recebe deslocamento `shift = 0.0f` (esquerda).
    - Qualquer tile com `px >= 104 || py >= 48` recebe deslocamento `shift = sLayerShift = 80.0f` (centralizado widescreen).
  - Essa divisão foi feita com a intenção de manter a **plaquinha de nome de rota/cidade** no canto esquerdo, mas como todos os menus do campo também usam a camada `BG0`:
    - Qualquer menu com altura > 48px é cortado horizontalmente (linha do `py = 48`).
    - Qualquer menu com largura > 104px (como `ITENS GUARDADOS`) é cortado verticalmente (linha do `px = 104`), gerando buracos negros gráficos!
- **Plano de Solução Arquitetônica Definitiva:**
  - Desativar a regra de corte de `px < 104 && py < 48` quando qualquer menu ou diálogo do jogo estiver ativo (`sFieldUi` centraliza o `BG0` de forma unificada).
  - Ou aplicar o shift horizontal somente se a tarefa ativa for estritamente a plaquinha de rota (`FuncIsActiveTask(Task_MapNamePopUpWindow)`), garantindo que todos os menus, diálogos, PC, Mart e caixas multichoice do jogo permaneçam 100% íntegros, sólidos e alinhados com suas respectivas caixas de texto.

---

### 🛒 Item D: Menu de Compras da Loja (Poké Mart Buy Menu) - Escala Touch e Sprite MONEY
- **Cenário Atual (v10):**
  - **Textos Validados:** Todos os nomes de itens (*POÇÃO*, *ANTÍDOTO*, *CURA PARALIS.*, *DESPERTAR*, *VOLTAR*) e descrições (*"Recupera 20 PS de um POKéMON."*) estão **100% traduzidos para PT-BR**.
  - **Ponto Pendente 1 (Área de Tela):** A tela de compras inteira é renderizada na tela inferior centralizada em um bloco reduzido de **240x160** pixels dentro do espaço de **320x240** (com 40px de borda ociosa em volta).
  - **Ponto Pendente 2 (Sprite em Inglês):** A etiqueta amarela de saldo no topo esquerdo exibe o texto gráfico em inglês **`MONEY`** (sprite de 32x16 pixels em `graphics/shop/money.png`).
- **Diagnóstico da Causa Raiz:**
  - Em `3ds_port/src/3ds_video.c`, telas centradas completas como `CTR_CENTRED_SHOP`, `CTR_CENTRED_BAG_WHOLE` e `CTR_CENTRED_PARTY_WHOLE` são compostas como recortes 1:1 da resolução nativa do GBA (240x160).
  - O texto `MONEY` é desenhado através de um sprite indexado 4bpp de 32x16 pixels (`sSpriteSheet_MoneyLabel` em `src/money.c`), não sendo uma string de texto dinâmica da tabela de fontes.
- **Plano de Solução Arquitetônica:**
  1. Tratar o redimensionamento/escala da tela de compras (`CTR_CENTRED_SHOP`) junto com a mochila de batalha (`CTR_CENTRED_BAG_WHOLE`) para preencher a área útil de 320x240 de forma ergonômica.
  2. Ajustar os offsets de toque táctil da lista (`CtrShop_ListTouch` e `CtrShop_QuantityTouch` em `src/shop.c`).
  3. Localizar o sprite `graphics/shop/money.png` (32x16) para exibir **`DINHEIRO`** ou **`SALDO`** (ou transformá-lo dinamicamente em `3ds_icons_ptbr.c`).

---

### 🐾 Item E: Área Reduzida no Menu da Equipe de Pokémon (Party Menu no Touch Screen)
- **Cenário Atual (v10):**
  - Ao abrir a aba "POKÉMON" na tela inferior touch (`media_1791822000000.png`), a interface da equipe fica alinhada à esquerda da coluna de botões, ocupando estritamente **160 pixels de altura** (proporção GBA) no centro da tela de **240 pixels de altura**.
  - Isso gera 40 pixels de faixa verde vazia no topo e 40 pixels no rodapé, fazendo com que as caixas dos slots dos Pokémon (Torchic e os 5 slots vazios) fiquem estreitas e compactas, deixando muito espaço ocioso vertical.
- **Diagnóstico da Causa Raiz:**
  - Em `3ds_bottom_ui.c` (linhas 6677 a 6680), a interface da equipe é posicionada com offset vertical fixo `oy = (H - 160) / 2 = 40px`.
  - Como a tela inferior do 3DS tem 240px de altura (50% a mais que os 160px do GBA), desenhar o layout original 1:1 desperdiça 80px de altura útil que poderiam deixar os slots maiores, mais espaçados e muito mais fáceis de tocar com os dedos ou com a Stylus.
- **Plano de Solução Arquitetônica:**
  - Incluir o Party Menu (`MODE_PARTY_MENU`) no plano de modernização ergonômica das sub-telas do GBA na tela inferior (junto da Bolsa e do Menu da Loja).
  - Ajustar o estiramento/escala vertical ou layout expandido dos slots e remapear o handler de toque `CtrMenu_PostTap` para responder com total precisão nas novas posições ampliadas.

---

### 💳 Item F: Gráficos em Inglês no Cartão de Treinador (Trainer Card)
- **Cenário Atual (v10):**
  - Ao abrir a aba do Trainer Card na tela inferior touch (`media_1791823000000.png`):
    - O cabeçalho azul do cartão exibe o texto em inglês **`TRAINER CARD`**.
    - A faixa inferior sobre as caixas das 8 insígnias exibe o texto em inglês **`BADGES`**.
    - Os demais dados dinâmicos (*Nº ID*, *NOME:*, *DINHEIRO*, *TEMPO*) já aparecem 100% corretos em português.
- **Diagnóstico da Causa Raiz:**
  - Em `3ds_bottom_ui.c` (linhas 638 a 641), o motor do 3DS carrega a moldura do cartão a partir do arquivo gráfico compactado `trainer_card/tiles.4bpp.lz` (gerado a partir de `graphics/trainer_card/tiles.png`, 128x80 pixels).
  - Como os textos `TRAINER CARD` e `BADGES` são estampados diretamente nos blocos (tiles) da imagem de fundo do cartão original em inglês, eles não passam pela tabela de strings traduzidas de `strings.c`.
- **Plano de Solução Arquitetônica:**
  - Implementar a substituição desses tiles para **`CARTÃO TREINADOR`** (ou `TREINADOR`) e **`INSÍGNIAS`**:
    1. Através de rotina gráfica dedicada em `3ds_port/src/3ds_icons_ptbr.c` (`Port_TransformAsset` para `trainer_card/tiles.4bpp`).
    2. Ou fornecendo a versão traduzida de `graphics/trainer_card/tiles.png` no pacote de assets localizados em `tools/locales/pt_br/`.

### 📦 Item G: Área Reduzida nas Caixas do PC (Pokémon Storage System) e Tradução de Botões Gráficos
- **Cenário Atual (v10):**
  - Ao abrir a opção de mover Pokémon ou itens nas Caixas do PC:
    - A tela inteira da caixa (papel de parede, slots dos 30 Pokémon e botões superiores) fica confinada em um bloco de **240x160** pixels centralizado na tela inferior de **320x240** (com 40px de borda ociosa em volta).
    - Os botões superiores exibem textos gráficos originais em inglês:
      - **`CLOSE BOX`** (botão azul de 72x16px): apontamento prioritário do usuário para tradução.
      - **`PARTY POKéMON`** (botão verde de 72x16px): usuário sinalizou que pode ser traduzido como `EQUIPE POKéMON` (ou até mantido `PARTY POKÉMON` se preferível).
      - **`PKMN DATA`** (aba cinza da esquerda de 48x16px): pode ser adaptado para `DADOS PKMN` ou `DADOS POKÉMON`.
      - *(A etiqueta da caixa já aparece traduzida como CAIXA 1)*.
- **Diagnóstico Técnico da Causa Raiz:**
  - Em `3ds_port/src/3ds_video.c`, a tela de caixas é tratada como `CTR_CENTRED_STORAGE`, pertencendo ao mesmo grupo de telas GBA renderizadas em proporção 1:1 estrita centralizada (240x160).
  - Os botões superiores (`PARTY POKéMON`, `CLOSE BOX`, `PKMN DATA`) e seus estados alternantes (normal e selecionado/piscando) são compostos a partir do arquivo gráfico indexado `graphics/pokemon_storage/menu.png` (128x72 pixels) e do mapa de blocos `close_box_button.bin` (9x4 tiles).
- **Plano de Solução Arquitetônica:**
  1. **Tradução dos Tiles Gráficos:**
     - `CLOSE BOX` -> **`FECHAR CAIXA`** (ou **`FECHAR`**), desenhado nos estados normal (azul) e piscando (destacado).
     - `PARTY POKéMON` -> **`EQUIPE POKéMON`** (ou `EQUIPE`, mantendo harmonia com o restante do jogo em PT-BR).
     - `PKMN DATA` -> **`DADOS PKMN`**.
  2. **Ergonomia e Escala Touch:**
     - Integrar `CTR_CENTRED_STORAGE` ao plano de ampliação/escala ergonômica das sub-telas do GBA na tela inferior touch de 320x240 (proporcionando ícones maiores e muito mais precisão para selecionar e arrastar Pokémon com os dedos/Stylus).
     - Ajustar os offsets do handler de toque em `3ds_bottom_ui.c` (`CtrStorage_Tap`).

### 📋 Item H: Corte Superior na Gaveta da Equipe nas Caixas do PC e Botão CANCEL
- **Cenário Atual (v10):**
  - Ao abrir a gaveta deslizante da equipe dentro do Sistema de Armazenamento de Pokémon:
    - A borda superior do painel vertical verde da equipe aparece com um corte horizontal reto e seco (clipping no topo), parecendo "cortada" contra o papel de parede laranja do PC.
    - O botão inferior da gaveta exibe o texto em inglês **`CANCEL`** (em vez de `VOLTAR` ou `CANCELAR`).
- **Diagnóstico Microscópico da Causa Raiz:**
  - **Tilemap e Geometria da Gaveta:** Em `pokemon_storage_system.c` (linha 4118), o tilemap da gaveta (`gStorageSystemPartyMenu_Tilemap` descompactado de `party_menu.bin.lz`) possui **12 colunas x 22 linhas** de blocos (`96 x 176` pixels).
  - **Diferença de Comportamento GBA vs 3DS Dual-Screen:**
    - No hardware original do GBA, a tela física possui exatamente **160 pixels de altura**. A gaveta saía pelo topo da tela (`Y = 0`), e a carcaça física de plástico do console ficava logo ali, dando a ilusão de que a gaveta continuava para fora do videogame. Além disso, as linhas 0 a 18 do tilemap original sequer possuem uma borda horizontal fechada (são listras verticais contínuas de 8px).
    - No Nintendo 3DS, a tela inferior possui **320x240 pixels** de resolução. O motor (`3ds_video.c`) renderiza o PC como `CTR_CENTRED_STORAGE` em uma janela centralizada de **240x160**, preenchendo as sobras (40px em cima, 40px embaixo) com a repetição da camada de fundo quadriculada laranja (`.wrap = true` no BG3).
    - Como o BG1 (que contém a gaveta e a janela *PKMN DATA*) é ceifado exatamente nos limites de `Y = 0` do GBA (que corresponde a `Y = 40` do 3DS), a gaveta verde é cortada abruptamente contra o fundo laranja do PC.
  - **Botão CANCEL:** Carregado a partir do mapa de blocos gráficos indexados `graphics/pokemon_storage/menu.png`.
- **Plano de Solução Arquitetônica:**
  - A modernização ergonômica da tela de caixas para ocupar os 240px de altura da tela do 3DS eliminará naturalmente o confinamento em 160px.
  - Desenhar/estender uma borda ou moldura de acabamento no topo da gaveta ou estender sua renderização vertical até o teto da tela touch (`Y = 0` do 3DS), garantindo um acabamento estético natural e polido.
  - Localizar o botão `CANCEL` em `graphics/pokemon_storage/menu.png` para **`VOLTAR`** ou **`CANCELAR`**.

### ⚔️ Item I: Transição de Batalha contra Treinadores (NPCs de Rota, May, Líderes, Vilões e Elite 4)
- **Cenário Atual (v10):**
  - Ao entrar em batalha contra **qualquer treinador NPC do jogo** (treinadores comuns de rotas, Rival May/Brendan, Líderes de Ginásio, Vilões Aqua/Magma e Elite dos Quatro):
    - A transição gráfica de entrada quebra visualmente: exibe elementos gráficos cortados ao meio, acompanhados de fatias ou blocos pretos desconexos ("tabuleiro quebrado"), revelando quadrados e faixas do cenário do mapa por trás de forma desalinhada antes do início da luta.
    - Capturas de tela recebidas mostram blocos do Overworld vazando isolados no topo e no centro da tela enquanto as Pokébolas realizam o rastro.
    - O problema **NÃO** ocorre em batalhas contra Pokémon selvagens.
- **Diagnóstico Técnico da Causa Raiz:**
  - **Mapeamento das Transições no Código:**
    - Em `battle_setup.c` (`sBattleTransitionTable_Trainer`), todas as batalhas de treinadores comuns e rivais utilizam transições geométricas de blocos e janelas: `B_TRANSITION_POKEBALLS_TRAIL` e `B_TRANSITION_ANGLED_WIPES`.
    - Vilões Aqua/Magma utilizam `B_TRANSITION_AQUA` e `B_TRANSITION_MAGMA`.
    - Elite dos Quatro e Campeão utilizam as transições de *mugshots* divididas ao meio (`B_TRANSITION_SIDNEY`, `B_TRANSITION_PHOEBE`, `B_TRANSITION_GLACIA`, `B_TRANSITION_DRAKE`, `B_TRANSITION_CHAMPION`).
  - **Origem da Quebra Widescreen no 3DS:**
    - Todas as transições de treinadores do GBA foram programadas para uma tela rígida de **240x160** pixels, utilizando scanlines de `BG0` e janelas de hardware (`WIN0`/`WIN1`).
    - No 3DS widescreen, o Overworld (`TransitionField` em `3ds_video.c`) é desenhado em **400x240** pixels, enquanto a camada da transição (`TransitionPicture`) é renderizada centralizada a 1.5x ocupando apenas **360x240** pixels (de `X = 20` até `X = 380`).
    - Além disso, o preenchimento automático das margens laterais com retângulos pretos fixos de 20px (`3ds_video.c:7359`) desenha pilares pretos antes do fechamento da cortina.
    - Como o motor tenta casar uma transição em 360px sobre um cenário widescreen em 400px, qualquer transição de treinador fatiada por scanline ou blocos sofre descompasso geométrico e corte lateral.
- **Plano de Solução Arquitetônica:**
  1. **Varredura e Enquadramento Widescreen:** Sincronizar as transições de treinadores para cobrir a extensão total de 400 pixels do 3DS, adaptando o rastro das Pokébolas, os cortes angulares e os logos/mugshots para o viewport widescreen completo.
  2. **Eliminação dos Pilares Pretos Prematuros:** Sincronizar as margens laterais de 20px para acompanhar a transição de forma contínua em vez de forçar corte preto sólido nas laterais.
  3. **Camada de Transição Limpa (Seamless):** Garantir que o fechamento da cortina seja 100% sólido e contínuo em todas as classes de treinadores antes do handoff para a cena de batalha.

### 📖 Item J: Tela de Registro da Pokédex na Captura (Corte da Descrição em 112px)
- **Cenário Atual (v10):**
  - Ao capturar qualquer Pokémon selvagem (ex.: Wurmple), a tela de registro da Pokédex exibe a descrição incompleta cortada no meio:
    - Aparece apenas a primeira linha: *"Gruda nos galhos e come folhas. O fio que"*
    - O restante do texto desaparece e o rodapé da moldura da Pokédex é cortado por uma barra preta horizontal sólida no meio da tela.
- **Diagnóstico Microscópico da Causa Raiz:**
  - **Texto da Pokédex:** Em `src/data/pokemon/pokedex_text.h` (linha 531), o texto completo do Wurmple possui 4 linhas:
    `"Gruda nos galhos e come folhas. O fio que\ncospe pela boca, que fica pegajoso ao\ntocar o ar, deixa os inimigos mais\nlentos."`
  - **Disparo via Batalha:** Ao capturar um monstro, o script da batalha chama `DisplayCaughtMonDexPage` (`src/pokedex.c:4041`), que renderiza a tela em tela cheia do GBA (240x160), iniciando o texto em `top = 95` com altura de linha de 16px.
  - **O Conflito de Batalha no 3DS (`bottom = 112`):**
    - Como a captura ocorre dentro do fluxo de batalha, a flag de batalha `sBattle` do motor do 3DS permanece ativa.
    - Em `3ds_port/src/3ds_video.c` (linhas 5047 e 5666), o motor assume que toda tela em `sBattle` possui altura útil restrita a **`bottom = 112`** (que equivale a 160px do GBA menos 48px da caixa de diálogo da arena de batalha).
    - Como o corte é cravado na linha `Y = 112`:
      - A linha 1 (Y=95 a 111) é renderizada.
      - A linha 2 (Y=111 a 127), as linhas 3 e 4, e toda a moldura inferior da Pokédex (Y=152 a 160) são **ceifadas pelo corte de 112px** contra o fundo preto da tela superior!
- **Plano de Solução Arquitetônica:**
  1. **Detecção da Tela de Captura:** Identificar quando `Task_DisplayCaughtMonDexPage` ou `sNewEntryInfoScreen_WindowTemplates` estiver ativa (ou quando o modo for captura de Pokédex).
  2. **Liberação da Altura Integral:** Suspender o corte de 112px da arena de batalha durante o registro da Pokédex, permitindo que a imagem seja composta em seus 160px completos de altura.
  3. **Visualização Completa do Texto:** As 4 linhas completas da descrição e a borda inferior arredondada da Pokédex serão desenhadas com perfeição e sem nenhum corte.

### 🏷️ Item K: Tela de Nomeação / Apelido (Escala Widescreen, Texto Colado e Botões em Inglês)
- **Cenário Atual (v10):**
  - Ao capturar um monstro e abrir a tela para dar apelido (*Naming Screen*):
    - **Área Reduzida:** A tela inteira fica confinada em um bloco de **240x160** pixels no centro da tela superior widescreen de **400x240** (com listras amarelas ociosas preenchendo as laterais), deixando as teclas do teclado e o sprite do monstro muito pequenos.
    - **Texto Colado e Invertido:** O cabeçalho da caixa estampa o texto sem espaço e com sintaxe invertida: **`WURMPLEApelido de ?`** (em vez de `Apelido de WURMPLE?`).
    - **Botões Gráficos em Inglês:** Os botões de controle à direita do teclado exibem etiquetas americanas: **`lower`** (tecla Select), **`BACK`** (botão B) e **`OK`** (tecla Start).
- **Diagnóstico Técnico da Causa Raiz:**
  - **Escala 1:1:** Em `3ds_video.c:2049`, a tela é tratada como `CTR_CENTRED_NAMING`, sendo renderizada na proporção nativa do GBA (240x160) com repetição de BG3 nas bordas.
  - **Concatenação Saxon Genitive (Inglês):** Em `src/naming_screen.c` (linha 1722), a função `DrawMonTextEntryBox` foi desenhada para a gramática inglesa (`WURMPLE` + `'s nickname?` = `WURMPLE's nickname?`):
    ```c
    StringCopy(buffer, gSpeciesNames[sNamingScreen->monSpecies]);
    StringAppendN(buffer, sNamingScreen->template->title, 15);
    ```
    Ao traduzir a string para português (`Apelido de ?`), a rotina concatena diretamente a espécie antes da frase sem espaço, resultando em `WURMPLEApelido de ?`.
  - **Sprites dos Botões:** Os botões `lower`, `BACK` e `OK` são blocos gráficos indexados carregados de `graphics/naming_screen/`.
- **Plano de Solução Arquitetônica:**
  1. **Aplicação de Escala / Zoom Widescreen:** Integrar a tela de nomeação ao grupo de telas ampliadas (1.5x / widescreen proporcional), expandindo o teclado e a área de digitação de forma confortável e preenchendo o display do 3DS.
  2. **Correção Sintática da Concatenação:** Ajustar `DrawMonTextEntryBox` para formatar a string na ordem gramatical natural do Português: `"Apelido de %s?"` (ex.: `"Apelido de WURMPLE?"`).
  3. **Localização dos Botões:** Traduzir os sprites para **`minúsc.`** (ou `abc`), **`VOLTAR`** (ou `APAGAR`) e **`OK`**.

### 💬 Item L: Tela de Perfil / Mensagens (Easy Chat) Deslocada no Canto Superior Esquerdo
- **Cenário Atual (v10):**
  - Ao abrir o Perfil do Treinador para editar frases ou mensagens personalizadas (*Easy Chat*, ex.: *"EU SOU UM POKéMON AMIGO"*, *"APAGAR"*, *"VOLTAR"*):
    - A tela inteira do GBA é projetada colada no canto superior esquerdo (`X = 0, Y = 0`) da tela superior panorâmica do 3DS (ocupando apenas 240x160 pixels).
    - O restante da tela superior (uma faixa de 160 pixels à direita e 80 pixels abaixo) fica em vácuo preto completo, sem repetição da grade xadrez de fundo.
    - Ao abrir a caixa de confirmação de saída (*"Parar de editar?"* e menu *"SIM / NÃO"*), os balões de diálogo e caixas de texto aparecem com artefatos visuais ou desalinhados em relação ao layout.
- **Diagnóstico Microscópico da Causa Raiz:**
  - **Ausência de Callback Centrado no Porte:** Em `3ds_port/src/3ds_game_full.c` e `3ds_video.c`, o motor do 3DS depende da tabela `sCentred` e do enum `CTR_CENTRED_*` para identificar telas estáticas do GBA que devem ser centralizadas com moldura ou fundo repetido.
  - **Chamada Direta no Código do GBA:** Em `src/easy_chat.c` (linha 1352), a rotina de transição chama diretamente o manipulador nativo do GBA:
    ```c
    SetVBlankCallback(VBlankCB_EasyChatScreen);
    ```
    Diferente de outras telas (como `CtrCentredNaming_SetVBlankCallback` ou `CtrCentredSummary_SetVBlankCallback`), o Easy Chat **não** foi interceptado pelo porte original do 3DS.
  - **Comportamento Padrão no Motor de Vídeo:** Como `sCentredRequested` permanece como `CTR_CENTRED_NONE`, o motor do 3DS interpreta o Easy Chat como se fosse o Overworld comum (que utiliza a resolução nativa expandida de 400x240 a partir da coordenada 0,0). Como o tilemap do Easy Chat só possui 240x160 pixels, ele fica confinado ao quadrante superior esquerdo, deixando todo o resto da tela em preto absoluto.
- **Plano de Solução Arquitetônica:**
  1. **Registro do Hook de VBlank Centrado:** Adicionar `CtrCentredEasyChat_SetVBlankCallback(VBlankCB_EasyChatScreen)` (ou vincular ao `CTR_CENTRED_PLAIN` / `CTR_CENTRED_EASY_CHAT`).
  2. **Centralização e Expansão de Bordas:**
     - Centralizar o viewport em `X = 80, Y = 40` da tela superior do 3DS (ou aplicar escala proporcional widescreen).
     - Configurar `.wrap = true` no preenchimento de fundo em `sCentredFills`, estendendo o padrão gráfico quadriculado bege/laranja até as extremidades de 400x240 pixels para cobrir 100% da tela superior sem barras pretas.
  3. **Sincronização de Janelas de Diálogo:** Garantir que o `BG0` (caixa *"Parar de editar?"* e menu *"SIM/NÃO"*) acompanhe o deslocamento de centralização da tela principal.

### 🎒 Item M: Captura do Wally (Batalha Tutorial com Ralts e Zigzagoon)
- **Cenário Atual (v10):**
  - Durante o evento de captura do Wally (tutorial na Rota 102 com o Zigzagoon emprestado):
    1. **Barras Pretas na Caixa de Diálogo:** A caixa de texto no rodapé da tela superior não se estende em widescreen; ela fica confinada em um bloco estreito de 240 pixels no centro, cercada por duas barras pretas sólidas de 80 pixels em cada lateral.
    2. **Colisão da Healthbox com a Base de Grama:** A caixa de HP do Zigzagoon (`ZIGZAGOON Lv7`) fica sobreposta/atrás da plataforma circular de grama do Ralts selvagem, gerando confusão visual e sobreposição de elementos.
    3. **Corte no Sprite do Zigzagoon:** O Pokémon do jogador/Wally tem sua base cortada de forma abrupta rente à caixa de diálogo.
    4. **Cena de Lançamento da Pokébola:** Quando Wally arremessa a bola (*"WALLY usou POKé BOLA!"*), a caixa de diálogo flutuando no meio mantém as barras pretas laterais, aparentando uma tela quebrada.
- **Diagnóstico Microscópico da Causa Raiz:**
  - **Recorte Rígido Emergencial em `3ds_video.c:1800`:**
    - Na v8, para contornar o fato de que a tela touch do 3DS fica desativada no tutorial e os menus do GBA (Fight, Bag, Run) precisavam aparecer na tela superior, foi inserida a seguinte rotina:
      ```c
      if (gBattleTypeFlags & BATTLE_TYPE_WALLY_TUTORIAL_BIT)
      {
          DrawBattleCut(bg, 0, 240, 0, 160, (CTR_GAME_WIDTH - 240) / 2);
          return;
      }
      ```
    - Essa instrução corta os 240 pixels nativos do GBA e os estampa com deslocamento de 80px no centro da tela de 400px. Porém, ela **não estende** o fundo nem a moldura da caixa até as extremidades do display, gerando as duas barras pretas laterais de 80px.
  - **Coordenadas Widescreen em Batalha Específica:**
    - As novas coordenadas de healthbox da v10 (`x = 160, y = 88` para o jogador) foram calibradas para o cenário de batalha individual padrão.
    - No Wally Tutorial, o Ralts e sua base verde estão posicionados mais próximos do centro da tela (`X ≈ 180~200` no GBA, escalando para `X ≈ 280` no 3DS). Como `x = 160` escala para `X ≈ 256`, a caixa do Zigzagoon colide diretamente com a borda circular da plataforma do Ralts.
- **Plano de Solução Arquitetônica:**
  1. **Caixa de Diálogo Widescreen Contínua no Tutorial:**
     - Substituir o recorte seco de 240px: desenhar a caixa de diálogo da batalha cobrindo os 400 pixels de largura (left cap na margem esquerda `X = 0`, right cap na margem direita `X = 368` e preenchimento contínuo de miolo), eliminando integralmente as barras pretas laterais.
     - Quando o menu de comandos do Wally estiver ativo no `BG0`, desenhá-lo sobreposto à caixa widescreen contínua sem quebrar as margens do display.
  2. **Calibração de Healthbox Exclusiva para `BATTLE_TYPE_WALLY_TUTORIAL`:**
     - Em `InitBattlerHealthboxCoords` (`battle_interface.c`), criar exceção quando `gBattleTypeFlags & BATTLE_TYPE_WALLY_TUTORIAL` estiver ativo, ajustando a healthbox do Zigzagoon para coordenadas livres de interferência com a base do Ralts.
  3. **Ajuste de Composição Visual:**
     - Garantir que os sprites de Zigzagoon, Ralts e Wally se apoiem com naturalidade sobre a nova caixa widescreen sem linhas de clipping indesejadas.

---

## 📌 Status Atual de Desenvolvimento (Milestone v11)
- [x] **Feedbacks e imagens anotados e catalogados.**
- [x] **Diagnósticos e Soluções Concluídos e Compilados na Milestone v11:**
  - [x] **Item A:** Posição da Healthbox do oponente ajustada para o alto e à esquerda (`x = 16, y = 12`).
  - [x] **Item C:** Menus do canto superior esquerdo (Mart, PC, Multichoice, itens guardados e caixas) íntegros e sem corte.
  - [x] **Item D (Sprite):** Etiqueta `MONEY` localizada para `SALDO`.
  - [x] **Item F:** Cabeçalho do Cartão de Treinador (`CARTÃO TREINADOR`) e faixa de insígnias (`INSÍGNIAS`) traduzidos em gráficos nativos.
  - [x] **Item G & H (Botões):** Botão `CLOSE BOX` localizado para `FECHAR`, e botão `CANCEL` da gaveta localizado para `VOLTAR`.
  - [x] **Item I:** Transições de treinadores em widescreen 400px contínuos sem fatiamento ou pilares pretos prematuros.
  - [x] **Item J:** Pokédex pós-captura exibindo altura integral de 160px (leitura completa das 4 linhas da descrição).
  - [x] **Item K:** Naming Screen com ordenação gramatical em português (`"Apelido de %s?"`) e botões gráficos traduzidos (`VOLTAR`, `MINUS.`, `MAIUS.`, `OUTROS`).
  - [x] **Item L:** Easy Chat / Perfil centralizado com papel de parede estendido em 400x240 (sem cortes no topo esquerdo).
  - [x] **Item M:** Wally Tutorial com caixa de diálogo contínua em 400px widescreen e healthbox do Zigzagoon desobstruída.
- [ ] **Backlog para Ciclos Futuros (v12+ - Ergonomia e Escala Touch Screen):**
  - [ ] **Item B:** Escala ampliada da Bolsa em batalha para preenchimento ergonômico da tela touch (320x240).
  - [ ] **Item D (Layout):** Ampliação da área de compra da loja na tela touch (320x240).
  - [ ] **Item E:** Ampliação vertical dos slots da equipe Pokémon na tela touch (320x240).
  - [ ] **Item G & H (Layout):** Ampliação das caixas de Pokémon do PC para 320x240 na tela touch.



