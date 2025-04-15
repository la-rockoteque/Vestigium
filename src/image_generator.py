
from diffusers import StableDiffusionPipeline
import inflection
# import torch
# import pandas as pd
# pd.options.display.float_format = '{:,.0f}'.format

# pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
# pipe.to("mps")
# _ = pipe("test", num_inference_steps=1)
def generate_icon(category: str, name: str, image_size=(128, 128), background_color="white", text_color="black", font_size=24):
  import inflection
  file_name = f"images/{category}/{inflection.underscore(name.replace('/', '_'))}.png"
  return f"https://raw.githubusercontent.com/la-rockoteque/Vestigium/refs/heads/main/{file_name}"
  import os.path
  if os.path.isfile(file_name):
    return file_name
  prompt = f"{category} icon for a {category} named {name}"
  image = pipe(prompt).images[0]
  image.save(file_name)
  return f"https://raw.githubusercontent.com/la-rockoteque/Vestigium/refs/heads/main/{file_name}"