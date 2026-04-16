import importlib

import torch
from benchmate.inference.utils import (TextRerank, TextEmbed, ImageRerank, ImageEmbed, SemanticChunk, InterpretImage)

class Inference:
    def __init__(self, config):
        self.config = config
        self.device="cuda" if torch.cuda.is_available() else "cpu"
        self.text_embed = TextEmbed(self.config["text_embed"]["cache_dir"],
                                    self.config["text_embed"]["model_name"],
                                    device=self.device,)

        self.text_rerank = TextRerank(self.config["text_rerank"]["cache_dir"],
                                      self.config["text_rerank"]["model_name"],
                                      self.config["text_rerank"]["model_kwargs"],
                                      self.config["text_rerank"]["tokenizer_kwargs"],
                                      device=self.device,
                                     )

        self.image_embed = ImageEmbed(self.config["image_embed"]["cache_dir"],
                                      self.config["image_embed"]["model_name"],
                                      self.config["image_embed"]["model_kwargs"],
                                      self.config["image_embed"]["processor_kwargs"],
                                      importlib.import_module(self.config["image_embed"]["model_class"]),
                                      importlib.import_module(self.config["image_embed"]["processor_class"]),
                                      device=self.device,)

        self.image_rerank = ImageRerank(self.config["image_rerank"]["cache_dir"],
                                        self.config["image_rerank"]["model_name"],
                                        self.config["image_rerank"]["model_kwargs"],
                                        self.config["image_rerank"]["processor_kwargs"],
                                        importlib.import_module(self.config["image_rerank"]["model_class"]),
                                        importlib.import_module(self.config["image_rerank"]["processor_class"]),
                                        device=self.device,)

        self.semantic_chunk = SemanticChunk(self.config["semantic_chunk"]["chunking_model"],
                                            **self.config["semantic_chunk"]["chunking_kwargs"],)

        self.interpret_image = InterpretImage(self.config["interpret_image"]["cache_dir"],
                                              self.config["interpret_image"]["model_name"],
                                              self.config["interpret_image"]["model_kwargs"],
                                              self.config["interpret_image"]["processor_kwargs"],
                                              importlib.import_module(self.config["interpret_image"]["model_class"]),
                                              importlib.import_module(self.config["interpret_image"]["processor_class"]),
                                              device=self.device )

    #TODO need to check if this is immediately compatible with the db
    def embed_text(self, texts):
        embeddings=self.text_embed(texts)
        return embeddings

    def embed_image(self, images):
        embeddings=self.image_embed(images)
        return embeddings

    def rerank_text(self, query, texts):
        scores=self.text_rerank.rerank(self.config["text_rerank"]["prefix"],
                                self.config["text_rerank"]["suffix"],
                                query, texts)
        return [(score, image) for score, image in sorted(zip(scores, texts), reverse=True)]

    def rerank_image(self, query, images):
        scores=self.image_rerank.rerank(query, images)
        return [(score, image) for score, image in sorted(zip(scores, images), reverse=True)]

    def chunk_text(self, text):
        return self.semantic_chunk.chunk_text(text)

    def interpret_image(self, images):
        return self.interpret_image.interpret(images)

