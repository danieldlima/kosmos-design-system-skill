# Meta-máquina — Background interativo

Background animado em Three.js/TypeScript, com duas variantes trocáveis via query string.
Veja `PLAN.md` para o racional de arquitetura, paleta e roadmap de performance.

## Uso

```sh
npm install
npm run dev
```

- `http://localhost:5173/?bg=scan` — campo de coordenadas lido como universo: grid de
  hairlines fixo, estrelas grid-snapped que cintilam sutilmente, e 4 órbitas finas cada
  uma com um planeta em movimento lento — na linguagem já documentada em
  `references/visual-behavior.md`/`visual-patterns.md`. O ponteiro acende os nós próximos e
  traça conectores finos até eles (sem glow seguindo o cursor); o clique dispara um anel
  que percorre a cena.
- `http://localhost:5173/?bg=intelligence` — rede de partículas com drift orgânico; o
  ponteiro acende a "atenção" das partículas próximas, e o clique propaga um sinal pelo
  grafo de vizinhança (gradiente Instituto Kunumi).
- Sem `?bg=`, cai no default (`scan`).
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
verdade da marca Kunumi), espelhadas em `src/utils/palette.ts`. A variante `scan` usa só a
paleta institucional sem restrição de escopo (chumbo/concreto/urucum) e segue o
comportamento visual documentado em `references/visual-behavior.md` (hairlines precisas,
urucum como acento seletivo). O gradiente Instituto usado na variante `intelligence` é um
placeholder — ver "Em aberto" no `PLAN.md`.
