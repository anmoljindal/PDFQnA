import os
import fitz  # PyMuPDF
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DATA_DIR = "data"

class PdfReader:
    def __init__(self, filepath):
        """
        Initializes the PdfReader with the provided PDF file path.

        :param filepath: Path to the PDF file.
        :raises ValueError: If the file is not a PDF.
        """
        if not filepath.endswith(".pdf"):
            raise ValueError(f"Unexpected file type '{filepath}', expected a .pdf file.")
        
        self.filename = os.path.basename(filepath).split(".pdf")[0]
        try:
            self.doc = fitz.open(filepath)
        except Exception as e:
            logger.error(f"Failed to open PDF file '{filepath}': {e}")
            raise IOError(f"Failed to open PDF file '{filepath}': {e}")

    def write_image_file(self, img, img_filename):
        """
        Extracts an image from the PDF and saves it as a PNG file.

        :param img: Image object from the PDF page.
        :param img_filename: Name of the image file to save (without extension).
        """
        try:
            xref = img[0]  # Get the XREF of the image
            pixmap = fitz.Pixmap(self.doc, xref)  # Create a Pixmap

            # Convert CMYK to RGB if necessary
            if pixmap.n - pixmap.alpha > 3:
                pixmap = fitz.Pixmap(fitz.csRGB, pixmap)

            # Save the image
            output_path = os.path.join(DATA_DIR, f"{img_filename}.png")
            pixmap.save(output_path)
        except Exception as e:
            logger.error(f"Error saving image '{img_filename}': {e}")
            raise
        finally:
            pixmap = None  # Release the Pixmap object

    @staticmethod
    def write_text_file(text, filepath):
        """
        Writes text content to a file.

        :param text: Text content to save.
        :param filepath: Path to the output text file.
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(text)
        except Exception as e:
            logger.error(f"Error writing text file '{filepath}': {e}")
            raise

    def parse_pdf(self, extract_images=False):
        """
        Parses the PDF to extract text and optionally images.

        :param extract_images: Boolean flag to indicate whether to extract images.
        """
        logger.info(f"Parsing PDF: {self.filename} (Extract Images: {extract_images})")
        try:
            for page_index, page in enumerate(self.doc):
                # Extract and save page text
                text = page.get_text()
                text_file_path = os.path.join(DATA_DIR, f"{self.filename}-{page_index}.txt")
                self.write_text_file(text, text_file_path)

                if extract_images:
                    # Extract and save images
                    for image_index, img in enumerate(page.get_images(full=True), start=1):
                        img_filename = f"{self.filename}-{page_index}-{image_index}"
                        self.write_image_file(img, img_filename)

                    # Perform OCR on images and save results
                    text_page_ocr = page.get_textpage_ocr()
                    text_ocr = page.get_text(textpage=text_page_ocr)
                    ocr_file_path = os.path.join(DATA_DIR, f"{self.filename}-ocr-{page_index}.txt")
                    self.write_text_file(text_ocr, ocr_file_path)
        except Exception as e:
            logger.error(f"Error parsing PDF '{self.filename}': {e}")
            raise

    def close(self):
        """
        Closes the PDF document to release resources.
        """
        if self.doc:
            self.doc.close()