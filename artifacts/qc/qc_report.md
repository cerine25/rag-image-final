# QC — g1-v1.1
**PASS** — 40 contrôles, 0 échec(s), 0 avertissement(s)

| contrôle | statut | détail |
|---|---|---|
| taille split kb | PASS | 10000 vs 10000 |
| hash des IDs kb = splits_meta | PASS |  |
| taille split val | PASS | 100 vs 100 |
| hash des IDs val = splits_meta | PASS |  |
| taille split test | PASS | 100 vs 100 |
| hash des IDs test = splits_meta | PASS |  |
| splits deux à deux disjoints | PASS |  |
| images invalides (corrompues/absentes) | PASS | 0 |
| IDs uniques dans images.csv | PASS |  |
| doublons exacts (sha256) inter/intra splits | PASS | 0 images |
| pas de NaN dans les stats pixel | PASS |  |
| KB : 5 captions / image | PASS | min=5 max=5 |
| val : 5 références / image | PASS |  |
| test : 5 références / image | PASS |  |
| caption_id uniques (KB) | PASS |  |
| ANTI-FUITE : aucune image val/test dans kb_captions | PASS |  |
| ANTI-FUITE : aucun caption_id d'éval dans la KB | PASS |  |
| captions brutes inchangées (raw != clean autorisé, raw non vide) | PASS |  |
| info : refs val identiques à une caption KB (texte) | PASS | 1.0% — normal pour des captions génériques; pas une fuite d'image |
| info : refs test identiques à une caption KB (texte) | PASS | 1.4% — normal pour des captions génériques; pas une fuite d'image |
| métadonnées pour toutes les images | PASS |  |
| attributs texte uniquement pour la KB | PASS |  |
| embeddings clip-b32/kb | PASS | shape=(10000, 512) |
| embeddings clip-b32/val | PASS | shape=(100, 512) |
| embeddings clip-b32/test | PASS | shape=(100, 512) |
| index clip-b32 : ntotal=KB et auto-retrouvabilité | PASS |  |
| embeddings siglip-b16/kb | PASS | shape=(10000, 768) |
| embeddings siglip-b16/val | PASS | shape=(100, 768) |
| embeddings siglip-b16/test | PASS | shape=(100, 768) |
| index siglip-b16 : ntotal=KB et auto-retrouvabilité | PASS |  |
| embeddings dinov2-s/kb | PASS | shape=(10000, 384) |
| embeddings dinov2-s/val | PASS | shape=(100, 384) |
| embeddings dinov2-s/test | PASS | shape=(100, 384) |
| index dinov2-s : ntotal=KB et auto-retrouvabilité | PASS |  |
| ANTI-FUITE : val jamais retrouvé pour lui-même (k=10) | PASS |  |
| info : val avec near-duplicate dans la KB | PASS | cos>=0.97: 0/100 | dHash<=4: 0 |
| ANTI-FUITE : test jamais retrouvé pour lui-même (k=10) | PASS |  |
| info : test avec near-duplicate dans la KB | PASS | cos>=0.97: 0/100 | dHash<=4: 0 |
| fumée val : NN-caption CIDEr > aléatoire | PASS | NN=0.674 random=0.024 | Jaccard classes@1=0.546 |
| fumée test : NN-caption CIDEr > aléatoire | PASS | NN=0.622 random=0.033 | Jaccard classes@1=0.506 |