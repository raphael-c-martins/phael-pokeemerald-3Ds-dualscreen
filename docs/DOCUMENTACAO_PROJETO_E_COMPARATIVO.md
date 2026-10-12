# 🏛️ Documentação Completa do Projeto e Análise Comparativa
**Projeto:** Pokémon Emerald 3DS (Dual-Screen PT-BR)  
**Repositório Ativo:** `raphael-c-martins/phael-pokeemerald-3Ds-dualscreen`  
**Branch Atual:** `tentativa11`  
**Data de Consolidação:** 12/10/2026  

---

## 📌 1. Visão Geral e Arquitetura do Projeto

O projeto **Pokémon Emerald 3DS Dual-Screen PT-BR** é uma engenharia de alto nível que adapta a descompilação oficial de *Pokémon Emerald* (`pokeemerald`) para o ecossistema do **Nintendo 3DS** (famílias Old 3DS, 2DS, New 3DS e New 2DS), integrando:
1. **Renderização Widescreen Panorâmica:** O jogo roda na tela superior aproveitando a resolução estendida de **400x240 pixels** (contra os 240x160 originais do GBA).
2. **Interface Táctil Dedicada (Dual-Screen Touch):** A tela inferior (**320x240 pixels**) atua como central de comando, substituindo o menu clássico START com acesso imediato a Mochila, Pokémon, Mapa, Trainer Card, Opções e Salvamento sem pausar a experiência.
3. **Localização Integral Oficial (PT-BR):** Aplicação das diretrizes oficiais brasileiras da franquia (nomenclaturas Bulbapedia pt_br para golpes, habilidades, itens, naturezas e categorias), com mais de 14.000 strings e gráficos retrabalhados com suporte nativo a acentuação (ã, õ, é, etc.).
4. **Compatibilidade Absoluta de Dados:** Saves de 128 KB (`emerald3ds.sav`) com paridade binária com o GBA, permitindo importação e exportação contínua de cartuchos reais e emuladores.

---

## ⏳ 2. Linha do Tempo e Evolução Histórica (Milestones v1 a v11)

| Milestone | Período | Foco Principal | Resultado & Impacto |
| :--- | :--- | :--- | :--- |
| **v1** | 08/10/2026 | Primeiro boot e setup da toolchain (devkitARM, libctru, citro2d/3d). | Executável gerado (33,68 MB). Console executou a 59.8 FPS, mas sofreu crash (`prefetch abort` ARM11) ao entrar no jogo ativo devido a corrupção em strings de menus. |
| **v2** | 08/10/2026 | Blindagem do ARM11, isolamento de strings de sistema e sanitização de menus. | **Sucesso Histórico no Old 3DS:** Primeiro boot estável, menus de Continue e Start 100% legíveis e acentuados, e zero crashes no processador. |
| **v3** | 09/10/2026 | Localização de diálogos de Save, interface touch (Opções/Melhorias/Trapaças) e eventos iniciais. | Sub-telas de salvamento e botões tácteis da tela inferior traduzidos com a macro `CTR_TEXT`. |
| **v4 - v5** | 10/10/2026 | Expansão de diálogos de mapas (Littleroot, Oldale, Rota 101/102/103) e fontes latinas estendidas. | Incorporação de caracteres com til (Ã, Õ, ã, õ) nas fontes do GBA e diálogos de vilas e casas homologados. |
| **v6 - v7** | 10/10/2026 | Refinamento do pipeline de assets comprimidos (`.4bpp.lz`) e estabilização de build no Windows. | Automação da compilação de gráficos com validação de 6.423 assets sem perda de integridade. |
| **v8** | 11/10/2026 | Integração do fork do parceiro (Carlos Mozart) e adaptação de layout widescreen preliminar. | Absorção de mais de 14 mil textos traduzidos da base da comunidade; identificação dos cortes laterais em batalhas e tutoriais. |
| **v9** | 11/10/2026 | Calibração de combate, telemetria contínua em `port.log`, velocidade configurável (boot 1x, aceleração 4x in-game). | Velocidade inteligente para preservar o áudio de abertura sem distorção e telemetria de 59.8 FPS persistida. |
| **v10** | 12/10/2026 | Blindagem do ciclo de vida de threads no Core 1 (Crash do botão HOME) e calibração de combate. | Eliminação definitiva de crashes ao suspender ou fechar a tampa do 3DS via encerramento cooperativo atômico de threads. |
| **v11** | 12/10/2026 | Sincronização Upstream/Parceiro, Widescreen Integral (Menus, Transições, Pokédex, Wally) e Botões Gráficos. | **Versão Definitiva Atual:** Correção de menus do Mart/PC (Item C), transições 400px sem fatiamento (Item I), Pokédex pós-captura 160px (Item J), gramática de apelido (Item K), Easy Chat 400x240 (Item L), Wally Tutorial 400px (Item M), Healthbox do oponente no céu (Item A) e botões gráficos traduzidos (SALDO, CARTÃO TREINADOR, INSÍGNIAS, FECHAR, VOLTAR). |

