from scapy import all
import os

def SeparateTraffic(filepath:str):
    pkts = all.rdpcap(filepath)
    ste = {}

    for pkt in pkts:
        src = pkt[all.Ether].src
        dst = pkt[all.Ether].dst

        if (dst in ste) and (src in ste[dst]):
            ste[dst][src].append(pkt)
        else:
            if src not in ste:
                ste[src] = {}
            if dst not in ste[src]:
                ste[src][dst] = []
            ste[src][dst].append(pkt)

    return ste

def extract_traffic(file_path:str, target_path:str, srcip:str, dstip:str, tcpports:list=None):
    all_packets = all.rdpcap(file_path, 200000)
    new_packets = []
    print("    " + str(len(all_packets)))
    for packet in all_packets:
        if all.IP not in packet:
            continue
        if tcpports is not None:
            if all.TCP not in packet:
                continue
            if packet[all.TCP].dport not in tcpports and packet[all.TCP].sport not in tcpports:
                continue
            if packet[all.IP].src == srcip and packet[all.IP].dst == dstip:
                new_packets.append(packet)
        elif packet[all.IP].src == dstip and packet[all.IP].dst == srcip:
            new_packets.append(packet)
    all.wrpcap(target_path, new_packets)

def pick_packets(pktlist, interval:int, pkt_num:int):
    length = len(pktlist)
    index = 0
    result = False
    for i in range(length-pkt_num+1):
        pkt1 = pktlist[i]
        pkt2 = pktlist[i+pkt_num-1]
        if pkt2.time - pkt1.time < interval:
            index = i
            result = True
            break
    return pktlist[index:index+pkt_num], result


def DividePcapFile(filepath:str, targetdir:str):
    ste = SeparateTraffic(filepath)
    for src in ste:
        for dst in ste[src]:
            froms = src.replace(":", "z")
            tos = dst.replace(":", "z")
            filename = f"{froms}-{tos}"
            filepath = os.path.join(targetdir, filename)
            all.wrpcap(filepath, ste[src][dst])

# 使用scapy保存的pcap文件，读取出来的数据包结构，里面的时间戳是捕获包的时间

def extract_info2():
    # print(1)
    # pkt_list = all.rdpcap("../../data/separated_pcap/http/http_cs_hit_edu_cn.pcap", 20000)
    # print(pkt_list[-1].time-pkt_list[0].time, len(pkt_list))
    # new_list, result = pick_packets(pkt_list, 10, 2000)
    # print(result)
    # all.wrpcap("../../data/for_simulation/http/http_cs_hit_edu_cn.pcap", new_list)

    print(2)
    pkt_list = all.rdpcap("../../data/separated_pcap/ftp/ftp_gnu_org_browser_download.pcap", 20000)
    print(pkt_list[-1].time-pkt_list[0].time, len(pkt_list))
    new_list, result = pick_packets(pkt_list, 10, 2000)
    print(result)
    all.wrpcap("../../data/for_simulation/ftp/ftp_gnu_org_browser_download.pcap", new_list)

    print(3)
    pkt_list = all.rdpcap("../../data/separated_pcap/imap_smtp/imap.pcap", 20000)
    print(pkt_list[-1].time-pkt_list[0].time, len(pkt_list))
    new_list, result = pick_packets(pkt_list, 10, 2000)
    print(result)
    all.wrpcap("../../data/for_simulation/imap_smtp/imap.pcap", new_list)

    print(4)
    pkt_list = all.rdpcap("../../data/separated_pcap/imap_smtp/smtp.pcap", 20000)
    print(pkt_list[-1].time-pkt_list[0].time, len(pkt_list))
    new_list, result = pick_packets(pkt_list, 10, 2000)
    print(result)
    all.wrpcap("../../data/for_simulation/imap_smtp/smtp.pcap", new_list)

    print(5)
    pkt_list = all.rdpcap("../../data/separated_pcap/pop_smtp/pop3.pcap", 20000)
    print(pkt_list[-1].time-pkt_list[0].time, len(pkt_list))
    new_list, result = pick_packets(pkt_list, 10, 2000)
    print(result)
    all.wrpcap("../../data/for_simulation/pop_smtp/pop3.pcap", new_list)

    print(6)
    pkt_list = all.rdpcap("../../data/separated_pcap/pop_smtp/smtp.pcap", 20000)
    print(pkt_list[-1].time-pkt_list[0].time, len(pkt_list))
    new_list, result = pick_packets(pkt_list, 10, 2000)
    print(result)
    all.wrpcap("../../data/for_simulation/pop_smtp/smtp.pcap", new_list)

def extract_info1():
    print(1)
    extract_traffic("../../data/origin_pcap/http/http_cs_hit_edu_cn.pcap",
                    "../../data/separated_pcap/http/http_cs_hit_edu_cn.pcap",
                    "192.168.199.104", "61.167.60.70", [80])
    print(2)
    extract_traffic("../../data/origin_pcap/ftp/ftp_gnu_org_browser_download.pcap",
                    "../../data/separated_pcap/ftp/ftp_gnu_org_browser_download.pcap",
                    "192.168.199.104", "209.51.188.20", [20, 21])
    print(3)
    extract_traffic("../../data/origin_pcap/imap_smtp/imap_smtp.pcap", "../../data/separated_pcap/imap_smtp/imap.pcap",
                    "192.168.199.104", "123.126.97.78", [143])
    print(4)
    extract_traffic("../../data/origin_pcap/imap_smtp/imap_smtp.pcap", "../../data/separated_pcap/imap_smtp/smtp.pcap",
                    "192.168.199.104", "220.181.12.13", [25])
    print(5)
    extract_traffic("../../data/origin_pcap/pop_smtp/pop3_smtp.pcap", "../../data/separated_pcap/pop_smtp/pop3.pcap",
                    "192.168.199.104", "123.126.97.79", [110])
    print(6)
    extract_traffic("../../data/origin_pcap/pop_smtp/pop3_smtp.pcap", "../../data/separated_pcap/pop_smtp/smtp.pcap",
                    "192.168.199.104", "220.181.12.18", [25])
    print(7)
    extract_traffic("../../data/origin_pcap/vpn/v2ray.pcap",
                    "../../data/separated_pcap/vpn/v2ray.pcap",
                    "192.168.199.104", "107.6.240.142")

if __name__ == "__main__":
    # SeparateTraffic("../data/origin_pcap/3.pcap")
    # DividePcapFile("../data/origin_pcap/3.pcap", "../data/separated_pcap/")
    # extract_info1()
    extract_info2()


