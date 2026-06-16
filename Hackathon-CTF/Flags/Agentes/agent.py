#!/usr/bin/env python3
"""
ctf_agents_enum.py

Uso:
    python3 ctf_agents_enum.py

O script tenta enumerar / descobrir flags no host fornecido.
Ele apenas faz requisições HTTP, baixa imagens referenciadas e procura por
padrões do tipo IDP{...} nas respostas e nos bytes das imagens.

Ajuste BASE_URL e UA_DEFAULT conforme necessário.
"""

import re
import os
import sys
import argparse
from urllib.parse import urljoin, urlparse
import requests

# ------- Configurações -------
BASE_URL = "http://20.102.93.39:33507/"   # altere se necessário
OUT_DIR = "agents_output"
IMG_DIR = os.path.join(OUT_DIR, "agents_imgs")
TIMEOUT = 6
# padrão User-Agent que vimos nas screenshots
UA_DEFAULT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"

# UAs para testar: mantenha UA_DEFAULT em primeiro lugar
UA_LIST = [
    UA_DEFAULT,
    "Mozilla/5.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "curl/7.68.0",
    "Python-requests/2.31.0",
]

# Endpoints a testar diretamente (serão combinados com base)
PATHS = [
    "/",
    "/app/flag.txt",
    "/flag",
    "/flag.txt",
    "/api",
    "/profile",
    "/agent",
    "/robots.txt",
    "/sitemap.xml",
    "/.git/HEAD",
    "/static/images/estamos-contratando.png",
]

# username values para testar como query param
USERNAME_TESTS = [
    UA_DEFAULT,
    "20.102.93.39",
    "Mozilla/5.0",
    "James Bond",
    "Jason Bourne",
]

# regex para flag
FLAG_RE = re.compile(rb"IDP\{[^}]+\}", re.IGNORECASE)
# também procurar por "flag" texto simples
FLAG_STR_RE = re.compile(rb"flag", re.IGNORECASE)

# ------- Helpers -------

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def search_flag_in_bytes(b):
    """Retorna lista de matches por padrão IDP{...} em bytes."""
    return FLAG_RE.findall(b)

def print_result(title, s):
    print(f"\n=== {title} ===")
    print(s)

# ------- Core -------

def do_request(session, url, ua, params=None):
    headers = {"User-Agent": ua}
    try:
        r = session.get(url, headers=headers, params=params, timeout=TIMEOUT)
        return r
    except Exception as e:
        return e

def extract_image_urls_from_html(base_url, html_bytes):
    # busca src="..." e url(...) simples
    try:
        html = html_bytes.decode("utf-8", errors="replace")
    except:
        html = str(html_bytes)
    urls = set()
    # <img src="...">
    for m in re.findall(r'src=["\']([^"\']+)["\']', html, flags=re.IGNORECASE):
        urls.add(m)
    # background-image: url('...')
    for m in re.findall(r'url\(([^)]+)\)', html, flags=re.IGNORECASE):
        u = m.strip().strip('\'"')
        urls.add(u)
    # normalizar para absolute
    norm = []
    for u in urls:
        if u.lower().startswith("http://") or u.lower().startswith("https://"):
            norm.append(u)
        else:
            norm.append(urljoin(base_url, u.lstrip("/")))
    return sorted(set(norm))

def download_image(session, url, ua, out_dir):
    headers = {"User-Agent": ua}
    try:
        r = session.get(url, headers=headers, timeout=TIMEOUT, stream=True)
    except Exception as e:
        return None, f"ERR {e}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    fname = os.path.basename(urlparse(url).path) or "img.bin"
    out_path = os.path.join(out_dir, fname)
    # garantir nome único
    base, ext = os.path.splitext(out_path)
    i = 1
    while os.path.exists(out_path):
        out_path = f"{base}-{i}{ext}"
        i += 1
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)
    return out_path, "OK"

def analyze_bytes_for_flag(b, context):
    found = []
    for m in search_flag_in_bytes(b):
        try:
            found.append(m.decode("utf-8", errors="replace"))
        except:
            found.append(str(m))
    # also search printable 'flag' mentions
    if FLAG_STR_RE.search(b) and not found:
        found.append("<contains 'flag' substring but no IDP{...}>")
    if found:
        print_result(f"FLAG(S) found in {context}", "\n".join(found))
    return found

