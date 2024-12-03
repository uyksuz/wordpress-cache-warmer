import requests
import xml.etree.ElementTree as ET
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import threading
import math


def download_sitemap(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"İndirdik: {filename}")
        return True
    else:
        print(f"Failed to download {filename} (Status code: {response.status_code})")
        return False


def parse_sitemap_index(xml_content):
    sitemap_urls = []
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()

    for sitemap in root.findall('.//ns:sitemap/ns:loc', namespaces):
        loc = sitemap.text
        if loc:
            sitemap_urls.append(loc)
    return sitemap_urls


def parse_sitemap(xml_content):
    urls = []
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()

    for url in root.findall('.//ns:url/ns:loc', namespaces):
        loc = url.text
        if loc:
            urls.append(loc)
    return urls


def get_all_urls_from_sitemap(url):
    all_urls = []
    sitemap_filename = 'sitemap.xml'
    if download_sitemap(url, sitemap_filename):
        with open(sitemap_filename, 'r', encoding='utf-8') as f:
            sitemap_content = f.read()

        sitemap_urls = parse_sitemap_index(sitemap_content)

        for sitemap in sitemap_urls:
            sitemap_filename = os.path.basename(sitemap)
            if download_sitemap(sitemap, sitemap_filename):
                with open(sitemap_filename, 'r', encoding='utf-8') as f:
                    additional_sitemap_content = f.read()
                    additional_urls = parse_sitemap(additional_sitemap_content)
                    all_urls.extend(additional_urls)

    return all_urls


def visit_urls(urls, thread_name):

    options = Options()
    options.headless = False 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    for url in urls:
        driver.get(url)
        print(f"Tarayıcı: {thread_name} ---- URL: {url}")

    driver.quit()


sitemap_url = "https://netyonetim.com/sitemap.xml"
all_urls = get_all_urls_from_sitemap(sitemap_url)

if all_urls:
    num_threads = 4  # Paralel çalışacak thread sayısı
    chunk_size = math.ceil(len(all_urls) / num_threads) 
    url_chunks = [all_urls[i:i + chunk_size] for i in range(0, len(all_urls), chunk_size)]

    threads = []

   
    for i, urls in enumerate(url_chunks):
        thread = threading.Thread(target=visit_urls, args=(urls, f"Thread-{i+1}"))
        threads.append(thread)
        thread.start()

   
    for thread in threads:
        thread.join()

    print("Tüm URL'ler ziyaret edildi.")
else:
    print("No URLs found.")
