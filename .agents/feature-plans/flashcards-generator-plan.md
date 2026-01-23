# Feature: Flashcards Generator

## Feature Description
An AI-powered flashcards generation system that creates spaced repetition learning cards from medical study materials. The feature transforms uploaded content into question-answer pairs optimized for medical concept memorization, with India-specific medical terminology and MBBS curriculum alignment.

## User Story
As a medical student preparing for MBBS exams  
I want to generate flashcards from my study materials  
So that I can use spaced repetition learning to memorize medical concepts, drug names, anatomy terms, and clinical facts more effectively

## Study Buddy Integration
**Affected Components**: 
- Backend: New Flashcard model, AI service extension, API endpoints
- Frontend: New flashcards tab in ResultsViewer, flashcard study interface
- Database: New flashcards collection with spaced repetition metadata

**Processing Pipeline Impact**: 
- Extends existing upload → process → results flow
- Adds new "GENERATING_FLASHCARDS" processing step
- Integrates with current AI service for content generation

**Medical Content Impact**: 
- Enhances medical study materials with active recall format
- Supports memorization of medical terminology, drug interactions, anatomy
- Includes India-specific medical concepts and terminology

---

## CONTEXT REFERENCES

### Study Buddy Codebase Files (MUST READ)
- `backend/app/models.py` - Existing Question, Mnemonic model patterns (lines 90-130)
- `backend/app/services/ai_service.py` - AI generation patterns (generate_new_questions method)
- `frontend/src/components/ResultsViewer.tsx` - Tabbed interface pattern (lines 1-50)
- `frontend/src/types/api.ts` - TypeScript type definitions pattern (lines 1-50)
- `backend/app/api/v1/endpoints/questions.py` - API endpoint pattern

### Medical Education Patterns
- Question-answer format for medical concepts
- Spaced repetition algorithms for long-term retention
- Medical terminology with phonetic pronunciations
- Clinical scenario-based flashcards
- Drug name-mechanism-indication triplets

### Existing API Patterns
```typescript
// API client pattern from frontend/src/lib/studybuddy-api.ts
const response = await axios.get(`/api/v1/flashcards/${sessionId}`)
```

```python
# FastAPI endpoint pattern from backend/app/api/v1/endpoints/
@router.get("/flashcards/{session_id}")
async def get_session_flashcards(session_id: str, request: Request):
```

---

## IMPLEMENTATION PLAN

### Phase 1: Backend Integration
- Add Flashcard model to database schema
- Extend AI service with flashcard generation method
- Create flashcards API endpoints following existing patterns
- Add flashcard processing to main pipeline

### Phase 2: Frontend Integration  
- Add flashcards tab to ResultsViewer component
- Create FlashcardViewer component with study interface
- Implement spaced repetition study mode
- Update TypeScript types for flashcard data

### Phase 3: Medical Content Enhancement
- Implement medical-specific flashcard templates
- Add India-specific medical terminology
- Include pronunciation guides for medical terms
- Validate content quality for MBBS preparation

---

## STEP-BY-STEP TASKS

### Backend Tasks

#### UPDATE backend/app/models.py
- **IMPLEMENT**: New Flashcard model class
- **PATTERN**: Follow existing Question/Mnemonic model structure
- **IMPORTS**: `from pydantic import BaseModel, Field`
- **FIELDS**: 
  ```python
  class Flashcard(BaseModel):
      flashcard_id: str = Field(..., description="Unique flashcard identifier")
      session_id: str = Field(..., description="Associated session")
      user_id: str = Field(..., description="User identifier")
      front_text: str = Field(..., description="Question/prompt side")
      back_text: str = Field(..., description="Answer/explanation side")
      category: str = Field(..., description="Medical category (anatomy, pharmacology, etc.)")
      difficulty: DifficultyLevel = Field(..., description="Flashcard difficulty")
      medical_topic: Optional[str] = Field(None, description="Specific medical topic")
      pronunciation: Optional[str] = Field(None, description="Phonetic pronunciation")
      spaced_repetition_data: Dict[str, Any] = Field(default={}, description="SR algorithm data")
      created_at: datetime = Field(default_factory=datetime.utcnow)
  ```
