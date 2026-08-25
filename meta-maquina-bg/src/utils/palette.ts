// Espelha os tokens validados em skills/kosmos-design-system/references/tokens.json.
// Não inventar cores novas aqui — mudanças de paleta entram primeiro no tokens.json.
export const palette = {
  chumbo: 0x1c2127,
  grafite: 0x5e5e5e,
  concreto: 0xb4ada4,
  gelo: 0xf0f0f0,
  urucum: 0xf04e44,
  // Gradiente-assinatura do Instituto Kunumi — usado aqui só como placeholder para a
  // variante "intelligence" até a Meta-máquina ter paleta própria documentada.
  institutoGradient: [
    0xff9516, // spectrum-orange
    0xff6330, // spectrum-coral
    0xf04e44, // urucum
    0xd73e5f, // magenta
    0x9355a0, // violeta
    0x5a61b6, // indigo
  ],
} as const;

export function sampleInstitutoGradient(t: number): number {
  const stops = palette.institutoGradient;
  const clamped = Math.min(Math.max(t, 0), 1);
  const scaled = clamped * (stops.length - 1);
  const index = Math.min(Math.floor(scaled), stops.length - 2);
  return stops[index];
}
