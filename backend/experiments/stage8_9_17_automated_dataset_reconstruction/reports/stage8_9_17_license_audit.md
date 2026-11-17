# Stage 8.9.17 Commercial License Audit & Provenance Report

## 1. Compliance Policy & Commercial Safeguards
To support commercial-intent festival deployments, the automated acquisition pipeline enforces strict license whitelisting:
- **Permitted Licenses:** Creative Commons 0 (CC0 1.0) and Creative Commons Attribution (CC BY 2.0, 3.0, 4.0).
- **Quarantined Licenses:** All Non-Commercial (CC BY-NC, CC BY-NC-ND) and ambiguous licenses were rejected prior to ingestion and recorded in `data_acquisition_log.csv`.

## 2. Ingested License Breakdown

| License Identifier | Recording Count | Commercial Eligibility | Primary Source Datasets |
|---|---:|---|---|
| `http://creativecommons.org/licenses/by/3.0/` | 1210 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| `http://creativecommons.org/publicdomain/zero/1.0/` | 998 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| `CC-BY-4.0` | 201 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| `CC0-1.0` | 150 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| `CC0 1.0` | 139 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| `CC-BY 4.0` | 91 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| `CC0 1.0 Universal (Public Domain Dedication)` | 9 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| `http://creativecommons.org/licenses/by/4.0/` | 6 | COMMERCIALLY_ELIGIBLE | FSD50K, Stage 8.9, NIGENS, OpenSLR, Synthetic |
| **Total Corpus** | **2804** | **100% Eligible** | **Whitelisted Commercial Only** |

## 3. Attribution & Provenance Guarantee
Every row in `data/manifests/reconstructed_dataset_manifest.csv` and `source_group_splits.csv` maintains exact provenance metadata: `original_id`, `uploader/author`, `source_url`, `attribution`, `license`, and `content_hash`.
