# 🎯 Backlog e Próximos Passos Prioritários

## 🚨 Tarefa #1 de Amanhã (Primeira Coisa):
### Mapear TODOS os Diálogos em Inglês Remanescentes no Jogo

1. **Varredura Completa de Scripts de Mapas:**
   - Analisar todos os 400+ arquivos em `build/upstream/data/maps/**/scripts.inc`.
   - Comparar strings em inglês contra o catálogo oficial `tools/locales/pt_br/` e identificar lacunas.

2. **Varredura de Treinadores e Batalhas:**
   - Textos de introdução, derrota e vitória de treinadores (`data/text/trainer_fan_club.inc`, `data/battle_scripts*.s`, etc.).

3. **Varredura de Menus, Utilidades e NPCs Globais:**
   - Textos de Centro Pokémon, Poké Mart, Pokénav, TV, Contest, Safári e Battle Frontier.

4. **Automação do Catálogo:**
   - Gerar os catálogos de tradução auditados com conformidade métrica estrita (`MESSAGE_BOX_WIDTH = 208px`).

---

## 🎮 Tarefa #2: Acompanhar Feedback do Usuário
- Validar as impressões do usuário no console 3DS real com o binário `emerald3ds_v7.3dsx` (layout das healthboxes e mensagem de sistema do SELECT).
