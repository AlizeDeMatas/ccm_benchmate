import gc
from functools import cached_property
from collections.abc import Iterable
import json
import torch

from transformers import (AutoTokenizer, AutoModelForCausalLM, AutoProcessor, AutoModelForImageTextToText,
                          CLIPModel, CLIPProcessor, ColPaliProcessor,BitsAndBytesConfig,
                          ColPaliForRetrieval, Qwen2_5_VLForConditionalGeneration)

from chonkie import SemanticChunker, Model2VecEmbeddings
from sentence_transformers import SentenceTransformer
from qwen_vl_utils import process_vision_info


#TODO neeed to do quantization kwargs in all of these

class CleanupMixin:
    def cleanup_cuda(self):
        """Fully clears GPU memory."""
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.synchronize()
        gc.collect()

    def cleanup_model(self, model):
        """Moves model to CPU, deletes it, and clears CUDA."""
        if model is not None:
            try:
                model.to("cpu")
            except Exception:
                pass
            del model
        gc.collect()
        self.cleanup_cuda()



class TextEmbed(CleanupMixin):
    def __init__(self, cache_dir, model_name, kwargs=None, device="cuda"):
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.kwargs = kwargs if kwargs is not None else {}
        self.device = device

    @cached_property
    def model(self):
        model = SentenceTransformer(self.model_name, **self.kwargs, cache_folder=self.cache_dir)
        return model

    def encode(self, texts):
        embeddings = self.model.encode(texts)
        self.cleanup_model(self.model)
        return embeddings


class TextRerank(CleanupMixin):
    def __init__(self, cache_dir, model_name, model_kwargs=None, tokenizer_kwargs=None, device="cuda"):
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.model_kwargs = model_kwargs if model_kwargs is not None else {}
        self.tokenizer_kwargs = tokenizer_kwargs if tokenizer_kwargs is not None else {}
        self.device = device

    @cached_property
    def model(self):
        model=AutoModelForCausalLM.from_pretrained(self.model_name, cache_dir=self.cache_dir, device_map=self.device,
                                                   **self.model_kwargs)
        return model

    @cached_property
    def tokenizer(self):
        tokenizer=AutoTokenizer.from_pretrained(self.model_name, self.cache_dir, **self.tokenizer_kwargs)
        return tokenizer

    def rerank(self, prefix, suffix, query, texts):
        prefix_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)
        suffix_tokens = self.tokenizer.encode(suffix, add_special_tokens=False)

        token_id_yes = self.tokenizer.convert_tokens_to_ids("yes")
        token_id_no = self.tokenizer.convert_tokens_to_ids("no")

        relevance = []
        for text in texts:
            prompt = prompt.format(query=query, context=text)
            inputs = self.tokenizer(
                prompt,
                truncation="longest_first",
                max_length=8192 - len(prefix_tokens) - len(suffix_tokens),
                add_special_tokens=False,
            )
            input_ids = [prefix_tokens + inputs["input_ids"] + suffix_tokens]
            attention_mask = [[1] * len(input_ids[0])]
            batch = {
                "input_ids": torch.tensor(input_ids, dtype=torch.long, device=self.device),
                "attention_mask": torch.tensor(attention_mask, dtype=torch.long, device=self.device),
            }

            with torch.inference_mode():
                outputs = self.model(**batch)
                logits = outputs.logits  # (1, L, V)
                last_logits = logits[:, -1, :]  # (1, V)
                score_no = last_logits[0, token_id_no]
                score_yes = last_logits[0, token_id_yes]
                # Compute softmax over the two (no, yes)
                two_logits = torch.stack([score_no, score_yes], dim=0)  # shape (2,)
                probs = torch.softmax(two_logits, dim=0)  # (2,)
                prob_yes = probs[1].item()
                relevance.append(prob_yes)
                self.cleanup_cuda()

        self.cleanup_model(self.model)
        return relevance


