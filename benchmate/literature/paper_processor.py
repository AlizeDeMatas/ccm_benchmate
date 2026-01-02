import os
import warnings
# this is weirdly needed to get tesseract to work
os.environ["TESSDATA_PREFIX"]=f"{os.environ['CONDA_PREFIX']}/share/tessdata"

import torch

import pymupdf
from PIL import Image
import pytesseract
import layoutparser as lp

from benchmate.inference.inference import Inference

class PaperProcessor:
    """
    paper processor class, this is the main class for extracting text figures and generating embeddings for the papers
    the pipeline method is the main caller where you can specify which steps you would like to run
    all the necessary parameters are passed in a config dict so there are no hard coded values and no values to fill
    """
    def __init__(self, inference:Inference, config):
        """
        Init the paper processor class
        :param inference: this will handle all the processing except for extracting text and figures from the paper that is
        a literature specific task and we do not need to process other items like that.
        :param config: settings related to literature, mostly layout parserstuff
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.config=config
        self.inference = inference

    # pass a list of files
    def extract(self, model, file_path, zoom=2):
        """
        extract text and images from a pdf, this model gets all the figures and tables from the pdf and returns them as images
        as well as extracting the pdf text using tesseract.
        :param file_path: pdf file path
        :return: text, figures and tables as pillow images
        """
        doc = pymupdf.open(file_path)
        zoom_x = zoom  # horizontal zoom
        zoom_y = zoom  # vertical zoom/
        mat = pymupdf.Matrix(zoom_x, zoom_y)
        texts = []
        figures = []
        tables = []
        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            pix = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            layout = model.detect(pix)
            figure_blocks = lp.Layout([b for b in layout if b.type == 'Figure'])
            table_blocks = lp.Layout([b for b in layout if b.type == 'Table'])
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
        texts = [text.replace("\n", " ").replace("  ", " ") for text in texts]
        article_text = " ".join(texts)

        return article_text, tables, figures

    def pipeline(self, papers, extract=True, embed_text=True, embed_images=True, interpret_images=False):
        """
        whole paper processing pipeline
        :param papers: list of papers see literature.paper for details
        :param extract: extract text, figues and tables (the latter two are images)
        :param embed_text: chunk and embed the pdf text
        :param embed_images: embed images
        :param interpret_images: run a vision language model on the images to generate text
        :param embed_iterpretations: embed the interpretations of the images
        :return: paper class instance with all the attributes filled
        """
        if extract:
            model = lp.Detectron2LayoutModel(   model_path=self.config["lp_model"]["model_path"],
                                            config_path=self.config["lp_model"]["config_path"],
                                            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
                                            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                                                )
            for paper in papers:
                paper.info.text, paper.info.tables, paper.info.figures = self.extract(model, paper.info.file_path)
        else:
            raise NotImplementedError("Extract must be true otherwise there is no data to process")

        if embed_text:
            for paper in papers:
                paper.info.text_chunks =self.inference.chunk(paper.info.text)
                paper.info.chunk_embeddings= self.inference.text_embeddings(paper.info.text_chunks)

        if embed_images:
            for paper in papers:
                if len(paper.info.figures)>0:
                    paper.info.figure_embeddings = self.inference.image_embeddings(paper.info.figures)

                if len(paper.info.tables)>0:
                    paper.info.table_embeddings = self.inference.image_embeddings(paper.info.tables)

        if interpret_images:
            for paper in papers:
                paper.info.figure_interpretation = []
                paper.info.table_interpretation = []
                if len(paper.info.figures) > 0:
                    for figure in paper.info.figures:
                        paper.info.figure_interpretation.append(self.inference.image_interpretation(figure, self.config["figure_prompt"]))

                if len(paper.info.tables) > 0:
                    for table in paper.info.tables:
                        paper.info.table_interpretation.append(self.inference.image_interpretation(table, self.config["table_prompt"]))

            for paper in papers:
                paper.info.figure_interpretation_embeddings = []
                paper.info.table_interpretation_embeddings = []
                if len(paper.info.figure_interpretation) > 0:
                    paper.info.figure_interpretation_embeddings.append(self.inference.text_embeddings(texts=paper.info.figure_interpretation))

                if len(paper.info.table_interpretation) > 0:
                    paper.info.table_interpretation_embeddings.append(self.inference.text_embeddings(texts=paper.info.table_interpretation))
        return papers

