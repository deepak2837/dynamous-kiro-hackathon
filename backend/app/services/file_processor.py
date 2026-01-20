import os
import logging
from typing import List, Dict, Any, Tuple
import PyPDF2
from PIL import Image
import cv2
import numpy as np
import pdf2image
import pytesseract
import uuid
from app.config import settings
from app.services.ai_service import AIService
from app.models import TextBatch

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        self.ai_service = AIService()
    
    def create_batches(self, file_path: str, session_id: str) -> List[TextBatch]:
        """
        Create batches from a document based on page count
        If pages <= 5: create single batch
        If pages > 5: create batches of 2-3 pages each
        Returns list of TextBatch objects
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Count pages
            if file_ext == '.pdf':
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                total_pages = 1  # Single image = 1 page
            elif file_ext in ['.pptx', '.ppt']:
                # For presentations, count slides
                from pptx import Presentation
                prs = Presentation(file_path)
                total_pages = len(prs.slides)
            else:
                total_pages = 1
            
            logger.info(f"Document has {total_pages} pages")
            
            # Determine batch size
            if total_pages <= 5:
                # Single batch for small documents
                batch_size = total_pages
                logger.info("Creating single batch for small document")
            else:
                # Batches of 2-3 pages for larger documents
                batch_size = 3
                logger.info(f"Creating batches of {batch_size} pages")
            
            # Create batches
            batches = []
            batch_number = 1
            total_batches = (total_pages + batch_size - 1) // batch_size  # Ceiling division
            
            for start_page in range(1, total_pages + 1, batch_size):
                end_page = min(start_page + batch_size - 1, total_pages)
                
                batch = TextBatch(
                    batch_id=str(uuid.uuid4()),
                    session_id=session_id,
                    page_range=(start_page, end_page),
                    text_content="",  # Will be filled during extraction
                    batch_number=batch_number,
                    total_batches=total_batches
                )
                
                batches.append(batch)
                batch_number += 1
            
            logger.info(f"Created {len(batches)} batches")
            return batches
            
        except Exception as e:
            logger.error(f"Failed to create batches: {str(e)}")
            # Return single batch as fallback
            return [TextBatch(
                batch_id=str(uuid.uuid4()),
                session_id=session_id,
                page_range=(1, 1),
                text_content="",
                batch_number=1,
                total_batches=1
            )]
    
    async def extract_text_default(self, file_path: str) -> str:
        """Extract text using default method (direct extraction)"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return await self._extract_pdf_text(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                return await self._extract_image_ocr(file_path)
            elif file_ext == '.pptx':
                return await self._extract_pptx_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            return ""
    
    async def extract_text_ocr(self, file_path: str, session_id: str = None) -> str:
        """Extract text using OCR method with page-based processing"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return await self._extract_pdf_with_ocr_processing(file_path, session_id)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                return await self._extract_image_ocr(file_path)
            elif file_ext == '.pptx':
                return await self._extract_pptx_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Failed to extract text with OCR from {file_path}: {str(e)}")
            return ""
    
    async def extract_text_ocr_batched(self, file_path: str, session_id: str) -> List[TextBatch]:
        """
        Extract text using OCR with batching support
        Returns list of TextBatch objects with extracted text
        """
        try:
            # Create batches first
            batches = self.create_batches(file_path, session_id)
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                # Extract text for each batch
                for batch in batches:
                    start_page, end_page = batch.page_range
                    batch_text = await self._extract_pdf_pages_ocr(file_path, start_page, end_page)
                    batch.text_content = batch_text
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # Single image - single batch
                text = await self._extract_image_ocr(file_path)
                batches[0].text_content = text
            elif file_ext in ['.pptx', '.ppt']:
                # Extract text from presentation
                text = await self._extract_pptx_text(file_path)
                batches[0].text_content = text
            
            return batches
            
        except Exception as e:
            logger.error(f"Failed to extract text with batching: {str(e)}")
            return []
    
    async def _extract_pdf_pages_ocr(self, file_path: str, start_page: int, end_page: int) -> str:
        """Extract text from specific PDF pages using OCR"""
        try:
            # Convert specific pages to images
            images = pdf2image.convert_from_path(
                file_path,
                first_page=start_page,
                last_page=end_page
            )
            
            batch_text = ""
            for i, image in enumerate(images):
                page_num = start_page + i
                page_text = await self._ocr_image(image)
                batch_text += f"Page {page_num}:\n{page_text}\n\n"
            
            return batch_text
            
        except Exception as e:
            logger.error(f"Failed to extract PDF pages {start_page}-{end_page}: {str(e)}")
            return ""
    
    async def extract_text_ai(self, file_path: str) -> str:
        """Extract text using AI-based method (direct image analysis)"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return await self._extract_pdf_with_ai_processing(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                return await self._extract_image_with_ai(file_path)
            elif file_ext == '.pptx':
                return await self._extract_pptx_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            logger.error(f"Failed to extract text with AI from {file_path}: {str(e)}")
            return ""
    
    async def extract_text_ai_batched(self, file_path: str, session_id: str) -> List[TextBatch]:
        """
        Extract text using AI with batching support
        Returns list of TextBatch objects with extracted text
        """
        try:
            # Create batches first
            batches = self.create_batches(file_path, session_id)
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                # Convert PDF to images and process in batches
                images = pdf2image.convert_from_path(file_path)
                
                for batch in batches:
                    start_page, end_page = batch.page_range
                    # Get images for this batch (0-indexed)
                    batch_images = images[start_page-1:end_page]
                    
                    # Save images temporarily
                    temp_paths = []
                    for i, image in enumerate(batch_images):
                        temp_path = f"/tmp/batch_{batch.batch_id}_page_{start_page+i}.png"
                        image.save(temp_path)
                        temp_paths.append(temp_path)
                    
                    # Analyze with AI
                    batch_text = await self.ai_service.analyze_images(temp_paths)
                    batch.text_content = batch_text
                    
                    # Clean up temp files
                    for temp_path in temp_paths:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # Single image - single batch
                text = await self._extract_image_with_ai(file_path)
                batches[0].text_content = text
            elif file_ext in ['.pptx', '.ppt']:
                # Extract text from presentation
                text = await self._extract_pptx_text(file_path)
                batches[0].text_content = text
            
            return batches
            
        except Exception as e:
            logger.error(f"Failed to extract text with AI batching: {str(e)}")
            return []
    
    async def _extract_pdf_with_ocr_processing(self, file_path: str, session_id: str = None) -> str:
        """Enhanced PDF processing with page-based OCR"""
        try:
            # Get page count
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
            
            logger.info(f"Processing PDF with {page_count} pages")
            
            if page_count <= 5:
                # For PDFs with 5 or fewer pages, process normally
                return await self._process_small_pdf(file_path)
            else:
                # For PDFs with more than 5 pages, use batched processing
                return await self._process_large_pdf(file_path, page_count)
                
        except Exception as e:
            logger.error(f"Failed to process PDF with OCR: {str(e)}")
            return ""
    
    async def _extract_pdf_with_ai_processing(self, file_path: str) -> str:
        """Enhanced PDF processing with AI-based analysis"""
        try:
            # Convert PDF pages to images
            images = pdf2image.convert_from_path(file_path)
            
            if len(images) <= 5:
                # Process all images with AI
                return await self._process_images_with_ai(images, batch_size=len(images))
            else:
                # Process in batches of 3 pages
                return await self._process_images_with_ai(images, batch_size=3)
                
        except Exception as e:
            logger.error(f"Failed to process PDF with AI: {str(e)}")
            return ""
    
    async def _process_small_pdf(self, file_path: str) -> str:
        """Process PDF with 5 or fewer pages"""
        try:
            # Try direct text extraction first
            text = await self._extract_pdf_text(file_path)
            
            if len(text.strip()) < 100:
                # If little text found, convert to images and OCR
                images = pdf2image.convert_from_path(file_path)
                ocr_text = ""
                
                for i, image in enumerate(images):
                    page_text = await self._ocr_image(image)
                    ocr_text += f"Page {i+1}:\n{page_text}\n\n"
                
                return ocr_text
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to process small PDF: {str(e)}")
            return ""
    
    async def _process_large_pdf(self, file_path: str, page_count: int) -> str:
        """Process PDF with more than 5 pages using batched OCR"""
        try:
            # Convert all pages to images
            images = pdf2image.convert_from_path(file_path)
            
            # Process in batches of 2 pages
            batch_size = 2
            all_text = ""
            
            for i in range(0, len(images), batch_size):
                batch_images = images[i:i + batch_size]
                batch_text = ""
                
                # OCR each image in the batch
                for j, image in enumerate(batch_images):
                    page_text = await self._ocr_image(image)
                    batch_text += f"Page {i+j+1}:\n{page_text}\n\n"
                
                all_text += batch_text
            
            return all_text
            
        except Exception as e:
            logger.error(f"Failed to process large PDF: {str(e)}")
            return ""
    
    async def _process_images_with_ai(self, images: List[Image.Image], batch_size: int) -> str:
        """Process images with AI in batches"""
        try:
            all_text = ""
            
            for i in range(0, len(images), batch_size):
                batch_images = images[i:i + batch_size]
                
                # Convert images to base64 for AI processing
                image_data = []
                for j, image in enumerate(batch_images):
                    # Save image temporarily
                    temp_path = f"/tmp/page_{i+j+1}.png"
                    image.save(temp_path)
                    image_data.append(temp_path)
                
                # Send to AI for analysis
                batch_text = await self.ai_service.analyze_images(image_data)
                all_text += batch_text + "\n\n"
                
                # Clean up temp files
                for temp_path in image_data:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            return all_text
            
        except Exception as e:
            logger.error(f"Failed to process images with AI: {str(e)}")
            return ""
    
    async def _ocr_image(self, image: Image.Image) -> str:
        """Perform OCR on a single image"""
        try:
            # Convert PIL image to numpy array
            img_array = np.array(image)
            
            # Preprocess image
            processed_img = self._preprocess_image_array(img_array)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_img, config='--psm 6')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to OCR image: {str(e)}")
            return ""
    
    async def _extract_image_with_ai(self, file_path: str) -> str:
        """Extract text from image using AI"""
        try:
            return await self.ai_service.analyze_images([file_path])
        except Exception as e:
            logger.error(f"Failed to extract image with AI: {str(e)}")
            return ""
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text directly from PDF"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {str(e)}")
            return ""
    
    async def _extract_image_ocr(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Load and preprocess image
            image = cv2.imread(file_path)
            processed_img = self._preprocess_image(file_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_img, config='--psm 6')
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract image with OCR: {str(e)}")
            return ""
    
    async def _extract_pptx_text(self, file_path: str) -> str:
        """Extract text from PowerPoint files"""
        try:
            from pptx import Presentation
            
            prs = Presentation(file_path)
            text = ""
            
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract PPTX text: {str(e)}")
            return ""
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Load image
            image = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
            
        except Exception as e:
            logger.error(f"Failed to preprocess image: {str(e)}")
            return None
    
    def _preprocess_image_array(self, img_array: np.ndarray) -> np.ndarray:
        """Preprocess image array for better OCR results"""
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
            
        except Exception as e:
            logger.error(f"Failed to preprocess image array: {str(e)}")
            return img_array
