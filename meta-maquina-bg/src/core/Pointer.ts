import * as THREE from "three";
import { hasHoverPointer } from "../utils/perf";

export type PointerListener = {
  onMove?(ndc: THREE.Vector2, velocity: THREE.Vector2): void;
  onDown?(ndc: THREE.Vector2): void;
  onUp?(ndc: THREE.Vector2): void;
};

/**
 * Normalizes mouse/touch input into NDC space ([-1, 1] on both axes) and
 * exposes a smoothed position plus per-frame velocity so scenes can react
 * to gesture speed, not just position.
 */
export class Pointer {
  readonly target = new THREE.Vector2(0, 0);
  readonly smoothed = new THREE.Vector2(0, 0);
  readonly velocity = new THREE.Vector2(0, 0);
  isDown = false;
  private hasMoved = false;
  private readonly listeners = new Set<PointerListener>();
  private readonly el: HTMLElement;
  private readonly continuousOnTouch: boolean;

  constructor(el: HTMLElement, { continuousOnTouch = hasHoverPointer() } = {}) {
    this.el = el;
    this.continuousOnTouch = continuousOnTouch;

    el.addEventListener("pointermove", this.handlePointerMove, { passive: true });
    el.addEventListener("pointerdown", this.handlePointerDown, { passive: true });
    window.addEventListener("pointerup", this.handlePointerUp, { passive: true });
    el.addEventListener("pointerleave", this.handlePointerUp, { passive: true });
  }

  addListener(listener: PointerListener): void {
    this.listeners.add(listener);
  }

  removeListener(listener: PointerListener): void {
    this.listeners.delete(listener);
  }

  /** Call once per frame; lerps the smoothed position and recomputes velocity. Stays
   * silent until the pointer has actually moved once, so scenes don't treat the
   * default (0, 0) target as a real cursor sitting at screen centre on load. */
  update(): void {
    if (!this.hasMoved) return;

    const prevX = this.smoothed.x;
    const prevY = this.smoothed.y;
    this.smoothed.lerp(this.target, 0.18);
    this.velocity.set(this.smoothed.x - prevX, this.smoothed.y - prevY);

    for (const listener of this.listeners) {
      listener.onMove?.(this.smoothed, this.velocity);
    }
  }

  dispose(): void {
    this.el.removeEventListener("pointermove", this.handlePointerMove);
    this.el.removeEventListener("pointerdown", this.handlePointerDown);
    window.removeEventListener("pointerup", this.handlePointerUp);
    this.el.removeEventListener("pointerleave", this.handlePointerUp);
    this.listeners.clear();
  }

  private toNdc(clientX: number, clientY: number): void {
    const rect = this.el.getBoundingClientRect();
    this.target.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    this.target.y = -(((clientY - rect.top) / rect.height) * 2 - 1);
  }

  private readonly handlePointerMove = (event: PointerEvent): void => {
    if (event.pointerType === "touch" && !this.continuousOnTouch && !this.isDown) return;
    this.toNdc(event.clientX, event.clientY);
    this.hasMoved = true;
  };

  private readonly handlePointerDown = (event: PointerEvent): void => {
    this.isDown = true;
    this.toNdc(event.clientX, event.clientY);
    this.hasMoved = true;
    for (const listener of this.listeners) listener.onDown?.(this.target);
  };

  private readonly handlePointerUp = (): void => {
    this.isDown = false;
    for (const listener of this.listeners) listener.onUp?.(this.target);
  };
}
