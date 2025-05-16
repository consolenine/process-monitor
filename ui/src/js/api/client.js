import $ from 'jquery';

const BASE_URL = 'http://localhost:8000/api';

export const API = {
  fetchMachines() {
    return $.ajax({
      url: `${BASE_URL}/machine/`,
      method: 'GET',
      dataType: 'json',
    });
  },
  fetchMachineDetails(machineId) {
    return $.ajax({
      url: `${BASE_URL}/machine/${machineId}/`,
      method: 'GET',
      dataType: 'json',
    });
  },
  updateAgent(machineId, data) {
    return $.ajax({
      url: `${BASE_URL}/machine/${machineId}/`,
      method: 'PATCH',
      contentType: 'application/json',
      data: JSON.stringify(data),
      dataType: 'json'
    });
  },
  fetchSnapshot(machineId) {
    return $.ajax({
      url: `${BASE_URL}/snapshot-batch/`,
      method: 'GET',
      data: { machine_id: machineId },
      dataType: 'json',
    });
  },
};
