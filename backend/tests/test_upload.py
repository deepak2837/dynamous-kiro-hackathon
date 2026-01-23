import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
from app.main import app
from app.services.file_processor import FileProcessor
from app.services.processing import ProcessingService

client = TestClient(app)

class TestUploadEndpoints:
    """Test cases for file upload endpoints"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.test_token = "Bearer valid_token"
        self.test_user_id = "user123"
        self.test_session_id = "session123"
        
        # Mock authentication
        self.auth_patcher = patch('app.api.upload_basic.get_current_user')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = self.test_user_id

    def teardown_method(self):
        """Cleanup after tests"""
        self.auth_patcher.stop()

    @patch('app.services.processing.ProcessingService.process_files')
    def test_upload_files_success(self, mock_process_files):
        """Test successful file upload"""
        mock_process_files.return_value = self.test_session_id
        
        # Create test file
        test_file_content = b"Test PDF content"
        test_file = ("test.pdf", BytesIO(test_file_content), "application/pdf")
        
        response = client.post(
            "/api/v1/upload/",
            files={"files": test_file},
            headers={"Authorization": self.test_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == self.test_session_id
        assert data["message"] == "Files uploaded and processing started"
        assert data["files_count"] == 1
        assert data["processing_started"] is True

    def test_upload_files_no_auth(self):
        """Test file upload without authentication"""
        test_file = ("test.pdf", BytesIO(b"content"), "application/pdf")
        
        response = client.post(
            "/api/v1/upload/",
            files={"files": test_file}
        )
        
        assert response.status_code == 401

    def test_upload_files_no_files(self):
        """Test upload endpoint with no files"""
        response = client.post(
            "/api/v1/upload/",
            headers={"Authorization": self.test_token}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "No files provided" in data["detail"]

    @patch('app.services.processing.ProcessingService.process_files')
    def test_upload_files_with_session_name(self, mock_process_files):
        """Test file upload with custom session name"""
        mock_process_files.return_value = self.test_session_id
        
        test_file = ("test.pdf", BytesIO(b"content"), "application/pdf")
        
        response = client.post(
            "/api/v1/upload/",
            files={"files": test_file},
            data={"session_name": "My Study Session"},
            headers={"Authorization": self.test_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == self.test_session_id

    @patch('app.services.processing.ProcessingService.process_text_input')
    def test_text_input_success(self, mock_process_text):
        """Test successful text input processing"""
        mock_process_text.return_value = self.test_session_id
        
        response = client.post(
            "/api/v1/text-input/",
            json={
                "text": "This is study material content about anatomy.",
                "session_name": "Anatomy Notes"
            },
            headers={"Authorization": self.test_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == self.test_session_id
        assert data["message"] == "Text processing started"
        assert data["processing_started"] is True

    def test_text_input_no_auth(self):
        """Test text input without authentication"""
        response = client.post(
            "/api/v1/text-input/",
            json={"text": "Study content"}
        )
        
        assert response.status_code == 401

    def test_text_input_empty_text(self):
        """Test text input with empty text"""
        response = client.post(
            "/api/v1/text-input/",
            json={"text": ""},
            headers={"Authorization": self.test_token}
        )
        
        assert response.status_code == 422

    @patch('app.services.progress_tracker.ProgressTracker.get_status')
    def test_get_status_success(self, mock_get_status):
        """Test successful status retrieval"""
        mock_status = {
            "session_id": self.test_session_id,
            "status": "processing",
            "progress": 65,
            "current_step": "Generating questions",
            "estimated_completion": "2026-01-23T10:30:00Z",
            "error": None
        }
        mock_get_status.return_value = mock_status
        
        response = client.get(
            f"/api/v1/upload/status/{self.test_session_id}",
            headers={"Authorization": self.test_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == self.test_session_id
        assert data["status"] == "processing"
        assert data["progress"] == 65

    def test_get_status_no_auth(self):
        """Test status retrieval without authentication"""
        response = client.get(f"/api/v1/upload/status/{self.test_session_id}")
        
        assert response.status_code == 401

    @patch('app.services.progress_tracker.ProgressTracker.get_status')
    def test_get_status_not_found(self, mock_get_status):
        """Test status retrieval for non-existent session"""
        mock_get_status.return_value = None
        
        response = client.get(
            f"/api/v1/upload/status/nonexistent",
            headers={"Authorization": self.test_token}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Session not found" in data["detail"]

class TestFileProcessor:
    """Test cases for FileProcessor class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.file_processor = FileProcessor()
        self.test_session_id = "session123"

    def test_validate_file_type_pdf(self):
        """Test PDF file type validation"""
        result = self.file_processor.validate_file_type("test.pdf", "application/pdf")
        assert result is True

    def test_validate_file_type_image(self):
        """Test image file type validation"""
        result = self.file_processor.validate_file_type("test.jpg", "image/jpeg")
        assert result is True
        
        result = self.file_processor.validate_file_type("test.png", "image/png")
        assert result is True

    def test_validate_file_type_pptx(self):
        """Test PowerPoint file type validation"""
        result = self.file_processor.validate_file_type("test.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
        assert result is True

    def test_validate_file_type_invalid(self):
        """Test invalid file type validation"""
        result = self.file_processor.validate_file_type("test.txt", "text/plain")
        assert result is False

    def test_validate_file_size_valid(self):
        """Test valid file size validation"""
        # 10MB file
        result = self.file_processor.validate_file_size(10 * 1024 * 1024)
        assert result is True

    def test_validate_file_size_invalid(self):
        """Test invalid file size validation"""
        # 60MB file (exceeds 50MB limit)
        result = self.file_processor.validate_file_size(60 * 1024 * 1024)
        assert result is False

    @patch('PyPDF2.PdfReader')
    def test_extract_text_from_pdf_success(self, mock_pdf_reader):
        """Test successful PDF text extraction"""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample PDF text content"
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        result = self.file_processor.extract_text_from_pdf("test.pdf")
        
        assert result == "Sample PDF text content"

    @patch('PyPDF2.PdfReader')
    def test_extract_text_from_pdf_failure(self, mock_pdf_reader):
        """Test PDF text extraction failure"""
        mock_pdf_reader.side_effect = Exception("PDF read error")
        
        result = self.file_processor.extract_text_from_pdf("test.pdf")
        
        assert result == ""

    @patch('pytesseract.image_to_string')
    @patch('PIL.Image.open')
    def test_extract_text_from_image_success(self, mock_image_open, mock_ocr):
        """Test successful image text extraction"""
        mock_ocr.return_value = "Sample image text content"
        mock_image_open.return_value = Mock()
        
        result = self.file_processor.extract_text_from_image("test.jpg")
        
        assert result == "Sample image text content"

    @patch('pytesseract.image_to_string')
    @patch('PIL.Image.open')
    def test_extract_text_from_image_failure(self, mock_image_open, mock_ocr):
        """Test image text extraction failure"""
        mock_ocr.side_effect = Exception("OCR error")
        
        result = self.file_processor.extract_text_from_image("test.jpg")
        
        assert result == ""

    @patch('pptx.Presentation')
    def test_extract_text_from_pptx_success(self, mock_presentation):
        """Test successful PowerPoint text extraction"""
        mock_shape = Mock()
        mock_shape.has_text_frame = True
        mock_shape.text = "Slide text content"
        
        mock_slide = Mock()
        mock_slide.shapes = [mock_shape]
        
        mock_ppt = Mock()
        mock_ppt.slides = [mock_slide]
        mock_presentation.return_value = mock_ppt
        
        result = self.file_processor.extract_text_from_pptx("test.pptx")
        
        assert "Slide text content" in result

    @patch('pptx.Presentation')
    def test_extract_text_from_pptx_failure(self, mock_presentation):
        """Test PowerPoint text extraction failure"""
        mock_presentation.side_effect = Exception("PPTX read error")
        
        result = self.file_processor.extract_text_from_pptx("test.pptx")
        
        assert result == ""

    @patch('app.services.file_processor.FileProcessor.extract_text_from_pdf')
    def test_process_file_pdf(self, mock_extract_pdf):
        """Test processing PDF file"""
        mock_extract_pdf.return_value = "PDF content"
        
        result = self.file_processor.process_file("test.pdf", "application/pdf")
        
        assert result == "PDF content"
        mock_extract_pdf.assert_called_once_with("test.pdf")

    @patch('app.services.file_processor.FileProcessor.extract_text_from_image')
    def test_process_file_image(self, mock_extract_image):
        """Test processing image file"""
        mock_extract_image.return_value = "Image content"
        
        result = self.file_processor.process_file("test.jpg", "image/jpeg")
        
        assert result == "Image content"
        mock_extract_image.assert_called_once_with("test.jpg")

    @patch('app.services.file_processor.FileProcessor.extract_text_from_pptx')
    def test_process_file_pptx(self, mock_extract_pptx):
        """Test processing PowerPoint file"""
        mock_extract_pptx.return_value = "PPTX content"
        
        result = self.file_processor.process_file("test.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
        
        assert result == "PPTX content"
        mock_extract_pptx.assert_called_once_with("test.pptx")

class TestProcessingService:
    """Test cases for ProcessingService class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processing_service = ProcessingService()
        self.test_user_id = "user123"
        self.test_session_id = "session123"

    @patch('app.services.processing.ProcessingService.save_session')
    @patch('app.services.file_processor.FileProcessor.process_file')
    @patch('app.services.ai_service.AIService.generate_all_content')
    def test_process_files_success(self, mock_generate_content, mock_process_file, mock_save_session):
        """Test successful file processing"""
        mock_process_file.return_value = "Extracted text content"
        mock_generate_content.return_value = {
            "questions": [],
            "mock_tests": [],
            "mnemonics": [],
            "cheat_sheets": [],
            "notes": {}
        }
        mock_save_session.return_value = self.test_session_id
        
        # Mock file objects
        mock_files = [Mock(filename="test.pdf", content_type="application/pdf")]
        
        result = self.processing_service.process_files(mock_files, self.test_user_id)
        
        assert result == self.test_session_id
        mock_process_file.assert_called()
        mock_generate_content.assert_called_once()

    @patch('app.services.processing.ProcessingService.save_session')
    @patch('app.services.ai_service.AIService.generate_all_content')
    def test_process_text_input_success(self, mock_generate_content, mock_save_session):
        """Test successful text input processing"""
        mock_generate_content.return_value = {
            "questions": [],
            "mock_tests": [],
            "mnemonics": [],
            "cheat_sheets": [],
            "notes": {}
        }
        mock_save_session.return_value = self.test_session_id
        
        result = self.processing_service.process_text_input(
            "Study material content", 
            self.test_user_id, 
            "Test Session"
        )
        
        assert result == self.test_session_id
        mock_generate_content.assert_called_once_with("Study material content")

    @patch('app.database.get_database')
    def test_save_session_success(self, mock_get_db):
        """Test successful session saving"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.sessions = mock_collection
        mock_collection.insert_one.return_value = Mock(inserted_id="session123")
        mock_get_db.return_value = mock_db
        
        session_data = {
            "user_id": self.test_user_id,
            "session_name": "Test Session",
            "files": [],
            "results": {}
        }
        
        result = self.processing_service.save_session(session_data)
        
        assert result is not None
        mock_collection.insert_one.assert_called_once()

    @patch('app.database.get_database')
    def test_get_session_success(self, mock_get_db):
        """Test successful session retrieval"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.sessions = mock_collection
        mock_collection.find_one.return_value = {
            "_id": "session123",
            "user_id": self.test_user_id,
            "session_name": "Test Session",
            "status": "completed"
        }
        mock_get_db.return_value = mock_db
        
        result = self.processing_service.get_session(self.test_session_id, self.test_user_id)
        
        assert result is not None
        assert result["user_id"] == self.test_user_id

    @patch('app.database.get_database')
    def test_get_session_not_found(self, mock_get_db):
        """Test session retrieval when session doesn't exist"""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.sessions = mock_collection
        mock_collection.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        result = self.processing_service.get_session("nonexistent", self.test_user_id)
        
        assert result is None
