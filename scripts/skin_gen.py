from utils.skin_utils import get_output, get_skin
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
from PIL import Image
import torch
import minepi
import numpy as np
import asyncio

# Load the model from Hugging Face
# pipe = StableDiffusionXLPipeline.from_pretrained(
#     "monadical-labs/minecraft-skin-generator-sdxl", 
#     torch_dtype=torch.float16,
#     cache_dir="E:/AI-models/Minecraft-Skins",
# )
# pipe.to("cuda")

print("Model loaded!")

SCALE = 12
MASK_IMAGE = "masks/mask2.png"
THRESHOLD = 35

def extract_minecraft_skin(generated_image):
    """
    Scale the texture
    """
    width, height = generated_image.size
    generated_skin = generated_image.crop((0, 0, width, height/2))

    width, height = generated_skin.size
    scale = width/64

    scaled_skin = generated_skin.resize((int(width / scale), int(height / scale)),
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

    mask_image = Image.open(MASK_IMAGE).crop((0, 0, converted_image.width, converted_image.height))

    bg = Image.new("RGBA", converted_image.size, (0, 0, 0, 0))
    
    return Image.composite(converted_image, bg, mask_image)

def generate_skin(prompt, uuid = None):

    image = pipe(prompt=prompt, width=768, height=768).images[0]

    image.save(get_output("full"))

    minecraft_skin = extract_minecraft_skin(image)

    minecraft_skin = restore_skin_alphachannels(minecraft_skin)
    minecraft_skin.save(get_skin(uuid)[1])

async def render_skin(texture):
    s = minepi.Skin(texture)
    await s.render_skin()
    s.skin.show()

if __name__ == "__main__":
    #generate_skin("A purple smiling dinosaur")
    image = Image.open(get_skin(additional="full")[1])
    minecraft_skin = extract_minecraft_skin(image)
    minecraft_skin = restore_skin_alphachannels(minecraft_skin)
    minecraft_skin.save(get_skin()[1])
    asyncio.run(render_skin(minecraft_skin))