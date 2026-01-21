STRICT_JSON_SUFFIX = """

CRITICAL OUTPUT RULES:
1. Return ONLY valid JSON - no markdown, no backticks, no explanations
2. Start response with [ and end with ]
3. Use double quotes for all strings
4. No trailing commas
5. Ensure all special characters are properly escaped

RESPOND WITH ONLY THE JSON ARRAY:"""

STUDY_NOTES_PROMPT = """You are an expert question generator for educational study materials.
Generate exactly {num_questions} high-quality multiple choice questions.

STUDY CONTENT:
{content}

Each question MUST follow this exact JSON structure:
[
  {{
    "question": "Clear, specific question text ending with ?",
    "difficulty": "easy|medium|hard",
    "topic": "Specific topic from the content",
    "options": {{
      "A": "First distinct option",
      "B": "Second distinct option",
      "C": "Third distinct option",
      "D": "Fourth distinct option"
    }},
    "correct_answer": "A",
    "explanation": "Concise explanation of why this is correct"
  }}
]

QUESTION GUIDELINES:
- Mix difficulty levels: 30% easy, 50% medium, 20% hard
- Cover different topics from the content
- Make options plausible but clearly distinguishable
- Explanations should reference the source material
""" + STRICT_JSON_SUFFIX

CHEAT_SHEET_PROMPT = """You are an expert at creating recall-based questions from cheat sheets.
Generate exactly {num_questions} questions focusing on key facts and definitions.

CHEAT SHEET CONTENT:
{content}

Each question MUST follow this exact JSON structure:
[
  {{
    "question": "Direct question about a key fact or definition?",
    "difficulty": "easy|medium|hard",
    "topic": "Topic name",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "correct_answer": "A",
    "explanation": "Brief explanation"
  }}
]

QUESTION GUIDELINES:
- Focus on quick recall and factual knowledge
- Test definitions, formulas, and key points
- Keep questions concise and direct
""" + STRICT_JSON_SUFFIX

MNEMONIC_PROMPT = """You are an expert at creating questions about mnemonic devices.
Generate exactly {num_questions} questions testing mnemonic understanding.

MNEMONIC CONTENT:
{content}

Each question MUST follow this exact JSON structure:
[
  {{
    "question": "Question about the mnemonic or its components?",
    "difficulty": "easy|medium|hard", 
    "topic": "Topic name",
    "options": {{
      "A": "Option A",
      "B": "Option B",
      "C": "Option C",
      "D": "Option D"
    }},
    "correct_answer": "A",
    "explanation": "Explanation connecting to the mnemonic"
  }}
]

QUESTION GUIDELINES:
- Ask what each letter/word in the mnemonic represents
- Test application of the mnemonic
- Include questions about when to use the mnemonic
""" + STRICT_JSON_SUFFIX

DOCUMENT_TYPE_DETECTION_PROMPT = """Analyze this document and determine its type.

DOCUMENT CONTENT (first 2000 chars):
{content}

Respond with ONLY ONE of these exact words (no other text):
- STUDY_NOTES (if it's detailed study material, textbook content, or lecture notes)
- CHEAT_SHEET (if it's a quick reference, summary, or condensed facts)
- MNEMONIC (if it contains memory aids, acronyms, or memory tricks)

YOUR RESPONSE (one word only):"""
