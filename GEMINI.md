# Regras Específicas do Projeto: Pokémon Emerald 3DS (Dual-Screen PT-BR)

## 🔄 Regra Master: Checagem Diária do Repositório Upstream (Oficial)
- **Verificação Diária Obrigatória:** Todo novo dia em que iniciarmos os trabalhos neste projeto, o agente DEVE verificar se foram lançadas atualizações no repositório original upstream (`ZallaxDev/pokeemerald-3Ds-dualscreen`).
- **Sincronização Ativa:** Se houver novos commits no upstream (`upstream/main`), o agente deve puxar e incorporar as novidades (correções de engine, relevo de voxels, suporte a áudio ou tentativas comunitárias de localização) na branch de desenvolvimento ativa.
- **Racional:** Outros desenvolvedores podem estar corrigindo bugs críticos do motor 3DS ou adicionando suporte a novas traduções. Manter o upstream sincronizado evita retrabalho e garante a melhor compatibilidade possível.

## 🌿 Gestão de Branches e Ciclo de Tentativas
- **Branches por Ciclo de Teste:** Cada tentativa de validação e compilação de ROM/binário para o hardware real deve residir em sua respectiva branch (ex.: `tentativa-rom-traduzida-v1`, `tentativa2`, etc.).
- **Rastreabilidade e Histórico:** O usuário gerenciará ou manterá as branches das tentativas para que tenhamos um histórico completo de evolução até alcançarmos a versão final perfeita.

## 🛡️ Preservação de Dados e Insumos
- **Arquivos Intocáveis:** É estritamente proibido apagar, resetar ou sobrescrever saves (`.sav`), pastas de logs (`/logs/` ou `port.log`) e os arquivos da pasta `# TEMPORARIO`.
- **Modificações Seguras:** Todas as alterações devem ser incrementais, defensivas e validadas contra quebras de compatibilidade no processador ARM11 do Nintendo 3DS.
