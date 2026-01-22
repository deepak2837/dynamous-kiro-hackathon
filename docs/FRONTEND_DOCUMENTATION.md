# Frontend Documentation - Study Buddy App

## Overview

The Study Buddy frontend is built with Next.js 14, React 18, TypeScript, and TailwindCSS. It provides a modern, responsive interface for medical students to upload study materials and generate AI-powered study resources.

## Architecture

### Tech Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: React Context API
- **HTTP Client**: Fetch API
- **Authentication**: JWT with OTP verification

### Directory Structure

```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Home page with Study Buddy card
│   ├── login/             # Login page
│   ├── register/          # Registration page
│   └── study-buddy/       # Study Buddy main page
├── components/            # React components
│   ├── AuthForm.tsx       # Authentication form
│   ├── FileUpload.tsx     # File upload with drag-and-drop
│   ├── Header.tsx         # Navigation header
│   ├── InteractiveQuestion.tsx  # Question display component
│   ├── MockTestDialog.tsx # Mock test modal
│   ├── MockTestInterface.tsx    # Mock test UI
│   ├── MockTestResults.tsx      # Test results display
│   ├── ProcessingStatus.tsx     # Progress indicator
│   ├── ResultsViewer.tsx        # Main results container
│   └── SessionHistory.tsx       # Session history viewer
├── contexts/              # React contexts
│   └── AuthContext.tsx    # Authentication state management
├── lib/                   # Utilities and API clients
│   ├── api.ts            # Generic API utilities
│   └── studybuddy-api.ts # Study Buddy specific API calls
├── types/                 # TypeScript type definitions
│   └── api.ts            # API response types
└── utils/                 # Helper functions
    └── errorLogger.ts     # Error logging utility
```

## Core Components

### 1. Authentication System

#### AuthContext (`src/contexts/AuthContext.tsx`)
Manages global authentication state using React Context.

**Features:**
- JWT token management
- User session persistence
- Login/logout functionality
- OTP verification flow

**Key Methods:**
```typescript
interface AuthContextType {
  user: User | null;
  login: (mobile: string, password: string) => Promise<void>;
  register: (mobile: string, password: string, otp: string) => Promise<void>;
  logout: () => void;
  sendOTP: (mobile: string) => Promise<void>;
  verifyOTP: (mobile: string, otp: string) => Promise<void>;
}
```

#### AuthForm (`src/components/AuthForm.tsx`)
Reusable authentication form component supporting both login and registration.

**Props:**
- `mode`: 'login' | 'register'
- `onSuccess`: Callback function on successful authentication

### 2. File Upload System

#### FileUpload (`src/components/FileUpload.tsx`)
Advanced file upload component with drag-and-drop support.

**Features:**
- Drag and drop interface
- Multiple file selection
- File type validation (PDF, JPG, PNG, PPTX)
- File size validation (50MB limit)
- Upload progress tracking
- Preview of selected files

**Supported File Types:**
- PDF documents
- Images (JPG, PNG)
- PowerPoint presentations (PPTX)

### 3. Processing System

#### ProcessingStatus (`src/components/ProcessingStatus.tsx`)
Real-time processing status display with progress tracking.

**Features:**
- Progress bar with percentage
- Current processing step display
- Estimated completion time
- Error handling and retry options

**Processing Steps:**
1. File upload validation
2. Text extraction
3. AI content generation
4. Results compilation

### 4. Results Display System

#### ResultsViewer (`src/components/ResultsViewer.tsx`)
Main container for displaying all generated study materials.

**Features:**
- Tabbed interface for different content types
- Search and filter functionality
- Export options
- Responsive design

**Content Types:**
- Questions (MCQs with explanations)
- Mock Tests (Timed assessments)
- Mnemonics (Memory aids)
- Cheat Sheets (Key points summary)
- Notes (Compiled study materials)

#### InteractiveQuestion (`src/components/InteractiveQuestion.tsx`)
Individual question display component with interactive features.

**Features:**
- Multiple choice options
- Answer selection
- Explanation display
- Difficulty indicators
- Subject categorization

### 5. Mock Test System

#### MockTestInterface (`src/components/MockTestInterface.tsx`)
Complete mock test taking interface.

**Features:**
- Timer functionality
- Question navigation
- Answer tracking
- Auto-submit on time completion
- Progress indicators

#### MockTestResults (`src/components/MockTestResults.tsx`)
Detailed test results and analytics.

**Features:**
- Score calculation
- Question-wise analysis
- Performance metrics
- Retry options

### 6. Session Management

#### SessionHistory (`src/components/SessionHistory.tsx`)
Display and manage previous study sessions.

**Features:**
- Session list with metadata
- Search and filter options
- Session deletion
- Quick access to results

## API Integration

### StudyBuddy API Client (`src/lib/studybuddy-api.ts`)

