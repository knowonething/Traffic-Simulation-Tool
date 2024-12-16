import multiprocessing
import time
from scapy import all

class ReplayProcess(multiprocessing.Process):
    def __init__(self, work_content: dict) -> None:
        multiprocessing.Process.__init__(self)
        self.work_content = work_content

    def run(self):
        start_time = self.work_content["start_time"]
        packets = self.work_content["packets"]
        print(self.work_content["requirement"] + " " + str(packets[-1].time - packets[0].time) + " seconds. " + str(len(packets)))

        num = 0
        for pkt in packets:
            if all.TCP in pkt:
                num += 1
        print("TCP: " + str(num) + "  Other: " + str(len(packets) - num))

        time.sleep(max(start_time - time.time(), 0))
        # all.sendp(packets, realtime=True, verbose=False)
        all.sendpfast(packets, realtime=True)
        print(self.work_content["requirement"] + " end.")
