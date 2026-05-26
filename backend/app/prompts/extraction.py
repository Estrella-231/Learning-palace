EXTRACTION_PROMPT = """You are a knowledge extraction engine. From the following Q&A, extract structured knowledge points.

User question: {question}
AI answer: {answer}

Extract and return a JSON object with the following structure:
{{
  "concepts": [
    {{
      "title": "Core concept name (concise, 2-6 words)",
      "type": "concept",
      "summary": "One-paragraph clear explanation of this concept",
      "key_points": ["key point 1", "key point 2"],
      "code_snippets": []
    }}
  ],
  "prerequisites": ["List of prerequisite knowledge needed to understand this"],
  "follow_up_questions": ["3 suggested questions the user might ask next"],
  "common_misconceptions": [
    {{
      "wrong": "Common wrong understanding",
      "correct": "The correct understanding"
    }}
  ]
}}

Rules:
- Extract 1-5 concepts max (not every minor term)
- Each concept title should be self-contained and meaningful
- Summaries should be useful standalone (someone seeing just this node should understand it)
- Only include code_snippets if actual code appeared in the answer
- prerequisites should be concepts someone needs to know BEFORE understanding this answer
- follow_up_questions should be natural next questions for deepening understanding
"""
