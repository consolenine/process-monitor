import { initWebSocket, subscribeToMachine, unsubscribeFromMachine } from '../socket.js';
import { renderProcesses } from '../ui/tabs.js';

let currentMachineId = null;

export function setupSocketListeners() {
  initWebSocket((data) => {
    // Ignore if the data is for a different machine
    if (!currentMachineId || data.message.machine_id !== currentMachineId) return;

    // Update the table in real-time
    if (data.type === 'snapshot_message') {
      const processes = data.message.process_tree || [];
      renderProcesses(processes);
    }
  });
}

export function subscribeToMachineUpdates(machineId) {
  if (currentMachineId && currentMachineId !== machineId) {
    unsubscribeFromMachine(currentMachineId);
  }

  currentMachineId = machineId;
  subscribeToMachine(machineId);
}
