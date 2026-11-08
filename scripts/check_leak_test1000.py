import json

def ids_from(obj):
    if isinstance(obj, list):
        out = set()
        for x in obj:
            out.add(str(x["image_id"]) if isinstance(x, dict) and "image_id" in x else str(x))
        return out
    if isinstance(obj, dict):
        for key in ("image_ids", "ids", "test", "test_ids", "images"):
            if key in obj:
                return ids_from(obj[key])
        return {str(k) for k in obj.keys()}
    return set()

new_raw = json.load(open("experiments/test_1000_val2017/splits/test_1000.json"))
print("Cles du split 1000 :", list(new_raw.keys())[:10])

new = ids_from(new_raw)
kb = ids_from(json.load(open("artifacts/splits/kb.json")))
val = ids_from(json.load(open("artifacts/splits/val.json")))
old = ids_from(json.load(open("artifacts/splits/test.json")))

print("Taille test 1000  :", len(new))
print("Taille KB         :", len(kb))
print("Taille val        :", len(val))
print("Taille ancien test:", len(old))
print("test1000 inter KB     :", len(new & kb))
print("test1000 inter val    :", len(new & val))
print("test1000 inter ancien :", len(new & old))

kb_caps = set()
for line in open("artifacts/tables/kb_captions.jsonl", encoding="utf-8"):
    r = json.loads(line)
    for k in ("caption", "raw_caption", "text"):
        if k in r:
            kb_caps.add(str(r[k]).strip().lower())

test_caps = set()
for line in open("experiments/test_1000_val2017/tables/eval_refs_test_1000.jsonl", encoding="utf-8"):
    r = json.loads(line)
    refs = r.get("references") or r.get("captions") or r.get("refs") or []
    for c in refs:
        test_caps.add(str(c).strip().lower())

print("Captions test identiques a des captions KB :", len(test_caps & kb_caps))