class ImageEmbed(CleanupMixin):
    def __init__(self, cache_dir, model_name, model_kwargs, processor_kwargs,
                 model_class=CLIPModel, processor_class=CLIPProcessor, device="cuda"):
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.model_class=  model_class
        self.processor_class=processor_class
        self.model_kwargs = model_kwargs
        self.processor_kwargs = processor_kwargs
        self.device = device

    @cached_property
    def model(self):
        model=self.model_class.from_pretrained(self.model_name, cache_dir=self.cache_dir,
                                               device_map=self.device, **self.model_kwargs)
        return model

    @cached_property
    def processor(self):
        processor=self.processor_class.from_pretrained(self.model_name, cache_dir=self.cache_dir, **self.processor_kwargs)
        return processor

    @torch.inference_mode()
    def embed(self, images):
        inputs = self.processor(images=images, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        emb = self.model.get_image_features(**inputs)
        emb = emb / emb.norm(dim=-1, keepdim=True)
        emb = emb.cpu().numpy().astype("float32")
        self.cleanup_model(self.model)
        return emb

class ImageRerank(CleanupMixin):
    def __init__(self, cache_dir, model_name, model_kwargs, processor_kwargs,
                 model_class=ColPaliForRetrieval, processor_class=ColPaliProcessor, device="cuda"):
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.model_class=  model_class
        self.processor_class=processor_class
        self.model_kwargs = model_kwargs
        self.processor_kwargs = processor_kwargs
        self.device = device

    @cached_property
    def model(self):
        model=self.model_class.from_pretrained(self.model_name, cache_dir=self.cache_dir,
                                               device_map=self.device, **self.model_kwargs)
        return model

    @cached_property
    def processor(self):
        processor=self.processor_class.from_pretrained(self.model_name, cache_dir=self.cache_dir,
                                                       **self.processor_kwargs)
        return processor

    @torch.inference_mode()
    def rerank(self, query, images):
        inputs = self.processor(
            images=[query] + images,
            return_tensors="pt",
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        scores = self.model.score_images(
            query_index=0,
            candidate_indices=list(range(1, len(images) + 1)),
            **inputs
        )
        scores= scores.cpu().numpy()
        self.cleanup_model(self.model)
        return scores


class SemanticChunk(CleanupMixin):
    def __init__(self, chunking_model, chunk_size=100, min_sentences=1,
                 threshold=0.8):
        """
        :param chunking_model: chunking model it can be anything really but we are using a static model for speed
        :param chunk_size: how many tokens approx a chunk should have
        :param min_sentences: how many sentences a chunk should have at the minimum. It did not makes sense to me to split sentences so we are
        sticking with 1
        :param threshold: when to start a new chunk, this is based on the delta for the embedding cosines.
        """
        self.chunking_model = Model2VecEmbeddings(chunking_model)
        self.chunk_size=chunk_size
        self.min_sentences=min_sentences
        self.threshold=threshold

    def chunk_text(self, texts):
        """Chunk notes into semantic segments. this will return a list of strings, i will then use an embedding model"""
        chunker = SemanticChunker(
            embedding_model=self.chunking_model,
            threshold=self.threshold,  # Similarity threshold (0-1) or (1-100) or "auto"
            chunk_size=self.chunk_size,  # Maximum tokens per chunk
            min_sentences=self.min_sentences,  # Initial sentences per chunk,
            return_type="texts"  # return a list of strings
        )
        if not isinstance(texts, Iterable):
            texts=[texts]

        chunked_texts = []
        for text in texts:
            chunked=chunker.chunk(text)
            for index, chunk in enumerate(chunked):
                chunked_texts.append((index, chunk))

        return chunked_texts


class InterpretImage(CleanupMixin):
    def __init__(self, cache_dir, model_name, model_kwargs, processor_kwargs,
                 model_class=Qwen2_5_VLForConditionalGeneration,
                 processor_class=AutoProcessor, device="cuda"):
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.model_class=  model_class
        self.model_kwargs=model_kwargs
        self.processor_class=processor_class
        self.processor_kwargs=processor_kwargs
        self.device = device

    @cached_property
    def model(self):
        model=self.model_class.from_pretrained(self.model_name, cache_dir=self.cache_dir, **self.model_kwargs)
        return model

    @cached_property
    def processor(self):
        processor=self.processor_class.from_pretrained(self.model_name, cache_dir=self.cache_dir, **self.processor_kwargs)
        return processor

    @torch.inference_mode
    def interpret(self, sys_prompt, images):
        outputs=[]
        for image in images:
            messages = [{"role": "system", "content": [{"type": "text",
                                                        "text": sys_prompt}]},
                        {"role": "user", "content": [{"type": "image", "image": image, }], }]


            text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            #TODO this actually breaks the flexibility, I will need to adress this later
            # this is here for compatibility I will not be processing videos
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.device)
            generated_ids = self.model.generate(**inputs, max_new_tokens=self.config["vl_model"]["model"]["max_tokens"])
            generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids,
            out_ids in zip(inputs.input_ids, generated_ids)]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            outputs.append(output_text)
            self.cleanup_cuda()

        self.cleanup_model(self.model)
        return outputs

