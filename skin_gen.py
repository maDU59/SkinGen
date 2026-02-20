import torch
import diffusers
import PIL
import minepi
import numpy as np
import asyncio
import backend
print("--- ENVIRONMENT CHECK ---")
print(f"✅ Torch version: {torch.__version__}")
print(f"✅ Diffusers version: {diffusers.__version__}")
print(f"✅ PIL (Pillow) version: {PIL.__version__}")
print("--------------------------")
print("Environment is ready for Minecraft Skin generation!")
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
from PIL import Image

# Load the model from Hugging Face
pipe = StableDiffusionXLPipeline.from_pretrained(
    "monadical-labs/minecraft-skin-generator-sdxl", 
    torch_dtype=torch.float16,
    cache_dir="E:/AI-models/Minecraft-Skins",
)
pipe.to("cuda")

print("Model loaded!")

SCALE = 12
MASK_IMAGE = "img/mask2.png"
THRESHOLD = 35

def extract_minecraft_skin(generated_image):
    """
    Scale the texture
    """
    width, height = generated_image.size
    scaled_skin = generated_image.resize((int(width / SCALE), int(height / SCALE)),
                                        resample=Image.Resampling.NEAREST) 
    
    return scaled_skin

def restore_skin_alphachannels(image):
    converted_image = image.convert('RGBA')

    image_data = np.array(converted_image)
    rgb_data = image_data[:, :, :3]
    bg_color = rgb_data[0, 0]
    diff = rgb_data.astype(np.int32) - bg_color.astype(np.int32)
    distance = np.sqrt(np.sum(diff ** 2, axis=2))
    background_mask = distance <= THRESHOLD
    image_data[background_mask, 3] = 0

    converted_image = Image.fromarray(image_data)
    converted_image = converted_image.convert("RGBA")

    mask_image = Image.open(MASK_IMAGE)
    mask_image.alpha_composite(converted_image)
    
    return converted_image

def generate_skin(prompt):

    image = pipe(prompt=prompt, width=768, height=768).images[0]

    image.save(backend.get_output("full"))

    minecraft_skin = extract_minecraft_skin(image)

    minecraft_skin = restore_skin_alphachannels(minecraft_skin)
    minecraft_skin.save(backend.get_output())

async def render_skin(texture):
    s = minepi.Skin(texture)
    await s.render_skin()
    s.skin.show()

if __name__ == "__main__":
    generate_skin("A purple smiling dinosaur")
    image = Image.open(backend.get_output("full"))
    minecraft_skin = extract_minecraft_skin(image)
    minecraft_skin = restore_skin_alphachannels(minecraft_skin)
    minecraft_skin.save(backend.get_output())
    asyncio.run(render_skin(minecraft_skin))