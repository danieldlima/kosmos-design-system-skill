import type { BackgroundScene } from "./BackgroundScene";
import { MachineScene } from "../scenes/MachineScene";
import { IntelligenceScene } from "../scenes/IntelligenceScene";

export type BackgroundName = "machine" | "intelligence";

export const DEFAULT_BACKGROUND: BackgroundName = "machine";

const factories: Record<BackgroundName, () => BackgroundScene> = {
  machine: () => new MachineScene(),
  intelligence: () => new IntelligenceScene(),
};

export function isBackgroundName(value: string | null): value is BackgroundName {
  return value === "machine" || value === "intelligence";
}

export function createScene(name: BackgroundName): BackgroundScene {
  return factories[name]();
}