class ExtractInfo(CleanupMixin):
    def __init__(
        self,
        cache_dir,
        model_name,
        model_kwargs=None,
        processor_kwargs=None,
        quantization_kwargs=None,
        generation_kwargs=None,
        model_class=AutoModelForImageTextToText,
        processor_class=AutoProcessor,
        device="cuda",
    ):
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.model_class = model_class
        self.processor_class = processor_class
        self.device = device

        # defensive copies (avoid external mutation bugs)
        self.model_kwargs = dict(model_kwargs or {})
        self.processor_kwargs = dict(processor_kwargs or {})
        self.generation_kwargs = dict(generation_kwargs or {})
        self.quantization_kwargs = dict(quantization_kwargs or {})

    @cached_property
    def model(self):
        if self.quantization_kwargs:
            quantization_config = BitsAndBytesConfig(**self.quantization_kwargs)
            # set attribute correctly (not dict-style)
            quantization_config.bnb_4bit_compute_dtype = torch.bfloat16
        else:
            quantization_config = None

        model = self.model_class.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            quantization_config=quantization_config,
            **self.model_kwargs,
        )

        # only move manually if NOT quantized
        if quantization_config is None:
            model = model.to(self.device)

        return model

    @cached_property
    def processor(self):
        return self.processor_class.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            **self.processor_kwargs,
        )

    def generate_extraction_prompt(self, items_to_extract: dict):
        description_text = []
        format_text = []

        for item, description in items_to_extract.items():
            description_text.append(f"- {item}: {description}\n")
            format_text.append(
                f'{item}: [comma(,) separated list of each member of {item}],\n'
            )

        prompt = f"""
For each of the texts that are provided extract the following information:

{''.join(description_text)}

For each of the items mentioned above your response should come in the following schema:
{{
{''.join(format_text)}
}}

Rules:
- Do not invent or modify what you are looking for
- Not every possible item will be in each text
- There might be more than one item in each text include all of them
- Always return json, no markdown, no comments, no additional formatting
- If there is no information relating to a specific field return empty list and nothing else

Text:
"""
        return prompt

    @torch.inference_mode()
    def extract_info(self, sys_prompt, items_to_extract: dict, texts: list):
        prompt = self.generate_extraction_prompt(items_to_extract)
        results = []

        for text in texts:
            if text is None:
                results.append(None)
                continue

            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": sys_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt + "\n" + text}],
                },
            ]

            inputs = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                padding=True,
                pad_to_multiple_of=8,
                return_dict=True,
                return_tensors="pt",
            )

            # move to device ONLY (no forced dtype)
            inputs = inputs.to(self.device)

            input_len = inputs["input_ids"].shape[-1]

            generation = self.model.generate(
                **inputs,
                **self.generation_kwargs,  # no override
            )

            generation = generation[0][input_len:]
            decoded = self.processor.decode(generation, skip_special_tokens=True)

            # optional: try parsing JSON (non-breaking)
            try:
                parsed = json.loads(decoded)
            except Exception:
                parsed = decoded  # fallback to raw string

            results.append(parsed)
            self.cleanup_cuda()

        self.cleanup_model()
        return results




