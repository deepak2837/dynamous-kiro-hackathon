import re
import json
# ...existing code...

def extract_json_from_response(self, response_text: str) -> dict:
    """Extract JSON from AI response with multiple fallback methods."""
    try:
        # Method 1: Direct JSON parse
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Method 2: Find JSON in markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Method 3: Find JSON array or object anywhere in text
    json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', response_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Method 4: Try to clean and parse
    cleaned = response_text.strip()
    if cleaned.startswith('```'):
        cleaned = re.sub(r'^```\w*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```$', '', cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    raise ValueError(f"Could not extract JSON from response: {response_text[:200]}...")

# ...existing code...