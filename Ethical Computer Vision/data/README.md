# Data Directory

This directory holds the two datasets used in The Audit lab. **Neither dataset is committed to this repository** — both must be downloaded separately due to size and licensing.

---

## Dataset 1 — HAM10000 Test Split

**Source**: Kaggle — `kmader/skin-lesion-analysis-toward-melanoma-detection`

**What you need**: The held-out test split only (~2,003 images). This is a subset of the full HAM10000 dataset.

**Download steps**:
1. Go to: https://www.kaggle.com/datasets/kmader/skin-lesion-analysis-toward-melanoma-detection
2. Download the dataset (requires a Kaggle account)
3. Extract and place files as follows:

```
data/
└── ham10000_test/
    ├── HAM10000_metadata.csv   ← from the Kaggle download
    └── images/
        ├── ISIC_0024306.jpg
        ├── ISIC_0024307.jpg
        └── ...                 ← ~2,003 test images
```

The `HAM10000_metadata.csv` file must contain at minimum the columns: `image_id`, `dx`.

Alternatively, run the provided download script:
```bash
python scripts/download_data.py --dataset ham10000
```
(Requires `kaggle` CLI configured with your API key.)

---

## Dataset 2 — African-Context Stress-Test Dataset

**Source**: Curated from Fitzpatrick17k (skin types V–VI) and SCIN dataset.

**What you need**: The ZIP file hosted on Google Drive (provided by the lab facilitator).

In the notebook, ACT 1 includes a cell that downloads and extracts this automatically using `gdown`. You only need to update `DRIVE_DATASET_ID` in the configuration cell if the file ID has changed.

The extracted structure will be:
```
data/
└── african_context/
    ├── african_context_labels.csv   ← image_id, dx, fitzpatrick_type
    └── images/
        ├── ISIC_XXXXXXX.jpg
        └── ...                      ← 60–80 images
```

---

## License

- HAM10000: CC BY-NC-SA 4.0 — non-commercial use only
- Fitzpatrick17k: See https://github.com/mattgroh/fitzpatrick17k for terms
- SCIN: See Google Research terms of use
