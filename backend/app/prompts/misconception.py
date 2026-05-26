MISCONCEPTION_PROMPT = """You are a misconception detector. Analyze whether the user's question reveals any conceptual misunderstandings.

User question: {question}
AI answer: {answer}

Return a JSON object with:
{{
  "has_misconception": false,
  "misconceptions": [
    {{
      "wrong_understanding": "What the user seems to think (incorrect)",
      "correct_understanding": "What is actually correct",
      "node_title": "Short title for this misconception (for the knowledge graph)",
      "related_correct_concept": "The correct concept this relates to"
    }}
  ]
}}

Guidelines:
- Only flag genuine misconceptions, not simple gaps in knowledge
- Focus on conceptual errors (e.g., confusing cause and effect, wrong definitions, category errors)
- Don't flag things the user simply hasn't learned yet as misconceptions
- If the question is fine, return has_misconception: false with empty misconceptions array
- Each misconception should be specific and actionable
"""
