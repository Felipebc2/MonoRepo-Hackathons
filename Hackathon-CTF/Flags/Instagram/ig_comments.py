# ig_collect_comments.py
# Requisitos:
#   pip install playwright
#   python -m playwright install chromium
#
# Uso:
#   python ig_collect_comments.py
#   -> abrirá Chromium; faça login se necessário e depois aperte ENTER no terminal.

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from pathlib import Path
import time, re, json, csv, os, sys
import unicodedata

PROFILE = "https://www.instagram.com/sejaidps/"
USER_DATA_DIR = str(Path.home() / ".cache" / "ig_pw")
OUTPUT_CSV = Path("comments_all.csv")
OUTPUT_DIR = Path("comments_json"); OUTPUT_DIR.mkdir(exist_ok=True)
PROCESSED_PATH = Path("processed_urls.txt")
SEARCH_WORD = "Parabéns"

# parâmetros de controle (reduza para menos agressivo se receber bloqueio)
MAX_SCROLLS = 120          # quantos scrolls ao coletar links
MAX_POSTS = 1000           # quantos posts processar (ajuste conforme necessidade)
WAIT_SCROLL_MS = 300       # ms entre scrolls
GOTO_TIMEOUT = 5000       # ms timeout pra abrir post
CLICK_RETRY = 3
LOAD_MORE_LIMIT = 200      # evita loop infinito — máximo de cliques "load more" por post
DELAY_AFTER_LOAD = 600     # ms depois de carregar mais comentário
HEADLESS = False           # coloque True para rodar sem UI (mais estável)

# helpers
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def save_json_for_post(post_url, data):
    safe = post_url.rstrip("/").split("/")[-1]
    out = OUTPUT_DIR / f"{safe}.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_processed(url):
    with PROCESSED_PATH.open("a", encoding="utf-8") as f:
        f.write(url + "\n")

def load_processed():
    if PROCESSED_PATH.exists():
        return {l.strip() for l in PROCESSED_PATH.read_text(encoding="utf-8").splitlines() if l.strip()}
    return set()

def collect_post_links(page, want_max):
    log("Coletando links do grid do perfil...")
    links = []
    seen = set()
    last_h = 0
    for i in range(1, MAX_SCROLLS + 1):
        anchors = page.locator('a[href*="/p/"], a[href*="/reel/"]').all()
        got = 0
        for a in anchors:
            try:
                href = a.get_attribute("href") or ""
                if href.startswith("/"):
                    href = "https://www.instagram.com" + href
                if ("/p/" in href or "/reel/" in href) and href not in seen:
                    seen.add(href); links.append(href); got += 1
            except Exception:
                pass
        log(f"scroll {i}/{MAX_SCROLLS} — novos: {got} | total: {len(links)}")
        if len(links) >= want_max:
            break
        page.keyboard.press("End")
        page.wait_for_timeout(WAIT_SCROLL_MS)
        try:
            h = page.evaluate("() => document.documentElement.scrollHeight")
        except Exception:
            h = None
        if h == last_h:
            log("Altura não aumentou — fim do feed carregável.")
            break
        last_h = h
    return links[:want_max]

def expand_all_comments(page):
    """
    Tenta:
     - clicar 'Ver todos os comentários' / 'View all comments' (se existir)
     - clicar repetidamente em 'Carregar mais comentários' / 'Load more comments' até não existir ou limite
    """
    clicked_any = False
    
    # Aguardar um pouco para a página carregar
    page.wait_for_timeout(500)
    
    # Step 1: 'View all comments' button - tentar múltiplos seletores
    view_all_patterns = [
        r"ver .*coment",
        r"view .*comment",
        r"view all",
        r"ver todos",
        r"todos os comentários"
    ]
    
    for pattern in view_all_patterns:
        try:
            # Tentar por role button
            btn = page.get_by_role("button", name=re.compile(pattern, re.I)).first
            if btn.count() > 0:
                btn.click(timeout=2000)
                clicked_any = True
                page.wait_for_timeout(DELAY_AFTER_LOAD)
                break
        except Exception:
            pass
        
        # Tentar por texto também
        try:
            btn = page.get_by_text(re.compile(pattern, re.I)).first
            if btn.count() > 0:
                btn.click(timeout=2000)
                clicked_any = True
                page.wait_for_timeout(DELAY_AFTER_LOAD)
                break
        except Exception:
            pass

    # Step 2: load more comments
    load_more_clicks = 0
    for _ in range(min(LOAD_MORE_LIMIT, 50)):  # limitar para não demorar muito
        clicked = False
        load_more_patterns = [
            r"carregar .*coment",
            r"load more comment",
            r"view more comment",
            r"mais coment",
            r"ver mais",
            r"view more",
            r"mostrar mais"
        ]
        
        for p in load_more_patterns:
            try:
                btn = page.get_by_role("button", name=re.compile(p, re.I)).first
                if btn.count() > 0:
                    btn.click(timeout=3000)
                    clicked = True
                    load_more_clicks += 1
                    page.wait_for_timeout(DELAY_AFTER_LOAD)
                    break
            except Exception:
                continue
        if not clicked:
            break
    
    return clicked_any, load_more_clicks

