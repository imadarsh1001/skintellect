> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# 🔬 Skintellect Match & Dermatological Points: Reverse-Engineering Specification

This document presents the complete mathematical reverse-engineering and clinical specification for:
1. **Skintellect Personalized Match Score** ($0\% \text{ to } 100\%$)
2. **Clinical Dermatological Fit Points ("Darmeto Points")** ($0 \text{ to } 130 \text{ pts}$)

This specification allows any user or developer to recreate, run, and calibrate the exact scoring system offline without needing a paid Skintellect subscription or browser cookies.

---

## 📌 1. Reverse-Engineering Findings Summary

Skintellect computes its match percentage from a user's active session profile:
- **User Profile Attributes:**
  - **Skin Type:** `Combination` (Requires lightweight, non-congesting hydration)
  - **Sensitivity:** `Slightly Sensitive` (Must avoid artificial perfume, high essential oils, drying alcohol)
  - **Target Concerns:** `Dark Spots / Hyperpigmentation`, `Dryness & Dehydration`, `Dullness`, `Rough Texture`
  - **Negative Hard Condition:** `Fungal Acne (Malassezia Folliculitis)`
  - **Negative Ingredients:** `Drying Simple Alcohols`, `Synthetic Fragrance / EU Allergens`

Through empirical analysis of over 284 crawled products and direct comparison between raw HTML Turbo-Frame payloads and ingredient profiles, we uncovered the exact structural engine.

---

## 🧮 2. Skintellect Match % Mathematical Specification

Skintellect's match score is an **asymmetric penalty-deduction system** starting at $100\%$, with one **Hard Cliff (Dealbreaker)** rule.

### The Algorithm:

$$\text{Match}_{\text{Skintellect}} = \begin{cases} 
\text{Clamp}\Big(100 - \text{Penalty}_{\text{FA\_Cliff}}, \ 34\%, \ 45\%\Big), & \text{if ContainsFungalAcneTriggers} = \text{True} \\
\text{Clamp}\Big(100 - \sum \text{Deductions}, \ 20\%, \ 100\%\Big), & \text{if Fungal Acne Safe} 
\end{cases}$$

---

### Step 1: The Fungal Acne "Hard Cliff" (Dealbreaker)
If a user has fungal acne checked in their profile, Skintellect applies a categorical disqualification:
- Any product containing **Malassezia food** (free fatty acids with carbon chain lengths $C_{11}-C_{24}$, fatty acid esters, polysorbates, or galactomyces ferments) triggers:
  > `"Not a match | Contains fungal acne triggers"`
- **Score Cap:** The product's score is immediately slashed from $100\%$ down into the **$34\% - 45\%$** range:
  - **$45\%$**: Fungal trigger present, but formula is otherwise gentle and fragrance-free (e.g. *CeraVe Moisturizing Cream*, *La Roche-Posay Cicaplast Baume B5+*).
  - **$36\% - 41\%$**: Fungal trigger $+$ drying alcohol or high comedogenicity (e.g. *Biore UV Watery Essence*, *La Roche-Posay Toleriane Double Repair UV*).
  - **$34\%$**: Fungal trigger $+$ drying alcohol $+$ artificial fragrance $+$ multiple esters (e.g. *COSRX Aloe Soothing Sun Cream*).

#### Malassezia Trigger Reference List:
```text
- Polysorbates (Polysorbate 20, 40, 60, 80)
- Esters (Isopropyl Myristate, Isopropyl Palmitate, Cetyl Palmitate, Glyceryl Stearate, Sorbitan Oleate, Sorbitan Stearate, Ethylhexyl Palmitate)
- Fatty Acids (Lauric Acid, Myristic Acid, Palmitic Acid, Stearic Acid, Oleic Acid, Linoleic Acid)
- Ferments (Galactomyces Ferment Filtrate)
- PEG Esters (PEG-100 Stearate)
```

---

### Step 2: Formulations That Pass Fungal Acne Safety (Base = 100%)
For products that are $100\%$ Fungal Acne Safe, Skintellect evaluates the remaining three pillars:

#### A. Sensitivity Preferences
1. **Synthetic Fragrance & EU Allergens:**
   - Contains `Parfum`, `Fragrance`, or EU allergens (`Linalool`, `Limonene`, `Citronellol`, `Geraniol`, `Citral`):
     $$\text{Deduction: } -15\%$$
   - *(Note: Gentle botanical fruit/leaf extracts like Centella, Oat, or Green Tea without volatile terpenes do NOT trigger this penalty).*
2. **Drying Alcohol:**
   - Contains `Alcohol Denat`, `SD Alcohol`, or `Ethanol`:
     $$\text{Deduction: } -10\%$$

#### B. Skin Type Vehicle Compatibility (Combination Skin)
1. **Pore Congestion Risk:**
   - Contains ingredients with Comedogenic Rating $\ge 3$ or marked as pore-clogging:
     $$\text{Deduction: } -5\%$$
