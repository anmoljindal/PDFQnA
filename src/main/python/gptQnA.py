import os
import re
import pandas as pd
import tiktoken  # for tokenization and token counting
from openai import OpenAI
from scipy.spatial.distance import cosine
from pdfReader import PdfReader

# Constants
GPT_MODELS = ["gpt-4o-mini"]
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_TOKENS = 8192  # Max token limit for embeddings
CHUNK_SIZE_TOKENS = 1000  # Chunk size to ensure tokens fit within model limits

# OpenAI Client
openai_api_key = ""
client = OpenAI(api_key=openai_api_key)

class pdfGPT:
    def __init__(self, pdf_path, data_dir="data"):
        """
        Initialize PdfProcessor with a PDF path and optional data directory.

        :param pdf_path: Path to the PDF file.
        :param data_dir: Directory to save and load intermediate files.
        """
        self.pdf_path = pdf_path
        self.data_dir = data_dir
        self.pdf_basename = os.path.basename(pdf_path).split(".pdf")[0]
        self.df = None
        os.makedirs(data_dir, exist_ok=True)

    @staticmethod
    def preprocess_text(text):
        """
        Clean and standardize the input text.
        
        :param text: Raw text.
        :return: Cleaned text.
        """
        text = text.lower()
        text = re.sub(r"\s+", " ", text)  # Normalize spaces
        text = re.sub(r"[^\w\s.,!?]", "", text)  # Remove special characters
        return text.strip()

    @staticmethod
    def tokenize_text(text, model=EMBEDDING_MODEL):
        """
        Tokenize text using tiktoken.

        :param text: Input text.
        :return: Tokenized text as a list of tokens.
        """
        enc = tiktoken.encoding_for_model(model)
        return enc.encode(text)

    @staticmethod
    def num_tokens(text, model=EMBEDDING_MODEL):
        """
        Return the number of tokens in a string.

        :param text: Input string.
        :return: Number of tokens.
        """
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))

    def chunk_text(self, text):
        """
        Chunk text into smaller segments based on token size.

        :param text: Input text.
        :return: List of text chunks.
        """
        tokens = self.tokenize_text(text)
        enc = tiktoken.encoding_for_model(EMBEDDING_MODEL)
        chunks = [
            enc.decode(tokens[i:i + CHUNK_SIZE_TOKENS])
            for i in range(0, len(tokens), CHUNK_SIZE_TOKENS)
        ]
        return chunks

    def parse_pdf(self):
        """
        Parse the PDF file into raw text and save text chunks to the data directory.
        """
        pdf_reader = PdfReader(self.pdf_path)
        try:
            pdf_reader.parse_pdf(extract_images=False)
        finally:
            pdf_reader.close()

    def create_embeddings(self):
        """
        Generate embeddings for each text chunk and save them in a DataFrame.
        """
        text_files = [
            os.path.join(self.data_dir, fname)
            for fname in os.listdir(self.data_dir)
            if fname.startswith(self.pdf_basename) and fname.endswith(".txt")
        ]
        
        data = []
        for text_file in text_files:
            with open(text_file, "r", encoding="utf-8") as file:
                raw_text = file.read()
            cleaned_text = self.preprocess_text(raw_text)
            chunks = self.chunk_text(cleaned_text)

            for chunk in chunks:
                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=chunk
                )
                embedding = response.data[0].embedding
                data.append({"text": chunk, "embedding": embedding})

        self.df = pd.DataFrame(data)

    def strings_ranked_by_relatedness(self, query, top_n=5):
        """
        Return text chunks ranked by relatedness to the query.

        :param query: User query.
        :param top_n: Number of top results to return.
        :return: Ranked strings and their relatedness scores.
        """
        query_embedding_response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query
        )
        query_embedding = query_embedding_response.data[0].embedding

        strings_and_scores = [
            (row["text"], 1 - cosine(query_embedding, row["embedding"]))
            for _, row in self.df.iterrows()
        ]
        strings_and_scores.sort(key=lambda x: x[1], reverse=True)
        strings, scores = zip(*strings_and_scores[:top_n])
        return strings, scores

    def query_message(self, query, token_budget=4096):
        """
        Construct a message for GPT with relevant chunks.

        :param query: User query.
        :param token_budget: Token limit for the context and query.
        :return: Message string.
        """
        strings, _ = self.strings_ranked_by_relatedness(query)
        introduction = (
            "Use the following document excerpts to answer the question. "
            'If the answer is not found, respond with "I could not find an answer."'
        )
        question = f"\n\nQuestion: {query}"
        message = introduction

        for string in strings:
            next_chunk = f'\n\nExcerpt:\n"""\n{string}\n"""'
            if self.num_tokens(message + next_chunk + question, model=GPT_MODELS[0]) > token_budget:
                break
            message += next_chunk

        return message + question

    def ask(self, query, top_n=5, token_budget=4096):
        """
        Answer a question using GPT based on PDF content.

        :param query: User question.
        :param top_n: Number of top relevant chunks to include.
        :param token_budget: Token limit for context and query.
        :return: GPT-generated answer.
        """
        message = self.query_message(query, token_budget=token_budget)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
        response = client.chat.completions.create(
            model=GPT_MODELS[0],
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content.strip()