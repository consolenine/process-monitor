import $ from 'jquery';
import { API } from '../api/client.js';

function initTabHandlers() {
  $('.tab-header').on('click', function () {
    $('.tab-header').removeClass('active');
    $(this).addClass('active');

    const target = $(this).data('target');
    $('.tab-content').removeClass('active');
    $(target).addClass('active');
  });
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

export function renderProcesses(processes) {
  const $tbody = $('#process-list');
  $tbody.empty();

  if (!processes.length) {
    $tbody.append(`
      <tr>
        <td colspan="5" class="text-center text-gray-400 py-4">
          No processes found.
        </td>
      </tr>
    `);
    return;
  }

  function renderRow(proc, depth = 0, parentId = null) {
    const rowId = `proc-${proc.id}`;
    const hasChildren = proc.children && proc.children.length > 0;

    const toggleIcon = hasChildren ? '▶' : '';

    const $row = $(`
      <tr
        id="${rowId}"
        data-depth="${depth}"
        ${parentId ? `data-parent="${parentId}"` : ''}
      >
        <td class="px-4 py-2 whitespace-nowrap items-center flex gap-2">
          ${hasChildren
            ? `<button class="toggle-btn" data-target="${rowId}" aria-label="Toggle">
                 <span class="icon">${toggleIcon}</span>
               </button>`
            : ``}
          <span class="pid" style="margin-left: ${depth * 2}rem;">${proc.pid}</span>
        </td>
        <td class="px-4 py-2">${proc.name}</td>
        <td class="px-4 py-2">${proc.cpu_usage.toFixed(2)}%</td>
        <td class="px-4 py-2">${proc.memory_usage.toFixed(2)} MB</td>
        <td class="px-4 py-2 text-green-400 font-semibold">Running</td>
      </tr>
    `);

    $tbody.append($row);

    if (hasChildren) {
      proc.children.forEach(child => {
        const $childRow = renderRow(child, depth + 1, rowId);
        $childRow.hide();
      });
    }

    return $row;
  }

  processes.forEach(proc => {
    renderRow(proc);
  });

  function toggleChildren(rowId, expand) {
    $tbody.find(`tr[data-parent="${rowId}"]`).each(function () {
      const childId = $(this).attr('id');
      if (expand) {
        $(this).show();
      } else {
        $(this).hide();
      }

      // Recursively hide nested children if collapsing
      if (!expand) {
        toggleChildren(childId, false);
        $tbody.find(`.toggle-btn[data-target="${childId}"] .icon`).text('▶');
        $tbody.find(`#${childId}`).removeClass('bg-stone-800 font-semibold');
      }
    });
  }

  $tbody.on('click', '.toggle-btn', function () {
    const targetId = $(this).data('target');
    const $firstChild = $tbody.find(`tr[data-parent="${targetId}"]:first`);
    const isVisible = $firstChild.is(':visible');

    toggleChildren(targetId, !isVisible);

    // Update toggle icon and highlight expanded row
    if (isVisible) {
      $(this).find('.icon').text('▶');
      $(`#${targetId}`).removeClass('bg-stone-800 font-semibold');
    } else {
      $(this).find('.icon').text('▼');
      $(`#${targetId}`).addClass('bg-stone-800 font-semibold');
    }
  });
}

function renderSystemConfig(config) {
  const $config = $('#system-config');
  $config.empty();

  const html = `
    <div class="bg-stone-800 shadow-md rounded-xl p-6 space-y-6">
      <h3 class="text-xl font-semibold text-gray-200">System Configuration</h3>
      <ul class="grid grid-cols-2 gap-4 text-sm text-gray-200">
        <li><span class="font-medium">Hostname:</span> ${config.hostname}</li>
        <li><span class="font-medium">OS:</span> ${config.os_name}</li>
        <li><span class="font-medium">Architecture:</span> ${config.architecture}</li>
        <li><span class="font-medium">Processor:</span> ${config.processor}</li>
        <li><span class="font-medium">CPU Cores:</span> ${config.cpu_cores}</li>
        <li><span class="font-medium">CPU Threads:</span> ${config.cpu_threads}</li>
        <li><span class="font-medium">Total RAM:</span> ${(config.total_ram / (1024 ** 3)).toFixed(2)} GB</li>
        <li><span class="font-medium">Total Storage:</span> ${(config.total_storage / (1024 ** 3)).toFixed(2)} GB</li>
      </ul>

      <div class="border-t pt-4">
        <h4 class="text-lg font-medium text-gray-300 mb-2">Update Agent Settings</h4>
        <form id="agent-config-form" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">
              Polling Interval (seconds):
            </label>
            <input
              type="number"
              name="polling_interval"
              value="${config.polling_interval}"
              min="1"
              class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-white-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-1">
              Enabled:
            </label>
            <select
              name="enabled"
              class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-white-500"
            >
              <option value="true" ${config.enabled ? "selected" : ""}>Yes</option>
              <option value="false" ${!config.enabled ? "selected" : ""}>No</option>
            </select>
          </div>
          <button
            type="submit"
          >
            Update
          </button>
        </form>
      </div>
    </div>
  `;

  $config.prepend(html);

  $('#agent-config-form').on('submit', function (e) {
    e.preventDefault();

    const formData = {
      polling_interval: parseInt($(this).find('input[name="polling_interval"]').val(), 10),
      enabled: $(this).find('select[name="enabled"]').val() === "true"
    };

    API.updateAgent(config.machine_id, formData)
      .then(updated => {
        alert('Settings updated successfully');
        renderSystemConfig(updated); // Refresh view
      })
      .catch(err => {
        console.error(err);
        alert('Error updating settings: ' + err.message);
      });
  });
}

export async function initTabs(machineId) {
  initTabHandlers();
  try {
    const response = await API.fetchMachineDetails(machineId);
    renderSystemConfig(response);
  } catch (err) {
    console.error('Failed to load machine details:', err);
    $('#system-config').html('<p class="text-red-500">Error loading config.</p>');
  }
  try {
    const response = await API.fetchSnapshot(machineId);
    const data = response.results[0];
    renderProcesses(data.process_tree || []);
  } catch (err) {
    console.error('Failed to load snapshot:', err);
    $('#process-list').html('<tr><td colspan="5">Error loading data.</td></tr>');
    $('#system-config').html('<p class="text-red-500">Error loading config.</p>');
  }
}