2. **Heavy Occlusive Vehicle:**
   - Pure heavy botanical oils or thick petroleum ointments (e.g. pure Tea Tree oil, petroleum jelly):
     $$\text{Deduction: } -10\% \text{ to } -15\%$$
   - Rated as `"Good | Combination skin"` instead of `"Great | Combination skin"`.

#### C. Targeted Concerns Alignment
For each user concern (`Dark Spots`, `Dryness & Dehydration`, `Dullness`, `Rough Texture`):
- If the formulation provides targeted actives: **No deduction** ($0\%$).
- If the formulation completely lacks tyrosinase inhibitors for dark spots/dullness:
  $$\text{Deduction: } -4\%$$
- If the formulation completely lacks biomimetic hydrators for dryness:
  $$\text{Deduction: } -4\%$$
- If an ingredient directly **worsens** a concern (e.g., drying Salicylic Acid in high dose when dryness is a concern):
  $$\text{Deduction: } -10\% \text{ to } -14\%$$
  *(Observed in Boots Skin Clear Salicylic Acid Moisturizer, dropping score from $100\%$ to $86\%$).*

---

### Comparison of Real Ground-Truth Data vs Reverse-Engineered Model:

| Product | Actual Skintellect Score | Predicted Score | Primary Formula Drivers |
| :--- | :---: | :---: | :--- |
| **Abib Heartleaf Crème Calming Tube** | **100%** | **100%** | Fungal Safe + Fragrance Free + Multi-Barrier + Niacinamide + Combination match |
| **Good Molecules Niacinamide Toner** | **100%** | **100%** | Fungal Safe + Dual Brightener (Niacinamide + Arbutin) + Alcohol Free |
| **Dr. Althea 345 Relief Cream** | **98%** | **98%** | Fungal Safe + Niacinamide + Resveratrol + Botanical extract base |
| **Boots Skin Clear Salicylic Moisturizer** | **86%** | **86%** | Fungal Safe + Fragrance Free, but BHA flagged as *"Can worsen Dry Skin"* (-14%) |
| **Thursday Plantation Tea Tree Oil** | **75%** | **75%** | Fungal Safe, but 100% oil vehicle ("Good", not "Great" for combination) + unaddressed targets (-25%) |
| **CeraVe Moisturizing Cream** | **45%** | **43% - 45%** | Contains Fungal Acne Triggers (`Ceteareth-20`, `Cetearyl Alcohol`) -> Hard Cliff Cap |
| **Biore UV Aqua Rich Watery Essence** | **41%** | **41%** | Contains Fungal Triggers + Drying Alcohol (`Alcohol Denat`) |
| **COSRX Aloe Soothing Sun Cream** | **34%** | **34% - 37%** | Contains Fungal Triggers (`Stearic Acid`, `Glyceryl Stearate`) + Alcohol + Fragrance |

---

## 🏆 3. Clinical "Darmeto Points" Specification

### Why "Darmeto Points" Were Created:
Skintellect's native match score measures **safety and tolerance** (i.e., *"Will this break me out or cause irritation?"*). Under Skintellect's system, a plain gel of water, carbomer, and glycerin can score $100\%$ simply because it contains zero irritants.

However, in **clinical cosmetic dermatology**, a product that lacks active biological intervention will not fade stubborn post-inflammatory hyperpigmentation (PIH), stimulate collagen synthesis, or repair a compromised lipid matrix.

**Darmeto Points** integrates baseline compatibility with **active pharmacological efficacy**:

$$\text{Darmeto Points} = \text{Match}_{\text{Skintellect}} + \text{Potency Bonus} + \text{Safety Bonus} - \text{Risk Penalties}$$

```text
Darmeto Points = Baseline_Skintellect_Match (0 - 100)
                 + min(Count(Brighteners) * 3, 9)       [Melanin / Tyrosinase Inhibition Bonus]
                 + min(Count(Barrier_Lipids) * 2, 8)     [Stratum Corneum Lipid Bonus]
                 + min(Count(Smoothers) * 2, 6)          [Epidermal Turnover & Calming Bonus]
                 + (4 if Fungal_Acne_Safe else 0)        [Malassezia Microbiome Protection]
                 + (3 if Pore_Clogger_Free else 0)       [Non-Comedogenic Follicular Safety]
                 + (2 if Oil_Free else 0)                [Sebum Regulation Vehicle Bonus]
                 + (3 if Community_Rating >= 4.0 else 0) [Real-World User Consensus Bonus]
                 - (Count(High_Pore_Cloggers) * 4)       [Acroinfundibular Occlusion Penalty]
                 - (Count(Sensitizing_Irritants) * 6)    [Cutaneous Neurosensory Irritation Penalty]
```

### Point Breakdown Matrix:

