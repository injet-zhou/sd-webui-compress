import traceback
from modules import scripts
from modules.scripts import PostprocessImageArgs
from modules import script_callbacks
from modules import processing

import gradio as gr
import oxipng
from io import BytesIO
from PIL import Image


def pil_to_bytes(pil_image):
    img_bytes = BytesIO()
    pil_image.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


def bytes_to_pil(img_bytes):
    return Image.open(BytesIO(img_bytes))


def size_in_KB(img_bytes):
    return len(img_bytes) / 1024


class Compressor(scripts.Script):
    def title(self):
        return "Compressor"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("Compressor"):
            enabled = gr.Checkbox(
                label="Enabled",
                value=False,
                elem_id=self.elem_id("enabled"),
            )
            level = gr.Slider(
                minimum=0,
                maximum=6,
                value=2.0,
                step=1.0,
                label="Level",
                # elem_id=self.elem_id("level"),
            )
            strip_safe_chunks = gr.Checkbox(
                label="Strip Safe Chunks",
                value=False,
                elem_id=self.elem_id("strip_safe_chunks"),
            )
        return [enabled, level, strip_safe_chunks]

    def postprocess(self, p, processed: processing.Processed, *args):
        try:
            enabled, level, strip_safe_chunks = args
            new_images = []
            if enabled:
                level = int(level)
                print(
                    f"Compressing image with level {level}, strip_safe_chunks {strip_safe_chunks}..."
                )
                for index, image in enumerate(processed.images):
                    bin_img = pil_to_bytes(image)
                    print(f"Image size before compression: {size_in_KB(bin_img)} KB")
                    compressed = oxipng.optimize_from_memory(
                        bin_img,
                        level=level,
                        strip=oxipng.StripChunks.safe()
                        if strip_safe_chunks
                        else oxipng.StripChunks.all(),
                    )
                    print(f"Image size after compression: {size_in_KB(compressed)} KB")
                    compressed_pil = bytes_to_pil(compressed)
                    new_images.append(compressed_pil)
                processed.images = new_images
            else:
                print("skipping image compression")

        except Exception as e:
            print(e)
            traceback.print_exc()
