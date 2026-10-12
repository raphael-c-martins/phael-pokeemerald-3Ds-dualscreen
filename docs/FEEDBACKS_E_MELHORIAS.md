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

### 🏪 Item C: Quebra no Menu da Vendinha (Poké Mart)
- **Cenário Atual (v10):**
  - Ao interagir com o atendente do Poké Mart em qualquer cidade (`media_1791818973379.png`), a janela de opções (`COMPRAR`, `VENDER`, `SAIR`) aparece graficamente partida ao meio:
    - O topo da janela (`COMPRAR`, `VENDER` e a metade de cima da palavra `SAIR`) fica encostado na esquerda.
    - A metade inferior da palavra `SAIR` (e a borda direita da janela) aparece deslocada 80 pixels para a direita, como um bloco flutuante duplicado/cortado.
- **Diagnóstico da Causa Raiz (RCA Cirúrgico):**
  - Em `3ds_port/src/3ds_video.c` (função `DrawFieldBgTex`, linhas 2885 a 2925), o compositor gráfico divide a camada `BG0` do overworld widescreen usando limites fixos:
    - `splitX = 104` e `splitY = 48`.
    - O objetivo original era deixar a plaquinha de cidade/rota (que fica no canto superior esquerdo até `x < 104, y < 48`) sem o shift horizontal de centralização (`sLayerShift = 80px`).
    - No entanto, a janela do Poké Mart é criada em `src/shop.c` com `tilemapLeft = 2, tilemapTop = 1` e altura de 6 tiles (48px de altura, atingindo `y = 56px`):
      - As linhas com `y < 48` são desenhadas sem o shift (`+ 0px`).
      - As linhas com `y >= 48` (onde fica a palavra `SAIR`) caem na regra 3 (`y1 > splitY`), que aplica `+ sLayerShift` (+80px).
    - Essa divisão arbitrária corta a janela ao meio e joga a parte inferior 80 pixels para o lado!
- **Plano de Solução Arquitetônica:**
  - Em vez de uma divisão geométrica ingênua por coordenadas fixas (`splitX = 104, splitY = 48`), o compositor de UI do campo deve identificar se há janelas de menu/diálogo ativas (`gTasks`, `sMartInfo` ou tipo de janela) ou aplicar o deslocamento consistente (`sLayerShift`) a toda a janela de diálogo/menu do Poké Mart para que ela seja renderizada inteira e unificada, ou elevar `splitY` adequadamente quando em ambientes fechados (interiores de prédios/lojas onde a plaquinha de rota nunca existe).

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

## 📌 Status Atual de Desenvolvimento
- [x] Feedbacks e imagens anotados e catalogados.
- [x] Diagnóstico técnico preliminar concluído (Healthboxes, Mochila em Batalha, Menu do Poké Mart, Loja Touch e Equipe de Pokémon).
- [ ] **Aguardando término da bateria de testes do usuário** para consolidar todos os novos requisitos antes de abrir uma nova branch de compilação.
