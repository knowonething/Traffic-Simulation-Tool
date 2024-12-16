from scapy import all
import time
import random

# 给包设置时间时会在时间间隔的基础上加入微小扰动 为间隔的十分之一
def ContinuousTraffic(interval:float, count:int, macaddr:tuple=None, ipaddr:tuple=None, payload:str=None):
    ctime = time.time()
    pktlist = []
    temp = interval/10
    for i in range(count):
        choice = random.random()
        pl = str(i) if payload is None else payload
        if choice >= 0.5:
            pkt = all.Ether()/all.IP()/all.TCP()/pl
        else:
            pkt = all.Ether()/all.IP()/all.UDP()/pl
        # pkt = all.fuzz(pkt)
        if random.random() >= 0.5:
            if not macaddr is None:
                pkt[all.Ether].src = macaddr[0]
                pkt[all.Ether].dst = macaddr[1]
            if not ipaddr is None:
                pkt[all.IP].src = ipaddr[0]
                pkt[all.IP].dst = ipaddr[1]
        else:
            if not macaddr is None:
                pkt[all.Ether].src = macaddr[1]
                pkt[all.Ether].dst = macaddr[0]
            if not ipaddr is None:
                pkt[all.IP].src = ipaddr[1]
                pkt[all.IP].dst = ipaddr[0]

        disturb = random.random()*temp - temp/2
        pkt.time = ctime + disturb

        ctime += interval
        pktlist.append(pkt)
    return pktlist

def InteractiveTraffic(interval:float, count:int, macaddr:tuple=None, ipaddr:tuple=None, tcpports:tuple=None, payload:str=None):
    ctime = time.time()
    pktlist = []
    temp = interval/10
    for i in range(count):
        pl = str(i) if payload is None else payload
        pkt = all.Ether()/all.IP()/all.TCP()/pl
        if random.random() >= 0.5:
            if not macaddr is None:
                pkt[all.Ether].src = macaddr[0]
                pkt[all.Ether].dst = macaddr[1]
            if not ipaddr is None:
                pkt[all.IP].src = ipaddr[0]
                pkt[all.IP].dst = ipaddr[1]
            if tcpports is not None:
                pkt[all.TCP].sport = tcpports[0]
                pkt[all.TCP].dport = tcpports[1]
        else:
            if not macaddr is None:
                pkt[all.Ether].src = macaddr[1]
                pkt[all.Ether].dst = macaddr[0]
            if not ipaddr is None:
                pkt[all.IP].src = ipaddr[1]
                pkt[all.IP].dst = ipaddr[0]
            if tcpports is not None:
                pkt[all.TCP].sport = tcpports[1]
                pkt[all.TCP].dport = tcpports[0]

        disturb = random.random()*temp - temp/2
        pkt.time = ctime + disturb

        ctime += interval
        pktlist.append(pkt)
    return pktlist

def test1():
    interval = 0.080  # 秒
    count = 10000
    macaddr = ("00:11:22:33:44:55", "01:02:03:04:05:06")
    ipaddr = ("10.0.2.5", "10.0.2.6")
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/ms80.pcap", pkts)
    interval = 0.060
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/ms60.pcap", pkts)
    interval = 0.040
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/ms40.pcap", pkts)
    interval = 0.020
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/ms20.pcap", pkts)
    count = 100000
    interval = 0.001000
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/ms1.pcap", pkts)
    interval = 0.000500
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/us500.pcap", pkts)
    interval = 0.000100
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/us100.pcap", pkts)
    interval = 0.000050
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/us50.pcap", pkts)
    interval = 0.000010
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../../data/gen_pcap/us10.pcap", pkts)
    count = 1000000
    interval = 0.000001
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../data/gen_pcap/us1.pcap", pkts)
    interval = 0.000000500
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../data/gen_pcap/ns500.pcap", pkts)
    interval = 0.000000100
    pkts = ContinuousTraffic(interval, count, macaddr, ipaddr)
    all.wrpcap("../data/gen_pcap/ns100.pcap", pkts)

def test2(num_Mbps:int):
    interval = cal_interval(num_Mbps)  # 秒
    count = int(10 / interval)
    macaddr = ("00:11:22:33:44:55", "01:02:03:04:05:06")
    ipaddr = ("10.0.2.5", "10.0.2.6")
    ports = (54321, 334)
    payload = "1"*1460
    pkts = InteractiveTraffic(interval, count, macaddr, ipaddr, ports, payload)
    all.wrpcap(f"../../data/gen_pcap/{num_Mbps}Mbps.pcap", pkts)

def cal_interval(num_Mbps:int):
    interval = 1 / (((num_Mbps / 8.0) * 1000 * 1000) / 1460)
    return interval


if __name__ == "__main__":
    # test2(600)
    # test2(550)
    # test2(540)
    # test2(530)
    # test2(520)
    # test2(510)
    # test2(500)
    # test2(490)
    # test2(480)
    # test2(470)
    # test2(460)
    # test2(450)
    test2(200)
    test2(210)
    test2(220)
    test2(230)
    test2(240)
    test2(250)
    for i in range(10):
        test2((10+i)*10)
    for i in range(9):
        test2((1+i)*10)