---

## 🔍 3. Análise Crítica: Erros, Diagnósticos e Acertos (Post-Mortem Técnico)

### ⚠️ Erros Encontrados e Como Foram Superados

1. **Erro: `prefetch abort` no processador ARM11 do Old 3DS ao carregar o jogo (v1)**
   - *Causa Raiz:* Na primeira tentativa de tradução direta da ROM, strings de interface curta (`TIME`, `BADGES`) foram preenchidas acidentalmente com textos longos de diálogos de minigames. A rotina `InkColumns` do motor do 3DS tentou calcular a largura dos caracteres e acessou endereços de memória inválidos.
   - *Solução Arquitetural:* Sanitização manual de todas as strings de sistema em `src/strings.c` e implementação de verificação estrita de limites (*bounds checking* `glyph < 272`) em todas as rotinas de desenho de texto em `3ds_bottom_ui.c`.

2. **Erro: Crash ao pressionar o botão HOME ou suspender o console no 3DS (v9/v10)**
   - *Causa Raiz:* Ao suspender o aplicativo para abrir o menu do sistema operacional do 3DS, a thread auxiliar no Core 1 (responsável pelo loop de lógica/renderização) era destruída de forma abrupta sem esperar a conclusão dos ciclos de I/O e GPU, gerando pânico no kernel Horizon do console.
   - *Solução Arquitetural:* Implementado cancelamento cooperativo atômico (`sGameThreadExitRequested`) com sincronização explícita via `threadJoin` em `3ds_platform.c` e `3ds_game_full.c`, garantindo encerramento limpo antes do sistema operacional tomar o controle.

3. **Erro: Menus do Poké Mart, PC de Pokémon e Multichoice cortados e fatiados ao meio (v10 - Item C)**
   - *Causa Raiz:* Em `3ds_port/src/3ds_video.c`, havia uma divisão rígida de coordenadas criada originalmente para a plaquinha de rotas: qualquer tile com `px < 104 && py < 48` recebia deslocamento `shift = 0.0f` (esquerda), enquanto o resto recebia `shift = 80.0f` (centro widescreen). Como os menus de compras e PC também abrem no canto superior esquerdo da camada `BG0`, menus com altura > 48px tinham a base jogada 80px para a frente, e menus com largura > 104px (como `ITENS GUARDADOS`) eram fatiados verticalmente gerando um buraco negro retangular no meio da janela.
   - *Solução Arquitetural:* Removido o corte forçado de `splitX = 104, splitY = 48` nas rotinas `DrawTextSpanAt` e `DrawFieldBgTex`, unificando a renderização da camada de diálogo e menus do overworld de forma contínua e sem quebras visuais.

4. **Erro: Transições de batalha contra treinadores quebradas e exibindo o mapa por trás (v10 - Item I)**
   - *Causa Raiz:* O overworld no 3DS é renderizado em 400x240 pixels, mas a camada das transições de treinadores (`TransitionPicture`) era renderizada a 1.5x ocupando apenas 360x240 pixels (de X=20 a X=380), além de desenhar pilares pretos prematuros de 20px nas margens laterais. Em transições fatiadas por scanline ou blocos (comuns em treinadores, May, Líderes e Elite dos Quatro), isso causava descompasso geométrico e vazamento de blocos do mapa.
   - *Solução Arquitetural:* Refatoração de `TransitionPicture` para projetar a cortina a 400 pixels contínuos (`scaleX = CTR_GAME_WIDTH / (240.0f * SCENE_ZOOM)`) e remoção dos pilares pretos prematuros, tornando a transição contínua e sólida.

5. **Erro: Descrição da Pokédex pós-captura cortada na primeira linha por uma barra preta (v10 - Item J)**
   - *Causa Raiz:* A captura ocorre dentro do fluxo de batalha, mantendo a flag `sBattle` ativa no motor de vídeo. Em `3ds_video.c`, qualquer tela em `sBattle` recebia um corte rígido em `bottom = 112px` (altura útil da arena sem a caixa de texto). Como a Pokédex pós-captura inicia seu texto em `Y = 95` com 4 linhas de 16px, o corte em 112px ceifava as linhas 2, 3 e 4 e toda a borda inferior arredondada da Pokédex.
   - *Solução Arquitetural:* Criação do patch `0053-caught-mon-dex-page-full-height.patch` conectado à engine via `CtrVideo_SetCaughtMonDexPage(bool)`. O corte de 112px é suspenso dinamicamente durante a exibição da Pokédex, permitindo a exibição dos 160px completos.

