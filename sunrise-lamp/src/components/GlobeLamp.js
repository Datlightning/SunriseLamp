import React, { useEffect, useRef, useState } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere } from '@react-three/drei';
import * as THREE from 'three';

// LED Component
function LED({ position, color, intensity, dot, parentRef }) {
  useEffect(() => {
    const width = 0.3;
    const height = 0.3;
    const rectLight = new THREE.RectAreaLight(color, intensity, width, height);
    rectLight.position.set(...position);
    rectLight.lookAt(0, 0, 0);

    parentRef.current?.add(rectLight);

    return () => {
      parentRef.current?.remove(rectLight);
    };
  }, [position, color, intensity, parentRef]);

  if (dot) {
    return (
      <mesh position={position}>
        <sphereGeometry args={[0.01, 8, 8]} />
        <meshBasicMaterial color={color} />
      </mesh>
    );
  }
  return null;
}

// Ambient Light Component
function AmbientLightComponent() {
  return <ambientLight intensity={0.3} />;
}

// Generate 8 distinct RGB colors evenly spaced
const generateRainbowColors = (count) => {
  const colors = [];
  for (let i = 0; i < count; i++) {
    const hue = (i / count) * 360;
    const color = new THREE.Color(`hsl(${hue}, 100%, 50%)`).getStyle();
    colors.push(color);
  }
  return colors;
};

// LED configuration
const ledConfig = (() => {
  const radius = 0.7;
  const arcCount = 8;
  const pointsPerArc = 10;
  const leds = [];
  const colors = generateRainbowColors(arcCount);

  for (let arc = 0; arc < arcCount; arc++) {
    const azimuth = (arc / arcCount) * 2 * Math.PI;
    for (let i = 0; i < pointsPerArc; i++) {
      const polar = (i / (pointsPerArc - 1)) * (135/180 * Math.PI) + Math.PI * 20/180;
      const x = radius * Math.sin(polar) * Math.cos(azimuth);
      const y = radius * Math.sin(polar) * Math.sin(azimuth);
      const z = radius * Math.cos(polar);
      leds.push({ position: [x, y, z], color: colors[arc], intensity: 1 });
    }
  }

  return leds;
})();

// Rotating Globe Component (with useFrame)
function RotatingGlobe({ rotationEnabled, dotsEnabled }) {
  const groupRef = useRef();

  useFrame(() => {
    if (rotationEnabled && groupRef.current) {
      groupRef.current.rotation.z += 0.01;
    }
  });

  return (
    <group ref={groupRef}>
      {ledConfig.map((led, index) => {
        const { position, color, intensity } = led;

        return (
          <LED
            key={index}
            position={position}
            color={color}
            intensity={intensity}
            dot={dotsEnabled}
            parentRef={groupRef}
          />
        );
      })}
      <Sphere args={[0.5, 32, 32]}>
        <meshStandardMaterial color="#ffffff" opacity={1} transparent />
      </Sphere>
    </group>
  );
}

// GlobeLamp Component
function GlobeLamp() {
  const [rotationEnabled, setRotationEnabled] = useState(true);
  const [dotsEnabled, setDotEnabled] = useState(true);

  return (
    <div className="flex">
      <div style={{ width: '70vw', height: '100vh' }}>
        <Canvas camera={{ position: [0, 2, 0], fov: 75 }}>
          <AmbientLightComponent />
          <RotatingGlobe rotationEnabled={rotationEnabled} dotsEnabled={dotsEnabled} />
          <OrbitControls enableRotate={false} />
        </Canvas>
      </div>
      <div className="p-4" style={{ width: '30vw' }}>
        <h2 className="text-lg font-bold mb-4">Control Panel</h2>
        <p className="text-sm mb-4">Edit LED positions and colors directly in <code>ledConfig</code> inside the code.</p>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={rotationEnabled}
            onChange={(e) => setRotationEnabled(e.target.checked)}
          />
          <span>Enable Globe Rotation</span>
        </label>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={dotsEnabled}
            onChange={(e) => setDotEnabled(e.target.checked)}
          />
          <span>Enable Dot Visuals</span>
        </label>
      </div>
    </div>
  );
}

export default GlobeLamp;
