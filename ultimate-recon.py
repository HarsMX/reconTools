import requests
import os
import sys
import socket
import re
import time
import random
import concurrent.futures
from urllib.parse import urlparse

# --- KONFIGURASI WARNA ---
G = '\033[92m'  # Green
R = '\033[91m'  # Red
Y = '\033[93m'  # Yellow
B = '\033[94m'  # Blue
W = '\033[0m'   # Reset

# --- DATABASE TARGET ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/89.0"
]

ADMIN_PATHS = [
    "admin/", "login/", "wp-admin/", "cpanel/", "dashboard/", "administrator/", 
    "phpmyadmin/", "user/", "signin/", "siakad/", "portal/"
]

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP", 
    110: "POP3", 443: "HTTPS", 3306: "MySQL", 8080: "HTTP-Proxy"
}

# [UPDATED] DAFTAR EKSTENSI YANG LEBIH LENGKAP
EXTENSIONS = {
    "SENSITIVE": [".sql", ".db", ".env", ".config", ".git", ".bak", ".bkp", ".json", ".xml", ".log"],
    "DOCUMENTS": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv", ".ppt", ".pptx", ".odt"],
    "IMAGES": [".jpg", ".png", ".jpeg", ".gif", ".ico", ".svg", ".bmp"],
    "SCRIPTS": [".php", ".js", ".py", ".sh", ".asp", ".aspx", ".jsp"],
    "ARCHIVES": [".zip", ".rar", ".tar", ".gz", ".7z", ".iso"],
    "MEDIA": [".mp3", ".mp4", ".wav", ".avi", ".mkv"],
    "WEB": [".html", ".htm", ".css"]
}

# --- FUNGSI BANTUAN ---
def get_random_header():
    return {'User-Agent': random.choice(USER_AGENTS)}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    clear_screen()
    print(f"""{B}
    ██╗   ██╗██╗     ████████╗██╗███╗   ███╗ █████╗ ████████╗███████╗
    ██║   ██║██║     ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔════╝
    ██║   ██║██║        ██║   ██║██╔████╔██║███████║   ██║   █████╗  
    ██║   ██║██║        ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝  
    ╚██████╔╝███████╗   ██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ███████╗
     ╚═════╝ ╚══════╝   ╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
    {Y}[+] RECON TOOL EXTENDED v2.1
    {Y}[+] Update: Expanded File Download Support
    {Y}[+] Outhor: Anioncode
    {Y}[+] Alert: I Hope You Like My Tools!!
    {W}""")

# --- MODULE 1: SUBDOMAIN ENUMERATION ---
def find_subdomains(domain):
    print(f"\n{Y}[*] Start Subdomain Enumeration via crt.sh (Passive)...{W}")
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    subs = set()
    try:
        r = requests.get(url, headers=get_random_header(), timeout=20)
        if r.status_code == 200:
            data = r.json()
            for entry in data:
                name_value = entry['name_value']
                subdomains = name_value.split('\n')
                for sub in subdomains:
                    if "*" not in sub: 
                        subs.add(sub)
        
        print(f"{G}[+] Found {len(subs)}  Subdomain:{W}")
        for s in list(subs)[:10]: 
            print(f"  - {s}")
        if len(subs) > 10: print(f"  ... and {len(subs)-10} anything.")
        
        with open(f"{domain}_subdomains.txt", "w") as f:
            f.write("\n".join(subs))
        print(f"{Y}[INFO] Save To {domain}_subdomains.txt{W}")
        
    except Exception as e:
        print(f"{R}[!] Got Fail : {e}{W}")

# --- MODULE 2: PORT SCANNER ---
def scan_port(ip, port, service_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0) 
    result = s.connect_ex((ip, port))
    s.close()
    if result == 0:
        print(f"{G}  [OPEN] Port {port} ({service_name}){W}")

def start_port_scan(domain):
    print(f"\n{Y}[*] Start Port Scanning...{W}")
    try:
        target_ip = socket.gethostbyname(domain)
        print(f"{B}[INFO] IP Target: {target_ip}{W}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for port, service in COMMON_PORTS.items():
                executor.submit(scan_port, target_ip, port, service)
    except Exception as e:
        print(f"{R}[!] Fail resolve IP: {e}{W}")

# --- MODULE 3: ADMIN PANEL FINDER ---
def check_admin(domain, path):
    url = f"http://{domain}/{path}"
    try:
        r = requests.get(url, headers=get_random_header(), timeout=5, allow_redirects=False)
        if r.status_code == 200:
            print(f"{G}  [FOUND] {url} (Status: 200){W}")
        elif r.status_code in [301, 302]:
            print(f"{B}  [REDIRECT] {url} -> {r.headers.get('Location')}{W}")
    except:
        pass

def start_admin_finder(domain):
    print(f"\n{Y}[*] Looking Admin/Login Panel...{W}")
    paths = ADMIN_PATHS 
    random.shuffle(paths)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for path in paths:
            executor.submit(check_admin, domain, path)

# --- MODULE 4: EMAIL EXTRACTOR ---
def extract_emails_from_text(text):
    emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text, re.I))
    return emails

