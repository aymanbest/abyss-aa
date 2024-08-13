import re
import base64
import json
from main import decode
from requests import get
import sys
from bs4 import BeautifulSoup

headers = {"Referer": "https://abysscdn.com"}

def fetch_todecode(v):
    url = f"https://abysscdn.com/?v={v}"
    response = get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script', string=re.compile(r'━┻'))
    for script in scripts:
        if '━┻' in script.string:
            return script.string
    return None

def teest(v):
    todecode = fetch_todecode(v)
    if not todecode:
        print("No valid script tag found.")
        return

    decoded_string = decode(todecode)   
    match = re.search(r'(?<=JSON\.parse\(atob\(")([^"]+)(?="\)\))', decoded_string)
    if match:
        base64_string = match.group(1)
        json_string = base64.b64decode(base64_string).decode('utf-8')
        json_data = json.loads(json_string)
        domain = "https://" + json_data.get("domain", "")
        id = json_data.get("id", "")
        urls = {}
        
        #source: https://github.com/PatrickL546/How-to-download-hydrax-abyss.to#download
        for source in json_data.get("sources", []):
            label = source.get("label", "")
            size = source.get("size", 0)
            if label == "360p":
                urls[label] = (f"{domain}/{id}", size)
            elif label == "720p":
                urls[label] = (f"{domain}/www{id}", size)
            elif label == "1080p":
                urls[label] = (f"{domain}/whw{id}", size)

        total_urls = len(urls)
        for label, (url, size) in urls.items():
            response = get(url, headers= headers, stream=True)
            with open(f"{label}.mp4", "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / size) * 100
                    sys.stdout.write(f"\rDownloading {label} [{progress:.2f}%]")
                    sys.stdout.flush()
                sys.stdout.write("\n")

if __name__ == '__main__':
    teest("i92uL0bsu")
