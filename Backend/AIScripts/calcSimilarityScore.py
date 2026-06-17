from functools import lru_cache

import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer


MODEL_NAME = "abhinand/MedEmbed-large-v0.1"


@lru_cache(maxsize=1)
def _load_model_and_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
    if torch.cuda.is_available():
        model = model.to("cuda")
    elif torch.backends.mps.is_available():
        model = model.to("mps")
    else:
        model = model.to("cpu").to(torch.float32)

    model.eval()
    return model, tokenizer


def _get_device(model):
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cpu")


def _mean_pool(last_hidden_state, attention_mask):
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    masked_embeddings = last_hidden_state * mask
    summed_embeddings = masked_embeddings.sum(dim=1)
    summed_mask = mask.sum(dim=1).clamp(min=1e-9)
    return summed_embeddings / summed_mask


def _encode_text(text):
    model, tokenizer = _load_model_and_tokenizer()
    device = _get_device(model)

    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.inference_mode():
        outputs = model(**inputs)
        embeddings = _mean_pool(outputs.last_hidden_state, inputs["attention_mask"])
        embeddings = F.normalize(embeddings, p=2, dim=1)

    return embeddings


def calculate_similarity_score(phrase1, phrase2):
    print("similarity score called")
    if not phrase1 or not phrase2:
        return 0.0

    embedding_1 = _encode_text(phrase1)
    embedding_2 = _encode_text(phrase2)

    return float(F.cosine_similarity(embedding_1, embedding_2).item())