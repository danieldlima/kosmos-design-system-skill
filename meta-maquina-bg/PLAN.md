# Plano — Background Interativo "Meta-máquina"

## 1. Conceito

O nome "Meta-máquina" sugere duas leituras que não competem entre si, mas se complementam:

- **Máquina** — mecanismo, engrenagem, estrutura física que se move e se conecta.
- **Meta** — o nível acima da máquina: processamento, inteligência, rede, abstração.

Em vez de escolher uma leitura, o plano cobre as duas como **variantes intercambiáveis do
mesmo sistema de background**, selecionáveis por query string:

```
index.html?bg=scan#/            → variante 1: Scan (painel de instrumentação técnica)
index.html?bg=intelligence#/    → variante 2: Rede/Inteligência (nós e sinapses)
```

`bg` ausente ou inválido cai no default (`scan`). O `#/` fica reservado para o roteamento
da aplicação-mãe (a plataforma Meta-máquina em si); o background não depende dele, só não
deve quebrar quando presente.

## 2. Stack técnica

| Camada | Escolha | Porquê |
|---|---|---|
| Linguagem | TypeScript | tipagem para as duas cenas e para a camada de interação, que serão reaproveitadas |
| Bundler/dev server | Vite | zero-config para TS + Three.js, HMR rápido, build estático simples de embutir depois |
| Render 3D | **Three.js** | ambas as variantes têm *muitos elementos* (dezenas a milhares de partículas/nós); WebGL via Three é o que sustenta isso a 60fps — canvas 2D não escalaria |
| Sem framework de UI | — | isto é só o background; a plataforma real consome o build como script/iframe/componente depois |

Estrutura de pastas:

```
meta-maquina-bg/
  index.html              # entry: lê ?bg=, monta a cena
  src/
    main.ts               # bootstrap
    core/
      Renderer.ts          # scene/camera/renderer/loop compartilhado
      Pointer.ts            # posição/velocidade do ponteiro (mouse + touch)
      SceneRegistry.ts       # mapa nome→factory de cena
      BackgroundScene.ts      # interface comum que as duas variantes implementam
    scenes/
      ScanScene.ts            # variante 1
      IntelligenceScene.ts    # variante 2
      scanShaders.ts           # shaders do grid de hairlines e do glow do ponteiro
    utils/
      palette.ts             # cores extraídas de kosmos tokens.json
      perf.ts                # DPR clamp, FPS watchdog, prefers-reduced-motion
    style.css
  package.json / tsconfig.json / vite.config.ts
  README.md
```

## 3. Paleta e tipografia

Reaproveitar os tokens já validados em `skills/kosmos-design-system/references/tokens.json`
em vez de inventar cores novas:

- Fundo: `chumbo` `#1C2127` (ground escuro institucional).
- Variante **Scan**: glifos em `concreto` `#B4ADA4` (estrutura inativa) com destaque
  `urucum` `#F04E44` nos glifos sob influência do ponteiro — a mesma leitura "neutro que
  acende sob comando" da versão anterior (gears), mas expressa em linguagem de
  instrumentação técnica em vez de mecanismo. Usa só paleta institucional sem restrição
  de escopo (`chumbo`/`concreto`/`grafite`/`urucum`) — sem o gradiente Instituto.
- Variante **Intelligence**: gradiente-assinatura do Instituto (`spectrum-orange → coral →
  urucum → magenta → violeta → indigo`) nas conexões que "disparam" perto do ponteiro —
  é literalmente a única paleta multi-stop que a marca aprova, e casa com a ideia de
  sinapse/processamento. Fora do raio do ponteiro, nós ficam em `grafite`.
- Nenhum preto/branco puros como ground (regra da marca): usar `chumbo`/`gelo`.
- Tipografia não entra no background em si (é decorativo), mas se houver wordmark
  sobreposto, segue `PP Neue Machina` (não bundlada — carregar via `font-family` com
  fallback `Space Grotesk`, nunca redistribuir o arquivo da fonte).

## 4. Arquitetura de interação (compartilhada pelas duas cenas)

`core/Pointer.ts` normaliza mouse/touch em coordenadas `[-1, 1]` (NDC) e também expõe:

- posição suavizada (lerp) para movimento menos nervoso;
- velocidade (delta entre frames) para variantes que reagem a *rapidez* do gesto, não só posição;
- estado de "pressed" (mousedown/touchstart) para um efeito de pulso/burst no clique;
- fallback quando não há ponteiro (mobile sem hover): media query `(hover: hover)` decide
  se a cena reage a toque contínuo ou só a tap.

