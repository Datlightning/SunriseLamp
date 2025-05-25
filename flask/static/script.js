const loadingContainer = document.getElementById('loading-container');
const loadingBar = document.getElementById('loading-bar');
const container = document.getElementById('threeContainer'); // Smaller render container

let progress = 0;

function simulateLoading() {
  progress += 1;
  loadingBar.style.width = progress + '%';

  if (progress < 100) {
    requestAnimationFrame(simulateLoading);
  } else {
    loadingContainer.classList.add('opacity-0');
    setTimeout(() => {
      loadingContainer.style.display = 'none';
      animate();
    }, 300);
  }
}

simulateLoading();

const scene = new THREE.Scene();

// Camera — uses container dimensions
const camera = new THREE.PerspectiveCamera(
  75,
  container.clientWidth / container.clientHeight,
  0.1,
  1000
);
camera.position.y = 2;
camera.lookAt(0, 0, 0);

// Renderer — uses container dimensions
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

// Sphere + parent group
const geometry = new THREE.SphereGeometry(0.5, 32, 32);
const material = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  metalness: 0.5,
  roughness: 0.1,
});
const sphere = new THREE.Mesh(geometry, material);
const parentGroup = new THREE.Group();
parentGroup.add(sphere);

const leds = [];
const led_visuals = [];

const radius = 0.7;
const arcCount = 8;
const pointsPerArc = 10;

const generateRainbowColors = (count) => {
  const colors = [];
  for (let i = 0; i < count; i++) {
    const hue = (i / count) * 360;
    const color = new THREE.Color(`hsl(${hue}, 100%, 50%)`);
    colors.push(color.getHex());
  }
  return colors;
};

function rgbToHex({ r, g, b }) {
  const toHex = (c) => c.toString(16).padStart(2, '0');
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function updateLEDColors(newColors) {
  let index = 0;
  // console.log(leds)
  // console.log(led_visuals)
  for (let arc = 0; arc < arcCount; arc++) {
    for (let i = 0; i < pointsPerArc; i++) {
      const color = newColors[arc][i];
      const hexColor = parseInt(rgbToHex(color).replace("#", ""), 16);

      leds[index].color.setHex(hexColor);
      led_visuals[index].material.color.setHex(hexColor);
      index++;
    }
  }
}
async function pollProcessedImage() {
  try {
    const response = await fetch('/processed-image');
    const data = await response.json();

    if (data.colors) {
      // console.log(data.colors)
      updateLEDColors(data.colors); // Create this function to update existing LEDs
    }
  } catch (err) {
    console.error('Error fetching processed image:', err);
  }
}

// Call every 10 seconds (match your backend sleep delay)
setInterval(pollProcessedImage, 5000);




async function init() {
  const response = await fetch('/processed-image');
  const data = await response.json();
  const colors = data.colors;
  // console.log("INIT")
  // console.log(colors)
  const shared_geometry = new THREE.SphereGeometry(0.01, 8, 8);

  for (let arc = 0; arc < arcCount; arc++) {
    const azimuth = (arc / arcCount) * 2 * Math.PI;
    for (let i = 0; i < pointsPerArc; i++) {
      const polar =
        (i / (pointsPerArc - 1)) * (135 / 180 * Math.PI) + Math.PI * 20 / 180;
      const x = radius * Math.sin(polar) * Math.cos(azimuth);
      const y = radius * Math.sin(polar) * Math.sin(azimuth);
      const z = radius * Math.cos(polar);

      const hexNum = parseInt(rgbToHex(colors[arc][i]).replace('#', ''), 16);

      const rectLight = new THREE.PointLight(hexNum, 0.3, 4);
      rectLight.position.set(x, y, z);
      rectLight.lookAt(0, 0, 0);

      const material = new THREE.MeshStandardMaterial({
        color: hexNum,
        metalness: 0.2,
        roughness: 1,
      });
      const sphere = new THREE.Mesh(shared_geometry, material);
      sphere.position.set(x, y, z);

      parentGroup.add(rectLight);
      parentGroup.add(sphere);
      leds.push(rectLight);
      led_visuals.push(sphere);
    }
  }
}
init();

scene.add(parentGroup);

// Ambient light
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// Animate
function animate() {
  requestAnimationFrame(animate);
  parentGroup.rotation.z += 0.01;
  renderer.render(scene, camera);
}
