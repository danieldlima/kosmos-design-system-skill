export const MAX_DPR = 2;

export function clampedDevicePixelRatio(): number {
  return Math.min(window.devicePixelRatio || 1, MAX_DPR);
}

export function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function hasHoverPointer(): boolean {
  return window.matchMedia("(hover: hover)").matches;
}

/**
 * Tracks a rolling FPS average and reports when it has stayed below
 * `threshold` for longer than `graceMs`, so callers can degrade element
 * counts instead of dropping frames silently.
 */
export class FpsWatchdog {
  private readonly threshold: number;
  private readonly graceMs: number;
  private lowSince: number | null = null;
  private smoothedFps = 60;

  constructor(threshold = 40, graceMs = 2000) {
    this.threshold = threshold;
    this.graceMs = graceMs;
  }

  /** Call once per frame with the frame's delta time in seconds. */
  tick(dt: number): boolean {
    const instantFps = dt > 0 ? 1 / dt : 60;
    this.smoothedFps += (instantFps - this.smoothedFps) * 0.1;

    if (this.smoothedFps < this.threshold) {
      if (this.lowSince === null) this.lowSince = performance.now();
      if (performance.now() - this.lowSince > this.graceMs) {
        this.lowSince = performance.now();
        return true;
      }
    } else {
      this.lowSince = null;
    }
    return false;
  }
}
