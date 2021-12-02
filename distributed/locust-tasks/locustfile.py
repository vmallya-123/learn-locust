import json
import logging
from locust import HttpUser, task, events, between
from locust.runners import MasterRunner, WorkerRunner
from google.cloud import storage

# list of filesnames whcih will be distributed between workers
filenames = []

# the default path in the container where the image files will be downloaded and stored
DEFAULT_FILE_PATH = "/locust-tasks/files/"

# files used for testing are stored here
BUCKET_NAME = "test_files_locust"

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)


def download_file(blob_name):
    """Download file to a worker and return the file path"""
    blob = bucket.get_blob(blob_name)
    blob.download_to_filename(f"{DEFAULT_FILE_PATH}{blob.name}")
    return f"{DEFAULT_FILE_PATH}{blob.name}"


def setup_workers(environment, msg, **kwargs):
    """Fired when the worker recieves a message of type 'handle_files'"""
    filenames.extend(map(lambda f: download_file(f), msg.data))
    environment.runner.send_message("acknowledge_file_recv", f"file recv!")


def on_acknowledge(msg, **kwargs):
    """Fired when the master recieves a message of type 'acknowledge_file_recv"""
    logging.debug(msg.data)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    """This runs on initialization of locust, before any test starts"""
    logging.info("initializing locust message types and listeners")
    if not isinstance(environment.runner, MasterRunner):
        environment.runner.register_message("handle_files", setup_workers)
    if not isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message("acknowledge_file_recv", on_acknowledge)


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    """When the test is started, evenly divides list between
    worker nodes to ensure unique data across threads"""
    if not isinstance(environment.runner, WorkerRunner):
        files = []

        for blob in storage_client.list_blobs(BUCKET_NAME):
            files.append(blob.name)

        worker_count = environment.runner.worker_count
        chunk_size = int(len(files) / worker_count)
        logging.info(
            f"number of files to be divided between each worker is {chunk_size}"
        )

        for i, worker in enumerate(environment.runner.clients):
            start_index = i * chunk_size

            if i + 1 < worker_count:
                end_index = start_index + chunk_size
            else:
                end_index = len(files)

            data = files[start_index:end_index]
            logging.debug(data)
            logging.debug(f"sending this data {data} to this {worker}")
            environment.runner.send_message("handle_files", data, worker)


class TestUser(HttpUser):
    """User who queries app"""

    wait_time = between(1, 2)

    def __init__(self, parent):
        self.filename = filenames.pop()
        super(TestUser, self).__init__(parent)

    @task
    def task(self):
        logging.debug("executing task")
        logging.debug(self.filename)
        with open(self.filename, "rb") as file:
            self.client.post("/fileSize", files={"file": file})
