from functools import lru_cache
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


@lru_cache(maxsize=1)
def _load_model_and_processor():
    
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2.5-VL-3B-Instruct",
        torch_dtype="auto",
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")
    return model, processor, Image, torch


def _resolve_image_path(image_dir):
    image_path = Path(image_dir)
    if image_path.is_file():
        return image_path

    if image_path.is_dir():
        for candidate in sorted(image_path.iterdir()):
            if candidate.is_file() and candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}:
                return candidate

    raise FileNotFoundError(f"No supported image found at: {image_dir}")


def run_vlm(system_promt, user_prompt, image_dir):
    model, processor, image_module, torch = _load_model_and_processor()
    image_path = _resolve_image_path(image_dir)

    image = image_module.open(image_path).convert("RGB")
    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": system_promt}],
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": user_prompt},
            ],
        },
    ]

    prompt_text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = processor(
        text=[prompt_text],
        images=[image],
        return_tensors="pt",
        padding=True,
    )

    if hasattr(model, "device"):
        inputs = inputs.to(model.device)
    else:
        inputs = {key: value.to("cuda" if torch.cuda.is_available() else "cpu") for key, value in inputs.items()}

    with torch.inference_mode():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
        )

    output_ids = generated_ids[:, inputs["input_ids"].shape[1]:]
    response = processor.batch_decode(
        output_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]
    return response.strip()