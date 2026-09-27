from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

print("Loading BLIP diagram understanding model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
model.eval()
print("BLIP ready.")


# Describe a diagram from an academic document using BLIP.
# Returns a text description of what the image shows.
def image_to_markdown(image_path):
    img = Image.open(image_path).convert("RGB")

    inputs = processor(
        img,
        "a diagram showing",
        return_tensors="pt"
    )

    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=200)

    return processor.decode(output[0], skip_special_tokens=True)