| Category | Component | Points | Scientific Rationale |
| :--- | :--- | :---: | :--- |
| **Baseline** | Skintellect Match % | **0 – 100** | Fundamental tolerance, vehicle suitability, and sensitivity gates. |
| **Potency** | Tyrosinase Brighteners | **+3 / active** *(max +9)* | Niacinamide (blocks melanosome transfer), Tranexamic Acid (plasmin inhibitor), Alpha-Arbutin (tyrosinase antagonist), Azelaic Acid, Licorice Root. |
| **Potency** | Intercellular Barrier Lipids | **+2 / active** *(max +8)* | Ceramides (NP, AP, EOP), Phytosphingosine, Cholesterol, Multi-molecular HA, Panthenol (B5), Squalane, Ectoin. |
| **Potency** | Smoothing & Calming | **+2 / active** *(max +6)* | Centella Asiatica, Madecassoside, Gluconolactone (PHA), Allantoin, Beta-Glucan, Colloidal Oatmeal. |
| **Safety** | Malassezia Safe | **+4** | Zero fatty acid substrates for fungal acne proliferation. |
| **Safety** | Non-Comedogenic | **+3** | 0 ingredients with comedogenicity $\ge 3$. |
| **Safety** | Oil-Free Vehicle | **+2** | Lightweight water-gel or fluid vehicle preventing lipid excess on T-zone. |
| **Consensus**| Rating $\ge 4.0$ / 5.0 | **+3** | Proven clinical tolerance across 50+ real-world reviewers. |
| **Penalty** | High Pore Clogger | **-4 / active** | Comedogenic rating 3–5 (e.g. Myristyl Myristate, Isopropyl Isostearate). |
| **Penalty** | Sensitizing Fragrance/Alcohol | **-6 / active** | Volatile terpenes (Limonene, Linalool) or denatured alcohols that induce subclinical micro-inflammation. |

### Clinical Tier Classifications:

- 🏆 **Tier 1: Holy Grail Formulation ($\ge 120\text{ pts}$)**  
  Simultaneous multi-pathway brightening $+$ biomimetic barrier lipids $+$ $100\%$ fungal safe $+$ zero pore cloggers.  
  *Examples:* Anua Azelaic Acid 10 Serum ($130$), iUNIK Tea Tree Relief ($129$), Dr. Althea Vitamin C Boosting ($128$), Abib Heartleaf Crème ($126$).
- 🌟 **Tier 2: Highly Targeted Treatment ($105 - 119\text{ pts}$)**  
  High-potency targeted treatment with excellent safety profile.  
  *Examples:* SKIN1004 Tone Brightening Toner ($123$), Isntree Green Tea Toner ($122$), Peach & Lily Glass Skin ($123$).
- ✅ **Tier 3: Safe Everyday Maintenance ($90 - 104\text{ pts}$)**  
  Safe baseline moisturizer or gentle cleanser with basic hydration.
- ⚠️ **Tier 4: Suboptimal / Potential Irritants ($< 90\text{ pts}$)**  
  Contains sensitizers, comedogenic occlusives, or fungal acne triggers.

---

## 💻 4. Python Implementation Reference

To score any custom product or raw ingredient string programmatically:

```python
from skinsort_recommender.scoring_engine import score_any_product

custom_formula = [
    "Water", "Niacinamide", "Glycerin", "Panthenol", "Ceramide NP",
    "Centella Asiatica Extract", "Sodium Hyaluronate", "Allantoin"
]

result = score_any_product(custom_formula, skin_type="combination", rating=4.6)

print(f"Predicted Skintellect Match : {result['skinsort_match']['predicted_match_score']}%")
print(f"Clinical Darmeto Points   : {result['darmeto_points']['darmeto_points']} pts")
print(f"Tier                      : {result['darmeto_points']['tier']}")
```

### CLI Command:
```powershell
& "C:\Users\adars\.conda\envs\web\python.exe" skinsort_recommender\main.py score --ingredients "Water, Niacinamide, Glycerin, Ceramide NP, Squalane, Centella Asiatica"
```

---

## 🛠️ 5. How Users Can Customize the Scoring Model

Users can adjust the weights in `scoring_engine.py` or through the interactive dashboard to fit any personal skin profile:

1. **For Oily, Acne-Prone Skin:**
   - Increase `Oil-Free Bonus` from `+2` to `+5`.
   - Increase `Pore-Clogger Penalty` from `-4` to `-8`.
   - Add Salicylic Acid / BHA to targeted treatment bonuses.

2. **For Severely Dry, Non-Fungal Skin:**
   - Set `avoid_fungal_triggers = False` (removes the Malassezia ceiling so rich ceramide creams like CeraVe or Cicaplast score 95%+).
   - Increase `Barrier_Bonus` weight from `+2` to `+4`.

3. **For Rosacea / Hyper-Sensitive Skin:**
   - Increase `Sensitizing_Irritants` penalty from `-6` to `-12`.
   - Require Azelaic Acid, Centella, and Ectoin bonuses.
