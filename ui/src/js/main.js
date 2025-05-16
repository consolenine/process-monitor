import $ from 'jquery';
import { loadAndRenderMachines, bindSidebarEvents } from './ui/sidebar.js';
import { initTabs } from './ui/tabs.js';
import {setupSocketListeners, subscribeToMachineUpdates} from './api/dataHandler.js';

$(document).ready(async () => {
  await loadAndRenderMachines();

  bindSidebarEvents(async (machineId) => {
    await initTabs(machineId);

    setupSocketListeners();
    await subscribeToMachineUpdates(machineId); // now safely waits
  });
});