def normalize_text(text):
    """Normaliza texto removendo acentos para comparação mais flexível"""
    if not text:
        return ""
    # Remove acentos e converte para minúsculas
    nfd = unicodedata.normalize('NFD', text.lower())
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

def extract_comments_from_article(page):
    """
    Retorna lista de dicts: {id, author, text, time_iso (se houver)}
    Tenta múltiplas estratégias para encontrar comentários e legenda.
    """
    comments = []
    try:
        # Estratégia 1: Tentar encontrar legenda do post (h1 dentro do article)
        try:
            caption_h1 = page.locator("article h1[dir='auto']").first
            if caption_h1.count() > 0:
                caption_text = caption_h1.inner_text(timeout=1000).strip()
                if caption_text and len(caption_text) > 3:
                    comments.append({
                        "author": "POST_CAPTION",
                        "text": caption_text,
                        "time": None
                    })
        except Exception:
            pass
        
        # Estratégia 2: Buscar comentários usando seletores mais específicos do Instagram
        # Instagram usa diferentes estruturas, vamos tentar várias
        comment_selectors = [
            # Estrutura moderna do Instagram
            "article ul li",
            "article div[role='dialog'] ul li",
            "article section ul li",
            # Estrutura alternativa
            "article span[dir='auto']",
            # Comentários em divs específicas
            "article div[data-testid]",
        ]
        
        seen_texts = set()  # evitar duplicatas
        
        for selector in comment_selectors:
            try:
                elements = page.locator(selector).all()
                for elem in elements:
                    try:
                        txt = elem.inner_text(timeout=300).strip()
                        if not txt or len(txt) < 3:
                            continue
                        
                        # Evitar duplicatas
                        txt_lower = txt.lower()[:100]  # primeiros 100 chars para comparação
                        if txt_lower in seen_texts:
                            continue
                        seen_texts.add(txt_lower)
                        
                        # Tentar identificar se é comentário (tem username e texto)
                        parts = [p.strip() for p in txt.split("\n") if p.strip()]
                        
                        if len(parts) >= 2:
                            # Parece ser um comentário: username + texto
                            author = parts[0]
                            comment_text = " ".join(parts[1:])
                            
                            # Filtrar textos muito curtos ou que parecem ser botões/controles
                            if len(comment_text) < 2 or comment_text.lower() in ["reply", "responder", "like", "curtir"]:
                                continue
                            
                            # Tentar pegar timestamp se existir
                            time_iso = None
                            try:
                                time_elem = elem.locator("time").first
                                if time_elem.count() > 0:
                                    time_iso = time_elem.get_attribute("datetime")
                            except Exception:
                                pass
                            
                            comments.append({
                                "author": author,
                                "text": comment_text,
                                "time": time_iso
                            })
                        elif len(parts) == 1 and len(txt) > 10:
                            # Pode ser um comentário sem quebra de linha (estrutura diferente)
                            # Verificar se não é a legenda que já pegamos
                            if "POST_CAPTION" not in [c.get("author") for c in comments] or txt not in [c.get("text") for c in comments]:
                                comments.append({
                                    "author": "UNKNOWN",
                                    "text": txt,
                                    "time": None
                                })
                    except Exception:
                        continue
            except Exception:
                continue
        
        # Estratégia 3: Buscar por spans com texto dentro de article (fallback)
        if len(comments) == 0:
            try:
                spans = page.locator("article span").all()
                for span in spans[:50]:  # limitar para não ser muito lento
                    try:
                        txt = span.inner_text(timeout=200).strip()
                        if txt and len(txt) > 5 and len(txt) < 500:  # tamanho razoável
                            # Verificar se parece ser um comentário (não é só um número ou símbolo)
                            if any(c.isalpha() for c in txt):
                                txt_lower = txt.lower()[:100]
                                if txt_lower not in seen_texts:
                                    seen_texts.add(txt_lower)
                                    comments.append({
                                        "author": "UNKNOWN",
                                        "text": txt,
                                        "time": None
                                    })
                    except Exception:
                        continue
            except Exception:
                pass
                
    except Exception as e:
        log(f"  → Erro ao extrair comentários: {e}")
        pass
    
    return comments

