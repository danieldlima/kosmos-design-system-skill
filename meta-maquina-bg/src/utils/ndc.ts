import * as THREE from "three";

const rayOrigin = new THREE.Vector3();
const rayTarget = new THREE.Vector3();
const rayDirection = new THREE.Vector3();

/**
 * Projects an NDC pointer position onto the world-space plane `z = planeZ`,
 * so scenes can compare 3D element positions against the pointer without a
 * full THREE.Raycaster per frame.
 */
export function ndcToWorldPlane(
  ndc: THREE.Vector2,
  camera: THREE.PerspectiveCamera,
  planeZ = 0,
  out = new THREE.Vector3(),
): THREE.Vector3 {
  rayOrigin.copy(camera.position);
  rayTarget.set(ndc.x, ndc.y, 0.5).unproject(camera);
  rayDirection.copy(rayTarget).sub(rayOrigin).normalize();

  const t = (planeZ - rayOrigin.z) / rayDirection.z;
  return out.copy(rayOrigin).addScaledVector(rayDirection, t);
}
