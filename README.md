# G1 — Shared preprocessing release `g1-v1.1` (RAG captioning, MS COCO)

A reproducible pipeline that produces the **frozen release** (splits,
normalized images, captions, metadata, embeddings, FAISS indexes, EDA, QC) that
all groups can load with a single class (`rag_data.Release`).

## Release g1-v1.1

The frozen release uses **SigLIP (`siglip-b16`) as its primary encoder**, with
CLIP ViT-B/32 and DINOv2-small also available. It contains 10,000 KB images,
100 validation images, and 100 test images. The 100-image test size is
documented in [`reports/split_confirmation.json`](reports/split_confirmation.json).
Other-group schema, loading, index, and limitation details are in
[`docs/DATASET_CARD.md`](docs/DATASET_CARD.md); preprocessing details are in
[`docs/preprocessing.md`](docs/preprocessing.md).

## Reproduce the pipeline

```bash
pip install -r requirements.txt
jupyter lab
```

For a new dataset build, run notebook stages in this order:
`00_download_annotations` → `01_make_splits` → `01b_download_images` →
`02_preprocess_images` → `02b_dedup_repair` (when it reports changes, repeat
download/preprocess/repair until no further repair is needed) →
`03_captions_metadata` → `04_embeddings_index` → `05_eda` →
`06_select_config` → `07_qc_leakage` → `08_freeze` → `09_demo_retrieval`.
`03b_detect_objects` is optional and supplies predicted object detections for
realistic query metadata. `06_select_config` selects using validation data;
the test split is report-only and must not be used for selection.

The complete pipeline can also be run with `python tools/run_notebooks.py`.
For the already frozen `g1-v1.1` release, do not rerun artifact-producing
notebooks in place.

Test without network access or a GPU (synthetic mini-COCO + fake encoder):
```bash
python tools/make_fake_coco.py
python tools/run_notebooks.py --config config_test.yaml --skip 00_download
```
In Jupyter/Colab: set `CONFIG = "config_test.yaml"` in the 1st cell (or set
the `RAG_CONFIG` environment variable).
The delivered notebooks contain the **outputs from the most recent run**;
shared helpers are in `common.py`, `visual.py`, and `rag_data.py` (keep them in
the same folder).

| notebook | purpose |
|---|---|
| `00_download_annotations` | COCO annotations (241 MB) |
| `01_make_splits` | stratified, frozen, hashed splits + anti-leakage assertions |
| `01b_download_images` | **only** the ~10 200 images in the splits (not the 18 GB) — run AFTER `01` |
| `02_preprocess_images` | audit (corrupt/missing/duplicates), EXIF, RGB, aspect-ratio-preserving resize, dHash, pixel statistics |
| `02b_dedup_repair` | removes and replaces any KB image identical or nearly identical to a val/test image (leakage); if repairs are made, rerun `01b` -> `02` -> `02b` until there is “nothing to repair” |
| `03_captions_metadata` | raw and cleaned captions, objects, sizes, object colors, spatial relations, context |
| `03b_detect_objects` | *(optional)* DETR detections for query metadata **without an oracle** |
| `04_embeddings_index` | image/text embeddings (CLIP, SigLIP, DINOv2, SBERT), exact FAISS + HNSW indexes |
| `05_eda` | all statistical exploration required by §4.3 (11 figures, including color and shape + `stats.json` + `EDA_REPORT.md`) |
| `06_select_config` | selects the best preprocessing configuration on **val** (CIDEr, 10-fold CV, 95% CI, Wilcoxon) |
| `07_qc_leakage` | 40 checks, including leakage audit and a retrieval smoke test |
| `08_freeze` | SHA-256 manifest, read-only files, shareable archive + integrity verification |
| `09_demo_retrieval` | demo: query → top-5 images/captions, anti-leakage guard, CIDEr baseline |

Each notebook follows this structure: explanation (docstring) → one cell per
function → “Run step” cell → “Results” cells (tables/figures).

## Verified SigLIP and release execution

The SigLIP-only extraction was run with
`.\.venv\Scripts\python.exe tools\run_siglip_only.py`. That runner executes the
definition/setup cells from `04_embeddings_index.ipynb`, then calls the
notebook's `main()` once with `--encoders siglip-b16 --skip-sbert`. It writes
the encoder outputs and index report, so it is **not** a dry-run command.

QC was run with
`.\.venv\Scripts\python.exe tools\run_qc_only.py`; the runner extracts the QC
notebook's required cells and invokes its `main()`. The frozen report records
40 passing checks, no failures, and no warnings; the full check details are in
[`reports/leakage_audit.md`](reports/leakage_audit.md).

Freeze was run with
`.\.venv\Scripts\python.exe tools\run_freeze_only.py`, followed by
`.\.venv\Scripts\python.exe tools\run_freeze_only.py --verify`. The manifest
hashes the release files and freeze marks files under `artifacts/` read-only.
**Do not run an artifact-writing step against this frozen directory.** Build a
new release in a separate working copy when changing data or embeddings.

## Design choices (what makes this release defensible)

1. **Anti-leakage by construction, not only by verification.** Captions are in
   separate files: `kb_captions.jsonl` (the only KB caption file a retriever
   loads) vs `eval_refs_{val,test}.jsonl` (references, never indexed).
   `Release.search_images(..., query_ids=...)` raises an error if an image
   retrieves itself.