6. **Erro: Falha de compilação 127 com `gbagfx.exe` no Windows durante montagem de gráficos (v11)**
   - *Causa Raiz:* O binário compilado de `gbagfx.exe` no MSYS2 dependia dinamicamente de `libpng16-16.dll`. Ao ser invocado fora do terminal MinGW através de scripts em Python no Windows, o sistema não localizava a DLL no PATH global, abortando a compilação de assets com erro 127.
   - *Solução Arquitetural:* Cópia preventiva da biblioteca `libpng16-16.dll` diretamente para a pasta de ferramentas `build/upstream/tools/gbagfx/`, garantindo execução autônoma em qualquer ambiente sem necessidade de variáveis globais.

---

### 🏆 Acertos de Engenharia e Boas Práticas

1. **Preservação Absoluta de Dados:** Saves de teste e histórico de partidas do usuário foram mantidos 100% intocados durante todas as 11 milestones, comprovando maturidade operacional.
2. **Atuação na Causa Raiz:** Nenhuma solução adotou "gambiarras" ou mascaramento de erros; todas as correções foram feitas no código da engine em C e em patches formais do decompilador.
3. **Pipeline de Tradução Gráfica Automatizado:** Em vez de editar manualmente milhares de tiles, desenvolvemos scripts em Python (`localize_graphics_ptbr.py`) que aplicam mapas de pixels preservando paletas indexadas e compactam usando as próprias ferramentas oficiais (`gbagfx`).
4. **Ciclo Rápido de Feedback (Console Real + Citra):** Todas as melhorias foram validadas e contrastadas contra prints e fotos tiradas diretamente de um Nintendo 3DS real e logs persistidos de frame rate.

---

## 📊 4. Matriz Comparativa: Nosso Projeto vs. Parceiro vs. Upstream Oficial

A tabela abaixo compara o estado atual da **nossa branch (`tentativa11`)** em relação ao repositório oficial em inglês (**Upstream / ZallaxDev**) e ao fork de tradução (**Parceiro / Carlos Mozart**):

| Recurso / Funcionalidade | Upstream Oficial (`ZallaxDev`) | Repositório Parceiro (`carlosmozart`) | Nosso Projeto (`tentativa11`) | Status de Validação |
| :--- | :---: | :---: | :---: | :--- |
| **Tradução de Textos e Diálogos (PT-BR)** | ❌ (Inglês) | ✅ (Completo) | ✅ (Completo) | Homologado até Rota 104 e cenários principais. |
| **Nomenclatura Oficial Bulbapedia PT-BR** | ❌ (Inglês) | ✅ (Presente) | ✅ (Presente) | 100% de golpes, itens, naturezas e habilidades. |
| **Fontes Latinas com Til (Ã, Õ, ã, õ)** | ❌ (Ausente) | ✅ (Presente) | ✅ (Presente) | Testado e aprovado em todas as caixas de texto. |
| **Blindagem do Botão HOME (Crash Core 1)** | ❌ (Suspeito a crash) | ❌ (Sem tratamento de threads) | 🌟 **EXCLUSIVO NOSSO (Blindado)** | **Validado no hardware real:** suspensão e retorno perfeitos. |
| **Fast-Forward Inteligente (Boot 1x, 4x in-game)**| ❌ (Velocidade fixa) | ❌ (Velocidade fixa) | 🌟 **EXCLUSIVO NOSSO** | **Validado no hardware real:** áudio de boot limpo e 4x in-game. |
| **Integridade de Menus no Canto Esquerdo (Item C)** | ❌ (Corta menus > 48px / > 104px)| ❌ (Corta menus e gera buraco negro)| 🌟 **EXCLUSIVO NOSSO (Corrigido)** | Mart, PC, Caixas e Multichoice 100% sólidos. |
| **Transições Widescreen 400px (Item I)** | ❌ (Quebra em 360px com faixas pretas)| ❌ (Quebra em 360px com faixas pretas)| 🌟 **EXCLUSIVO NOSSO (Corrigido)** | Transição limpa contra NPCs, May, Líderes e E4. |
| **Pokédex Pós-Captura 160px Completa (Item J)** | ❌ (Corte em 112px na batalha) | ❌ (Constava como problema no README)| 🌟 **EXCLUSIVO NOSSO (Corrigido)** | 4 linhas de texto e moldura exibidas sem cortes. |
| **Gramática na Tela de Apelido (Item K)** | ❌ (Inglês saxão) | ❌ (`WURMPLEApelido de ?`) | 🌟 **EXCLUSIVO NOSSO (Corrigido)** | `"Apelido de %s?"` com sintaxe correta em português. |
| **Easy Chat / Perfil Centralizado 400x240 (Item L)**| ❌ (Canto esquerdo X=0, Y=0) | ❌ (Canto esquerdo X=0, Y=0) | 🌟 **EXCLUSIVO NOSSO (Corrigido)** | Viewport centralizado e fundo xadrez expandido. |
| **Tutorial do Wally em 400px Widescreen (Item M)**| ❌ (Caixa estreita com barras pretas)| ❌ (Caixa estreita com barras pretas)| 🌟 **EXCLUSIVO NOSSO (Corrigido)** | Caixa contínua de 400px e Zigzagoon desobstruído. |
| **Healthbox do Adversário Calibrada (Item A)** | ❌ (Layout padrão) | ❌ (Layout padrão) | 🌟 **EXCLUSIVO NOSSO (Ajustado)** | Posicionada no alto à esquerda (`x = 16, y = 12`). |
| **Botão Gráfico SALDO (Item D)** | ❌ (`MONEY`) | ❌ (`MONEY`) | 🌟 **EXCLUSIVO NOSSO (Localizado)** | Substituído no sprite indexado de 32x16. |
| **Cabeçalhos do Trainer Card (Item F)** | ❌ (`TRAINER CARD`/`BADGES`) | ❌ (`TRAINER CARD`/`BADGES`) | 🌟 **EXCLUSIVO NOSSO (Localizado)** | `CARTÃO TREINADOR` e `INSÍGNIAS` compilados em 4bpp. |
| **Botões das Caixas do PC (Item G & H)** | ❌ (`CLOSE BOX` / `CANCEL`) | ❌ (`CLOSE BOX` / `CANCEL`) | 🌟 **EXCLUSIVO NOSSO (Localizado)** | `FECHAR` e `VOLTAR` compilados e indexados. |
| **Botões da Tela de Apelido (Item K)** | ❌ (`BACK`, `lower`, `others`)| ❌ (`BACK`, `lower`, `others`)| 🌟 **EXCLUSIVO NOSSO (Localizado)** | `VOLTAR`, `MINUS.`, `MAIUS.`, `OUTROS` localizados. |
| **Telemetria de FPS e Frame Time em Log** | ❌ (Apenas console básico) | ❌ (Apenas console básico) | 🌟 **EXCLUSIVO NOSSO** | Log contínuo em `port.log` registrando performance. |
| **Ferramentas de QA Automatizadas (Citra Runner)** | ❌ (Ausente) | ❌ (Ausente) | 🌟 **EXCLUSIVO NOSSO** | Runner autônomo com scripts de teste headless. |

