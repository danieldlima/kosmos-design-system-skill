import * as THREE from "three";
import type { BackgroundScene } from "./BackgroundScene";
import { Pointer } from "./Pointer";
import { clampedDevicePixelRatio, prefersReducedMotion, FpsWatchdog } from "../utils/perf";
import { palette } from "../utils/palette";

/**
 * Owns the Three.js scene/camera/renderer and the animation loop. A single
 * BackgroundScene is mounted at a time; switching variants disposes the
 * previous one and mounts the next without recreating the renderer.
 */
export class Renderer {
  readonly renderer: THREE.WebGLRenderer;
  readonly scene = new THREE.Scene();
  readonly camera: THREE.PerspectiveCamera;
  readonly pointer: Pointer;
  readonly reducedMotion = prefersReducedMotion();

  private current: BackgroundScene | null = null;
  private readonly clock = new THREE.Clock();
  private readonly watchdog = new FpsWatchdog();
  private rafId: number | null = null;
  private visible = true;

  constructor(canvas: HTMLCanvasElement) {
    this.scene.background = new THREE.Color(palette.chumbo);

    this.camera = new THREE.PerspectiveCamera(
      55,
      window.innerWidth / window.innerHeight,
      0.1,
      100,
    );
    this.camera.position.z = 12;

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
    });
    this.renderer.setPixelRatio(clampedDevicePixelRatio());
    this.renderer.setSize(window.innerWidth, window.innerHeight);

    this.pointer = new Pointer(canvas);
    this.pointer.addListener({
      onMove: (ndc, velocity) => this.current?.onPointerMove(ndc, velocity),
      onDown: (ndc) => this.current?.onPointerDown(ndc),
    });

    window.addEventListener("resize", this.handleResize);
    document.addEventListener("visibilitychange", this.handleVisibility);
  }

  mount(scene: BackgroundScene): void {
    if (this.current) {
      this.scene.remove(this.current.object);
      this.current.dispose();
    }
    this.current = scene;
    scene.setCamera(this.camera);
    this.scene.add(scene.object);
    scene.resize(window.innerWidth, window.innerHeight);
  }

  start(): void {
    if (this.rafId !== null) return;
    this.clock.start();
    this.loop();
  }

  stop(): void {
    if (this.rafId !== null) cancelAnimationFrame(this.rafId);
    this.rafId = null;
  }

  dispose(): void {
    this.stop();
    window.removeEventListener("resize", this.handleResize);
    document.removeEventListener("visibilitychange", this.handleVisibility);
    this.pointer.dispose();
    this.current?.dispose();
    this.renderer.dispose();
  }

  private readonly loop = (): void => {
    this.rafId = requestAnimationFrame(this.loop);
    if (!this.visible) return;

    const dt = Math.min(this.clock.getDelta(), 1 / 30);
    this.pointer.update();
    this.current?.update(this.reducedMotion ? 0 : dt);

    if (!this.reducedMotion && this.watchdog.tick(dt)) {
      this.current?.degrade();
    }

    this.renderer.render(this.scene, this.camera);
  };

  private readonly handleResize = (): void => {
    const { innerWidth, innerHeight } = window;
    this.camera.aspect = innerWidth / innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(innerWidth, innerHeight);
    this.current?.resize(innerWidth, innerHeight);
  };

  private readonly handleVisibility = (): void => {
    this.visible = document.visibilityState === "visible";
  };
}
