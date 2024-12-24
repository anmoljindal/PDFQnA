# PDFQnA

**PDFQnA** is an AI-powered assistant that uses large language models (LLMs) to answer questions based on the content of a PDF file. This tool leverages state-of-the-art natural language processing (NLP) techniques and integrates with the OpenAI API to provide accurate, context-based answers from a PDF document. 

## Features
- **PDF Parsing**: Extract text and content from PDF documents.
- **Question Answering**: Ask any question, and the AI will find and return the most relevant answer from the uploaded PDF.
- **Tokenization & Embeddings**: Tokenize the content and create embeddings to enable fast and relevant question answering.
- **User-friendly Interface**: Easy-to-use Streamlit web interface to upload PDFs and ask questions.

## Project Setup

### Prerequisites
- Python 3.8+
- Docker (optional, for containerization)
- OpenAI API Key

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/anmoljindal/PDFQnA.git
   cd PDFQnA
   ```

2. **Create a virtual environment** (Optional, recommended for local setups):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OpenAI API Key**:

   You'll need to set up your OpenAI API key. For security reasons, do not hardcode it in your code.

   - Create a `.env` file in the root directory of your project.
   - Add the following line with your OpenAI key:

     ```
     OPENAI_API_KEY=your-api-key-here
     ```

   You can obtain the key from [OpenAI's website](https://platform.openai.com/).

### Running the Application

1. **Run the Streamlit app**:

   ```bash
   streamlit run src/main/python/app.py
   ```

   This will launch a local development server, and the app will be accessible at `http://localhost:8501` in your browser.

2. **Upload a PDF**:

   Once the app is running, you will be prompted to upload a PDF file. After uploading, the document will be processed, and embeddings will be created for the content.

3. **Ask Questions**:

   After the PDF has been processed, you can input your questions into the provided chat interface. The assistant will respond based on the content of the uploaded PDF.

### Docker Setup (Optional)

If you prefer to run the app inside a Docker container, follow these steps:

1. **Build the Docker image**:

   ```bash
   docker build -t pdfqna .
   ```

2. **Run the Docker container**:

   ```bash
   docker run -p 8501:8501 pdfqna
   ```

   This will start the application inside a Docker container, accessible at `http://localhost:8501`.

## File Structure

```
├───data
└───src
    └───main
        └───python
            ├───app.py            # Main entry point for Streamlit app
            ├───gptQnA.py         # Handles question answering logic
            ├───pdfReader.py      # PDF processing and parsing
            ├───config.py         # Configuration for the app (e.g., OpenAI keys)
            └───resources         # configuration files or other resources
                └───config.yaml
```

## Contributing

We welcome contributions to improve **PDFQnA**. Here are a few ways you can help:

- Report bugs or issues.
- Submit feature requests.
- Open a pull request to fix issues or add features.

If you'd like to contribute, please fork the repository and create a new branch. Submit your pull request with a detailed description of the changes you've made.

## How to Improve the Solution

Here are a few suggestions for improving the accuracy and scalability of this solution:

- **Improved PDF Parsing**: Enhance the PDF parsing logic to handle complex document structures (tables, images, etc.).
- **Better Embeddings**: Use advanced embeddings (e.g., OpenAI's latest models) for better understanding and retrieval.
- **Caching**: Implement caching for large documents to improve performance on repeated queries.
- **Error Handling**: Add more robust error handling for various file types and potential parsing issues.
- **Modularize**: Break down the functionality into smaller, reusable components to improve code readability and maintainability.
- **Scalability**: Consider using a cloud service (e.g., AWS, GCP, or Azure) for hosting the app for better scalability.

## Acknowledgments

- OpenAI for providing the API used for question answering.
- Streamlit for enabling easy creation of web applications.
- PyMuPDF (fitz) for efficient PDF processing.