- **VALIDATE**: `python -c "from app.models import Flashcard"`

#### UPDATE backend/app/services/ai_service.py  
- **IMPLEMENT**: `generate_flashcards` method
- **PATTERN**: Follow existing `generate_new_questions` pattern (line 176)
- **MEDICAL**: Include India-specific medical prompts
- **PROMPT TEMPLATE**:
  ```python
  async def generate_flashcards(self, text: str, num_cards: int = 20) -> List[Dict[str, Any]]:
      operation = "GENERATE_FLASHCARDS"
      
      prompt = f"""Generate {num_cards} medical flashcards from this content.
      
      Focus on:
      - Medical terminology with pronunciations
      - Drug names, mechanisms, indications
      - Anatomy structures and functions
      - Clinical signs and symptoms
      - India-specific medical practices
      
      Format each flashcard as:
      {{
          "front": "Question or term",
          "back": "Answer or explanation", 
          "category": "anatomy|pharmacology|pathology|physiology|clinical",
          "difficulty": "easy|medium|hard",
          "medical_topic": "specific topic",
          "pronunciation": "phonetic guide if applicable"
      }}
      
      Content: {text[:4000]}
      
      Return valid JSON array of flashcards."""
  ```
- **VALIDATE**: `python -m pytest tests/test_ai_service.py::test_generate_flashcards`

#### CREATE backend/app/api/v1/endpoints/flashcards.py
- **IMPLEMENT**: Flashcards API endpoints
- **PATTERN**: Follow existing questions.py structure
- **ENDPOINTS**:
  ```python
  @router.get("/flashcards/{session_id}")
  async def get_session_flashcards(session_id: str, request: Request):
      # Get flashcards for session
      
  @router.post("/flashcards/{flashcard_id}/review")
  async def review_flashcard(flashcard_id: str, review_data: FlashcardReview):
      # Update spaced repetition data
      
  @router.get("/flashcards/{session_id}/study")
  async def get_study_flashcards(session_id: str, limit: int = 10):
      # Get flashcards due for review
  ```
- **VALIDATE**: `curl -X GET http://localhost:8000/api/v1/flashcards/test-session`

#### UPDATE backend/app/services/processing.py
- **IMPLEMENT**: `_generate_flashcards` method
- **PATTERN**: Follow existing `_generate_mnemonics` pattern (line 924)
- **INTEGRATION**: Add to main processing pipeline
- **PROCESSING STEP**: Add `GENERATING_FLASHCARDS` to ProcessingStep enum
- **VALIDATE**: `python -m pytest tests/test_processing.py`

### Frontend Tasks

#### UPDATE frontend/src/types/api.ts
- **IMPLEMENT**: Flashcard TypeScript types
- **PATTERN**: Follow existing Question interface structure
- **TYPES**:
  ```typescript
  export interface Flashcard {
    flashcard_id: string;
    session_id: string;
    front_text: string;
    back_text: string;
    category: MedicalCategory;
    difficulty: DifficultyLevel;
    medical_topic?: string;
    pronunciation?: string;
    spaced_repetition_data: SpacedRepetitionData;
    created_at: string;
  }
  
  export interface SpacedRepetitionData {
    ease_factor: number;
    interval: number;
    repetitions: number;
    next_review_date: string;
    last_reviewed: string;
  }
  
  export type MedicalCategory = 'anatomy' | 'pharmacology' | 'pathology' | 'physiology' | 'clinical';
  ```
- **VALIDATE**: `npx tsc --noEmit`

#### UPDATE frontend/src/components/ResultsViewer.tsx
- **IMPLEMENT**: New flashcards tab
- **PATTERN**: Follow existing tabbed interface structure (lines 20-30)
- **TAB ADDITION**:
  ```typescript
  type ContentType = 'questions' | 'mock-tests' | 'mnemonics' | 'cheat-sheets' | 'notes' | 'flashcards';
  
  // Add to tab navigation
  <button
    onClick={() => setActiveTab('flashcards')}
    className={`tab-button ${activeTab === 'flashcards' ? 'active' : ''}`}
  >
    <FiLayers className="w-4 h-4" />
    Flashcards
  </button>
  
  // Add to content rendering
  {activeTab === 'flashcards' && (
    <FlashcardViewer flashcards={flashcards} sessionId={sessionId} />
  )}
  ```