`core/BackgroundScene.ts` define a interface que as duas cenas implementam:

```ts
interface BackgroundScene {
  mount(renderer: Renderer): void;
  onPointerMove(ndc: THREE.Vector2, velocity: THREE.Vector2): void;
  onPointerDown(ndc: THREE.Vector2): void;
  update(dt: number): void;
  resize(width: number, height: number): void;
  dispose(): void;
}
```

Isso mantém `Renderer.ts` agnóstico de qual variante está montada — trocar `?bg=` troca só
a implementação, o loop e o pointer handling são únicos.

## 5. Variante 1 — Scan (campo de coordenadas)

Passou por duas rejeições antes deste desenho, ambas por feedback direto:

1. Uma primeira versão em engrenagens ("Machine") não comunicava nada de "Meta-máquina"
   nem de tecnologia.
2. Uma segunda versão em ícones de linha fina soltos (mira, radar, sparkle, viewfinder...)
   espalhados com rotação/escala aleatórias, sobre um fundo com textura de dither, foi
   classificada como "infantil e amadora" — clip-art solto, não um sistema.

Este desenho parte de `references/visual-behavior.md` e `references/visual-patterns.md`
(que já documentam a linguagem gráfica real da Kunumi para superfícies escuras) em vez de
inventar formas livres:

- "Hairline rules and precise edge alignment carry the structure" — nada aqui tem rotação
  ou posição aleatória; todo elemento está encaixado numa grade.
- "Urucum is a reading accent, used selectively — not an all-over fill" — o acento urucum
  só aparece pequeno e pontual (nós ativos, conector, glow contido), nunca como preenchimento.
- O motivo `dark-hero-orbit` ("thin orbital lines, peripheral glow") e a receita documentada
  de grid sutil para fundos escuros ("1 px line every 44–68 px at ~3.5% opacity") foram
  usados como precedente direto, não como inspiração livre.

- **Fundo**: grid de hairlines preciso (`src/scenes/scanShaders.ts`, `gridFragmentShader`) —
  linhas retas anti-aliased a intervalo regular no espaço do mundo (não em UV, para não
  distorcer com o aspect ratio), `concreto` sobre `chumbo` a ~7% de opacidade constante.
  Sem ruído, sem quantização — a primeira versão (dither dividido por canal RGB) produzia
  franjas de cor; esta é matematicamente neutra por construção.
- **Elementos**: uma grade de pontos menores (`THREE.InstancedMesh`, uma draw call, ~300+
  instâncias) marca cada interseção da grade — é aqui que mora o "muitos elementos" que
  justifica Three.js. Um subconjunto mais esparso dessas interseções (a cada 3 linhas)
  recebe um nó maior: um anel fino idêntico em todos os pontos — sem variação de forma,
  tamanho ou rotação por instância. Uniformidade é o objetivo, não ornamento.
- **Anéis orbitais**: 4 círculos grandes, finos, concêntricos, girando lentamente
  (24–46s por volta, os valores de "large orbit / background rings" do motion grammar
  documentado) — o motivo `dark-hero-orbit`, como pano de fundo estrutural, independente
  do ponteiro.
- **Reação ao ponteiro**: um glow pequeno e contido (não um blob grande) segue o ponteiro;
  nós dentro do raio de atenção clareiam de `concreto` para `urucum`. Linhas finas
  (`LineSegments`, no máximo 4 segmentos ativos) conectam o ponteiro aos nós mais próximos —
  o uso documentado da rampa expressiva como "thin progress rails, connectors, data-flow
  paths", nada além disso.
- **Clique**: um anel fino (`THREE.LineLoop`) se expande a partir do ponto clicado e ativa
  os nós que atravessa.
- **Paleta**: só tokens institucionais sem restrição de escopo (`chumbo`/`concreto`/`urucum`),
  sem gradiente Instituto e sem a rampa expressiva do deck (`#FF6A3D`/`#7765DF`) — mantém a
  variante inteiramente dentro do léxico canônico do `tokens.json`, sem depender da camada
  "deck-derived, subordinada".
- **Performance**: grid de pontos menores em uma única draw call; nós maiores e anéis
  compartilham geometria entre instâncias (só material clonado varia). `degrade()` reduz
  os anéis orbitais ambientes primeiro, sem quebrar a continuidade da grade principal.

