import type { BackgroundScene } from "./BackgroundScene";
import { ScanScene } from "../scenes/ScanScene";
import { IntelligenceScene } from "../scenes/IntelligenceScene";

export type BackgroundName = "scan" | "intelligence";

export const DEFAULT_BACKGROUND: BackgroundName = "scan";

const factories: Record<BackgroundName, () => BackgroundScene> = {
  scan: () => new ScanScene(),
  intelligence: () => new IntelligenceScene(),
};

export function isBackgroundName(value: string | null): value is BackgroundName {
  return value === "scan" || value === "intelligence";
}

export function createScene(name: BackgroundName): BackgroundScene {
  return factories[name]();
}