def safe_visit_and_collect(page, url):
    """Tenta abrir o post e coletar comentários com retry leve"""
    for attempt in range(1, 4):
        try:
            page.goto(url, wait_until="networkidle", timeout=GOTO_TIMEOUT)
            page.wait_for_timeout(1000)  # dar mais tempo para carregar
            
            # Aguardar o article aparecer
            try:
                page.wait_for_selector("article", timeout=5000)
            except Exception:
                log(f"  → Article não encontrado, tentando continuar...")
            
            # expand caption/comments and then scrape
            expand_all_comments(page)
            
            # Tentar fazer scroll na área de comentários para carregar mais
            try:
                # Procurar área de comentários e fazer scroll
                comment_area = page.locator("article ul, article section").first
                if comment_area.count() > 0:
                    for _ in range(3):  # fazer scroll 3 vezes
                        comment_area.evaluate("el => el.scrollTop += 500")
                        page.wait_for_timeout(500)
            except Exception:
                pass
            
            # wait to ensure DOM updated
            page.wait_for_timeout(1000)  # mais tempo para comentários carregarem
            
            # extract
            comments = extract_comments_from_article(page)
            return comments
        except Exception as e:
            log(f"  → Erro ao processar {url}: {e} (tentativa {attempt})")
            page.wait_for_timeout(1000)
            continue
    return []

def append_csv_rows(rows):
    header = ["post_url", "comment_id", "author", "text", "time"]
    write_header = not OUTPUT_CSV.exists()
    with OUTPUT_CSV.open("a", encoding="utf-8", newline="") as csvf:
        writer = csv.writer(csvf)
        if write_header:
            writer.writerow(header)
        for r in rows:
            writer.writerow([r.get("post_url"), r.get("comment_id"), r.get("author"), r.get("text"), r.get("time")])

# ==== EXECUÇÃO ====
with sync_playwright() as p:
    log("Inicializando Playwright Chromium...")
    ctx = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=HEADLESS, args=["--lang=pt-BR"])
    page = ctx.new_page()
    log(f"Abrindo perfil: {PROFILE}")
    page.goto(PROFILE, wait_until="domcontentloaded")

    log("Se NÃO estiver logado no Instagram nesta janela, faça o login agora.")
    try:
        input("Depois de logar (ou se já estiver logado), pressione ENTER para continuar...")
    except KeyboardInterrupt:
        log("Cancelado pelo usuário."); ctx.close(); sys.exit(1)

    # collect post links
    links = collect_post_links(page, MAX_POSTS)
    if not links:
        log("Nenhum link coletado. Verifique perfil/permissões.")
        ctx.close(); sys.exit(0)
    log(f"Coletados {len(links)} links (limit {MAX_POSTS}).")

    done = load_processed()
    if done:
        log(f"Retomando — {len(done)} posts já processados.")
        links = [u for u in links if u not in done]
        log(f"{len(links)} posts restantes para processar.")

    total_comments = 0
    for idx, post_url in enumerate(links, 1):
        log(f"[{idx}/{len(links)}] Processando: {post_url}")
        comments = safe_visit_and_collect(page, post_url)
        
        # Debug: se não encontrou comentários, salvar HTML para análise
        if len(comments) == 0:
            try:
                debug_dir = OUTPUT_DIR / "debug_html"
                debug_dir.mkdir(exist_ok=True)
                safe_name = post_url.rstrip("/").split("/")[-1]
                html_path = debug_dir / f"{safe_name}.html"
                html_path.write_text(page.content(), encoding="utf-8")
                log(f"  → DEBUG: HTML salvo em {html_path} (nenhum comentário encontrado)")
            except Exception as e:
                log(f"  → Erro ao salvar debug HTML: {e}")
        
        # salvar JSON por post (útil para auditoria)
        save_json_for_post(post_url, {"post_url": post_url, "collected": comments})
        log(f"  → Extraídos {len(comments)} comentários/legendas deste post")
        
        # transformar e salvar CSV (filtrar apenas comentários que contenham a palavra procurada)
        rows = []
        search_normalized = normalize_text(SEARCH_WORD)
        for ci, c in enumerate(comments):
            comment_text = c.get("text", "")
            # busca case-insensitive com normalização: verifica se a palavra está contida no texto
            # funciona mesmo com outras palavras ou emojis ao redor (ex: "Parabéns Fulano 🎉")
            # normaliza para lidar com variações de acentos (parabens vs parabéns)
            comment_normalized = normalize_text(comment_text)
            if search_normalized not in comment_normalized:
                continue
            # criar id simples
            cid = f"{post_url.rstrip('/')}_{ci}"
            rows.append({
                "post_url": post_url,
                "comment_id": cid,
                "author": c.get("author"),
                "text": c.get("text"),
                "time": c.get("time")
            })
            log(f"  → MATCH: {c.get('author')}: {comment_text[:50]}...")
        
        if rows:
            append_csv_rows(rows)
            total_comments += len(rows)
            log(f"  → Salvados {len(rows)} comentários com '{SEARCH_WORD}' deste post.")
        else:
            log(f"  → Nenhum comentário com '{SEARCH_WORD}' encontrado neste post.")
        append_processed(post_url)
        # pequeno delay entre posts para reduzir chance de bloqueio
        page.wait_for_timeout(600)

    log(f"Finalizado. Comentários totais salvos: {total_comments}")
    ctx.close()

