"""
Skintellect Studio - End-to-End API Test Suite
Uses standard library urllib (no external test client dependencies required).
Tests all core catalog, multi-domain taxonomy (Skin, Hair, Body, Makeup),
and ingredient explorer endpoints.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("SKINTELLECT_TEST_BASE_URL", "http://127.0.0.1:8000")


def http_get(path: str, timeout: float = 10.0):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "Skintellect-TestSuite/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        status = resp.status
        try:
            data = json.loads(body)
        except Exception:
            data = body
        return status, data


def http_post(path: str, json_data: dict, timeout: float = 10.0):
    url = f"{BASE_URL}{path}"
    payload = json.dumps(json_data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Skintellect-TestSuite/2.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        status = resp.status
        try:
            data = json.loads(body)
        except Exception:
            data = body
        return status, data


def wait_for_server(max_retries: int = 15, delay: float = 1.0):
    print(f"Waiting for server at {BASE_URL} to become ready...")
    for i in range(max_retries):
        try:
            status, _ = http_get("/api/stats", timeout=2.0)
            if status == 200:
                print(f"[OK] Server is up and responding (attempt {i + 1})")
                return True
        except Exception:
            time.sleep(delay)
    return False


def run_tests():
    if not wait_for_server():
        print(f"[FAIL] Could not connect to server at {BASE_URL}. Ensure it is running.")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("  RUNNING SKINTELLECT STUDIO VERIFICATION SUITE")
    print("=" * 65)

    # 1. HTML Shell
    print("1. Testing GET / (HTML Shell)")
    status, html = http_get("/")
    assert status == 200, f"Expected 200, got {status}"
    assert "Skintellect Studio" in html, "HTML shell missing title"
    print("   [PASS] HTML shell served successfully (200 OK)")

    # 2. Stats
    print("2. Testing GET /api/stats")
    status, stats = http_get("/api/stats")
    assert status == 200, f"Expected 200, got {status}"
    print(f"   [PASS] Catalog stats: {stats['total_products']} products, {stats['total_reviews']} reviews")

    # 3. Personas
    print("3. Testing GET /api/personas")
    status, personas = http_get("/api/personas")
    assert status == 200, f"Expected 200, got {status}"
    uap = next((p for p in personas if p["username"] == "uap"), None)
    assert uap is not None, "Persona uap not found!"
    print(f"   [PASS] Active default persona: @{uap['username']} ({uap['label']})")

    # 4. Multi-Domain Taxonomy
    print("4. Testing GET /api/domains & /api/sources")
    status, dom_res = http_get("/api/domains")
    assert status == 200, f"Expected 200, got {status}"
    domain_ids = [d["id"] for d in dom_res["domains"]]
    assert "skin" in domain_ids and "hair" in domain_ids and "body" in domain_ids and "makeup" in domain_ids
    print(f"   [PASS] Domains registered: {domain_ids}")

    status, src_res = http_get("/api/sources")
    assert status == 200, f"Expected 200, got {status}"
    source_ids = [s["id"] for s in src_res["sources"]]
    print(f"   [PASS] Data sources registered: {source_ids}")

    # 5. Products Listing across All 4 Domains (Skin, Hair, Body, Makeup)
    print("5. Testing Multi-Domain Products Filtering (Skin, Hair, Body, Makeup)")
    status, data_skin = http_get("/api/products?domain=skin&page=1&limit=6&persona_id=uap")
    assert status == 200 and len(data_skin["products"]) > 0, "No skin products"
    top_p = data_skin["products"][0]
    print(f"   [PASS] Skin Domain: {top_p['brand']} - {top_p['name']} ({top_p['match_score']}%)")

    status, data_hair = http_get("/api/products?domain=hair&page=1&limit=6&include_seeds=true")
    assert status == 200 and len(data_hair["products"]) > 0, "No hair products"
    top_h = data_hair["products"][0]
    assert top_h['is_seed'], 'Hair coverage should be labeled as demonstration data'
    print(f"   [PASS] Hair Domain: {top_h['brand']} - {top_h['name']} (Target: {top_h.get('target_area', 'scalp')})")

    status, data_body = http_get("/api/products?domain=body&page=1&limit=6&include_seeds=true")
    assert status == 200 and len(data_body["products"]) > 0, "No body products"
    top_b = data_body["products"][0]
    print(f"   [PASS] Body Domain: {top_b['brand']} - {top_b['name']} (Target: {top_b.get('target_area', 'arms_legs')})")

    status, data_mk = http_get("/api/products?domain=makeup&page=1&limit=6&include_seeds=true")
    assert status == 200 and len(data_mk["products"]) > 0, "No makeup products"
    top_m = data_mk["products"][0]
    print(f"   [PASS] Makeup Domain: {top_m['brand']} - {top_m['name']} (Target: {top_m.get('target_area', 'complexion')})")

    # 6. Product Deep Dive
    print(f"6. Testing GET /api/products/{top_p['id']} (Deep Dive)")
    status, detail = http_get(f"/api/products/{top_p['id']}?persona_id=uap")
    assert status == 200, f"Expected 200, got {status}"
    print(f"   [PASS] Product detail: {len(detail.get('ingredients', []))} ingredients, {len(detail.get('reviews', []))} reviews")

    # 7. Ingredient Explorer - List & Filters
    print("7. Testing GET /api/ingredients (1,490+ Catalog Registry)")
    status, ing_data = http_get("/api/ingredients?page=1&limit=6")
    assert status == 200, f"Expected 200, got {status}"
    assert ing_data["total"] >= 1400, f"Expected >= 1400 ingredients, got {ing_data['total']}"
    sample_ing = ing_data["ingredients"][0]
    print(f"   [PASS] Indexed ingredients: {ing_data['total']} total. Sample: {sample_ing['name']} (ID: {sample_ing['id']})")

    # 8. Ingredient Functions Meta
    print("8. Testing GET /api/ingredients/meta/functions")
    status, func_res = http_get("/api/ingredients/meta/functions")
    assert status == 200, f"Expected 200, got {status}"
    functions = func_res.get("functions", [])
    assert len(functions) > 10, f"Expected >10 functions, got {len(functions)}"
    print(f"   [PASS] Cosmetic functions cataloged: {len(functions)} functions (e.g. {functions[:4]})")

    # 9. Ingredient Deep Dive Dossier
    sample_ing_id = sample_ing["id"]
    print(f"9. Testing GET /api/ingredients/{sample_ing_id} (Dossier & Product Formulations)")
    status, ing_detail = http_get(f"/api/ingredients/{sample_ing_id}")
    assert status == 200, f"Expected 200, got {status}"
    products_count = len(ing_detail.get("products", []))
    print(f"   [PASS] Ingredient '{ing_detail['name']}' found in {products_count} catalog formulations (Sources: {ing_detail.get('sources')})")


    print("\n" + "=" * 65)
    print("  ALL MULTI-DOMAIN AND MULTI-SOURCE VERIFICATION CHECKS PASSED!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_tests()
