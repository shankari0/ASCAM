from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Send a prompt via Groq and return the response.
def ask_llm(prompt):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def summarise(text):
    prompt = f"Summarise the following academic text clearly and concisely:\n\n{text}"
    return ask_llm(prompt)

def answer_question(question, context):
    prompt = f"""Answer the following question based only on the context provided.

Context:
{context}

Question: {question}

Answer:"""
    return ask_llm(prompt)

def generate_flashcards(text, num=5):
    prompt = f"""Generate {num} flashcards from the following academic text.
Format each flashcard exactly like this:
Q: [question]
A: [answer]

Text:
{text}"""
    return ask_llm(prompt)

def generate_quiz(text, num=5):
    prompt = f"""Generate {num} multiple choice questions from the following academic text.
Format each question exactly like this:
Q: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct letter]

Text:
{text}"""
    return ask_llm(prompt)

def extract_key_concepts(text):
    prompt = f"List the key concepts from the following academic text as bullet points:\n\n{text}"
    return ask_llm(prompt)