---

## 🎯 5. Recursos Exclusivos do Nosso Projeto já Homologados como Válidos

Estes recursos foram expressamente testados pelo usuário no hardware real (Nintendo 3DS) e/ou emulador e receberam parecer de **100% Aprovado e Válido**:

1. **Logo da Tela de Título ("VERSÃO ESMERALDA"):** Paleta de cores oficial em português e alinhamento linear perfeito com o dragão Rayquaza.
2. **Velocidade Inteligente de Abertura (Boot Seguro 1x -> 4x in-game):** Áudio de introdução cristalino e sem aceleração mecânica na tela de Continue; aceleração suave ativada assim que o mundo do jogo é carregado.
3. **Menu de Inspeção e Resumo de Golpes (Pokémon Summary Screen):** Cabeçalhos (*GOLPES DE LUTA*, *EFEITO*, *DESCRIÇÃO*), atributos (*PODER*, *PRECISÃO*, *PP*) e botões de troca 100% acentuados e alinhados.
4. **Colheita de Frutas (Overworld Berry Picking):** Interação e diálogos nos arbustos (*"Phael colheu 2 FRUTAS ORAN."*) com concordância e caixas centralizadas.
5. **Diálogos de NPCs até a Rota 104:** Toda a narrativa e conversas com personagens de Littleroot Town, Oldale Town, Rota 102, Petalburg City e Rota 104 exibidas sem cortes de texto, sem estouro de balão e com localização oficial.
6. **Estabilidade de 59.8 FPS Contínuos no Old 3DS:** Consumo de CPU de 3.94 ms por frame e tempo de áudio de 1.3 ms, sem sobreaquecimento ou stuttering.

---

## 🚀 6. Próximos Passos e Backlog (Milestone v12+)

Com as correções de widescreen, menus do campo e localização gráfica concluídas na v11, o backlog para versões futuras está focado na **modernização ergonômica da tela touch inferior (320x240 pixels)**:
- **Item B:** Ampliação proporcional da interface da Mochila em Batalha para preencher a tela touch.
- **Item D (Layout):** Ampliação da lista de itens da Loja (Poké Mart) para ocupar a tela touch.
- **Item E:** Ampliação vertical dos slots da equipe Pokémon (Party Menu) aproveitando os 240px de altura.
- **Item G & H (Layout):** Ampliação e acabamento da gaveta e caixas de Pokémon do PC para ocupar a tela touch.
