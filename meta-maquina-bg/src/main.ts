import { Renderer } from "./core/Renderer";
import { createScene, isBackgroundName, DEFAULT_BACKGROUND, type BackgroundName } from "./core/SceneRegistry";

function readBackgroundName(): BackgroundName {
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("bg");
  return isBackgroundName(requested) ? requested : DEFAULT_BACKGROUND;
}

const canvas = document.getElementById("bg-canvas") as HTMLCanvasElement;
const renderer = new Renderer(canvas);

renderer.mount(createScene(readBackgroundName()));
renderer.start();
