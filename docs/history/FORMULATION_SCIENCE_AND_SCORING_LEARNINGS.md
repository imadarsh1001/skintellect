> Historical record. This document describes an earlier design, experiment or release; counts, paths and provider assumptions may be outdated. Use the [current development guide](../DEVELOPMENT.md) and [source layout](../SOURCE_LAYOUT.md) for supported commands and ownership.

# Formulation Science & Algorithmic Scoring — Knowledge Base

> **Authoritative Context Document**  
> *Status: Active Living Standard (Clinical Formulation Ground Truth for Future AI Sessions)*  
> *Last Updated: October 2026*

---

## 1. Overview & Dermatological Objectives

Cosmetic formulation evaluation requires balancing biochemical efficacy against clinical irritation risks. This document encapsulates the exact mathematical rules, clinical thresholds, and chemical mechanisms reverse-engineered and implemented in **Formulation Studio**.

---

## 2. Reverse-Engineered Skintellect Match % Algorithm

Skintellect's personalized match percentage ($0\% - 100\%$) is not a simple keyword count; it is a **rule-based multi-tier penalty model** designed to prioritize safety and active targeting.

### A. The Baseline
Every product formulation begins with a baseline score:
$$\text{Base Score} = 100\%$$

### B. The Malassezia / Fungal Acne Cliff (Hard Ceiling)
For users with a fungal acne condition or avoidance profile, detecting any Malassezia yeast food trigger enforces a non-negotiable hard ceiling:
* **Biological Mechanism**: *Malassezia furfur* and *Malassezia globosa* lack fatty acid synthase enzymes and rely on exogenous fatty acids with carbon chain lengths between $\text{C}_{11}$ and $\text{C}_{24}$ (including their esters and polysorbates) to proliferate, causing pityrosporum folliculitis.
* **Algorithmic Rule**:
  $$\text{Penalty} = \min(55 + 2 \times N_{\text{fa}}, 66)\%$$
  $$\text{Capped Score} = \max(34, 100 - \text{Penalty})\%$$
  *Result*: Score immediately plummets into the **$34\% - 45\%$ range**, classifying the product as "Not a match" regardless of how many beneficial actives it contains.

### C. Sensitivity & Irritation Deductions
Applied progressively when the formulation conflicts with user sensitivities:
* **Artificial Fragrance / EU Allergens**: $-15\%$  
  *(Flagged: `fragrance`, `parfum`, `linalool`, `limonene`, `geraniol`, `citronellol`, `citral`)*
* **Drying Alcohols**: $-10\%$  
  *(Flagged: `alcohol denat`, `sd alcohol`, `isopropyl alcohol`)*
* **High-Comedogenic Pore Cloggers** (for Combination/Oily skin): $-5\%$  
  *(Flagged: `isopropyl myristate`, `ethylhexyl palmitate`, `cetearyl alcohol + ceteareth-20`, `coconut oil`)*

### D. Concern Alignment Rewards & Deductions
Evaluates whether the product supplies biological actives to address targeted concerns:
* **Dark Spots & Dullness**: If targeted concern is active and product contains $0$ tyrosinase inhibitors: $-4\%$.
* **Dryness & Dehydration**: If targeted concern is active and product contains $0$ intercellular barrier lipids or hydrators: $-4\%$.
* **Drying Ingredient Conflict**: If product contains exfoliating acids (`salicylic acid`) without barrier lipid compensation ($\le 1$ barrier active): $-6\%$.

$$\text{Final Match Score} = \max(20, \min(100, \text{Calculated Score}))$$

---

## 3. Clinical Fit ("Darmeto Points") Score Framework

While the Skintellect Match Score operates defensively (avoiding triggers), **Darmeto Points ($0 - 130+$ pts)** measures **active formulation excellence, clinical potency, and dermatological synergy**.

### A. Mathematical Derivation
$$\text{Darmeto Points} = \text{Baseline Match Score} + \text{Bonuses} - \text{Penalties}$$

#### 1. Potency Actives Bonuses
* **Active Tyrosinase Brighteners**: $+3$ pts each, capped at $+9$ pts max.  
  *(Niacinamide, Tranexamic Acid, Alpha-Arbutin, Ascorbic Acid, Licorice Root, Azelaic Acid, Glutathione)*
* **Biomimetic Barrier Lipids & Hydrators**: $+2$ pts each, capped at $+8$ pts max.  
  *(Ceramide NP/AP/EOP, Cholesterol, Squalane, Hyaluronic Acid, Panthenol, Centella Asiatica, Allantoin, Glycerin)*
* **Gentle Texture Smoothers**: $+2$ pts each, capped at $+6$ pts max.  
  *(Gluconolactone PHA, Galactomyces, Zinc PCA, Colloidal Oatmeal, Betaine Salicylate)*

