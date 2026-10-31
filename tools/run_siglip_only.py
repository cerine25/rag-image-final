import sys
import os
import json
import pathlib
import time

# تعيين وضع الأوففلاين لضمان عدم حدوث أي محاولات اتصال عشوائية بالهب
os.environ["HF_HUB_OFFLINE"] = "1"

print(f"sys.executable: {sys.executable}")
import torch, transformers, faiss, numpy
print(f"Versions -> torch: {torch.__version__}, transformers: {transformers.__version__}, faiss: {faiss.__version__}, numpy: {numpy.__version__}")
print(f"START_TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}")

root = pathlib.Path.cwd()
nb_path = root / "04_embeddings_index.ipynb"
nb = json.loads(nb_path.read_text(encoding="utf-8-sig"))

# الخلايا المطلوبة حسب ترتيب 0-based: 2, 4, 6, 10, 12, 14, 16, 18, 20
target_indices = [2, 4, 6, 10, 12, 14, 16, 18, 20]
namespace = {"__name__": "__main__"}

print("Extracting and executing notebook cells for SigLIP pipeline...")
for idx in target_indices:
    cell = nb["cells"][idx]
    if cell["cell_type"] == "code":
        code = "".join(cell["source"])
        print(f"--- Executing Cell {idx} ---")
        exec(code, namespace)

# تشغيل argumentos الخلية 20 للبدء بالترميز الفعلي لـ siglip-b16 مع تخطي sbert
print("Executing cell 20 main function with arguments: --encoders siglip-b16 --skip-sbert")
if "main" in namespace:
    # تعديل الـ sys.argv مؤقتاً لتمرير المعاملات المطلوبة للوظيفة الرئيسية في النوت بوك
    old_argv = sys.argv
    sys.argv = ["04_embeddings_index.ipynb", "--encoders", "siglip-b16", "--skip-sbert"]
    try:
        namespace["main"]()
    finally:
        sys.argv = old_argv

print(f"END_TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("SigLIP run pipeline completed successfully.")
