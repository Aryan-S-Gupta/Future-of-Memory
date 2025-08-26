import requests, time, os, json
from datetime import datetime

COMFY = "http://127.0.0.1:8000"
OUTPUT_DIR = "/Users/brynndu/Documents/ComfyUI/output"

# exported workflow
EXPORTED = {
    "3": {"inputs": {"seed": 807094087800881, "steps": 20, "cfg": 8,
                     "sampler_name": "euler", "scheduler": "normal", "denoise": 1,
                     "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
                     "latent_image": ["5", 0]},
          "class_type": "KSampler", "_meta": {"title": "KSampler"}},
    "4": {"inputs": {"ckpt_name": "v1-5-pruned-emaonly-fp16.safetensors"},
          "class_type": "CheckpointLoaderSimple", "_meta": {"title": "Load Checkpoint"}},
    "5": {"inputs": {"width": 512, "height": 512, "batch_size": 1},
          "class_type": "EmptyLatentImage", "_meta": {"title": "Empty Latent Image"}},
    "6": {"inputs": {"text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
                     "clip": ["4", 1]},
          "class_type": "CLIPTextEncode", "_meta": {"title": "CLIP Text Encode (Prompt)"}},
    "7": {"inputs": {"text": "text, watermark", "clip": ["4", 1]},
          "class_type": "CLIPTextEncode", "_meta": {"title": "CLIP Text Encode (Prompt)"}},
    "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]},
          "class_type": "VAEDecode", "_meta": {"title": "VAE Decode"}},
    "9": {"inputs": {"filename_prefix": "ComfyUI", "images": ["8", 0]},
          "class_type": "SaveImage", "_meta": {"title": "Save Image"}}
}

def run(description: str, timeout_s=600):
    wf = json.loads(json.dumps(EXPORTED))  # deep copy
    wf["6"]["inputs"]["text"] = description # llm world description

    # unique prefix for easy detection "py_20250817_204230_00001_"
    prefix = datetime.now().strftime("py_%Y%m%d_%H%M%S") 
    wf["9"]["inputs"]["filename_prefix"] = prefix

    # send request to ComfyUI
    print("Sending request to ComfyUI…")
    r = requests.post(f"{COMFY}/prompt",
                      json={"prompt": wf, "client_id": "py-script"},
                      timeout=60)
    # if failed
    if r.status_code != 200:
        print("Server said:", r.text)
        r.raise_for_status()

    # wait for output file with that prefix
    print("Generation started, waiting for output…")
    start = time.time()
    last_seen = None
    while True:

        # ComfyUI usually writes directly into OUTPUT_DIR (sometimes subfolders).
        hits = [f for f in os.listdir(OUTPUT_DIR)
                if f.endswith(".png") and f.startswith(prefix)]
        if hits:
            hits.sort(key=lambda f: os.path.getmtime(os.path.join(OUTPUT_DIR, f)))
            last_seen = hits[-1]
            full = os.path.join(OUTPUT_DIR, last_seen)
            print("Image generated:", full)
            return full

        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out waiting for files with prefix '{prefix}'")

        time.sleep(0.5)

if __name__ == "__main__":
    path = run("A very happy dog running on the grass.")
    print("Done:", path)
