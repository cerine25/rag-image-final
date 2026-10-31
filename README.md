# G1 — Shared preprocessing release `g1-v1.1` (RAG captioning, MS COCO)

Pipeline reproductible qui produit la **release figée** (splits, images normalisées, captions, métadonnées, embeddings,
index FAISS, EDA, QC) que tous les groupes peuvent charger avec une seule classe (`rag_data.Release`).

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

Test sans réseau ni GPU (mini-COCO synthétique + encodeur factice) :
```bash
python tools/make_fake_coco.py
python tools/run_notebooks.py --config config_test.yaml --skip 00_download
```
Dans Jupyter/Colab : mettre `CONFIG = "config_test.yaml"` dans la 1re cellule (ou définir la variable d'environnement `RAG_CONFIG`).
Les notebooks livrés contiennent les **sorties de la dernière exécution** ; les helpers partagés sont dans `common.py`, `visual.py`, `rag_data.py` (à garder dans le même dossier).

| notebook | rôle |
|---|---|
| `00_download_annotations` | annotations COCO (241 Mo) |
| `01_make_splits` | splits stratifiés, gelés, hashés + assertions anti-fuite |
| `01b_download_images` | **seulement** les ~10 200 images des splits (pas les 18 Go) — à lancer APRÈS `01` |
| `02_preprocess_images` | audit (corrompu/manquant/doublons), EXIF, RGB, resize ratio conservé, dHash, stats pixel |
| `02b_dedup_repair` | retire de la KB toute image identique / quasi identique à une image val/test (fuite) et la remplace ; si elle répare, relancer `01b` -> `02` -> `02b` jusqu'à « rien à réparer » |
| `03_captions_metadata` | captions brutes + nettoyées, objets, tailles, couleurs d'objets, relations spatiales, contexte |
| `03b_detect_objects` | *(optionnel)* détections DETR pour des métadonnées de requête **sans oracle** |
| `04_embeddings_index` | embeddings image/texte (CLIP, SigLIP, DINOv2, SBERT), index FAISS exact + HNSW |
| `05_eda` | toute l'exploration statistique de l'énoncé §4.3 (11 figures, dont couleur et forme + `stats.json` + `EDA_REPORT.md`) |
| `06_select_config` | choix de la meilleure config de prétraitement sur **val** (CIDEr, CV 10 plis, IC95, Wilcoxon) |
| `07_qc_leakage` | 40 contrôles dont l'audit de fuite et un test de fumée du retrieval |
| `08_freeze` | manifest SHA-256, lecture seule, archive partageable + vérification d'intégrité |
| `09_demo_retrieval` | démo : requête → top-5 images/captions, garde-fou anti-fuite, baseline CIDEr |

Chaque notebook : explication (docstring) → une cellule par fonction → cellule « Lancer l'étape » → cellules « Résultats » (tableaux/figures).

## Exécution vérifiée de SigLIP et release

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

## Choix de conception (ce qui rend cette release défendable)

1. **Anti-fuite par construction, pas seulement par vérification.** Les captions sont dans des fichiers séparés :
   `kb_captions.jsonl` (seul fichier qu'un retriever charge) vs `eval_refs_{val,test}.jsonl` (références, jamais indexées).
   `Release.search_images(..., query_ids=...)` lève une erreur si une image se retrouve elle-même.
2. **Disjonction garantie par l'ordre de tirage** : test (val2017) → val (train2017) → KB (train2017 privée de val), avec assertions.
3. **Échantillons d'évaluation réellement stratifiés** (énoncé : scènes simples/complexes, interactions, contextes variés) :
   couverture gloutonne des 80 classes, quotas de complexité 25/30/30/15 %, ≥ 30 % d'images avec interaction, rotation indoor/outdoor/mixed.
   La **KB**, elle, reste à distribution naturelle COCO avec un plancher de 60 images par classe (le retrieval doit refléter les vraies données).
4. **Métadonnées sans fuite** : pour val/test, aucune métadonnée n'est dérivée des captions ; les attributs extraits du texte n'existent que pour la KB.
   Les objets viennent des annotations COCO (**oracle**) → utiliser `03b_detect_objects` pour des requêtes réalistes (obligatoire pour G28-G30).
5. **Reproductibilité** : seed unique, tout piloté par `config.yaml`, ré-exécution = fichiers identiques octet pour octet (hors temps de calcul dans `index_report.json`) ; versions logguées.
6. **Sélection du prétraitement documentée** (`audit/preproc_config_selection.json`) avec tests statistiques — avec 100 images, la différence entre encodeurs peut ne pas être significative, le rapport le dit.
7. **Audit complet** : `audit/image_audit.json` (corrompues, EXIF corrigés, gris→RGB, doublons exacts, quasi-doublons val/test↔KB), `qc/qc_report.md`.

## Contenu de `artifacts/`

```
splits/{kb,val,test}.json, splits_meta.json   IDs + strates + hash SHA-256 des listes
images_rgb/<split>/<id>.jpg                   RGB, EXIF corrigé, côté max 512 (ratio conservé)
tables/images.csv                             1 ligne/image : dims, hash, luminosité, couleurs, nettété, statut
tables/kb_captions.jsonl                      caption_raw + caption_clean + n_tokens (KB uniquement)
tables/eval_refs_{val,test}.jsonl             références brutes (évaluation uniquement)
tables/metadata.jsonl                         objets, tailles, couleur par objet, relations, contexte, jour/nuit
embeddings/<enc>/{kb,val,test}_img.npy        float32 L2-normalisés ; ids_*.npy = ordre des lignes ; kb_txt.npy (CLIP/SigLIP)
index/<enc>_flatip.faiss, _hnsw.faiss, _txt_flatip.faiss (CLIP/SigLIP), index_report.json
eda/ , qc/ , audit/ , manifest.json
```

## Utilisation par les autres groupes

```python
from rag_data import Release
R = Release()  # primary encoder from config.yaml: siglip-b16
Q = R.image_embeddings("test"); ids = R.ids("test")
scores, kb_ids = R.search_images(Q, k=5, query_ids=ids)       # top-5 images KB (cosinus)
caps = R.kb_captions_of(kb_ids[0, 0])                         # captions brutes de la 1re image retrouvée
refs = R.eval_refs("test")                                    # {image_id: [5 captions]} — évaluation seulement
```

Documentation exigée par l'énoncé (type d'index, dimension, métrique, taille, temps d'indexation) : `index/index_report.json`.

## Décisions de split

- **Taille du test : 100 images** (§4.1 et §4.2 du sujet, val2017). Le §4.4.2-4.4.3 mentionne 1 000 ; 100 a été confirmé par la professeure et documenté dans `reports/split_confirmation.json`.
- **Validation : 100 images tirées de train2017** (§4.1) mais le résumé §4.4.2 les compte à part → on les prend dans train2017, disjointes de la KB.
- **Images à 6-7 captions** : on garde les 5 premières par `caption_id`.
- **Images sans annotation d'objet** (~1 %) exclues (pas de métadonnées possibles) — documenté dans `splits_meta.json`.

## Limites connues

- Les métadonnées d'objets val/test reposent sur les annotations COCO ground truth (oracle) ; employer `03b_detect_objects` pour des requêtes réalistes sans oracle.
- SigLIP, CLIP et DINOv2 sont des encodeurs image ; CLIP et SigLIP disposent aussi d'une tour texte dans cette release. SBERT est fourni comme embeddings de captions.
- Les embeddings GPU peuvent différer de ~1e-6 selon matériel/version de torch : le manifest garantit l'identité des fichiers **partagés**, pas leur recalcul bit-à-bit.
- Relations spatiales = géométrie des boîtes (pas une vraie scene-graph) ; attributs texte = lexique couleur/taille/matière/état.
- Les versions runtime historiques diffèrent : `artifacts/manifest.json` indique Python 3.13.7 pour g1-v1.1; le manifeste v1.0 conserve Python 3.11.9. La version Python 3.13.3 citée séparément pour SigLIP n'est pas cohérente avec le manifeste courant et reste à confirmer.
- Après `08_freeze`, les fichiers d'`artifacts/` sont en lecture seule. Ne les déverrouillez pas pour modifier cette release ; préparez une nouvelle copie/version.

## Rapports et documentation

- [`docs/DATASET_CARD.md`](docs/DATASET_CARD.md): schémas, embeddings, index, chargement, anti-fuite.
- [`docs/preprocessing.md`](docs/preprocessing.md): image, captions, métadonnées, processors.
- [`reports/leakage_audit.md`](reports/leakage_audit.md): toutes les vérifications QC et les correspondances texte.
- [`reports/test_stratification.md`](reports/test_stratification.md) and
  [`reports/tables/test_strata.csv`](reports/tables/test_strata.csv): procédure
  de tirage et comptes observés.
- `reports/tables/` and `reports/figures/`: encoder-comparison results.