## 6. Variante 2 — Intelligence (rede/IA)

- **Elementos**: nuvem de partículas em volume 3D (não em clusters fixos), representando
  "nós de processamento". Conexões são geradas dinamicamente por proximidade (grafo de
  vizinhos próximos, recalculado a cada N frames — não todo frame, para custo controlado).
- **Movimento base**: drift lento tipo *flow field* (ruído simplex aplicado à velocidade de
  cada partícula) — deliberadamente mais orgânico e fluido que a quietude alinhada à grade
  da variante Scan, sugerindo "pensamento" em vez de "instrumento".
- **Reação ao ponteiro**: partículas próximas ao ponteiro entram em um raio de "atenção" —
  suas conexões acendem com o gradiente Instituto e pulsam (opacidade oscilante), simulando
  um sinal se propagando pela rede a partir do ponto tocado. É diferente da Machine: aqui a
  interação **propaga** por partículas conectadas (1–2 saltos no grafo), não só localmente.
- **Clique**: gera um "pulso de ativação" que se propaga pelo grafo a partir do ponto clicado,
  com decaimento por distância de salto — o momento de maior espetáculo da cena.
- **Performance**: `Points`/`InstancedMesh` para as partículas, grafo de vizinhos via grid
  espacial (bucket por célula) para não ser O(n²) a cada recomputo, `LineSegments` para as
  arestas ativas apenas (a maioria das conexões possíveis nunca é desenhada).

## 7. Orçamento de performance (as duas variantes)

- Cap de devicePixelRatio em 2 (evita 3x/4x em telas retina de alta densidade sem ganho visual).
- `prefers-reduced-motion: reduce` → desativa drift automático e reação a velocity, mantém
  só uma resposta discreta ao ponteiro (sem loop perpétuo).
- Watchdog de FPS simples: se a média cair abaixo de ~40fps por mais de 2s, reduz a contagem
  de elementos ativos em runtime (degradação graciosa, sem trocar de cena).
- `dispose()` obrigatório ao trocar de variante em runtime (geometrias/materiais/texturas) —
  relevante se a plataforma-mãe permitir trocar `bg` sem reload de página no futuro.
- Pausar o loop de render via `IntersectionObserver`/`visibilitychange` quando o canvas não
  está visível (tab em background, scroll longo).

## 8. Entrega faseada

1. **Scaffold** — Vite + TS + Three, `Renderer`/`Pointer`/`SceneRegistry`, cena vazia
   renderizando fundo `chumbo` e lendo `?bg=`. *(este commit)*
2. **Intelligence v1** — nuvem de partículas com drift, sem grafo.
3. **Intelligence v2** — grafo de vizinhos + propagação de sinal por ponteiro/clique.
4. **Machine (descartada)** — primeira tentativa em engrenagens; substituída por feedback
   direto de que não comunicava "Meta-máquina"/tecnologia.
5. **Scan v1, ícones soltos (descartada)** — campo de glifos técnicos (radar, mira,
   sparkle...) com rotação/escala aleatórias sobre um fundo com dither; substituída por
   feedback direto de que lia como clip-art amador, não como sistema de marca.
6. **Scan v2, campo de coordenadas** — reconstrução a partir de `visual-behavior.md` e
   `visual-patterns.md`: grid de hairlines preciso, nós grid-snapped uniformes, anéis
   orbitais finos, glow e conectores contidos como acento seletivo. Ver seção 5.
7. **Perf pass** — DPR clamp, reduced-motion, FPS watchdog, teste em mobile real.
8. **Empacotamento** — decidir com a plataforma-mãe se isso vira script standalone,
   web component ou pacote npm interno; hoje entrega como app Vite standalone.

## 9. Em aberto (preciso de você para avançar além do scaffold)

- Stack real da plataforma Meta-máquina (React? Next? outro?) — define se a entrega final
  vira um `<script type="module">` solto, um web component, ou um pacote consumido via import.
- Se o background convive com conteúdo por cima (texto, UI) — se sim, preciso saber contraste
  mínimo exigido para não brigar com a regra de acessibilidade da marca.
- Se `intelligence` deve usar exatamente o gradiente Instituto (hoje reservado, no brandbook,
  só para uso do Instituto Kunumi) ou se a Meta-máquina tem paleta própria ainda não
  documentada neste repositório — enquanto isso não for confirmado, o scaffold usa o
  gradiente Instituto apenas como placeholder, claramente isolado em `utils/palette.ts`.
