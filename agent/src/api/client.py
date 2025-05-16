from .base import BaseClient


class ApiClient:
    def __init__(self, base_url: str, rate_limit_delay: float = 1.0, persist_failed: str = None):
        self.client = BaseClient(base_url, rate_limit_delay, persist_failed)

    def register(self, **kwargs):
        """Register the agent/machine with the server."""
        endpoint = f"machine/"
        response = self.client.send_request("POST", endpoint, json=kwargs)
        return response

    def get_agent_config(self, machine_id: str):
        """Get the agent configuration from the server."""
        endpoint = f"machine/{machine_id}/"
        response = self.client.send_request("GET", endpoint)
        return response

    def send_snapshot(self, snapshot):
        """Send a snapshot to the server."""
        endpoint = f"snapshot-batch/"
        response = self.client.send_request("POST", endpoint, json=snapshot)
        return response