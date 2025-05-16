import requests
import time
import backoff
import json
from requests.exceptions import RequestException


class BaseClient:
    def __init__(self, base_url: str, rate_limit_delay: float = 1.0, persist_failed: str = None):
        self.base_url = base_url.rstrip("/")
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.last_request_time = 0
        self.failed_requests = []

        # Optionally persist to file (e.g., 'failed_requests.json')
        self.persist_failed = persist_failed
        if self.persist_failed:
            self._load_failed_requests()

    def _rate_limit(self):
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _load_failed_requests(self):
        try:
            with open(self.persist_failed, "r") as f:
                self.failed_requests = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.failed_requests = []

    def _save_failed_requests(self):
        if self.persist_failed:
            with open(self.persist_failed, "w") as f:
                json.dump(self.failed_requests, f)

    def _enqueue_failed(self, method, endpoint, kwargs):
        self.failed_requests.append({
            "method": method,
            "endpoint": endpoint,
            "kwargs": kwargs,
        })
        self._save_failed_requests()

    def _retry_failed(self):
        if not self.failed_requests:
            return

        to_retry = self.failed_requests.copy()
        self.failed_requests = []

        for req in to_retry:
            try:
                print(f"Retrying: {req['method']} {req['endpoint']}")
                self.send_request(req["method"], req["endpoint"], **req["kwargs"])
            except RequestException:
                self._enqueue_failed(req["method"], req["endpoint"], req["kwargs"])

    @backoff.on_exception(backoff.expo, RequestException, max_tries=3)
    def send_request(self, method: str, endpoint: str, **kwargs):
        self._rate_limit()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method.upper(), url, timeout=10, **kwargs)
            response.raise_for_status()
            self._retry_failed()  # trigger any retries after a successful call
            return response.json()
        except RequestException as e:
            print(f"RequestException: {e}")
            if e.response.status_code >= 500:
                self._enqueue_failed(method, endpoint, kwargs)
            raise e  # or return None / custom error

    def get(self, endpoint: str, **kwargs):
        return self.send_request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, data=None, json=None, **kwargs):
        return self.send_request("POST", endpoint, data=data, json=json, **kwargs)

    def put(self, endpoint: str, data=None, json=None, **kwargs):
        return self.send_request("PUT", endpoint, data=data, json=json, **kwargs)

    def retry_all_failed(self):
        """Manually trigger retrying failed requests."""
        self._retry_failed()