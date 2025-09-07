{
  "980ebb00-073e-4393-901d-14701f2ad6f3": {
    "prompt": [0, "980ebb00-073e-4393-901d-14701f2ad6f3",
      {
        "3": {
          "inputs": {
            "seed": 49289279412421,
            "steps": 20,
            "cfg": 8,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": [
              "4",
              0],
            "positive": [
              "6",
              0],
            "negative": [
              "7",
              0],
            "latent_image": [
              "5",
              0]
          },
          "class_type": "KSampler",
          "_meta": {
            "title": "KSampler"
          }
        },
        "4": {
          "inputs": {
            "ckpt_name": "dreamshaper_7.safetensors"
          },
          "class_type": "CheckpointLoaderSimple",
          "_meta": {
            "title": "Load Checkpoint"
          }
        },
        "5": {
          "inputs": {
            "width": 512,
            "height": 512,
            "batch_size": 1
          },
          "class_type": "EmptyLatentImage",
          "_meta": {
            "title": "Empty Latent Image"
          }
        },
        "6": {
          "inputs": {
            "text": "A speculative future city where memories are traded like currency: glowing neural marketplaces, people exchanging luminous memory orbs, brain-linked kiosks pulsing with circuits, surreal architecture shaped by thought. Streets shimmer with fragments of others' pasts drifting like holograms. Faces half-formed with borrowed recollections blur into fluid identities. The scene is speculative, artistic, dreamlike—vivid yet unsettling, merging science and imagination in symbolic, painterly style.",
            "clip": [
              "4",
              1]
          },
          "class_type": "CLIPTextEncode",
          "_meta": {
            "title": "CLIP Text Encode (Prompt)"
          }
        },
        "7": {
          "inputs": {
            "text": "text, watermark",
            "clip": [
              "4",
              1]
          },
          "class_type": "CLIPTextEncode",
          "_meta": {
            "title": "CLIP Text Encode (Prompt)"
          }
        },
        "8": {
          "inputs": {
            "samples": [
              "3",
              0],
            "vae": [
              "4",
              2]
          },
          "class_type": "VAEDecode",
          "_meta": {
            "title": "VAE Decode"
          }
        },
        "9": {
          "inputs": {
            "filename_prefix": "ComfyUI",
            "images": [
              "8",
              0]
          },
          "class_type": "SaveImage",
          "_meta": {
            "title": "Save Image"
          }
        }
      },
      {
        "client_id": "76643025-b8d1-4fe8-b682-b83172e99507"
      },
      [
        "9"
      ]
    ],
    "outputs": {
      "9": {
        "images": [
          {
            "filename": "ComfyUI_00001_.png",
            "subfolder": "",
            "type": "output"
          }
        ]
      }
    },
    "status": {
      "status_str": "success",
      "completed": true,
      "messages": [
        [
          "execution_start",
          {
            "prompt_id": "980ebb00-073e-4393-901d-14701f2ad6f3",
            "timestamp": 1756354387817
          }
        ],
        [
          "execution_cached",
          {
            "nodes": [],
            "prompt_id": "980ebb00-073e-4393-901d-14701f2ad6f3",
            "timestamp": 1756354387819
          }
        ],
        [
          "execution_success",
          {
            "prompt_id": "980ebb00-073e-4393-901d-14701f2ad6f3",
            "timestamp": 1756354408020
          }
        ]
      ]
    },
    "meta": {
      "9": {
        "node_id": "9",
        "display_node": "9",
        "parent_node": null,
        "real_node_id": "9"
      }
    }
  }
}