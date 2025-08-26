// BasePage.jsx
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, useTexture, OrbitControls } from '@react-three/drei';
import { useRef } from 'react';
import "../BasePage/BasePage.css";
import highRes from "../../assets/background.jpg";

function AutoRotateSphere() {
  const groupRef = useRef();
  const texture = useTexture(highRes);

  useFrame(() => {
    if (groupRef.current) groupRef.current.rotation.y += 0.0008;
  });

  return (
    <group ref={groupRef}>
      <Sphere args={[50, 64, 64]} scale={[-1, 1, 1]}>
        <meshBasicMaterial map={texture} side={2} />
      </Sphere>
    </group>
  );
}

export default function BasePage({ children }) {
  return (
    <div className="screen">
      <Canvas
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          zIndex: 0,
          pointerEvents: "auto",
        }}
        camera={{ position: [0, 0, 20] }}
      >
        <ambientLight intensity={0.5} />
        <AutoRotateSphere />
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          enableDamping
          dampingFactor={0.01}
          rotateSpeed={-0.5}
          autoRotate={false}
        />
      </Canvas>

      <div style={{ position: "relative", zIndex: 1 }}>
        {children}
      </div>
    </div>
  );
}