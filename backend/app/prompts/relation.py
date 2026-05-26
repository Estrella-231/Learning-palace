RELATION_PROMPT = """You are a knowledge relationship extraction engine. Given new concepts and existing nodes, identify relationships between them.

New concepts:
{new_concepts}

Existing knowledge nodes:
{existing_nodes}

Return a JSON object with the following structure:
{{
  "relations": [
    {{
      "source_title": "source concept name",
      "target_title": "target concept name",
      "relation_type": "one of: prerequisite_of, part_of, example_of, contrast_with, cause_of, used_for, improves, similar_to, contains",
      "confidence": 0.0-1.0,
      "evidence": "Brief justification for this relationship"
    }}
  ]
}}

Guidelines:
- Only create relationships that are clearly supported by the content
- relation_type "prerequisite_of" means source must be learned BEFORE target
- relation_type "part_of" means source is a component of target
- relation_type "contains" means source contains/owns target (e.g., YOLO contains Backbone)
- relation_type "contrast_with" means two concepts are alternatives or opposites
- relation_type "similar_to" means concepts are analogous or easily confused
- Confidence should be high (0.8+) for explicit relationships, lower for inferred ones
- Include relationships between new concepts AND between new and existing concepts
- Don't force relationships if none are meaningful
"""
