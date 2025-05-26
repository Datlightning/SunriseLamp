// Already declared:
// const input = document.getElementById('imageInput');

async function updateQueueDisplay() {
    const res = await fetch('/queue');
    const data = await res.json();
    const container = document.getElementById('queueContainer');
    container.innerHTML = '';

    data.queue.forEach(url => {
    const img = document.createElement('img');
    img.src = url;
    img.className = 'w-24 h-24 object-cover rounded shadow';
    container.appendChild(img);
    });
}
async function updateCurrentDisplay() {
    const res = await fetch('/current-image');
    const data = await res.json();
    const container = document.getElementById('currentImage');
    container.innerHTML = '';

    data.current.forEach(url => {
    const img = document.createElement('img');
    img.src = url;
    img.className = 'w-24 h-24 object-cover rounded shadow';
    container.appendChild(img);
    });
}

// input.addEventListener('change', async () => {
//     const file = input.files[0];
//     if (!file) return;


//     // Upload to server
//     const formData = new FormData();
//     formData.append('file', file);

//     const response = await fetch('/upload', {
//     method: 'POST',
//     body: formData
//     });

//     if (response.ok) {
//     const data = await response.json();
//     updateQueueDisplay();  // Immediately update queue
//     } else {
//     alert('Upload failed');
//     }
// });

setInterval(() => {
updateQueueDisplay();
updateCurrentDisplay();
}, 5000);

updateQueueDisplay();
updateCurrentDisplay();

 setInterval(() => {
    const token = '68c2b6ceb89ed3cd1f1c0e78d5fd79f710bef290bda90a70';

    fetch(`/process-image-queue?token=${token}`)
      .then(response => response.json())
      .then(data => {
        console.log("Queue status:", data.status);
        if (data.status === "processed") {
            updateQueueDisplay();
            updateCurrentDisplay();
          console.log("Processed:", data.image);
          // You can update the UI here if needed
        }
      })
      .catch(error => console.error('Error:', error));
  }, 20000); // Every 20 seconds