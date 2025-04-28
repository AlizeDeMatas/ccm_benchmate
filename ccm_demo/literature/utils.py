import os
import copy
import tarfile

from PIL import Image
import pytesseract
import layoutparser as lp

import pymupdf
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from chonkie import SemanticChunker

from ccm_demo.literature.configs import *

def interpret_image(image, prompt, processor, model, max_tokens, device):
    prompt[1]["content"][0]["image"] = image
    text = processor.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
    # this is here for compatibility I will not be processing videos
    image_inputs, video_inputs = process_vision_info(prompt)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to(device)
    generated_ids = model.generate(**inputs, max_new_tokens=max_tokens)
    generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids,
    out_ids in zip(inputs.input_ids, generated_ids)]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return output_text

#TODO add tables test a paper with wester/northern blots
#TODO alternate method to include paper abstract
def process_pdf(pdf, lp_model=paper_processing_config["lp_model"], interpret_figures=True, interpret_tables=True,
                vl_model=paper_processing_config["vl_model"], zoomx=2, device="cuda", max_tokens=400, figure_prompt=figure_messages,
                table_prompt=table_message):


    lp_model=lp.Detectron2LayoutModel(lp_model["config"], lp_model["model"],
                             label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
                             extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                             )

    doc = pymupdf.open(pdf)
    zoom_x = zoomx  # horizontal zoom
    zoom_y = zoomx  # vertical zoom
    mat = pymupdf.Matrix(zoom_x, zoom_y)
    texts = []
    figures = []
    tables=[]
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        pix = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        layout = lp_model.detect(pix)
        figure_blocks = lp.Layout([b for b in layout if b.type == 'Figure'])
        table_blocks = lp.Layout([b for b in layout if b.type == 'Figure'])
        if len(figure_blocks) > 0:
            for block in figure_blocks:
                coords = block.block
                coords = (coords.x_1, coords.y_1, coords.x_2, coords.y_2,)
                figure_img = pix.crop(coords)
                figures.append(figure_img)

        if len(table_blocks) > 0:
            for block in table_blocks:
                coords = block.block
                coords = (coords.x_1, coords.y_1, coords.x_2, coords.y_2,)
                table_img = pix.crop(coords)
                tables.append(table_img)

        page_text = pytesseract.image_to_string(pix)
        texts.append(page_text)
    article_text = "\n".join(texts)

    if interpret_figures or interpret_tables:
        vl_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            vl_model, torch_dtype="auto", device_map="auto", cache_dir="models",
        )
        processor = AutoProcessor.from_pretrained(vl_model)

    figure_interpretation = []
    if interpret_figures:
        for figure in figures:
            figure_interpretation.append(interpret_image(figure, figure_prompt, processor, lp_model, max_tokens, device,))

    table_interpretation = []
    if interpret_tables:
        for table in tables:
            table_interpretation.append(interpret_image(table, table_prompt, processor, lp_model, max_tokens, device,))

    return article_text, figures, tables, figure_interpretation, table_interpretation


#TODO image embedding model, same function for figures and tables
def embed_images(image, model):
    pass


# same model for article text and captions
def embed_text(text, embedding_model, splitting_strategy="semantic",
               params=paper_processing_config["chunking"]):

    if splitting_strategy == "semantic":
        chunker = SemanticChunker(
            embedding_model=params["model"],
            threshold=params["threshold"],  # Similarity threshold (0-1) or (1-100) or "auto"
            chunk_size=params["chunk_size"],  # Maximum tokens per chunk
            min_sentences=params["min_sentences"],  # Initial sentences per chunk,
            return_type=params["return_type"]  # return a list of strings
        )
        chunks = chunker.chunk(text)
    elif splitting_strategy == "none":
        chunks=[text]
    else:
        raise NotImplementedError("Semantic splitting and none are the only implemented methods.")

    for chunk in chunks:
        #TODO embed
        pass


def extract_pdfs_from_tar(file, destination):
    """Lists the contents of a .tar.gz file.
    Args:
        file_path: The path to the .tar.gz file.
    """
    if not os.path.exists(destination):
        raise FileNotFoundError("{} does not exist.".format(destination))

    try:
        if file.endswith(".tar.gz"):
            read_str="r:gz"
        elif file.endswith(".tar.bz2"):
            read_str="r:bz2"
        elif file.endswith(".zip"):
            read_str="r:zip"
        else:
            read_str="r"

        paths=[]
        with tarfile.open(file, read_str) as tar:
            for member in tar.getmembers():
                if member.name.endswith("pdf"):
                    tar.extract(member, destination)
                    paths.append(os.path.abspath(os.path.join(destination, file, member.name)))

        return paths

    except FileNotFoundError:
        print(f"Error: File not found: {file}")
        return None

    except tarfile.ReadError:
        print(f"Error: Could not open or read {file}. It might be corrupted or not a valid tar.gz file.")
        return None


