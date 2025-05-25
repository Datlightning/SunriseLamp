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
}, 5000);

updateQueueDisplay();
