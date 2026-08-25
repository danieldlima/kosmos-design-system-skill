# Plano — Background Interativo "Meta-máquina"

## 1. Conceito

O nome "Meta-máquina" sugere duas leituras que não competem entre si, mas se complementam:

- **Máquina** — mecanismo, engrenagem, estrutura física que se move e se conecta.
- **Meta** — o nível acima da máquina: processamento, inteligência, rede, abstração.

Em vez de escolher uma leitura, o plano cobre as duas como **variantes intercambiáveis do
mesmo sistema de background**, selecionáveis por query string:

```
index.html?bg=machine#/         → variante 1: Mecanismo (engrenagens/linkages)
index.html?bg=intelligence#/    → variante 2: Rede/Inteligência (nós e sinapses)
```

`bg` ausente ou inválido cai no default (`machine`). O `#/` fica reservado para o roteamento
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
      MachineScene.ts        # variante 1
      IntelligenceScene.ts    # variante 2
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
- Variante **Machine**: linhas/nós em `concreto` `#B4ADA4` (estrutura inativa) com destaque
  `urucum` `#F04E44` nos pontos sob influência do ponteiro — reforça leitura "mecânica,
  neutra, que acende sob comando".
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

## 5. Variante 1 — Machine (mecanismo)

- **Elementos**: clusters de "engrenagens" — grupos de nós dispostos em círculo, ligados por
  linhas (via `THREE.LineSegments` com `BufferGeometry` atualizada por frame, não uma linha
  por par — isso é o que permite escalar a centenas de nós).
- **Movimento base**: cada cluster gira lentamente em torno do próprio centro (velocidades
  levemente distintas por cluster, para não parecer sincronizado/artificial).
- **Reação ao ponteiro**: nós dentro de um raio de influência são "puxados" para fora de
  sua órbita (repulsão radial), e a linha que os liga ao centro do cluster muda de
  `concreto` para `urucum`. Ao soltar/o ponteiro se afastar, retornam à órbita com easing.
- **Clique**: pulso de repulsão mais forte, como se a "máquina" tivesse levado um impacto —
  todos os nós próximos saltam e voltam.
- **Performance**: `InstancedMesh` para os nós (uma draw call para todos), `LineSegments`
  único para as conexões. Alvo: 300–800 nós no desktop, densidade reduzida em mobile.

## 6. Variante 2 — Intelligence (rede/IA)

- **Elementos**: nuvem de partículas em volume 3D (não em clusters fixos), representando
  "nós de processamento". Conexões são geradas dinamicamente por proximidade (grafo de
  vizinhos próximos, recalculado a cada N frames — não todo frame, para custo controlado).
- **Movimento base**: drift lento tipo *flow field* (ruído simplex aplicado à velocidade de
  cada partícula) — mais orgânico que a variante Machine, sugerindo "pensamento" em vez de
  "mecanismo".
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
2. **Machine v1** — clusters estáticos girando, sem interação ainda.
3. **Machine v2** — repulsão por ponteiro + pulso de clique.
4. **Intelligence v1** — nuvem de partículas com drift, sem grafo.
5. **Intelligence v2** — grafo de vizinhos + propagação de sinal por ponteiro/clique.
6. **Perf pass** — DPR clamp, reduced-motion, FPS watchdog, teste em mobile real.
7. **Empacotamento** — decidir com a plataforma-mãe se isso vira script standalone,
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
