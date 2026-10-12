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

## 📌 Status Atual de Desenvolvimento
- [x] Feedbacks e imagens anotados e catalogados.
- [x] Diagnóstico técnico preliminar concluído.
- [ ] **Aguardando término da bateria de testes do usuário** para consolidar todos os novos requisitos antes de abrir uma nova branch de compilação.
