// Frontend Error Logger
class ErrorLogger {
  private static logToConsole = true;
  private static logToServer = true;
  private static apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  static logError(
    error: Error | string,
    context: string,
    userId?: string,
    additionalInfo?: Record<string, any>
  ) {
    const errorData = {
      timestamp: new Date().toISOString(),
      context,
      userId,
      error: typeof error === 'string' ? error : error.message,
      stack: typeof error === 'object' ? error.stack : undefined,
      additionalInfo,
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Log to console in development
    if (this.logToConsole && process.env.NODE_ENV === 'development') {
      console.error('Frontend Error:', errorData);
    }

    // Log to local storage for debugging
    this.logToLocalStorage(errorData);

    // Send to server (optional)
    if (this.logToServer) {
      this.sendToServer(errorData);
    }
  }

  private static logToLocalStorage(errorData: any) {
    try {
      const existingLogs = JSON.parse(localStorage.getItem('error_logs') || '[]');
      existingLogs.push(errorData);
      
      // Keep only last 50 errors
      if (existingLogs.length > 50) {
        existingLogs.splice(0, existingLogs.length - 50);
      }
      
      localStorage.setItem('error_logs', JSON.stringify(existingLogs));
    } catch (e) {
      console.error('Failed to log error to localStorage:', e);
    }
  }

  private static async sendToServer(errorData: any) {
    try {
      await fetch(`${this.apiUrl}/api/v1/logs/frontend-error`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorData),
      });
    } catch (e) {
      // Silently fail - don't log errors about logging errors
    }
  }

  static getStoredErrors(): any[] {
    try {
      return JSON.parse(localStorage.getItem('error_logs') || '[]');
    } catch (e) {
      return [];
    }
  }

  static clearStoredErrors() {
    localStorage.removeItem('error_logs');
  }
}

export default ErrorLogger;
