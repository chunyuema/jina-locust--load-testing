import time, random, os
from locust import User, task
from jina import Client, Document


class JinaReuqestService:
    def get(*args, **kwargs):
        ## todo: replace with actual Client get
        print("Making get request!")
        time.sleep(random.random())

    def post(*args, **kwargs):
        ## todo: replace with actual Client get
        print("Making post request with: ", kwargs["text"])
        jina_client = kwargs["jina_client"]
        jina_client.post('/', Document(text=kwargs["text"]))


class JinaRequestHandler:
    def __init__(self, environment, stub):
        self.env = environment
        self._stub_class = stub.__class__
        self._stub = stub

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            func = self._stub_class.__getattribute__(self._stub, name)

            request_meta = {
                "request_type": "jina-client",
                "name": name,
                "start_time": time.time(),
                "response_length": 0,
                "response": None,
                "context": {},
                "exception": None,
            }

            start_perf_counter = time.perf_counter()
            try:
                func(*args, **kwargs)
                time.sleep(1)
                request_meta["response"] = "testing response"
            except Exception as e:
                request_meta["exception"] = "testing exception"
            request_meta["response_time"] = (
                time.perf_counter() - start_perf_counter
            ) * 1000
            self.env.events.request.fire(**request_meta)

        return wrapper


class JinaLoadTestUser(User):
    def __init__(self, environment):
        super().__init__(environment)
        self.req_handler = JinaRequestHandler(environment, JinaReuqestService)
        host = "https://1df7973034.wolf.jina.ai"
        self.client = Client(host=host)

    @task
    def get_request_load_test(self):
        self.req_handler.get()

    @task
    def post_request_load_test(self):
        self.req_handler.post(text="Hello World", jina_client=self.client)
