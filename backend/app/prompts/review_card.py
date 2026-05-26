REVIEW_CARD_PROMPT = """You are a review card generator. Create spaced-repetition flashcards from the given knowledge concepts.

Concepts:
{concepts}

Context (the original answer):
{context}

Return a JSON object with:
{{
  "cards": [
    {{
      "concept_title": "Which concept this card tests",
      "question": "A clear question that tests understanding (not just recall)",
      "answer": "The correct answer, concise but complete",
      "card_type": "basic"
    }},
    {{
      "concept_title": "Concept name",
      "question": "A question asking to compare or contrast two concepts",
      "answer": "The comparison answer",
      "card_type": "contrast"
    }},
    {{
      "concept_title": "Concept name",
      "question": "An application question: given a scenario, what should you use/do?",
      "answer": "The application answer",
      "card_type": "application"
    }}
  ]
}}

Guidelines:
- Generate 1-3 cards in total (not 3 per concept)
- Basic cards: test core understanding of a single concept
- Contrast cards: ask about differences between two related concepts (only if there are at least 2 concepts to compare)
- Application cards: present a scenario and ask what approach/method/concept applies (only if applicable)
- Questions should promote active recall, not recognition
- Answers should be self-contained and useful for review
"""
