import time
from scapy import all
from copy import deepcopy
import random
from decimal import Decimal

from util.ParseConfig import Config
from Replay.ReplayProcess import ReplayProcess


class ReplayControl:
    def __init__(self, config_path: str):
        self.config = Config(config_path)
        self.scene = {}
        self.prepare_scene()
        self.processes = []

    def prepare_scene(self):
        config = self.config.get_info()
        if config["Characteristic"] == "Proportion":
            self.gen_proportion()
        else:
            self.gen_simulation()

    def set_addr(self, packets: list, pairs: list):
        config = self.config.get_info()
        nodes = config["Nodes"]

        initiator_ip = packets[0]
        for packet in packets:
            if packet[all.IP].src == initiator_ip:
                packet[all.Ether].src = nodes[pairs[0]]["MAC"]
                packet[all.Ether].dst = nodes[pairs[1]]["MAC"]
                packet[all.IP].src = nodes[pairs[0]]["IP"]
                packet[all.IP].dst = nodes[pairs[1]]["IP"]
            else:
                packet[all.Ether].src = nodes[pairs[1]]["MAC"]
                packet[all.Ether].dst = nodes[pairs[0]]["MAC"]
                packet[all.IP].src = nodes[pairs[1]]["IP"]
                packet[all.IP].dst = nodes[pairs[0]]["IP"]

    def gen_proportion(self):
        config = self.config.get_info()
        requirements = config["Requirements"]
        traffic_files = config["TrafficFile"]

        total_packet = config["Total"]
        total_weight = 0

        for requirement in requirements:
            total_weight += requirements[requirement]["Weight"]

        for requirement in requirements:
            print("prepare for " + requirement + "......")
            work_content = {}
            pairs = requirement.split(":")[0].split("->")
            requirement_info = requirements[requirement]
            num_limit = int((requirement_info["Weight"]/total_weight)*total_packet)
            origin_packets = all.rdpcap(traffic_files[requirement_info["Type"]], count=1000)

            new_packets = origin_packets[:num_limit]
            while len(new_packets) < num_limit:
                add_num = num_limit - len(new_packets)
                add_ones = deepcopy(origin_packets[:add_num])
                new_packets.extend(add_ones)

            self.set_addr(new_packets, pairs)

            interval = 1/requirement_info["Rate"]
            temp = interval / 10
            ctime = 1
            for packet in new_packets:
                disturb = random.random() * temp - temp / 2
                packet.time = ctime + disturb
                ctime += interval

            work_content["packets"] = new_packets
            if "Delay" in requirement_info:
                work_content["start_time"] = requirement_info["Delay"]
            else:
                work_content["start_time"] = 0

            work_content["requirement"] = requirement
            self.scene[requirement] = work_content


    def gen_simulation(self):
        config = self.config.get_info()
        requirements = config["Requirements"]
        traffic_files = config["TrafficFile"]

        for requirement in requirements:
            print("prepare for " + requirement + "......")
            work_content = {}
            pairs = requirement.split(":")[0].split("->")
            requirement_info = requirements[requirement]
            origin_packets = all.rdpcap(traffic_files[requirement_info["Type"]], count=1000)
            interval = float((origin_packets[-1].time - origin_packets[0].time) / len(origin_packets))

            if "Duration" in requirement_info:
                duration = requirement_info["Duration"]
                new_packets = origin_packets[:]
                temp = interval / 10
                disturb = Decimal(random.random() * temp - temp / 2)
                while new_packets[-1].time - new_packets[0].time < duration:
                    add_time = new_packets[-1].time - new_packets[0].time + disturb
                    add_ones = deepcopy(origin_packets[:])
                    for packet in add_ones:
                        packet.time += add_time
                    new_packets.extend(add_ones)
                while new_packets[-2].time - new_packets[0].time >= duration:
                    new_packets.pop(-1)
            else:
                new_packets = origin_packets

            self.set_addr(new_packets, pairs)

            for packet in new_packets:
                packet.time = float(packet.time)

            work_content["packets"] = new_packets
            if "Delay" in requirement_info:
                work_content["start_time"] = requirement_info["Delay"]
            else:
                work_content["start_time"] = 0

            work_content["requirement"] = requirement
            self.scene[requirement] = work_content

    def start(self, delay: int = 10):
        if self.scene is None:
            return
        print("start replay......")
        start_time = time.time() + delay
        for requirement in self.scene:
            work_content = deepcopy(self.scene[requirement])
            work_content["start_time"] += start_time
            process = ReplayProcess(work_content)
            process.daemon = True
            self.processes.append(process)
            process.start()

    def wait(self):
        while len(self.processes) != 0:
            time.sleep(2)
            i = len(self.processes) - 1
            while i >= 0:
                if not self.processes[i].is_alive():
                    self.processes.pop(i)
                i -= 1

    def stop(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()