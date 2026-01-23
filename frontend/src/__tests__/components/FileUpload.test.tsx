import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { FileUpload } from '../../components/FileUpload';

// Mock the API
const mockUploadFiles = jest.fn();
jest.mock('../../lib/studybuddy-api', () => ({
  uploadFiles: mockUploadFiles
}));

// Mock the AuthContext
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'user123', mobile: '9876543210' },
    token: 'mock-token'
  })
}));

describe('FileUpload Component', () => {
  const mockOnUploadSuccess = jest.fn();
  const mockOnUploadError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders file upload interface correctly', () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    expect(screen.getByText(/drag & drop files here/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to select files/i)).toBeInTheDocument();
    expect(screen.getByText(/supported formats: pdf, jpg, png, pptx/i)).toBeInTheDocument();
    expect(screen.getByText(/max size: 50mb per file/i)).toBeInTheDocument();
  });

  it('shows file input when clicked', () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByRole('button', { name: /select files/i });
    expect(fileInput).toBeInTheDocument();
  });

  it('validates file types correctly', async () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    
    // Create a mock file with invalid type
    const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
    
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    await waitFor(() => {
      expect(screen.getByText(/unsupported file type/i)).toBeInTheDocument();
    });
  });

  it('validates file size correctly', async () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    
    // Create a mock file that's too large (51MB)
    const largeFile = new File(['x'.repeat(51 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' });
    
    Object.defineProperty(largeFile, 'size', {
      value: 51 * 1024 * 1024,
      writable: false
    });
    
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    await waitFor(() => {
      expect(screen.getByText(/file size exceeds 50mb limit/i)).toBeInTheDocument();
    });
  });

  it('accepts valid files and shows preview', async () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [validFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /upload files/i })).toBeInTheDocument();
    });
  });

  it('allows removing selected files', async () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [validFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);

    await waitFor(() => {
      expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
    });
  });

  it('uploads files successfully', async () => {
    const mockResponse = {
      session_id: 'session123',
      message: 'Files uploaded successfully',
      files_count: 1,
      processing_started: true
    };
    
    mockUploadFiles.mockResolvedValue(mockResponse);

    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [validFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    const uploadButton = screen.getByRole('button', { name: /upload files/i });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockUploadFiles).toHaveBeenCalledWith([validFile], undefined);
      expect(mockOnUploadSuccess).toHaveBeenCalledWith(mockResponse);
    });
  });

  it('handles upload errors correctly', async () => {
    const errorMessage = 'Upload failed';
    mockUploadFiles.mockRejectedValue(new Error(errorMessage));

    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [validFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    const uploadButton = screen.getByRole('button', { name: /upload files/i });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockOnUploadError).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  it('shows loading state during upload', async () => {
    mockUploadFiles.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [validFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    const uploadButton = screen.getByRole('button', { name: /upload files/i });
    fireEvent.click(uploadButton);

    expect(uploadButton).toBeDisabled();
    expect(screen.getByText(/uploading/i)).toBeInTheDocument();
  });

  it('supports drag and drop functionality', async () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const dropZone = screen.getByText(/drag & drop files here/i).closest('div');
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });

    const dropEvent = new Event('drop', { bubbles: true });
    Object.defineProperty(dropEvent, 'dataTransfer', {
      value: {
        files: [validFile]
      }
    });

    fireEvent(dropZone!, dropEvent);

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });
  });

  it('handles multiple file selection', async () => {
    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    const fileInput = screen.getByLabelText(/file upload/i);
    
    const file1 = new File(['content1'], 'test1.pdf', { type: 'application/pdf' });
    const file2 = new File(['content2'], 'test2.jpg', { type: 'image/jpeg' });
    
    fireEvent.change(fileInput, { target: { files: [file1, file2] } });

    await waitFor(() => {
      expect(screen.getByText('test1.pdf')).toBeInTheDocument();
      expect(screen.getByText('test2.jpg')).toBeInTheDocument();
      expect(screen.getByText(/2 files selected/i)).toBeInTheDocument();
    });
  });

  it('includes session name in upload when provided', async () => {
    const mockResponse = {
      session_id: 'session123',
      message: 'Files uploaded successfully',
      files_count: 1,
      processing_started: true
    };
    
    mockUploadFiles.mockResolvedValue(mockResponse);

    render(
      <FileUpload 
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    );

    // Add session name input
    const sessionNameInput = screen.getByLabelText(/session name/i);
    fireEvent.change(sessionNameInput, { target: { value: 'My Study Session' } });

    const fileInput = screen.getByLabelText(/file upload/i);
    const validFile = new File(['content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [validFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    const uploadButton = screen.getByRole('button', { name: /upload files/i });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockUploadFiles).toHaveBeenCalledWith([validFile], 'My Study Session');
    });
  });
});
