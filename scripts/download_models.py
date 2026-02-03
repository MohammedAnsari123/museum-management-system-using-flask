from huggingface_hub import snapshot_download
import os

repo_id = "Qwen/Qwen1.5-1.8B-Chat"

local_dir = os.path.join(os.getcwd(), "models", "qwen_1_8b_chat")

print(f"Starting download of {repo_id}...")
print(f"Destination: {local_dir}")

try:
    snapshot_download(
        repo_id=repo_id, 
        local_dir=local_dir, 
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
    )
    print("\nSUCCESS: Model downloaded successfully!")
    print(f"Model path to use: {local_dir}")
except Exception as e:
    print(f"\nERROR: Download failed. {e}")
