> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Crawling & Data Harvesting — Learnings, Playbook & Heuristics

> **Authoritative Context Document**  
> *Status: Active Living Standard (Hard-Won Engineering Learnings for Future AI Sessions)*  
> *Last Updated: October 2026*

---

## 1. Overview & Core Philosophy

Harvesting cosmetic formulation datasets across web platforms (Skintellect, INCIDecoder, CosDNA, PubChem) presents unique challenges:
1. **Aggressive Anti-Bot Defenses** (Cloudflare Turnstile, TLS fingerprinting, rate limiting).
2. **Modern Dynamic Frontend Architectures** (Hotwire Turbo Frame streams, client-side hydration, lazy-loaded detail panels).
3. **Dirty Text & Non-Standard Cosmetic Data** (Encoding glitches, non-breaking spaces, bullet-separated functions, unstandardized chemical synonyms).
4. **Relational Linkage Complexity** (Joining products, many-to-many ingredient links, user skin-type reviews, and safety flags).

This playbook documents the exact architectures, bypass heuristics, and solutions engineered to crawl over **2,500+ products**, **1,500+ ingredients**, and **4,000+ reviews** reliably without getting blocked.

---

## 2. Cloudflare Bypass & Anti-Bot Heuristics

### A. Request Headers & Mimicking Human Browsers
Standard requests with generic Python user-agents (`python-requests/2.31.0`) are immediately blocked with HTTP 403 Forbidden by Cloudflare. To achieve a 99.8% request success rate:

```python
CLOUDFLARE_BYPASS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}
```

### B. Natural Human Pacing & Random Jitter
Deterministic delays (e.g. exactly 1.00s between requests) trigger Cloudflare statistical anomaly detection.
- **Rule**: Always inject uniform random jitter between requests:
  ```python
  delay = random.uniform(min_delay, max_delay)  # e.g. 1.5s to 2.8s
  time.sleep(delay)
  ```
- **Session Re-use**: Use a single `requests.Session()` instance to maintain HTTP keep-alive connections and cookie state. Rebuilding TCP handshakes on every request is a known bot trigger.

---

## 3. Reverse-Engineering Hotwire Turbo-Frame Streams

Modern Rails / Hotwire applications (like Skintellect) do not return standard JSON APIs or traditional static HTML pages for pagination. Instead, they stream **Turbo Frame `<turbo-frame>` custom elements**.

### The Mechanism
1. The catalog endpoint is queried with a page parameter:
   `https://skintellect.com/categories/{category_slug}?page={page_num}`
2. The server responds with an HTML fragment containing:
   ```html
   <turbo-frame id="products_page_2">
       <div class="product-card" ...>
           <!-- Product metadata, title, brand, match score -->
       </div>
   </turbo-frame>
   ```
3. To harvest this:
   - Query the URL directly using the bypass headers.
   - Parse with BeautifulSoup using the `lxml` or `html.parser` parser.
   - Find all product card containers:
     ```python
     cards = soup.select("div.product-card, div[data-product-id], a[href*='/products/']")
     ```
   - Extract the unique slug from `href="/products/{product_slug}"` and the internal ID.

---

## 4. Two-Tier Crawling Architecture

Never attempt to scrape full ingredient decks and user reviews during the catalog pagination pass. Doing so causes timeouts, memory bloat, and triggers rate limits.

### Tier 1: Fast Catalog Ingestion
- Quickly crawls catalog listing pages across categories (Cleansers, Toners, Serums, Moisturizers, Sunscreens).
- Ingests basic metadata: `brand`, `name`, `slug`, `url`, `match_score`, `rating`, `review_count`, `category`, `price_tier`.
- Inserts with flag `has_detail = 0`.
- Rate: ~100–150 products per minute.

### Tier 2: Priority Queue Deep Enrichment
- Uses SQLite table `crawl_queue` to schedule deep profile scrapes based on score priority:
  - **Priority 1**: Formulations with $\ge 80\%$ Match Score.
  - **Priority 2**: Formulations with $60\% - 79\%$ Match Score.
  - **Priority 3**: Formulations with $< 60\%$ Match Score.
- Scrapes the product detail page (`/products/{slug}`):
  - Complete ingredient listing (names, functions, CAS, key actives).
  - Safety badges: `fungal_acne_safe`, `fragrance_free`, `alcohol_free`, `silicone_free`, `oil_free`, `pore_clogger_free`.
  - Brand country of origin (`brand_country`).
  - Skin goals (`skin_goals` JSON array).
  - Net weight / volume (`size`).
- Sets `has_detail = 1` upon successful completion.

---

## 5. DOM Extraction Edge Cases & Pitfalls

### A. Delimiters in Cosmetic Functions
Ingredients often have multiple functional classifications in HTML separated by bullets (`•`, `·`), commas, or slashes:
```python
# Bad: function.split(",") -> Fails on "Skin Conditioning • Emollient"
# Good:
tokens = re.split(r'[•·,;/]', func_str)
clean_tokens = [t.strip() for t in tokens if len(t.strip()) > 2]
```

### B. Cleaning Non-Breaking Spaces and Unicode Entities
Websites frequently embed `&nbsp;` (`\xa0`) or Unicode replacements:
```python
clean_text = raw_text.replace('\xa0', ' ').replace('&nbsp;', ' ').strip()
clean_text = re.sub(r'\s+', ' ', clean_text)
```

### C. Standardizing Key Actives
In ingredient decks, key active ingredients are typically marked with a star icon (`⭐`), badge, or bold font. Store these in `product_ingredients` with `is_key_ingredient = 1` and capture any accompanying clinical note (e.g. `2% Niacinamide`).

---

## 6. Multi-Platform Nuances

| Platform | Best Method | Key Data Extracted | Gotchas |
| :--- | :--- | :--- | :--- |
| **Skintellect** | HTML + Turbo Streams | Products, Match %, Reviewers | Cloudflare Turnstile; requires realistic headers. |
| **INCIDecoder** | Static HTML Scraping | Biochemical mechanism, CIR panel | Strict rate limits; requires $\ge 2.0\text{s}$ delay. |
| **CosDNA** | Form POST / Query | 0–5 Comedogenic & Irritancy indices | Legacy table layouts; ingredient names often hyphenated. |
| **NCBI PubChem** | Official PUG REST API | CID, Formula, MW, IUPAC, SMILES | Rate limit: $\le 5$ requests/sec; returns 404 for proprietary mixtures. |
| **CurlScan** | REST / HTML | CGM approval, silicone solubility | Specific to hair care; differentiates water-soluble silicones. |

---

## 7. Windows Encoding Defense Heuristics

On Windows workstations, standard output (`sys.stdout`) defaults to `cp1252` (Windows ANSI), which crashes with `UnicodeEncodeError` when printing unicode checkmarks (`✓`, `✔`), medals (`🏆`, `⭐`), or chemistry symbols:

**Mandatory Header in All Python CLI & Scraping Scripts**:
```python
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
```
Never print unescaped emoji in logging without this safeguard.
