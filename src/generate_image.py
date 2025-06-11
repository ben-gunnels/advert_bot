import random 
import os
import base64
import pathlib
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

__all__ = ["edit_image"]

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4.1"  # "dall-e-2 "

def encode_image(file_path):
    with open(file_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return base64_image

def edit_image(prompt, input_filename, model_filename):
    try:
        if os.path.exists(input_filename):
            print(f"File is valid and can be used for image generation.")
        
        else:
            print(f"File is invalid and cannot be used for image generation.")
        
        base64_image1 = encode_image(input_filename)
        base64_image2 = encode_image(model_filename)

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image1}",
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image2}",
                        },
                    ],
                }
            ],
            tools=[{"type": "image_generation"}],
        )

        image_generation_calls = [
            output
            for output in response.output
            if output.type == "image_generation_call"
        ]

        image_data = [output.result for output in image_generation_calls]

        image_bytes = base64.b64decode(image_data[0])

        return image_bytes
    except Exception as e:
        print(f"Error during image generation: {e}")
        raise