- **VALIDATE**: `npm run build`

#### CREATE frontend/src/components/FlashcardViewer.tsx
- **IMPLEMENT**: Flashcard study interface component
- **PATTERN**: Follow existing InteractiveQuestion component structure
- **FEATURES**:
  - Card flip animation
  - Study mode with spaced repetition
  - Progress tracking
  - Category filtering
  - Pronunciation audio (text-to-speech)
- **COMPONENT STRUCTURE**:
  ```typescript
  interface FlashcardViewerProps {
    flashcards: Flashcard[];
    sessionId: string;
  }
  
  export default function FlashcardViewer({ flashcards, sessionId }: FlashcardViewerProps) {
    const [currentCard, setCurrentCard] = useState(0);
    const [showBack, setShowBack] = useState(false);
    const [studyMode, setStudyMode] = useState(false);
    
    // Spaced repetition logic
    // Card flip animations
    // Progress tracking
    // Category filtering
  }
  ```
- **VALIDATE**: `npm run dev && curl http://localhost:3000/study-buddy`

#### UPDATE frontend/src/lib/studybuddy-api.ts
- **IMPLEMENT**: Flashcard API client methods
- **PATTERN**: Follow existing API method structure
- **METHODS**:
  ```typescript
  async getSessionFlashcards(sessionId: string): Promise<Flashcard[]> {
    const response = await this.api.get(`/flashcards/${sessionId}`);
    return response.data;
  }
  
  async reviewFlashcard(flashcardId: string, reviewData: FlashcardReview): Promise<void> {
    await this.api.post(`/flashcards/${flashcardId}/review`, reviewData);
  }
  
  async getStudyFlashcards(sessionId: string, limit: number = 10): Promise<Flashcard[]> {
    const response = await this.api.get(`/flashcards/${sessionId}/study?limit=${limit}`);
    return response.data;
  }
  ```
- **VALIDATE**: `npx tsc --noEmit`

---

## TESTING STRATEGY

### Backend Tests (pytest)
- **Unit Tests**: 
  - `test_flashcard_model()` - Pydantic model validation
  - `test_generate_flashcards()` - AI service flashcard generation
  - `test_spaced_repetition_algorithm()` - SR logic validation
- **API Tests**:
  - `test_get_session_flashcards()` - Endpoint functionality
  - `test_review_flashcard()` - Review data update
  - `test_flashcard_study_mode()` - Study session logic
- **Medical Content Tests**:
  - `test_medical_terminology_accuracy()` - Content quality
  - `test_india_specific_content()` - Regional relevance
  - `test_pronunciation_generation()` - Phonetic accuracy

### Frontend Tests (Jest)
- **Component Tests**:
  - `FlashcardViewer.test.tsx` - Component rendering and interactions
  - `FlashcardStudyMode.test.tsx` - Study mode functionality
  - `SpacedRepetitionLogic.test.tsx` - SR algorithm frontend logic
- **API Integration Tests**:
  - `flashcard-api.test.ts` - API client method testing
  - `flashcard-types.test.ts` - TypeScript type validation

### Medical Content Tests
- **Content Quality**: Validate medical accuracy of generated flashcards
- **India-Specific Terms**: Ensure regional medical terminology inclusion
- **MBBS Alignment**: Verify curriculum relevance
- **Pronunciation Accuracy**: Test phonetic guide quality

---

## VALIDATION COMMANDS

### Backend Validation
```bash
cd backend

# Test model creation
python -c "from app.models import Flashcard; print('Flashcard model imported successfully')"

# Test AI service
python -m pytest tests/test_ai_service.py::test_generate_flashcards -v

# Test API endpoints
uvicorn app.main:app --reload --port 8001 &
sleep 3
curl -X GET http://localhost:8001/api/v1/flashcards/test-session-id
curl -X GET http://localhost:8001/docs | grep flashcards

# Test processing integration
python -m pytest tests/test_processing.py::test_flashcard_generation -v
```

