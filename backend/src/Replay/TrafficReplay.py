from scapy import all
import time

class Replay:

    # 假设通信机器都在运行中，并且后手机器在先手机器发送第一个包之前就处于待命状态
    # 先读取包，准备包，然后收发
    # 问题就是，如果不做包内容匹配，容易被其他的包干扰，做匹配浪费时间
    def InteractiveReplay(self, filepath: str, firsthand: bool, src: str, dst: str):
        self.pkts = list(all.rdpcap(filepath))
        self.pkts.sort(key=lambda x: x.time)

        # 换Ether地址
        ssrc = self.pkts[0].src
        for pkt in self.pkts:
            if pkt.src != ssrc:
                pkt.src = dst
                pkt.dst = src
            else:
                pkt.src = src
                pkt.dst = dst

        # 在交互式方法中，先手机器会发送第一个包，然后引起之后的包的收发
        if firsthand:
            bpffilter = f"ether src {dst} and ether dst {src}"
            self.src = src
            self.dst = dst
            input("开始")
        else:
            bpffilter = f"ether src {src} and ether dst {dst}"
            self.src = dst
            self.dst = src

        all.sniff(store=False, prn=self.InteractiveSend, stop_filter=self.InteractiveStop, filter=bpffilter)

    def InteractiveSend(self, pkt):
        # 当前接收了一个包，先从列表中除掉一个包
        self.pkts.pop(0)
        # 如果接下来的包还是要接收的，循环开始就退出
        while len(self.pkts) != 0:
            # 如果这个包是我要接收的包
            if self.pkts[0].src != self.src:
                break
            # 这个包要发出去
            all.sendp(self.pkts.pop(0))

    # 没有数据包时，就停止
    def InteractiveStop(self, pkt):
        return len(self.pkts) == 0

    # 两端直接发包，约定一个开始时间，开始时间应当足够远
    def DirectlyReplay(self, filepath:str, starttime:float, firsthand: bool, src:str, dst:str):
        pkts = all.rdpcap(filepath)

        # 找到自己的包
        pktlist = []
        if firsthand:
            ssrc = pkts[0].src
        else:
            ssrc = pkts[0].dst
            for i in range(len(pkts)):
                if pkts[i].src != ssrc:
                    continue
                starttime += float(pkts[i].time-pkts[0].time)
                break
        for pkt in pkts:
            if pkt.src != ssrc:
                continue
            pkt.src = src
            pkt.dst = dst
            pktlist.append(pkt)

        # 假设给定的时间比现在要大
        time.sleep(starttime-time.time())

        # realtime的意义是，根据包的时间戳，按时间戳关系发送各个包，力求间隔差不多
        # 一种写法是sendpfast，使用了tcpreplay，文档说有更好的性能
        # tcpreplay重放时考虑了包之间的间隔
        all.sendp(pktlist, realtime=True, verbose=False)

        print("over")

    def ReplayOneEnd(self, filepath:str, src:str, dst:str):
        pkts = all.rdpcap(filepath)

        ssrc = pkts[0].src
        for pkt in pkts:
            if pkt.src != ssrc:
                pkt.src = dst
                pkt.dst = src
            else:
                pkt.src = src
                pkt.dst = dst

        all.sendp(pkts, realtime=True, verbose=False)

if __name__ == "__main__":
    filepath = "../../data/separated_pcap/d4zeez07z47z5ezd8-58zfbz84z65ze5z64"
    r = Replay()
    # t = time.time()+40.00
    m1 = "58:fb:84:65:e5:64"
    m2 = "a4:b1:c1:0a:33:db"
    # r.DirectlyReplay(filepath, t, True, m1, m2)
    r.ReplayOneEnd(filepath, m1, m2)