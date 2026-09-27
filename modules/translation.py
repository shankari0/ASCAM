from transformers import MarianMTModel, MarianTokenizer

print("Loading translation models...")

MODELS = {
    "fr": "Helsinki-NLP/opus-mt-en-fr",
    "de": "Helsinki-NLP/opus-mt-en-de",
    "zh": "Helsinki-NLP/opus-mt-en-zh",
    "es": "Helsinki-NLP/opus-mt-en-es",
    "ar": "Helsinki-NLP/opus-mt-en-ar",
}

# Load all tokenizers and models at startup
loaded = {}
for code, model_name in MODELS.items():
    print(f"  Loading {code}...")
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    loaded[code] = (tokenizer, model)

print("Translation models ready.")

"""
Translate text into the target language.
Supported codes: fr, de, zh, es, ar
"""
def translate(text, target_language_code="fr"):
    if target_language_code not in loaded:
        return f"Language '{target_language_code}' not supported. Choose from: {list(loaded.keys())}"

    tokenizer, model = loaded[target_language_code]

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    outputs = model.generate(**inputs, max_new_tokens=512)
    translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated