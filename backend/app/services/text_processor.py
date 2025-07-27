import PyPDF2
import docx
import markdown
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List
import logging
import aiofiles

from ..core.config import settings

logger = logging.getLogger(__name__)

class TextProcessor:
    
    async def extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file type and extract text
        if file_path.suffix.lower() == '.pdf':
            return await self._extract_from_pdf(file_path)
        elif file_path.suffix.lower() == '.docx':
            return await self._extract_from_docx(file_path)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            return await self._extract_from_text(file_path)
        elif file_path.suffix.lower() == '.html':
            return await self._extract_from_html(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into chunks with overlap"""
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap or settings.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence or word boundary
            if end < len(text):
                # Look for sentence ending
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    # Private extraction methods
    
    async def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return text.strip()
    
    async def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    
    async def _extract_from_text(self, file_path: Path) -> str:
        """Extract text from plain text or markdown file"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            content = await file.read()
        
        # If it's markdown, convert to plain text
        if file_path.suffix.lower() == '.md':
            html = markdown.markdown(content)
            soup = BeautifulSoup(html, 'html.parser')
            content = soup.get_text()
        
        return content.strip()
    
    async def _extract_from_html(self, file_path: Path) -> str:
        """Extract text from HTML file"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            content = await file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        # Clean up extra whitespace
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)