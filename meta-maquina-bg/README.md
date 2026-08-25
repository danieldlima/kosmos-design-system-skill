# Meta-máquina — Background interativo

Background animado em Three.js/TypeScript, com duas variantes trocáveis via query string.
Veja `PLAN.md` para o racional de arquitetura, paleta e roadmap de performance.

## Uso

```sh
npm install
npm run dev
```

- `http://localhost:5173/?bg=machine` — clusters de nós girando como engrenagens, empurrados
  pelo ponteiro; clique gera um pulso de repulsão.
- `http://localhost:5173/?bg=intelligence` — rede de partículas com drift orgânico; o
  ponteiro acende a "atenção" das partículas próximas, e o clique propaga um sinal pelo
  grafo de vizinhança (gradiente Instituto Kunumi).
- Sem `?bg=`, cai no default (`machine`).
- `#/` é ignorado pelo background e fica livre para o roteamento da aplicação-mãe.

## Build

```sh
npm run build
```

Gera um bundle estático em `dist/`, pronto para ser servido, embutido em `<iframe>`, ou
adaptado para um web component — ver seção "Empacotamento" do `PLAN.md` para as opções em
aberto até sabermos a stack real da plataforma Meta-máquina.

## Paleta

As cores vêm de `skills/kosmos-design-system/references/tokens.json` (fonte única de
verdade da marca Kunumi), espelhadas em `src/utils/palette.ts`. O gradiente Instituto usado
na variante `intelligence` é um placeholder — ver "Em aberto" no `PLAN.md`.
