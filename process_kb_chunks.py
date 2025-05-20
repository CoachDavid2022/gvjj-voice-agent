## Python Script

import fitz # PyMuPDF for PDF processing
import json
import re
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import os
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AVAChunker:
    """
    A class to process the AVA knowledge base PDF into structured JSON chunks.
    """
    def __init__(self, chunk_size=600, chunk_overlap=80, tag_keywords=None, behavior_engine_keywords=None):
        """
        Initializes the AVAChunker with chunking parameters and keyword mappings.

        Args:
        chunk_size (int): The maximum size of each text chunk.
        chunk_overlap (int): The number of overlapping characters between adjacent chunks.
        tag_keywords (dict, optional): A dictionary mapping tags to regular expression patterns. Defaults to project-specific keywords.
        behavior_engine_keywords (dict, optional): A dictionary mapping behavior engines to regular expression patterns. Defaults to project-specific keywords.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", ", ", " ", ""],
            keep_separator=True
        )
        self.tag_keywords = tag_keywords if tag_keywords else {
            "tone_user_hesitant": r"(seems hesitant|appears unsure|sounds uncertain)",
            "emotion_user_joyful": r"(sounds happy|seems excited|is enthusiastic)",
            "prosody_velvet_true": r"(gentle tone|soft voice|smoothly)",
            "consent_seeking": r"(Is now a good time|Can I tell you about)",
            "objection_price": r"(how much does it cost|what's the price)",
            "booking_stage_qualification": r"(classes for you or someone)",
        }
        self.behavior_engine_keywords = behavior_engine_keywords if behavior_engine_keywords else {
            "velvet_stack": r"(gentle pacing|smooth transitions|calming voice)",
            "rhythm_engine": r"(varied intonation|dynamic speech)",
        }

    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Processes the PDF knowledge base into a list of JSON chunks.

        Args:
        pdf_path (str): The path to the Ava Core KB PDF file.

        Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a chunk
        with its metadata and text content.
        """
        logging.info(f"Starting processing of PDF: {pdf_path}")
        chunks = []
        module_id = "general"
        current_section_heading = ""

        try:
            doc = fitz.open(pdf_path)
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text()
                lines = text.splitlines()

                for line in lines:
                    line = line.strip()
                    section_match = re.match(r"^((\d+(\.\d+)*)\s+)(.+)", line)
                    if section_match:
                        module_id = section_match.group(2).strip()
                        current_section_heading = section_match.group(4).strip()

                page_chunks = self.text_splitter.split_text(text)

                for chunk_text in page_chunks:
                    tags = self._extract_tags(chunk_text)
                    labels = self._extract_labels(chunk_text, current_section_heading, tags)
                    chunks.append({
                        "uuid": str(uuid.uuid4()),
                        "module_id": module_id,
                        "tags": list(set(tags)),
                        "labels": list(set(labels)),
                        "textcontent": chunk_text.strip(),
                        "source_location": f"Page {page_num + 1}, Section: {current_section_heading}"
                    })
            doc.close()
            logging.info(f"Successfully processed {len(chunks)} chunks from {pdf_path}")
        except FileNotFoundError:
            logging.error(f"Error: PDF file not found at {pdf_path}")
        except Exception as e:
            logging.error(f"An error occurred during PDF processing: {e}")
        return chunks

    def _extract_tags(self, chunk_text: str) -> List[str]:
        """
        Extracts relevant tags from the chunk text based on explicit mentions and keywords.

        Args:
        chunk_text (str): The text content of the chunk.

        Returns:
        List[str]: A list of extracted tags.
        """
        tags = set(re.findall(r"tag: ([a-zA-Z0-9_=]+)", chunk_text))
        for tag, pattern in self.tag_keywords.items():
            if re.search(pattern, chunk_text, re.IGNORECASE):
                tags.add(tag)
        for engine, pattern in self.behavior_engine_keywords.items():
            if re.search(pattern, chunk_text, re.IGNORECASE):
                tags.add(f"behavior_engine={engine}")
        return list(tags)

    def _extract_labels(self, chunk_text: str, section_heading: str, tags: List[str]) -> List[str]:
        """
        Extracts relevant labels for the chunk based on its content, section heading, and tags.

        Args:
        chunk_text (str): The text content of the chunk.
        section_heading (str): The heading of the section the chunk belongs to.
        tags (List[str]): The list of tags associated with the chunk.

        Returns:
        List[str]: A list of extracted labels.
        """
        labels = set()
        if section_heading:
            labels.add(section_heading.lower().replace(" ", "_"))
        if "greeting" in chunk_text.lower():
            labels.add("greeting_related")
        if "booking" in chunk_text.lower():
            labels.add("booking_related")
        if "objection" in chunk_text.lower():
            labels.add("objection_related")
        if any(tag.startswith("emotion_user") for tag in tags):
            labels.add("user_emotion_context")
        if any(tag.startswith("tone_user") for tag in tags):
            labels.add("user_tone_context")
        return list(labels)

def main(pdf_file: str, output_file: str, chunk_size: int = 500, chunk_overlap: int = 100):
    """
    Main function to initialize the AVAChunker and process the knowledge base.

    Args:
    pdf_file (str): The path to the Ava Core KB PDF file.
    output_file (str): The path to save the processed JSON chunks.
    chunk_size (int, optional): The maximum size of each text chunk. Defaults to 500.
    chunk_overlap (int, optional): The number of overlapping characters between adjacent chunks. Defaults to 100.
    """
    logging.info("Starting AVA Knowledge Base Chunking Process")
    chunker = AVAChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    processed_chunks = chunker.process_pdf(pdf_file)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(processed_chunks, f, indent=4)
            logging.info(f"✅ Successfully processed {len(processed_chunks)} chunks and saved to {output_file}")
    except IOError as e:
        logging.error(f"Error writing to output file {output_file}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during JSON serialization: {e}")

if __name__ == "__main__":
    KB_FILE = "Ava Core KB_4-25-25.pdf"
    OUTPUT_FILE = "ava_kb_chunks_production.json"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

    # Ensure the KB file exists
    if not os.path.exists(KB_FILE):
        logging.error(f"Error: Knowledge Base file not found at {KB_FILE}")
    else:
        main(KB_FILE, OUTPUT_FILE, CHUNK_SIZE, CHUNK_OVERLAP)
