import * as THREE from "three";

/**
 * Common contract every background variant implements. Renderer.ts stays
 * agnostic of which variant is mounted — swapping `?bg=` swaps only the
 * implementation; the render loop and pointer wiring are shared.
 */
export interface BackgroundScene {
  readonly object: THREE.Object3D;

  /** Renderer injects its camera on mount so scenes can unproject pointer NDC into world space. */
  setCamera(camera: THREE.PerspectiveCamera): void;

  onPointerMove(ndc: THREE.Vector2, velocity: THREE.Vector2): void;
  onPointerDown(ndc: THREE.Vector2): void;

  /** dt in seconds. */
  update(dt: number): void;

  resize(width: number, height: number): void;

  /** Reduce active element count in response to sustained low FPS. */
  degrade(): void;

  dispose(): void;
}
