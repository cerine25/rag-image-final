# G1 data release g1-v1.2

Prebuilt data for the shared preprocessing of the RAG image-captioning study (Group G1).
Code, splits, metadata, captions, EDA and reports are in the repository; this release holds the
large binary files that are not versioned in Git.

## Test sets

- **Official test: 1,000 images** (COCO val2017), `experiments/test_1000_val2017/`.
- Legacy test: 100 images (release `g1-v1.1`), kept unchanged.
- Knowledge base: 10,000 COCO train2017 images (50,000 captions); validation: 100 images.

## Assets

| Asset | Content | Restore to |
|---|---|---|
| `g1-v1.2-embeddings.zip` | CLIP-B/32 (512-d), SigLIP-B/16 (768-d), DINOv2-S (384-d) image embeddings for KB / val / legacy test, text embeddings, SBERT embeddings | repository root |
| `g1-v1.2-faiss-indexes.zip` | FAISS flat inner-product (exact, cosine on L2-normalised vectors) and HNSW (M=32, efC=200, efS=64) indexes | repository root |
| `g1-v1.2-test1000-embeddings.zip` | Image embeddings of the official 1,000-image test, 3 encoders | repository root |
| `g1-v1.2-images-rgb.zip` (optional) | Normalised RGB images (max side 512, JPEG q95) | repository root |
| `SHA256SUMS.txt` | SHA-256 of each asset | — |

## Use

    unzip g1-v1.2-embeddings.zip -d .          # archives contain repo-relative paths
    unzip g1-v1.2-faiss-indexes.zip -d .
    unzip g1-v1.2-test1000-embeddings.zip -d .
    sha256sum -c SHA256SUMS.txt                # Windows: certutil -hashfile <file> SHA256
    python scripts/qc_test_1000.py             # the SKIP checks now run

Embeddings are L2-normalised float32. Notes on the encoder choice on the official test
are in `README.md` and in section 11.3 of `reports/phase1_technical_report.pdf`.
