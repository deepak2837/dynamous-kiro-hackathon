# Study Buddy App - Database Schema Documentation

## 📊 MongoDB Database Design

Complete database schema for Study Buddy App with collections, relationships, and indexing strategies.

---

## 🗄️ Database Overview

- **Database Name**: `studybuddy` (development) / `studybuddy_prod` (production)
- **Database Type**: MongoDB 6.0+
- **Connection**: `mongodb://localhost:27017`
- **ODM**: Motor (async PyMongo)

---

## 📋 Collections Schema

### 1. users
User authentication and profile information.

```javascript
{
  _id: ObjectId,
  mobile: String, // Unique mobile number
  password: String, // Hashed password
  name: String,
  email: String,
  created_at: ISODate,
  last_login: ISODate,
  is_active: Boolean,
  profile: {
    medical_year: String, // "1st Year", "2nd Year", etc.
    college: String,
    specialization: String,
    study_preferences: {
      difficulty_level: String, // "Easy", "Medium", "Hard"
      subjects: [String],
      study_hours_per_day: Number
    }
  }
}
```

### 2. study_sessions
Main session tracking for uploaded content and generated materials.

```javascript
{
  _id: ObjectId,
  session_id: String, // UUID
  user_id: ObjectId, // Reference to users._id
  session_name: String,
  created_at: ISODate,
  updated_at: ISODate,
  files_uploaded: [{
    filename: String,
    original_name: String,
    file_type: String, // "pdf", "jpg", "png", "pptx"
    file_size: Number,
    file_path: String,
    processing_mode: String // "default", "ocr", "ai-based"
  }],
  text_input: String, // Direct text input
  processing_status: String, // "pending", "processing", "completed", "failed"
  progress: Number, // 0-100
  error_message: String,
  outputs_generated: {
    questions: Boolean,
    mock_tests: Boolean,
    mnemonics: Boolean,
    cheat_sheets: Boolean,
    notes: Boolean,
    flashcards: Boolean
  },
  metadata: {
    total_questions: Number,
    total_flashcards: Number,
    processing_time_seconds: Number,
    ai_tokens_used: Number
  }
}
```

### 3. questions
Generated MCQ questions from study materials.

```javascript
{
  _id: ObjectId,
  question_id: String, // UUID
  session_id: String, // Reference to study_sessions.session_id
  user_id: ObjectId,
  question_text: String,
  options: [{
    option_id: String, // "A", "B", "C", "D"
    text: String,
    is_correct: Boolean
  }],
  correct_answer: String, // "A", "B", "C", "D"
  explanation: String,
  difficulty: String, // "Easy", "Medium", "Hard"
  medical_subject: String, // "Anatomy", "Physiology", etc.
  medical_system: String, // "Cardiovascular", "Respiratory", etc.
  tags: [String],
  bloom_taxonomy: String, // "Remember", "Understand", "Apply", etc.
  created_at: ISODate,
  source_content: String // Original text that generated this question
}
```

### 4. mock_tests
Curated mock tests from generated questions.

```javascript
{
  _id: ObjectId,
  mock_test_id: String, // UUID
  session_id: String,
  user_id: ObjectId,
  test_name: String,
  description: String,
  questions: [ObjectId], // References to questions._id
  duration_minutes: Number,
  total_marks: Number,
  difficulty_distribution: {
    easy: Number,
    medium: Number,
    hard: Number
  },
  subject_distribution: [{
    subject: String,
    question_count: Number
  }],
  created_at: ISODate,
  is_active: Boolean
}
```

### 5. mock_test_attempts
User attempts at mock tests with results.

```javascript
{
  _id: ObjectId,
  attempt_id: String, // UUID
  mock_test_id: String,
  user_id: ObjectId,
  started_at: ISODate,
  completed_at: ISODate,
  time_taken_minutes: Number,
  answers: [{
    question_id: String,
    selected_option: String, // "A", "B", "C", "D"
    is_correct: Boolean,
    time_spent_seconds: Number
  }],
  results: {
    total_questions: Number,
    correct_answers: Number,
    wrong_answers: Number,
    unanswered: Number,
    score_percentage: Number,
    subject_wise_score: [{
      subject: String,
      correct: Number,
      total: Number,
      percentage: Number
    }]
  },
  status: String // "in_progress", "completed", "abandoned"
}
```

### 6. mnemonics
AI-generated memory aids and mnemonics.

```javascript
{
  _id: ObjectId,
  session_id: String,
  user_id: ObjectId,
  topic: String,
  mnemonic_text: String,
  mnemonic_type: String, // "acronym", "rhyme", "story", "visual"
  explanation: String,
  key_terms: [String],
  medical_context: String,
  is_india_specific: Boolean,
  cultural_references: [String],
  difficulty_level: String,
  created_at: ISODate,
  user_rating: Number, // 1-5 stars
  usage_count: Number
}
```

### 7. cheat_sheets
High-yield summary sheets and quick references.

