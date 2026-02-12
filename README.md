🛡️ Functional Overview: Ultimate Recon v2.1

This script is designed for historical data mining and surface analysis. It focuses on what a target has exposed in the past and what services are currently visible.
1. Subdomain Enumeration (find_subdomains)

    Method: Uses passive recon by querying crt.sh (Certificate Transparency logs).

    Purpose: Discovers subdomains associated with the target without sending a single packet to the target's actual server, keeping you "silent."

2. Port Scanner (start_port_scan)

    Method: Uses a multi-threaded socket connection to check a predefined list of Common Ports (21, 22, 80, 443, 3306, etc.).

    Purpose: Quickly identifies active services (like Web Servers, Databases, or SSH) running on the target IP.

3. Admin Panel Finder (start_admin_finder)

    Method: Brute-forces a curated list of sensitive paths (e.g., /phpmyadmin/, /cpanel/, /config/) using concurrent.futures for speed.

    Purpose: Locates login portals or dashboard entry points that might be poorly secured.

4. Wayback Machine Engine (start_wayback_machine)

    Method: Interacts with the Internet Archive CDX API to pull every URL ever crawled for that domain.

    Purpose: Categorizes history into "Sensitive," "Documents," "Scripts," and "Archives" to help you find deleted or forgotten data.

5. Smart Download Manager (download_single_file)

    Method: A robust downloader with Retry Logic, Rate Limit handling (Error 429), and Connection Timeout management.

    Purpose: Automatically "loots" the files discovered in the Wayback Machine and saves them locally into organized folders.

images
<img width="770" height="475" alt="image" src="https://github.com/user-attachments/assets/b1867747-f788-41bb-9cb4-e36e6eb559aa" />

<img width="772" height="433" alt="image" src="https://github.com/user-attachments/assets/65f4dee6-e448-4aa5-8502-09b843e3ff56" />

<img width="494" height="317" alt="image" src="https://github.com/user-attachments/assets/15cead9d-3a75-46b5-b1b3-44dafcead203" />


🛡️ Ultimate Recon v2.1: Setup Guide
1. Create a Project Folder

Open your terminal and create a dedicated directory for the tool to keep your "loot" files organized.
Bash


cd reconTools

2. Initialize the Virtual Environment

Creating a venv creates a self-contained "bubble" for your Python project.
Bash

python3 -m venv venv

3. Activate the Environment

You must activate the environment every time you want to use the tool.

    Linux / macOS:
    Bash

    source venv/bin/activate

    Windows:
    Bash

    venv\Scripts\activate

    Note: Once activated, your terminal prompt will usually show (venv) at the beginning.

4. Install Dependencies

This version of the script primarily relies on the requests library for its API calls and file downloads.
Bash

pip install requests

5. Run the Script

Make sure the ultimate-recon.py file is inside your folder, then execute:
Bash

python ultimate-recon.py

💡 Informatics Recommendations

    Terminal Aesthetics: Since you enjoy aesthetics, I recommend running this on Windows Terminal or iTerm2 with a "Monokai" or "Dracula" color scheme to make the colored output (G/R/Y/B) pop beautifully.

    Operational Security: When using Module 2 (Wayback Machine), the script is set to 2 threads (max_workers=2). Keep it this way to avoid getting your IP temporary blocked by the Wayback Machine API.

    Data Management: The script creates a {domain}_loot folder. If you plan to scan many domains, consider moving these folders into a results/ subdirectory to keep your workspace tidy.
