import React, { useState, useRef } from 'react';

function ImageUploader({ setImageData, gridHeight, gridWidth }) {
  const [image, setImage] = useState(null);
  const canvasRef = useRef();

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();

    if (!file) return;

    setImage(URL.createObjectURL(file));

    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        
        const { width, height } = canvas;
        const cellW = Math.floor(width / gridWidth);
        const cellH = Math.floor(height / gridHeight);
        
        const averages = [];

          for (let x = 0; x < gridWidth; x++) {
            for (let y = gridHeight - 1; y >= 0; y--) {

            const imageData = ctx.getImageData(x * cellW, y * cellH, cellW, cellH);
            const data = imageData.data;
            let r = 0, g = 0, b = 0;

            for (let i = 0; i < data.length; i += 4) {
              r += data[i];
              g += data[i + 1];
              b += data[i + 2];
            }

            const totalPixels = data.length / 4;
            const avg = {
              r: Math.round(r / totalPixels),
              g: Math.round(g / totalPixels),
              b: Math.round(b / totalPixels)
            };
            averages.push(avg);

            // Draw average color to cell
            ctx.fillStyle = `rgb(${avg.r}, ${avg.g}, ${avg.b})`;
            ctx.fillRect(x * cellW, y * cellH, cellW, cellH);

            // Optional: draw grid lines
            ctx.strokeStyle = 'red';
            ctx.strokeRect(x * cellW, y * cellH, cellW, cellH);
          }
        } 
        setImageData(averages);
      };

      img.src = reader.result;
    };

    reader.readAsDataURL(file);
  };

  return (
    <div className="p-4 border rounded-lg shadow-md max-w-md mx-auto">
      <h2 className="text-lg font-semibold mb-2">Upload an Image</h2>
      <input
        type="file"
        accept="image/*"
        onChange={handleImageChange}
        className="mb-4"
      />
      {image && (
        <div className="mt-4">
          <p className="mb-2">Preview:</p>
          <img src={image} alt="Uploaded preview" className="max-w-full h-auto rounded" />
          <canvas className="w-96" ref={canvasRef} style={{ border: '1px solid black', marginTop: '1rem' }} />
        </div>
      )}
    </div>
  );
}

export default ImageUploader;
