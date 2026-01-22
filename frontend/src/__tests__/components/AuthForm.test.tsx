import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthForm } from '../../components/AuthForm';

// Mock the AuthContext
const mockLogin = jest.fn();
const mockRegister = jest.fn();
const mockSendOTP = jest.fn();

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    register: mockRegister,
    sendOTP: mockSendOTP,
    user: null,
    loading: false
  })
}));

describe('AuthForm Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Login Mode', () => {
    it('renders login form correctly', () => {
      render(<AuthForm mode="login" onSuccess={() => {}} />);
      
      expect(screen.getByLabelText(/mobile number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });

    it('validates mobile number format', async () => {
      render(<AuthForm mode="login" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(mobileInput, { target: { value: '123' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid 10-digit mobile number/i)).toBeInTheDocument();
      });
    });

    it('validates password requirement', async () => {
      render(<AuthForm mode="login" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });
    });

    it('calls login function with correct parameters', async () => {
      const onSuccess = jest.fn();
      mockLogin.mockResolvedValue(undefined);
      
      render(<AuthForm mode="login" onSuccess={onSuccess} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('9876543210', 'password123');
        expect(onSuccess).toHaveBeenCalled();
      });
    });
  });

  describe('Register Mode', () => {
    it('renders register form correctly', () => {
      render(<AuthForm mode="register" onSuccess={() => {}} />);
      
      expect(screen.getByLabelText(/mobile number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send otp/i })).toBeInTheDocument();
    });

    it('sends OTP when mobile number is valid', async () => {
      mockSendOTP.mockResolvedValue(undefined);
      
      render(<AuthForm mode="register" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const sendOTPButton = screen.getByRole('button', { name: /send otp/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.click(sendOTPButton);
      
      await waitFor(() => {
        expect(mockSendOTP).toHaveBeenCalledWith('9876543210');
      });
    });

    it('shows OTP input after sending OTP', async () => {
      mockSendOTP.mockResolvedValue(undefined);
      
      render(<AuthForm mode="register" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const sendOTPButton = screen.getByRole('button', { name: /send otp/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.click(sendOTPButton);
      
      await waitFor(() => {
        expect(screen.getByLabelText(/otp/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
      });
    });

    it('validates OTP format', async () => {
      mockSendOTP.mockResolvedValue(undefined);
      
      render(<AuthForm mode="register" onSuccess={() => {}} />);
      
      // First send OTP
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const sendOTPButton = screen.getByRole('button', { name: /send otp/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.click(sendOTPButton);
      
      await waitFor(() => {
        expect(screen.getByLabelText(/otp/i)).toBeInTheDocument();
      });
      
      // Try to register with invalid OTP
      const otpInput = screen.getByLabelText(/otp/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const registerButton = screen.getByRole('button', { name: /register/i });
      
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(otpInput, { target: { value: '123' } });
      fireEvent.click(registerButton);
      
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid 6-digit otp/i)).toBeInTheDocument();
      });
    });

    it('calls register function with correct parameters', async () => {
      const onSuccess = jest.fn();
      mockSendOTP.mockResolvedValue(undefined);
      mockRegister.mockResolvedValue(undefined);
      
      render(<AuthForm mode="register" onSuccess={onSuccess} />);
      
      // Send OTP first
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const sendOTPButton = screen.getByRole('button', { name: /send otp/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.click(sendOTPButton);
      
      await waitFor(() => {
        expect(screen.getByLabelText(/otp/i)).toBeInTheDocument();
      });
      
      // Complete registration
      const otpInput = screen.getByLabelText(/otp/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const registerButton = screen.getByRole('button', { name: /register/i });
      
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(otpInput, { target: { value: '123456' } });
      fireEvent.click(registerButton);
      
      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith('9876543210', 'password123', '123456');
        expect(onSuccess).toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message when login fails', async () => {
      const errorMessage = 'Invalid credentials';
      mockLogin.mockRejectedValue(new Error(errorMessage));
      
      render(<AuthForm mode="login" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('displays error message when OTP sending fails', async () => {
      const errorMessage = 'Failed to send OTP';
      mockSendOTP.mockRejectedValue(new Error(errorMessage));
      
      render(<AuthForm mode="register" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const sendOTPButton = screen.getByRole('button', { name: /send otp/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.click(sendOTPButton);
      
      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading state during login', async () => {
      mockLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      render(<AuthForm mode="login" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);
      
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/logging in/i)).toBeInTheDocument();
    });

    it('shows loading state during OTP sending', async () => {
      mockSendOTP.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      render(<AuthForm mode="register" onSuccess={() => {}} />);
      
      const mobileInput = screen.getByLabelText(/mobile number/i);
      const sendOTPButton = screen.getByRole('button', { name: /send otp/i });
      
      fireEvent.change(mobileInput, { target: { value: '9876543210' } });
      fireEvent.click(sendOTPButton);
      
      expect(sendOTPButton).toBeDisabled();
      expect(screen.getByText(/sending otp/i)).toBeInTheDocument();
    });
  });
});
