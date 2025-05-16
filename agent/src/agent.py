import asyncio
import json
import os
from datetime import datetime
from platformdirs import user_config_dir
from requests import RequestException

from .api import ApiClient
from .utils import get_machine_config, get_process_stats


class Agent:
    def __init__(self, app_name="ProcessMonitorAgent", filename="agent_state.json"):
        self.config_file_path = os.path.join(user_config_dir(app_name), filename)
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)

        self.__state = {
            "is_registered": False,
            "machine_id": "",
            "enabled": True,
            "polling_interval": 5
        }

        self._client = ApiClient("http://localhost:8000/api/")
        self.running = True

        self._load()
        self._register()

    def _load(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, "r") as f:
                self.__state.update(json.load(f))

    def _save(self):
        with open(self.config_file_path, "w") as f:
            json.dump(self.__state, f)

    def _reset(self):
        self.__state = {
            "is_registered": False,
            "machine_id": "",
            "enabled": True,
            "polling_interval": 5
        }

    def _register(self):
        if self.__state["is_registered"]:
            return
        print("Registering...")
        machine_config = get_machine_config()
        result = self._client.register(**machine_config)
        if result:
            self.__state["machine_id"] = result.get("machine_id", "")
            self.__state["is_registered"] = True
            self._save()
        else:
            print("[Agent] Registration failed.")

    async def poll_remote_config(self):
        while self.running:
            try:
                if self.__state["is_registered"]:
                    try:
                        config = self._client.get_agent_config(self.__state["machine_id"])
                        if config:
                            self.__state["enabled"] = config.get("enabled", True)
                            self.__state["polling_interval"] = config.get("polling_interval", 5)
                            self._save()
                    except RequestException as e:
                        print("Agent")
                        if e.response.status_code == 404:
                            # Agent not registered
                            self._reset()
                            self._register()

            except Exception as e:
                print(f"[Remote Config] Error: {e}")
            await asyncio.sleep(15)

    async def sync_snapshots_loop(self):
        while self.running:
            if not self.__state["enabled"]:
                print("[Snapshots] Agent is disabled remotely.")
                await asyncio.sleep(5)
                continue

            try:
                await self._sync_snapshots()
            except Exception as e:
                print(f"[Snapshots] Error: {e}")
            await asyncio.sleep(self.__state["polling_interval"])

    async def _sync_snapshots(self):
        print(f"[Snapshots] Capturing at {datetime.now()}")
        snapshot_data = get_process_stats()  # sync call, okay here
        snapshot_data["machine_id"] = self.__state["machine_id"]
        self._client.send_snapshot(snapshot_data)

    async def run(self):
        await asyncio.gather(
            self.poll_remote_config(),
            self.sync_snapshots_loop()
        )

    def stop(self):
        self.running = False