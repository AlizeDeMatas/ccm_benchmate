
import torch

from chonkie import SemanticChunker, Model2VecEmbeddings
from sentence_transformers import SentenceTransformer

from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from colpali_engine.models import ColPali, ColPaliProcessor

from benchmate.config import inference


class Inference:
    def __init__(self, config):
        """
        Inference class, this will take all the models and will call them one by one based on the task
        :param config: a config file specifiying where the models are and how they are to be used (like temperature, or
        embedding settings or chunking settings etc)
        """
        self.config = config

    def text_embeddings(self, texts):
        """
        genereate text embeddings using a chunking strategy and an embedding model. The model is a huggingface senntence transformer
        and the chunker is a chonkie semantic chunker
        :param text: text to embed
        :param chunker: chonkie semantic chunker
        :param splitting_strategy: whether to use semantic chunking or not
        :param embedding_model: sentence transformer model
        :return: chunks and embeddings if not chunked then the whole text and its embedding
        """
        if "config" in self.config["text_embedding_model"].keys():
            text_embedding_kwargs = self.config["text_embedding_model"]["config"]
            model = SentenceTransformer(self.config["text_embedding_model"]["name"],
                                        **text_embedding_kwargs)
        else:
            model = SentenceTransformer(self.config["text_embedding_model"]["name"])

        embeddings = model.encode(texts)
        return embeddings

    def chunk(self, texts):
        chunker_model = Model2VecEmbeddings(self.config["chunker_model"]["model"])
        chunker = SemanticChunker(
            embedding_model=chunker_model,
            threshold=self.config["chunker_model"]["threshold"],
            chunk_size=self.config["chunker_model"]["chunk_size"],
            min_sentences=self.config["chunker_model"]["min_sentences"],
            return_type=self.config["chunker_model"]["return_type"]
        )

        chunks = chunker.chunk(texts)
        return chunks

    def image_embeddings(self, images):
        if "config" in self.config["image_embedding_model"]["model"].keys():
            image_embedding_model_kwargs = self.config["image_embedding_model"]["model"]["config"]

            model = ColPali.from_pretrained(self.config["image_embedding_model"]["model"]["name"],
                                            **image_embedding_model_kwargs,
                                            torch_dtype=torch.bfloat16,
                                            device_map=self.device
                                            ).eval()
        else:
            model = ColPali.from_pretrained(self.config["image_embedding_model"]["model"]["name"],
                                            torch_dtype=torch.bfloat16,
                                            device_map=self.device
                                            ).eval()

        if "config" in self.config["image_embedding_model"]["processor"].keys():
            image_embedding_processor_kwargs = self.config["image_embedding_model"]["processor"]["config"]

            processor = ColPaliProcessor.from_pretrained(
                self.config["image_embedding_model"]["processor"]["name"],
                **image_embedding_processor_kwargs, )
        else:
            processor = ColPaliProcessor.from_pretrained(
                self.config["image_embedding_model"]["processor"]["name"])

        batch_images = processor.process_images(images).to(self.device)
        with torch.no_grad():
            image_embeddings = model(**batch_images)

        ems = []
        for i in range(image_embeddings.shape[0]):
            ems.append(image_embeddings[i, :, :])
        return ems

    def image_interpretation(self, images, prompt):
        if "config" in self.config["vl_model"]["model"].keys():
            vl_model_kwargs = self.config["vl_model"]["model"]["config"]

            model = Qwen2_5_VLForConditionalGeneration.from_pretrained(self.config["vl_model"]["model"]["name"],
                                                                       **vl_model_kwargs,
                                                                       device_map=self.device)
        else:
            model = Qwen2_5_VLForConditionalGeneration.from_pretrained(self.config["vl_model"]["model"]["name"],
                                                                       device_map=self.device)

        if "config" in self.config["vl_model"]["processor"].keys():
            vl_processor_kwargs = self.config["vl_model"]["processor"]["config"]

            processor = AutoProcessor.from_pretrained(self.config["vl_model"]["processor"]["name"],
                                                      **vl_processor_kwargs)
        else:
            processor = AutoProcessor.from_pretrained(self.config["vl_model"]["processor"]["name"])

        outputs=[]
        for image in images:

            messages = [{"role": "system", "content": [{"type": "text",
                                                        "text": prompt}]},
                        {"role": "user", "content": [{"type": "image", "image": image, }], }]

            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            # this is here for compatibility I will not be processing videos
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.device)
            generated_ids = model.generate(**inputs, max_new_tokens=self.config["vl_model"]["model"]["max_tokens"])
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids,
            out_ids in zip(inputs.input_ids, generated_ids)]
            output_text = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            outputs.append(output_text)
        return outputs

    def text_score(self, query, texts):
        query_chunks=self.chunk(query)
        query_embeddings = self.text_embeddings(query_chunks)
        query_embeddings = torch.tensor(query_embeddings)
        scores=[]
        for text in texts:
            text_chunks=self.chunk(text)
            text_embeddings = self.text_embeddings(text_chunks)
            text_embeddings = torch.tensor(text_embeddings)
            similarity_scores = torch.matmul(query_embeddings, text_embeddings.T)
            score = self._symmetric_score(similarity_scores)
            scores.append(score)
        return scores

    def rerank(self, query, texts):
        pass

    def _symmetric_score(self, sim):
        """
        get symetric score for a similarity matrix of a given text and project description
        :param sim: pairwise similarlty matrix of semantic chunks
        :return: float, symmetric score of mean max similarities
        """
        # Mean of max similarities from rows (text1 to other)
        mean_max_row = torch.max(sim, dim=1).values.mean().item()
        # Mean of max similarities from columns (other to text1)
        mean_max_col = torch.max(sim, dim=0).values.mean().item()
        # Symmetric score
        return (mean_max_row + mean_max_col) / 2


