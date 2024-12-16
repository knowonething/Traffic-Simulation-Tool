import docker
from util.ParseConfig import Config
import time

class GenerationControl:
    def __init__(self, config_path: str, intervel: int = 10):
        self.config = Config(config_path)
        self.client = docker.from_env()
        self.server_nodes = {}  # nodeid -> container obj
        self.client_nodes = {}
        self.interval = intervel
        self.duration = 60

        self.prepare()

    def create_container(self, container_config: dict):
        params = {}
        image = container_config["Image_tag"]
        if "Command" in container_config:
            cmd = container_config["Command"]
        else:
            cmd = None
        if "Name" in container_config:
            params["name"] = container_config["Name"]
            container_name = params["name"]
            container = self.get_container(container_name)
            if container is not None:
                self.kill_container(container)
                self.remove_container(container)
        if "Environment" in container_config:
            params["environment"] = container_config["Environment"]
            for env in params["environment"]:
                if type(params["environment"][env]) is not str:
                    continue
                if not params["environment"][env].startswith("####"):
                    continue
                item = params["environment"][env][4:]
                if item not in self.server_nodes:
                    continue
                server_container = self.server_nodes[item]
                result = self.get_container_mac_ip(server_container.id)
                if result[1] is None:
                    continue
                ip = result[1]
                params["environment"][env] = ip
        if "Volume" in container_config:
            params["volumes"] = container_config["Volume"]
        if "Network" in container_config:
            params["network_mode"] = container_config["Network"]

        params["detach"] = True

        try:
            containers = self.client.containers
            container = containers.create(image, cmd, **params)
        except docker.errors.ImageNotFound or docker.errors.APIError:
            return None
        return container

    def prepare(self):
        config = self.config.get_info()
        servers_config = config["Servers"]
        clients_config = config["Clients"]
        if "duration" in config:
            self.duration = config["duration"]

        for nodeid in servers_config:
            server_config = servers_config[nodeid]
            server_container = self.create_container(server_config)
            self.server_nodes[nodeid] = server_container
            server_container.start()

        for nodeid in clients_config:
            client_config = clients_config[nodeid]
            client_container = self.create_container(client_config)
            self.client_nodes[nodeid] = client_container

    def start(self):
        time.sleep(self.interval)
        for nodeid in self.client_nodes:
            container = self.client_nodes[nodeid]
            container.start()

    def wait(self):
        time.sleep(self.duration)

    def restart(self):
        for nodeid in self.client_nodes:
            container = self.client_nodes[nodeid]
            container.restart()

    def clear(self):
        for nodeid in self.client_nodes:
            container = self.client_nodes[nodeid]
            self.remove_container(container)
        for nodeid in self.server_nodes:
            container = self.server_nodes[nodeid]
            self.kill_container(container)
            self.remove_container(container)

    def stop(self):
        for nodeid in self.client_nodes:
            container = self.client_nodes[nodeid]
            self.kill_container(container)

    def pull_image(self, repository: str, tag: str = None):
        try:
            if tag is None:
                image = self.client.images.pull(repository)
            else:
                image = self.client.images.pull(repository, tag)
        except docker.errors.APIError:
            return False
        if image is None:
            return False
        return True

    def stop_container(self, container_id_or_name: str, timeout: int):
        try:
            container = self.client.containers.get(container_id_or_name)
            container.stop(timeout)
        except docker.errors.NotFound or docker.errors.APIError:
            return False
        return True

    def start_container(self, container_id_or_name: str):
        try:
            container = self.client.containers.get(container_id_or_name)
            container.start()
        except docker.errors.NotFound or docker.errors.APIError:
            return False
        return True

    def get_container_mac_ip(self, container_id_or_name: str):
        result = [None, None]
        try:
            container = self.client.containers.get(container_id_or_name)
        except docker.errors.NotFound or docker.errors.APIError:
            return result
        if "IPAddress" in container.attrs["NetworkSettings"]:
            result[1] = container.attrs["NetworkSettings"]["IPAddress"]
        if "MacAddress" in container.attrs["NetworkSettings"]:
            result[0] = container.attrs["NetworkSettings"]["MacAddress"]
        return result

    def get_container(self, container_id_or_name: str):
        try:
            container = self.client.containers.get(container_id_or_name)
            return container
        except docker.errors.NotFound or docker.errors.APIError:
            return None

    def kill_container(self, container):
        try:
            container.kill()
        except docker.errors.APIError:
            return

    def remove_container(self, container):
        try:
            container.remove()
        except docker.errors.APIError:
            return