2. **Disjointness guaranteed by sampling order**: test (val2017) → val
   (train2017) → KB (train2017 excluding val), with assertions.
3. **Genuinely stratified evaluation samples** (per specification: simple and
   complex scenes, interactions, varied contexts): greedy coverage of 80
   classes, complexity quotas of 25/30/30/15 %, ≥ 30 % images with interactions,
   and indoor/outdoor/mixed rotation. The **KB** retains the natural COCO
   distribution with a floor of 60 images per class (retrieval should reflect
   real data).
4. **Leakage-free metadata**: no val/test metadata is derived from captions;
   text-derived attributes exist only for the KB. Objects come from COCO
   annotations (**oracle**) → use `03b_detect_objects` for realistic queries
   (required for G28-G30).
5. **Reproducibility**: one seed, everything controlled by `config.yaml`, and
   reruns produce byte-identical files (except computation times in
   `index_report.json`); versions are logged.
6. **Documented preprocessing selection** (`audit/preproc_config_selection.json`)
   with statistical tests—the report notes that with 100 images, differences
   between encoders may not be statistically significant.
7. **Complete audit**: `audit/image_audit.json` (corrupt images, EXIF
   corrections, grayscale→RGB conversion, exact duplicates, val/test↔KB
   near-duplicates) and `qc/qc_report.md`.

## Contents of `artifacts/`

```
splits/{kb,val,test}.json, splits_meta.json   IDs + strata + SHA-256 hashes of ID lists
images_rgb/<split>/<id>.jpg                   RGB, EXIF-corrected, max side 512 (aspect ratio preserved)
tables/images.csv                             1 row/image: dimensions, hash, brightness, colors, sharpness, status
tables/kb_captions.jsonl                      caption_raw + caption_clean + n_tokens (KB only)
tables/eval_refs_{val,test}.jsonl             raw references (evaluation only)
tables/metadata.jsonl                         objects, sizes, per-object colors, relations, context, day/night
embeddings/<enc>/{kb,val,test}_img.npy        L2-normalized float32; ids_*.npy = row order; kb_txt.npy (CLIP/SigLIP)
index/<enc>_flatip.faiss, _hnsw.faiss, _txt_flatip.faiss (CLIP/SigLIP), index_report.json
eda/ , qc/ , audit/ , manifest.json
```

## Usage by other groups

```python
from rag_data import Release
R = Release()  # primary encoder from config.yaml: siglip-b16
Q = R.image_embeddings("test"); ids = R.ids("test")
scores, kb_ids = R.search_images(Q, k=5, query_ids=ids)       # top-5 KB images (cosine)
caps = R.kb_captions_of(kb_ids[0, 0])                         # raw captions for the first retrieved image
refs = R.eval_refs("test")                                    # {image_id: [5 captions]} — evaluation only
```

Index type, dimension, metric, size, and build-time documentation required by
the specification: `index/index_report.json`.

## Split decisions

- **Test size: 100 images** (§4.1 and §4.2 of the specification, val2017).
  Sections §4.4.2-4.4.3 mention 1 000; 100 was confirmed by the professor and
  documented in `reports/split_confirmation.json`.
- **Validation: 100 images sampled from train2017** (§4.1), counted separately
  in the §4.4.2 summary → they are taken from train2017, disjoint from the KB.
- **Images with 6-7 captions**: keep the first 5 by `caption_id`.
- **Images without object annotations** (~1 %) are excluded (metadata cannot
  be produced); this is documented in `splits_meta.json`.

## Known limitations

- Val/test object metadata comes from COCO ground-truth annotations (an
  oracle); use `03b_detect_objects` for realistic queries without an oracle.
- SigLIP, CLIP, and DINOv2 are image encoders; CLIP and SigLIP also have text
  towers in this release. SBERT is provided as caption embeddings.
- GPU embeddings may differ by ~1e-6 depending on hardware/torch version: the
  manifest guarantees identity of the **shared** files, not bit-for-bit
  reproducibility when recalculated.
- Spatial relations are based on bounding-box geometry (not a true scene
  graph); text attributes use a color/size/material/state lexicon.
- Historical runtime versions differ: `artifacts/manifest.json` records
  Python 3.13.7 for g1-v1.1; the v1.0 manifest records Python 3.11.9.
  SigLIP's Python 3.13.7 provenance is sourced from `env.python` in the
  current manifest.
- After `08_freeze`, files in `artifacts/` are read-only. Do not unlock them to
  modify this release; prepare a new copy/version instead.

## Reports and documentation

- [`docs/DATASET_CARD.md`](docs/DATASET_CARD.md): schemas, embeddings, indexes, loading, anti-leakage.
- [`docs/preprocessing.md`](docs/preprocessing.md): image, captions, metadata, processors.
- [`reports/leakage_audit.md`](reports/leakage_audit.md): all QC checks and text matches.
- [`reports/test_stratification.md`](reports/test_stratification.md) and
  [`reports/tables/test_strata.csv`](reports/tables/test_strata.csv): sampling
  procedure and observed counts.
- `reports/tables/` and `reports/figures/`: encoder comparison results.
