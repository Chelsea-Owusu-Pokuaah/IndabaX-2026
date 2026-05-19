# Dataset Datasheet — HAM10000

*Human Against Machine with 10000 Training Images*

---

## Basic Information

| Field | Value |
|---|---|
| **Full name** | HAM10000 (Human Against Machine with 10000 training images) |
| **Version** | v1.0 (2018) |
| **License** | CC BY-NC-SA 4.0 (non-commercial use only) |
| **Citation** | Tschandl, P., Rosendahl, C. & Kittler, H. *The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.* Sci. Data **5**, 180161 (2018). |

---

## Collection

**Institutions involved:**
- Department of Dermatology, Medical University of Vienna, Austria
- Melanoma Institute Australia, Sydney, Australia
- Skin cancer practice in Queensland, Australia

**Collection period:** 2007–2018

**Collection method:** Dermatoscopy — a handheld device that uses polarised light to image the skin surface. Images are taken with the device pressed against the skin, typically in a controlled clinical setting. **This is not a phone camera.** Dermatoscopic images have significantly different visual characteristics from consumer smartphone photos: uniform lighting, no motion blur, no ambient background, standardised magnification.

---

## Scale

| Split | Images |
|---|---|
| Training | 10,015 |
| Test (held-out) | ~2,003 |
| **Total** | **~12,018** |

---

## Class Distribution

The dataset is **severely imbalanced**. Melanocytic nevi (benign moles) account for over two-thirds of all images.

| Class | Abbreviation | Approx. % of training set |
|---|---|---|
| Melanocytic Nevi | `nv` | ~67% |
| Melanoma | `mel` | ~11% |
| Benign Keratoses | `bkl` | ~11% |
| Basal Cell Carcinoma | `bcc` | ~5% |
| Actinic Keratoses | `akiec` | ~3% |
| Dermatofibroma | `df` | ~1% |
| Vascular Lesions | `vasc` | ~1% |

This imbalance has direct consequences: a model trained naively on this data will over-predict melanocytic nevi. The training script (`scripts/train_baseline.py`) addresses this with a **weighted random sampler**, but the imbalance also affects which classes the model learns most reliably.

---

## Demographics and Skin Type

**Patient demographics:** Not released. Age range estimated 20–85 years based on collection context. Gender not recorded in publicly available metadata.

**Fitzpatrick skin type distribution:** Not systematically recorded at the time of collection. The following is an estimate inferred from the geographic and institutional sources of the data:

| Fitzpatrick Type | Estimated % |
|---|---|
| Type I (very fair, always burns) | ~25% |
| Type II (fair, usually burns) | ~35% |
| Type III (medium, sometimes burns) | ~25% |
| Type IV (olive, rarely burns) | ~10% |
| Type V (brown, very rarely burns) | ~4% |
| Type VI (dark brown/black, never burns) | <1% |

> ⚠️ **These figures are estimates, not measurements.** The original dataset authors did not record Fitzpatrick types, and the distribution above is inferred from the known demographics of the patient populations at the three collection sites (Vienna, Sydney, Queensland). All three sites serve predominantly lighter-skinned European-heritage patients. No data was collected from Sub-Saharan Africa, South Asia, or East Africa.

---

## Annotation

**Method:** Expert dermatologist consensus. Each image was reviewed by 2–3 board-certified dermatologists. In cases of disagreement, a senior dermatologist cast the deciding classification.

**Histopathology confirmation:** Approximately 30% of images have biopsy-confirmed diagnoses. The remaining ~70% are classified by expert visual consensus only.

**Annotation limitations:** Dermatoscopic diagnosis is known to be less reliable on darker skin tones. The visual features used for melanoma detection (colour variation, asymmetry, border irregularity) present differently on darker skin, and the expert consensus was drawn from clinicians trained primarily on lighter-skinned patient populations.

---

## Known Limitations

The following limitations are relevant to any deployment decision:

1. **Geographic exclusion of Sub-Saharan Africa.** No images were collected from any institution in Africa. The dataset does not represent the skin conditions, presentation patterns, or acquisition conditions of patients in Ghana, Nigeria, Kenya, or any other African country.

2. **Dermatoscope ≠ phone camera.** The model was trained on dermatoscopic images. Deployment with smartphone cameras introduces a significant domain shift: different lighting, different focal distance, different noise characteristics, and potential motion blur. Performance on phone-acquired images is expected to be lower.

3. **Severe class imbalance.** The ~67% nevus class means that a naive classifier can achieve high accuracy by predicting nevus for everything. Overall accuracy is a misleading metric; F1 score per class is more informative.

4. **Fitzpatrick types not systematically recorded.** The dataset cannot be audited for skin-tone bias using its own metadata. Any bias analysis requires inference from geographic data or external labelling.

5. **Performance on darker skin tones not evaluated at time of publication.** The original paper (Tschandl et al., 2018) does not report sub-group performance by skin type. There is no benchmark figure for how the model performs on Fitzpatrick Type V or VI patients.

---

## Intended Use (as stated by original authors)

HAM10000 was created to support research into automated skin lesion classification. It was not designed for direct clinical deployment and does not carry any clinical certification.

---

*This datasheet was prepared for the Building Ethical Vision Systems lab, GDSS 2026.*
*It follows the Datasheets for Datasets framework (Gebru et al., 2021).*
