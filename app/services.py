# -*- coding: utf-8 -*-
"""
Core business logic for the Amplify AI project.

This module contains stateless utility functions and a stateful service class
that performs the main tasks of the application, orchestrating multiple AI
models in a multimodal pipeline using LangChain.
"""
# =======================================================================
#  3. BUSINESS LOGIC (SERVICES) - Amplify AI (Final Production-Standard)
# =======================================================================

# -----------------------------------------------------------------------
#  IMPORTS
# -----------------------------------------------------------------------
import warnings
warnings.filterwarnings('ignore')

# Core libraries
import base64
import io
from typing import List, Tuple

import joblib
import torch
from diffusers import StableDiffusionPipeline
from fastapi import UploadFile
from PIL import Image
from transformers import pipeline

# LangChain components
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.text_splitter import MarkdownHeaderTextSplitter

# Internal imports
from .config import settings
from .schemas import ContentGenerationOutput


# =======================================================================
#  STATELESS UTILITY FUNCTIONS
# =======================================================================
# These are "pure" functions: they don't depend on the service's state (self).
# Placing them outside the class enhances clarity, testability, and reusability.

def _encode_image_to_base64(image: Image.Image) -> str:
    """Utility to convert a PIL Image to a Base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def _build_text_generation_prompt() -> ChatPromptTemplate:
    """Builds the LangChain prompt template for the main text generation task."""
    return ChatPromptTemplate.from_template(
        """You are Amplify AI, a world-class social media marketing expert. Your task is to write a compelling and creative post based on the user's request and the provided brand context.

        ### BRAND & STYLE CONTEXT (from Text Guide and Images) ###
        - **Post Goal/Intent:** {intent}
        - **Key Context Snippets to Follow:**
          {context}

        ### USER'S REQUEST ###
        "{user_prompt}"

        ### YOUR TASK ###
        Write the social media post copy. Be creative, strictly follow the context provided, and make it engaging."""
    )

def _build_image_prompt_generation_prompt() -> ChatPromptTemplate:
    """Builds the LangChain prompt template for generating a descriptive image prompt."""
    return ChatPromptTemplate.from_template(
        """Based on the following social media post, create a short, descriptive, and photorealistic prompt for an image generation AI. Focus on objects, scenery, and mood.
        POST: "{post_text}"
        IMAGE PROMPT:"""
    )

# -----------------------------------------------------------------------
#  STATEFUL SERVICE CLASS
# -----------------------------------------------------------------------

class ContentGenerationService:
    """
    Manages the stateful components (AI models) and orchestrates the content generation pipeline.
    Models are loaded once during initialization for maximum efficiency.
    """
    def __init__(self):
        """Initializes the service and loads all necessary AI models and LangChain components."""
        print("Initializing ContentGenerationService with LangChain stack...")
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # 1. Load non-LangChain Models
        self.classifier = joblib.load(settings.CLASSIFIER_MODEL_PATH)
        self.image_captioner = pipeline("image-to-text", model=settings.IMAGE_CAPTION_MODEL_ID, device=0 if device == "cuda" else -1)
        self.diffusion_pipeline = StableDiffusionPipeline.from_pretrained(
            settings.DIFFUSION_MODEL_ID, torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)
        print("-> Classifier, Captioner, and Diffusion models loaded.")

        # 2. Initialize LangChain LLMs (Two-Tier Strategy)
        self.llm_generator = ChatOllama(model=settings.LLM_GENERATOR_MODEL)
        self.llm_retriever = ChatOllama(model=settings.LLM_RETRIEVER_MODEL)
        print(f"-> Main LLM: {settings.LLM_GENERATOR_MODEL} | Retriever LLM: {settings.LLM_RETRIEVER_MODEL}")

        # 3. Initialize LangChain Embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"-> Embedding Model: {settings.EMBEDDING_MODEL_NAME}")

        print("✅ All models and components initialized successfully.")

    # =======================================================================
    #  ATOMIC PUBLIC FUNCTIONS (PIPELINE STEPS)
    # =======================================================================

    def classify_intent(self, text: str) -> str:
        """STEP 1: Predicts the intent of the user's prompt."""
        print(f"1. Classifying intent for: '{text[:50]}...'")
        return self.classifier.predict([text])[0]

    async def generate_captions_from_images(self, images: List[UploadFile]) -> List[str]:
        """STEP 2: Processes uploaded images and generates text descriptions."""
        print(f"2. Generating captions for {len(images)} style images...")
        captions = []
        for image_file in images:
            image_bytes = await image_file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            caption_result = self.image_captioner(image)
            captions.append(caption_result[0]['generated_text'])
        return captions

    def setup_and_retrieve_context(self, brand_guide_text: str, image_captions: List[str], user_prompt: str) -> Tuple[List[str], List[Document]]:
        """STEP 3: Sets up the full RAG pipeline and retrieves context."""
        print("3. Setting up RAG pipeline and retrieving context...")

        # A. Split brand guide and create Document objects
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_chunks = markdown_splitter.split_text(brand_guide_text)
        caption_docs = [Document(page_content=caption, metadata={"source": "style_image"}) for caption in image_captions]
        all_docs = md_chunks + caption_docs

        # B. Setup Vector Store and Retriever
        vectorstore = Chroma.from_documents(documents=all_docs, embedding=self.embeddings)
        base_retriever = vectorstore.as_retriever(search_type="mmr")
        
        # C. Setup and invoke the MultiQueryRetriever
        class LoggingMultiQueryRetriever(MultiQueryRetriever):
            """A custom retriever to capture the generated queries."""
            generated_queries: List[str] = []
            def _get_relevant_documents(self, question: str, **kwargs):
                # LangChain's MultiQueryRetriever generates queries and then runs them.
                # We tap into this process to log the queries.
                # Note: This is an adaptation of the internal logic for logging purposes.
                from langchain.chains.llm import LLMChain
                from langchain.output_parsers.list import LineListOutputParser
                
                output_parser = LineListOutputParser()
                llm_chain = LLMChain(llm=self.llm, prompt=self.prompt, output_parser=output_parser)
                self.generated_queries = llm_chain.run(question)
                
                return super()._get_relevant_documents(question, **kwargs)

        multi_query_retriever = LoggingMultiQueryRetriever.from_llm(retriever=base_retriever, llm=self.llm_retriever)
        retrieved_docs = multi_query_retriever.invoke(user_prompt)
        
        print(f"   -> Generated {len(multi_query_retriever.generated_queries)} sub-queries.")
        return multi_query_retriever.generated_queries, retrieved_docs

    def generate_text_copy(self, intent: str, context_docs: List[Document], user_prompt: str) -> str:
        """STEP 4: Generates the post copy using a LangChain Expression Language (LCEL) chain."""
        print("4. Generating text copy with main LLM...")
        context_str = "\n- ".join([doc.page_content for doc in context_docs])
        
        prompt = _build_text_generation_prompt()
        chain = prompt | self.llm_generator | StrOutputParser()
        
        return chain.invoke({
            "intent": intent,
            "context": context_str,
            "user_prompt": user_prompt
        })

    def generate_image(self, post_text: str) -> Image.Image:
        """STEP 5: Generates an image using the diffusion model."""
        print("5. Generating image with Diffusion Model...")
        
        prompt = _build_image_prompt_generation_prompt()
        chain = prompt | self.llm_retriever | StrOutputParser() # Use faster LLM for this task
        image_prompt = chain.invoke({"post_text": post_text})
        
        print(f"   -> Generated Image Prompt: '{image_prompt}'")
        return self.diffusion_pipeline(image_prompt).images[0]

    # =======================================================================
    #  MAIN ORCHESTRATOR
    # =======================================================================

    async def create_post_pipeline(self, user_prompt: str, brand_guide_file: UploadFile, style_images: List[UploadFile]) -> ContentGenerationOutput:
        """Orchestrates the full multimodal content generation pipeline."""
        print("\n--- Starting New MULTIMODAL Content Generation Pipeline ---")
        
        brand_guide_content = (await brand_guide_file.read()).decode("utf-8")

        # Step 1: Classify intent
        intent = self.classify_intent(user_prompt)

        # Step 2: Generate captions from images
        image_captions = await self.generate_captions_from_images(style_images)
        
        # Step 3: Setup RAG and retrieve context and queries
        generated_queries, retrieved_docs = self.setup_and_retrieve_context(
            brand_guide_text=brand_guide_content,
            image_captions=image_captions,
            query=user_prompt
        )

        # Step 4: Generate post text copy
        generated_text = self.generate_text_copy(intent, retrieved_docs, user_prompt)
        
        # Step 5: Generate image
        generated_image_obj = self.generate_image(generated_text)
        generated_image_b64 = _encode_image_to_base64(generated_image_obj)

        # Step 6: Assemble and return final output
        print("--- Pipeline Finished Successfully ---\n")
        return ContentGenerationOutput(
            generated_copy_text=generated_text,
            generated_image_b64=generated_image_b64,
            classified_intent=intent,
            generated_queries=generated_queries,
            retrieved_context=[doc.page_content for doc in retrieved_docs]
        )