from huggingface_hub import snapshot_download
from huggingface_hub import login
login(token="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")
cache_dir = r'C:/Users/Administrator/Desktop/Meta'

model_dir = snapshot_download('epfl-llm/meditron-7b',cache_dir=cache_dir)