**Core Functions:**

```typescript
// File upload
export const uploadFiles = async (files: File[], sessionName?: string): Promise<UploadResponse>

// Text input processing
export const processTextInput = async (text: string, sessionName?: string): Promise<ProcessResponse>

// Get processing status
export const getProcessingStatus = async (sessionId: string): Promise<StatusResponse>

// Fetch results
export const getSessionResults = async (sessionId: string): Promise<SessionResults>

// Get session history
export const getSessionHistory = async (): Promise<SessionHistoryResponse>

// Delete session
export const deleteSession = async (sessionId: string): Promise<void>
```

### Authentication API (`src/lib/api.ts`)

```typescript
// Send OTP
export const sendOTP = async (mobile: string): Promise<void>

// Verify OTP
export const verifyOTP = async (mobile: string, otp: string): Promise<void>

// Login
export const login = async (mobile: string, password: string): Promise<LoginResponse>

// Register
export const register = async (mobile: string, password: string, otp: string): Promise<RegisterResponse>
```

## State Management

### Authentication State
Managed through React Context with localStorage persistence.

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}
```

### Component State
Individual components manage their own state using React hooks:
- `useState` for local component state
- `useEffect` for side effects and API calls
- Custom hooks for reusable logic

## Styling System

### TailwindCSS Configuration
Custom configuration in `tailwind.config.js`:

```javascript
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
        accent: '#F59E0B'
      }
    }
  }
}
```

### Design System
- **Colors**: Blue primary, green secondary, amber accent
- **Typography**: System fonts with proper hierarchy
- **Spacing**: Consistent 4px grid system
- **Components**: Reusable utility classes

## Error Handling

### Error Logger (`src/utils/errorLogger.ts`)
Centralized error logging and reporting system.

**Features:**
- Client-side error capture
- API error handling
- User-friendly error messages
- Error reporting to backend

### Error Boundaries
React error boundaries for graceful error handling:
- Component-level error catching
- Fallback UI display
- Error reporting

## Performance Optimization

### Code Splitting
- Route-based code splitting with Next.js
- Dynamic imports for heavy components
- Lazy loading of non-critical features

### Caching Strategy
- API response caching
- Image optimization with Next.js
- Static asset caching

### Bundle Optimization
- Tree shaking for unused code
- Minification and compression
- Optimal chunk splitting

## Security Measures

### Authentication Security
- JWT token validation
- Secure token storage
- Automatic token refresh
- Session timeout handling

### Input Validation
- Client-side form validation
- File type and size validation
- XSS prevention
- CSRF protection

### API Security
- Request authentication headers
- Rate limiting awareness
- Secure API endpoints

## Testing Strategy

### Unit Testing
- Component testing with React Testing Library
- Hook testing with custom test utilities
- API client testing with mocked responses

### Integration Testing
- End-to-end user flows
- API integration testing
- Authentication flow testing

### Performance Testing
- Bundle size monitoring
- Runtime performance profiling
- Memory leak detection

## Development Workflow

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Environment Configuration
- `.env.local` for local development
- `.env.example` for environment template
- Environment-specific API endpoints

## Deployment

### Build Process
1. TypeScript compilation
2. Next.js optimization
3. Static asset generation
4. Bundle analysis

### Production Considerations
- Environment variable configuration
- CDN setup for static assets
- Performance monitoring
- Error tracking

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Progressive Enhancement
- Core functionality without JavaScript
- Graceful degradation for older browsers
- Responsive design for all screen sizes

## Accessibility

### WCAG Compliance
- Semantic HTML structure
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

### Accessibility Features
- Alt text for images
- ARIA labels and roles
- Focus management
- Skip navigation links

## Future Enhancements

### Planned Features
- Offline mode support
- Push notifications
- Advanced analytics
- Collaborative features

### Technical Improvements
- Service worker implementation
- Advanced caching strategies
- Performance optimizations
- Enhanced error handling

## Troubleshooting

### Common Issues
1. **Authentication failures**: Check token expiration and API endpoints
2. **File upload errors**: Verify file size and type restrictions
3. **Processing timeouts**: Check backend service status
4. **Display issues**: Verify responsive design breakpoints

### Debug Tools
- React Developer Tools
- Network tab for API debugging
- Console logging for state inspection
- Performance profiler for optimization

## API Endpoints Reference

### Base Configuration
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### Endpoint List
- `POST /api/v1/auth/send-otp` - Send OTP
- `POST /api/v1/auth/verify-otp` - Verify OTP
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/upload/` - File upload
- `POST /api/v1/text-input/` - Text processing
- `GET /api/v1/history/sessions` - Session history
- `GET /api/v1/sessions/{id}/results` - Session results
- `DELETE /api/v1/sessions/{id}` - Delete session
