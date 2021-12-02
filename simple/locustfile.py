from locust import HttpUser, task, between
import json

URL = f"http://localhost:8000/"
sample_data = {"id": 123, "name": "Jay", "city": "Pune"}


class APIUser(HttpUser):
    wait_time = between(1, 2)

    @task(1)
    def hello_world(self):
        self.client.get(URL)

    @task(2)
    def get_information(self):
        self.client.post(URL + "getInfo", json.dumps(sample_data))