```javascript
{
  _id: ObjectId,
  session_id: String,
  user_id: ObjectId,
  title: String,
  content: String, // HTML/Markdown formatted content
  key_topics: [String],
  high_yield_points: [String],
  medical_subject: String,
  format_type: String, // "table", "list", "flowchart", "diagram"
  download_formats: {
    pdf_url: String,
    image_url: String,
    html_content: String
  },
  created_at: ISODate,
  view_count: Number,
  download_count: Number
}
```

### 8. notes
Comprehensive compiled study notes.

```javascript
{
  _id: ObjectId,
  session_id: String,
  user_id: ObjectId,
  title: String,
  content: {
    summary: String,
    important_points: [String],
    related_questions: [ObjectId], // References to questions
    mnemonics: [ObjectId], // References to mnemonics
    cheat_sheet_references: [ObjectId]
  },
  structure: {
    sections: [{
      title: String,
      content: String,
      subsections: [{
        title: String,
        content: String
      }]
    }]
  },
  metadata: {
    word_count: Number,
    reading_time_minutes: Number,
    complexity_score: Number
  },
  download_url: String,
  created_at: ISODate
}
```

### 9. flashcards
Spaced repetition flashcard system.

```javascript
{
  _id: ObjectId,
  flashcard_id: String, // UUID
  session_id: String,
  user_id: ObjectId,
  front_text: String, // Question/Term
  back_text: String, // Answer/Definition
  card_type: String, // "definition", "concept", "clinical", "drug"
  medical_subject: String,
  difficulty: String,
  tags: [String],
  spaced_repetition: {
    ease_factor: Number, // SM-2 algorithm
    interval: Number, // Days until next review
    repetitions: Number,
    next_review_date: ISODate,
    last_reviewed: ISODate
  },
  user_performance: {
    total_reviews: Number,
    correct_reviews: Number,
    success_rate: Number,
    average_response_time: Number
  },
  created_at: ISODate
}
```

### 10. flashcard_reviews
Individual flashcard review sessions.

```javascript
{
  _id: ObjectId,
  review_id: String, // UUID
  flashcard_id: String,
  user_id: ObjectId,
  reviewed_at: ISODate,
  user_rating: String, // "easy", "medium", "hard", "again"
  response_time_seconds: Number,
  was_correct: Boolean,
  notes: String // User notes about the card
}
```

### 11. study_plans
AI-generated personalized study schedules.

```javascript
{
  _id: ObjectId,
  plan_id: String, // UUID
  user_id: ObjectId,
  plan_name: String,
  description: String,
  start_date: ISODate,
  end_date: ISODate,
  total_days: Number,
  sessions_included: [String], // Array of session_ids
  daily_schedule: [{
    day: Number, // 1-based day number
    date: ISODate,
    tasks: [{
      task_type: String, // "study", "review", "mock_test", "flashcards"
      content_id: String, // Reference to specific content
      estimated_time_minutes: Number,
      priority: String, // "high", "medium", "low"
      status: String, // "pending", "in_progress", "completed", "skipped"
      completed_at: ISODate
    }],
    total_study_time: Number,
    completion_status: String
  }],
  progress: {
    days_completed: Number,
    tasks_completed: Number,
    total_tasks: Number,
    completion_percentage: Number,
    current_streak: Number,
    longest_streak: Number
  },
  created_at: ISODate,
  updated_at: ISODate,
  is_active: Boolean
}
```

---

## 🔗 Relationships

### Primary Relationships
```
users (1) ←→ (N) study_sessions
study_sessions (1) ←→ (N) questions
study_sessions (1) ←→ (N) mnemonics
study_sessions (1) ←→ (N) cheat_sheets
study_sessions (1) ←→ (N) notes
study_sessions (1) ←→ (N) flashcards
questions (N) ←→ (N) mock_tests
mock_tests (1) ←→ (N) mock_test_attempts
flashcards (1) ←→ (N) flashcard_reviews
users (1) ←→ (N) study_plans
```

### Reference Patterns
- **User-centric**: All content tied to specific users
- **Session-based**: Content organized by study sessions
- **Cross-references**: Questions linked to mock tests and notes

---

## 📊 Indexes