def download_single_file(data):
    ts, original_url, save_folder = data
    
    parsed_path = urlparse(original_url).path
    filename = os.path.basename(parsed_path)
    if not filename or filename.endswith('/'): 
        filename = f"index_{ts}.html"
    
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    if len(filename) > 200: filename = filename[:200]
    
    save_path = os.path.join(save_folder, filename)
    
    if os.path.exists(save_path):
        return 

    archive_link = f"https://web.archive.org/web/{ts}if_/{original_url}"

    # RETRY LOGIC (UPDATED)
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            # JEDA LEBIH LAMA (3 sampai 6 detik)
            # Ini kunci agar tidak kena Connection Refused
            time.sleep(random.uniform(3.0, 6.0))
            
            # Gunakan session untuk header standard
            headers = get_random_header()
            headers['Connection'] = 'close' # Mencegah penumpukan socket
            
            r = requests.get(archive_link, headers=headers, timeout=60)
            
            if r.status_code == 200:
                if len(r.content) == 0:
                    print(f"{R}[Empty] {filename}{W}")
                    break
                
                with open(save_path, "wb") as f:
                    f.write(r.content)
                
                print(f"{G}[OK] {filename} ({len(r.content)} bytes){W}")
                return 

            elif r.status_code == 429: # Rate Limit
                print(f"{Y}[Limit] Server Tired. Delay 15 second...{W}")
                time.sleep(15)
                attempt += 1
            
            elif r.status_code == 404:
                print(f"{R}[404] {filename} Emty.{W}")
                break
            
            else:
                attempt += 1
        
        except requests.exceptions.ConnectionError:
            print(f"{R}[Conn] Cant Get Requests The  server. Cooling down 10s...{W}")
            time.sleep(10)
            attempt += 1
        except requests.exceptions.Timeout:
            print(f"{Y}[Time] Timeout. Retrying...{W}")
            attempt += 1
        except Exception as e:
            print(f"{R}[Err] {filename}: {str(e)}{W}")
            break
    
    if attempt == max_retries:
        print(f"{R}[Skip] {filename} Fail.{W}")

def start_wayback_machine(domain):
    print(f"\n{Y}[*] Calling  Wayback Machine CDX API...{W}")
    # Filter status 200 only
    api_url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=timestamp,original&filter=statuscode:200&collapse=urlkey"
    
    try:
        r = requests.get(api_url, headers=get_random_header(), timeout=60)
        data = r.json()
        if len(data) <= 1:
            print(f"{R}[-] Nothing Archive Data.{W}")
            return
            
        urls = data[1:] # Skip header
        print(f"{G}[+] Foud URL Arsip : {len(urls)}{W}")
        
        # --- KATEGORISASI FILE ---
        categories = {
            "SENSITIVE": [], "DOCUMENTS": [], "IMAGES": [], 
            "ARCHIVES": [], "MEDIA": [], "SCRIPTS": [], "WEB": [], "OTHER": []
        }
        
        for ts, link in urls:
            matched = False
            for cat, exts in EXTENSIONS.items():
                if any(link.lower().endswith(e) for e in exts):
                    categories[cat].append((ts, link))
                    matched = True
                    break
            if not matched:
                categories["OTHER"].append((ts, link))
        
        # --- TAMPILKAN STATISTIK ---
        print("\n[Statistik File]")
        for cat, items in categories.items():
            if len(items) > 0:
                print(f" -> {cat}: {len(items)} files")
                
        # --- MENU PILIHAN DOWNLOAD ---
        print(f"\n{B}Choice Donwload Mode:{W}")
        print("1. Just Sensitive & Documents (Default)")
        print("2. Sensitive, Docs, & Archives (Source code/Backup)")
        print("3. Images & Media (Asset visual)")
        print("4. ALL FILE (Maybe this's will take a long time!)")
        print("0. Exit")
        
        mode = input("Choice >> ")
        target_list = []
        
        if mode == "1":
            target_list = categories["SENSITIVE"] + categories["DOCUMENTS"]
        elif mode == "2":
            target_list = categories["SENSITIVE"] + categories["DOCUMENTS"] + categories["ARCHIVES"] + categories["SCRIPTS"]
        elif mode == "3":
            target_list = categories["IMAGES"] + categories["MEDIA"]
        elif mode == "4":
            for cat in categories:
                target_list += categories[cat]
        else:
            return

        if not target_list:
            print(f"{R}[!] What?!.{W}")
            return

        print(f"\n{Y}[*] Download Is Ready {len(target_list)} files...{W}")
        folder = f"{domain}_loot"
        os.makedirs(folder, exist_ok=True)
        
        # Max workers 5 agar tidak membebani network/firewall
        # UBAH DARI 5 KE 2 AGAR LEBIH SANTAL DAN TIDAK DIBLOKIR
        print(f"{Y}[*] Staring Download With 2 Threads (Safe Mode)...{W}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            tasks = [(ts, link, folder) for ts, link in target_list]
            executor.map(download_single_file, tasks)
            
        print(f"{G}[DONE] Finis. Cheking folder: {folder}{W}")

    except Exception as e:
        print(f"{R}[!] Error Wayback: {e}{W}")

# --- MAIN MENU ---
def main():
    banner()
    target = input(f"{Y}Insert Target Domain (cth: example.com): {W}").strip()
    
    if "://" in target: target = urlparse(target).netloc
    if "/" in target: target = target.split("/")[0]
    
    while True:
        print(f"\n{B}--- MENU OF {target} ---{W}")
        print("1. Full Scan (All Tools)")
        print("2. Wayback Machine (Download Manager)")
        print("3. Subdomain Enumeration")
        print("4. Port Scanning")
        print("5. Admin Panel Finder")
        print("0. EXIT")
        
        opt = input("Choice >> ")
        
        if opt == "1":
            find_subdomains(target)
            start_port_scan(target)
            start_admin_finder(target)
            start_wayback_machine(target)
        elif opt == "2":
            start_wayback_machine(target)
        elif opt == "3":
            find_subdomains(target)
        elif opt == "4":
            start_port_scan(target)
        elif opt == "5":
            start_admin_finder(target)
        elif opt == "0":
            sys.exit()
        else:
            print("Wrong Choice.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Exit The Program.{W}")
