import $ from 'jquery';
import { API } from '../api/client.js';

const $machineList = $('#machine-list');

/**
 * Render machine cards in sidebar using jQuery
 * @param {Array} machines
 */
export function renderSidebar(machines) {
  $machineList.empty();

  if (!machines.length) {
    $machineList.html('<p class="p-4 text-gray-500">No machines connected.</p>');
    return;
  }

  machines.forEach(({ machine_id, hostname }) => {
    const $card = $(`
      <li>
        <div class="machine-title-card cursor-pointer" data-machine-id="${machine_id}">
          <p>
             ${hostname}
             <span class="inline-block ms-4 w-4 h-4 rounded-full bg-green-500"></span>
          </p>
        </div>
      </li>
    `);
    $machineList.append($card);
  });
}

/**
 * Fetch machines from API and render sidebar
 * @returns {Promise<void>}
 */
export async function loadAndRenderMachines() {
  try {
    const machines = await API.fetchMachines();
    renderSidebar(machines);
  } catch (err) {
    console.error('Failed to load machines:', err);
    $machineList.html('<p class="p-4 text-red-600">Error loading machines.</p>');
  }
}

/**
 * Bind click events on sidebar cards
 * @param {(machineId: string) => void} onCardClick
 */
export function bindSidebarEvents(onCardClick) {
  $machineList.on('click', 'div[data-machine-id]', function () {
    const $cards = $machineList.children();
    $cards.removeClass('active');
    $(this).addClass('active');

    const machineId = $(this).data('machine-id');
    onCardClick(machineId);
  });
}