### Performance Indexes
```javascript
// users collection
db.users.createIndex({ mobile: 1 }, { unique: true })
db.users.createIndex({ email: 1 }, { sparse: true })

// study_sessions collection
db.study_sessions.createIndex({ user_id: 1, created_at: -1 })
db.study_sessions.createIndex({ session_id: 1 }, { unique: true })
db.study_sessions.createIndex({ processing_status: 1 })

// questions collection
db.questions.createIndex({ session_id: 1 })
db.questions.createIndex({ user_id: 1 })
db.questions.createIndex({ medical_subject: 1, difficulty: 1 })
db.questions.createIndex({ question_id: 1 }, { unique: true })

// mock_tests collection
db.mock_tests.createIndex({ session_id: 1 })
db.mock_tests.createIndex({ user_id: 1, created_at: -1 })
db.mock_tests.createIndex({ mock_test_id: 1 }, { unique: true })

// mock_test_attempts collection
db.mock_test_attempts.createIndex({ user_id: 1, completed_at: -1 })
db.mock_test_attempts.createIndex({ mock_test_id: 1 })

// mnemonics collection
db.mnemonics.createIndex({ session_id: 1 })
db.mnemonics.createIndex({ user_id: 1 })
db.mnemonics.createIndex({ topic: "text" }) // Text search

// cheat_sheets collection
db.cheat_sheets.createIndex({ session_id: 1 })
db.cheat_sheets.createIndex({ user_id: 1 })
db.cheat_sheets.createIndex({ medical_subject: 1 })

// notes collection
db.notes.createIndex({ session_id: 1 })
db.notes.createIndex({ user_id: 1 })

// flashcards collection
db.flashcards.createIndex({ session_id: 1 })
db.flashcards.createIndex({ user_id: 1 })
db.flashcards.createIndex({ "spaced_repetition.next_review_date": 1 })
db.flashcards.createIndex({ flashcard_id: 1 }, { unique: true })

// flashcard_reviews collection
db.flashcard_reviews.createIndex({ flashcard_id: 1, reviewed_at: -1 })
db.flashcard_reviews.createIndex({ user_id: 1, reviewed_at: -1 })

// study_plans collection
db.study_plans.createIndex({ user_id: 1, created_at: -1 })
db.study_plans.createIndex({ plan_id: 1 }, { unique: true })
db.study_plans.createIndex({ is_active: 1 })
```

### Text Search Indexes
```javascript
// Full-text search capabilities
db.questions.createIndex({ 
  question_text: "text", 
  explanation: "text",
  "options.text": "text"
})

db.mnemonics.createIndex({ 
  topic: "text", 
  mnemonic_text: "text",
  explanation: "text"
})

db.cheat_sheets.createIndex({ 
  title: "text", 
  content: "text",
  key_topics: "text"
})

db.notes.createIndex({ 
  title: "text", 
  "content.summary": "text"
})
```

---

## 🔧 Database Operations

### Common Queries

#### Get User Sessions
```javascript
db.study_sessions.find({ 
  user_id: ObjectId("user_id") 
}).sort({ created_at: -1 })
```

#### Get Session Content
```javascript
// Get all content for a session
db.questions.find({ session_id: "session_uuid" })
db.mnemonics.find({ session_id: "session_uuid" })
db.cheat_sheets.find({ session_id: "session_uuid" })
```

#### Flashcard Due for Review
```javascript
db.flashcards.find({
  user_id: ObjectId("user_id"),
  "spaced_repetition.next_review_date": { $lte: new Date() }
})
```

#### Mock Test Performance
```javascript
db.mock_test_attempts.aggregate([
  { $match: { user_id: ObjectId("user_id") } },
  { $group: {
    _id: null,
    avg_score: { $avg: "$results.score_percentage" },
    total_attempts: { $sum: 1 }
  }}
])
```

---

## 📈 Data Analytics Queries

### User Engagement Analytics
```javascript
// Active users in last 30 days
db.users.find({ 
  last_login: { $gte: new Date(Date.now() - 30*24*60*60*1000) } 
}).count()

// Sessions created per day
db.study_sessions.aggregate([
  { $group: {
    _id: { $dateToString: { format: "%Y-%m-%d", date: "$created_at" } },
    count: { $sum: 1 }
  }},
  { $sort: { _id: -1 } }
])
```

### Content Performance
```javascript
// Most popular medical subjects
db.questions.aggregate([
  { $group: { _id: "$medical_subject", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

// Average processing time
db.study_sessions.aggregate([
  { $match: { processing_status: "completed" } },
  { $group: {
    _id: null,
    avg_time: { $avg: "$metadata.processing_time_seconds" }
  }}
])
```

---

## 🔒 Data Security

### Sensitive Data Handling
- **Passwords**: Hashed using bcrypt
- **JWT Secrets**: Environment variables only
- **File Paths**: Relative paths, no absolute system paths
- **User Data**: Isolated by user_id in all queries

### Data Retention
- **User Sessions**: Retained indefinitely (user-controlled deletion)
- **File Uploads**: Auto-cleanup after 90 days
- **Logs**: Rotated weekly, kept for 30 days
- **Temporary Data**: Cleaned up after processing

---

## 🔄 Migration Scripts

### Initial Database Setup
```javascript
// Create collections with validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["mobile", "password", "created_at"],
      properties: {
        mobile: { bsonType: "string", pattern: "^[0-9]{10}$" },
        password: { bsonType: "string", minLength: 6 }
      }
    }
  }
})
```

### Data Migration Example
```javascript
// Migrate old session format to new format
db.study_sessions.updateMany(
  { outputs_generated: { $exists: false } },
  { $set: { 
    outputs_generated: {
      questions: false,
      mock_tests: false,
      mnemonics: false,
      cheat_sheets: false,
      notes: false,
      flashcards: false
    }
  }}
)
```

---

*Database Schema Documentation - Study Buddy App v1.0.0*
