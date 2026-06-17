import torch
from functools import lru_cache
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer

@lru_cache(maxsize=1)
def get_llm():
    model_id = "LiquidAI/LFM2.5-1.2B-Instruct"
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="mps",
        torch_dtype=torch.float16
    #   attn_implementation="flash_attention_2" <- uncomment on compatible GPU
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    return model, tokenizer

def run_llm(user_prompt, max_tokens = 128):
    model, tokenizer = get_llm()
    prompt = user_prompt

    input_ids = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        add_generation_prompt=True,
        return_tensors="pt",
        tokenize=True,
    ).to("mps")

    output = model.generate(
        input_ids,
        do_sample=True,
        top_k=50,
        repetition_penalty=1.05,
        max_new_tokens=max_tokens,
    )
    response = tokenizer.batch_decode(
        output,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]

    return response.strip()