def main(base_url):
    safe_mkdir(OUT_DIR)
    safe_mkdir(IMG_DIR)
    session = requests.Session()
    log_lines = []
    overall_found = []

    print("Base URL:", base_url)
    print("Output dir:", OUT_DIR)
    print("Trying UAs and endpoints...")

    # 1) Try direct paths with multiple UAs
    for ua in UA_LIST:
        print(f"\n--- Trying with UA: {ua} ---")
        for p in PATHS:
            url = urljoin(base_url, p.lstrip("/"))
            res = do_request(session, url, ua)
            if isinstance(res, Exception):
                print(f"{url} -> ERR {res}")
                log_lines.append(f"{ua} {url} ERR {res}")
                continue
            status = res.status_code
            l = len(res.content or b"")
            print(f"{url} -> {status} ({l} bytes)")
            log_lines.append(f"{ua} {url} {status} {l}")
            # search for IDP pattern in response body
            found = analyze_bytes_for_flag(res.content, url)
            if found:
                overall_found.extend(found)
            # if root page, extract images for later
            if p == "/" and status == 200:
                imgs = extract_image_urls_from_html(base_url, res.content)
                if imgs:
                    print(f" -> found {len(imgs)} image urls")
                    for u in imgs:
                        log_lines.append(f"IMG_URL {u}")
    # 2) Try username query variations on root and /api
    for ua in UA_LIST[:1]:  # concentrate on primary UA first (the special one)
        target_paths = ["/", "/api", "/profile", "/agent"]
        for p in target_paths:
            for username in USERNAME_TESTS + ["IDP{test123}"]:
                url = urljoin(base_url, p.lstrip("/"))
                print(f"\n[username test] {url} username={username} UA={ua}")
                try:
                    r = session.get(url, headers={"User-Agent": ua}, params={"username": username}, timeout=TIMEOUT)
                except Exception as e:
                    print("  ERR", e)
                    continue
                print(f"  -> {r.status_code} ({len(r.content)} bytes)")
                log_lines.append(f"username_test {url} {username} {r.status_code} {len(r.content)}")
                found = analyze_bytes_for_flag(r.content, f"{url}?username={username}")
                if found:
                    overall_found.extend(found)

    # 3) Download all images found on root page (using UA_DEFAULT)
    print("\n--- Downloading images from root page (using primary UA) ---")
    try:
        rroot = session.get(base_url, headers={"User-Agent": UA_DEFAULT}, timeout=TIMEOUT)
    except Exception as e:
        print("Failed to fetch root page:", e)
        rroot = None
    if rroot and rroot.status_code == 200:
        imgs = extract_image_urls_from_html(base_url, rroot.content)
        print("Images discovered:", len(imgs))
        for u in imgs:
            print(" Downloading:", u)
            out_path, status = download_image(session, u, UA_DEFAULT, IMG_DIR)
            print("  ->", status, out_path or "")
            if out_path:
                with open(out_path, "rb") as f:
                    data = f.read()
                # search for flags inside image bytes
                found = analyze_bytes_for_flag(data, out_path)
                if found:
                    overall_found.extend(found)
                # also dump some printable strings around 'IDP' if present
                # and save hex/snippet if needed (not printing to keep console clean)
    else:
        print("No root content to scan images from.")

    # 4) Brute /.git/HEAD etc already attempted above; additionally try robots/sitemap
    print("\n--- Quick check for common sensitive files ---")
    for p in ["/robots.txt", "/sitemap.xml", "/.env", "/.git/config", "/backup.zip"]:
        url = urljoin(base_url, p.lstrip("/"))
        try:
            r = session.get(url, headers={"User-Agent": UA_DEFAULT}, timeout=TIMEOUT)
        except Exception as e:
            print(url, "ERR", e)
            continue
        print(url, "->", r.status_code, "len", len(r.content))
        if r.status_code == 200:
            analyze_bytes_for_flag(r.content, url)

    # 5) Save log
    log_path = os.path.join(OUT_DIR, "scan_log.txt")
    with open(log_path, "w", encoding="utf-8", errors="replace") as f:
        f.write("\n".join(log_lines))
    print("\nLog saved to", log_path)

    if overall_found:
        print_result("OVERALL FLAG(S) FOUND", "\n".join(overall_found))
    else:
        print("\nNo IDP{...} matches found automatically. Review saved files in", IMG_DIR, "and", log_path)
        print("If nothing found, try:")
        print(" - Use exact User-Agent string for requests (already attempted).")
        print(" - Manually run binwalk / zsteg / exiftool on downloaded images.")
        print(" - Inspect HTML saved at", os.path.join(OUT_DIR, "agents_root.html"))

    # save root HTML for manual inspection
    try:
        with open(os.path.join(OUT_DIR, "agents_root.html"), "wb") as f:
            if rroot:
                f.write(rroot.content)
    except Exception:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enumerate CTF 'Agentes' site for flags (IDP{...})")
    parser.add_argument("--url", "-u", default=BASE_URL, help="Base URL (default from script)")
    args = parser.parse_args()
    main(args.url)

