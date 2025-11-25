# rag_module.py

from rag import retrieve_passages, answer_question, generate_styled_image

_last_sources = []

def get_answer(question: str, age_group: str) -> str:
    global _last_sources
    _last_sources = retrieve_passages(question, age_group)
    return answer_question(question, _last_sources, age_group)

def get_sources():
    return _last_sources

def generate_image(prompt: str):
    return generate_styled_image(prompt)