#### 2. Clean Vehicle & Safety Bonuses
* **$100\%$ Malassezia Safe**: $+4$ pts
* **$100\%$ Non-Comedogenic (0 Cloggers)**: $+3$ pts
* **Oil-Free Vehicle (Optimal for T-Zone)**: $+2$ pts
* **High Community Consensus** ($\text{Rating} \ge 4.0/5.0$): $+3$ pts

#### 3. Risk Deductions
* **Pore Clogger Penalty**: $-4$ pts per flagged high-comedogenic ingredient.
* **Sensitizing Fragrance / Essential Oil Penalty**: $-6$ pts per flagged irritant.

### B. Clinical Tier Benchmark Scale
$$\text{Score} \ge 120 \implies \text{🏆 Tier 1: Holy Grail Formulation}$$
$$105 \le \text{Score} < 120 \implies \text{🌟 Tier 2: Highly Targeted Treatment}$$
$$90 \le \text{Score} < 105 \implies \text{✅ Tier 3: Safe Everyday Base}$$
$$\text{Score} < 90 \implies \text{⚠️ Tier 4: Suboptimal / Potential Irritants}$$

---

## 4. 5-Step Routine Conflict & Synergy Matrix

Formulation Studio’s routine validator evaluates simultaneous chemical applications across Cleanse, Tone, Treat, Moisturize, and Protect:

| Combination | Mechanism / Hazard | Clinical Recommendation |
| :--- | :--- | :--- |
| **Retinoids + Direct AHA/BHA** | Multi-pathway cellular turnover without stratum corneum recovery; severe barrier degradation. | **Conflict**: Alternate nights (e.g. BHA on Monday/Wednesday, Retinol on Tuesday/Thursday). |
| **Pure L-Ascorbic Acid + Direct Acids** | Low pH stacking ($\text{pH} < 3.5$); causes stinging, erythema, and acid burns in sensitive phenotypes. | **Conflict**: Apply Vitamin C in AM, Direct Acids in PM. |
| **Copper Peptides + Low pH Acids** | Low pH hydrolyzes and chelates copper ions, denaturing peptide signal activity. | **Conflict**: Separate by routine step or time of day. |
| **Benzoyl Peroxide + Pure Retinol** | Benzoyl peroxide oxidizes retinol molecules into inactive retinoic fragments. | **Conflict**: Use Benzoyl Peroxide in AM/Wash, Retinol in PM. |
| **Ceramides + Cholesterol + Squalane** | **Biomimetic 1:3:1 Equimolar Ratio**: Accelerates natural stratum corneum lipid lamellae recovery. | **Synergy**: Optimal barrier restoration. |
| **Niacinamide + Salicylic Acid (BHA)** | BHA clears follicular lipid debris; Niacinamide regulates sebum excretion and reduces pore dilation. | **Synergy**: Complementary dual pore therapy. |

---

## 5. Multi-Domain & Cross-Body Dermatology

### A. 💇 Hair & Scalp Care (Trichology)
* **Scalp as an Extension of Facial Skin**: The scalp possesses the highest density of sebaceous glands and hair follicles on the human body.
* **Sulfate System**: Harsh anionic surfactants (Sodium Lauryl Sulfate - SLS) strip the scalp barrier, triggering compensatory reactive seborrhea. Mild amphoteric surfactants (Sodium Lauroyl Methyl Isethionate, Cocamidopropyl Hydroxysultaine) clean without disruption.
* **Curly Girl Method (CGM)**: Excludes non-water-soluble silicones (Dimethicone) that cause hydrophobic polymer accumulation on hair cuticles, requiring harsh sulfates to remove.
* **Dandruff Antifungals**: 1% Ketoconazole or Zinc Pyrithione inhibit Malassezia yeast proliferation on the scalp.

### B. 🧼 Bath & Body Care
* **Keratosis Pilaris (KP)**: Caused by follicular hyperkeratinization where keratin forms hard plugs in hair follicles on arms and thighs. Requires dual keratolytic therapy:
  - **Urea ($10\% - 20\%$)**: Disrupts hydrogen bonds in keratin and acts as an intensive humectant.
  - **Lactic Acid ($10\% - 12\%$) / Salicylic Acid ($2\%$)**: Exfoliates within the pore and on the cutaneous surface.
* **Body Acne (Bacne)**: Back skin is thicker and possesses deeper follicles than facial skin. Responds to $10\%$ Benzoyl Peroxide wash or leave-on $2\%$ BHA spray.

### C. 💄 Makeup & Complexion Care
* **Non-Acnegenic Cosmetics**: Complexion products must balance long-wear film formers (Silicone elastomers, Acrylates) with zero comedogenic oils (Coconut Oil, Cocoa Butter, Isopropyl Isostearate).
* **Mineral Oxides**: Purity-tested Titanium Dioxide and Iron Oxides provide inert, hypoallergenic color and broad-spectrum visible light (HEV) protection.
