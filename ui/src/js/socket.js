let socket = null;
let socketReady = null;

export function initWebSocket(onMessageCallback) {
  socket = new WebSocket('ws://localhost:8000/ws/snapshot/');

  // Create a new Promise that resolves when socket is open
  socketReady = new Promise((resolve, reject) => {
    socket.onopen = () => {
      console.log('WebSocket connected');
      resolve();
    };
    socket.onerror = (err) => {
      console.error('WebSocket error', err);
      reject(err);
    };
  });

  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (onMessageCallback) {
      onMessageCallback(message);
    }
  };

  socket.onclose = () => {
    console.log('WebSocket closed');
    socketReady = null;
  };
}

export async function subscribeToMachine(machineId) {
  if (!socketReady) return;

  await socketReady;

  socket.send(JSON.stringify({
    action: 'subscribe',
    machine_id: machineId
  }));
}

export async function unsubscribeFromMachine(machineId) {
  if (!socketReady) return;

  await socketReady;

  socket.send(JSON.stringify({
    action: 'unsubscribe',
    machine_id: machineId
  }));
}