### Frontend Validation
```bash
cd frontend

# TypeScript validation
npx tsc --noEmit

# Component build test
npm run build

# Development server test
npm run dev &
sleep 5
curl -X GET http://localhost:3000 | grep -i flashcard

# Component testing
npm test -- FlashcardViewer.test.tsx
```

### Integration Validation
```bash
# Test full flashcard generation pipeline
cd backend
python -c "
import asyncio
from app.services.ai_service import AIService
from app.services.processing import ProcessingService

async def test_flashcard_pipeline():
    ai_service = AIService()
    processing_service = ProcessingService()
    
    # Test flashcard generation
    sample_text = 'The heart has four chambers: right atrium, right ventricle, left atrium, left ventricle.'
    flashcards = await ai_service.generate_flashcards(sample_text, 5)
    print(f'Generated {len(flashcards)} flashcards')
    
    for card in flashcards:
        print(f'Front: {card[\"front\"]}')
        print(f'Back: {card[\"back\"]}')
        print(f'Category: {card[\"category\"]}')
        print('---')

asyncio.run(test_flashcard_pipeline())
"

# Test API endpoint with real data
curl -X POST http://localhost:8000/api/v1/flashcards/test-session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"text": "The cardiovascular system consists of the heart, blood vessels, and blood."}'
```

---

## ACCEPTANCE CRITERIA

- [ ] **Seamless Integration**: Flashcards appear as new tab in ResultsViewer
- [ ] **Medical Content Quality**: Generated flashcards meet MBBS preparation standards
- [ ] **Spaced Repetition**: Implements effective SR algorithm for long-term retention
- [ ] **India-Specific Content**: Includes regional medical terminology and practices
- [ ] **Interactive Study Mode**: Provides engaging flashcard study experience
- [ ] **Processing Pipeline**: Integrates with existing upload → process → results flow
- [ ] **Performance**: Generates 20+ flashcards within 30 seconds
- [ ] **Responsive Design**: Works seamlessly on mobile and desktop
- [ ] **Pronunciation Support**: Includes phonetic guides for medical terms
- [ ] **Category Filtering**: Allows filtering by medical category
- [ ] **Progress Tracking**: Tracks study progress and review statistics
- [ ] **API Consistency**: Follows existing Study Buddy API patterns
- [ ] **Type Safety**: Full TypeScript support with proper type definitions
- [ ] **Error Handling**: Graceful error handling and user feedback
- [ ] **Accessibility**: Keyboard navigation and screen reader support

---

## MEDICAL EDUCATION NOTES

### MBBS Curriculum Alignment
- **Anatomy**: Anatomical structures, systems, and relationships
- **Physiology**: Body functions, mechanisms, and processes  
- **Pharmacology**: Drug names, mechanisms, indications, contraindications
- **Pathology**: Disease processes, symptoms, diagnostic criteria
- **Clinical Medicine**: Signs, symptoms, differential diagnosis

### India-Specific Medical Features
- **Regional Terminology**: Hindi/local language medical terms with English equivalents
- **Indian Medical Practices**: Ayurveda integration where relevant
- **Local Disease Patterns**: India-specific epidemiology and health concerns
- **Medical Education System**: Align with Indian medical college curriculum

### Spaced Repetition Optimization
- **Initial Interval**: 1 day for new cards
- **Ease Factor**: Start at 2.5, adjust based on performance
- **Interval Multiplication**: Successful reviews increase interval
- **Difficulty Adjustment**: Failed reviews reset to shorter intervals
- **Long-term Retention**: Target 90%+ retention rate after 6 months

### Content Quality Standards
- **Medical Accuracy**: All content verified against standard medical references
- **Clarity**: Simple, clear language appropriate for medical students
- **Completeness**: Include essential context and explanations
- **Relevance**: Focus on high-yield, exam-relevant information
- **Progressive Difficulty**: Easy → Medium → Hard progression available
