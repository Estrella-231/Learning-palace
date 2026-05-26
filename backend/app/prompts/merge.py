MERGE_PROMPT = """You are a knowledge deduplication engine. Decide whether a new concept should be merged with existing similar concepts.

New concept:
{new_node}

Existing similar concepts:
{similar_nodes}

Return a JSON object with:
{{
  "action": "create_new | update_existing | merge",
  "similar_node_id": "id of the node to merge/update, or null",
  "reasoning": "Brief explanation of your decision",
  "merged_summary": "If merging, provide the combined summary"
}}

Decision rules:
- "create_new": The new concept is distinct enough to stand alone (choose this by default)
- "update_existing": The new concept adds information to an existing one (e.g., deeper explanation of same topic)
- "merge": The concepts are essentially the same, combine them

Be conservative: only merge if the concepts are truly the same thing. Different aspects of the same broad topic should remain separate nodes. For example, "CNN Architecture" and "CNN Training" are different nodes even though both are about CNN.
"""
