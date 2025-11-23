import os
import argparse
from typing import Optional
from openai import OpenAI
import sqlite3
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

# Pydantic model to structure the response
class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    english_grammar: Optional[str]
    japanese_text: Optional[str]
    hiragana_pronunciation: Optional[str]
    japanese_grammar: Optional[str]
    timestamp: str

# Initialize OpenAI Application
client = OpenAI(
    api_key=api_key,
    base_url="https://api.chatanywhere.tech/v1",
    http_client=None
)

def gpt_response(prompt: str) -> TranslationResponse:
    """Call OpenAI's chat model API and return the result as a structured Pydantic model."""
    chat_completions = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Translate the given text and explain the grammar"},
            {"role": "user", "content": prompt}
        ],
        response_format=TranslationResponse,
    )

    # Get the parsed result
    completion = chat_completions.choices[0].message.parsed
    return completion

# Set up SQLite database for storing translations
def setup_database():
    conn = sqlite3.connect("translations.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chinese TEXT NOT NULL,
        english TEXT NOT NULL,
        english_grammar TEXT,
        japanese TEXT,
        hiragana TEXT,
        japanese_grammar TEXT,
        timestamp TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

def store_translation(chinese: str, english: str, english_grammar: str, japanese: str, hiragana: str, japanese_grammar: str, timestamp: str):
    """Store the translation in the database."""
    conn = sqlite3.connect("translations.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO translations (chinese, english, english_grammar, japanese, hiragana, japanese_grammar, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (chinese, english, english_grammar, japanese, hiragana, japanese_grammar, timestamp)
    )
    conn.commit()
    conn.close()

def translate_text(text: str):
    """Translate the input text and get the structured output."""
    prompt = (
        f"Translate this text to English and explain the grammar: {text} \n"
        "Also, provide a Japanese translation and the Hiragana pronunciation of the Japanese text. "
        "Be sure to include Hiragana for the Japanese translation and the Japanese grammar."
    )
    structured_output = gpt_response(prompt).model_dump()
    if isinstance(structured_output, dict):
        return structured_output
    else:
        print(f"warning: structured_output for the model output is not a dictionary")
    

def correct_english_grammar(text: str):
    """Correct the English sentence grammar using OpenAI."""
    # Use the original English text as the 'original_text'
    prompt = (
        f"Correct the grammar of the following English sentence and provide an explanation:\n"
        f"Original English: {text}\n"
        "Also, provide a Japanese translation and the Hiragana pronunciation of the Japanese text. "
        "Be sure to include Hiragana for the Japanese translation and the Japanese grammar."
    )
    
    # Call the gpt_response function with the updated prompt
    structured_output = gpt_response(prompt).model_dump()

    if isinstance(structured_output, dict):
        return structured_output
    else:
        print(f"warning: structured_output for the model output is not a dictionary")

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Translate and correct English sentences.")
    parser.add_argument('-c', '--chinese', type=str, help="Translate Chinese to English and Japanese.")
    parser.add_argument('-e', '--english', type=str, help="Correct the grammar of an English sentence.")
    parser.add_argument('-g', '--grammar', action='store_true', help="include grammar explanations.")
    args = parser.parse_args()

    # Set up the database
    setup_database()

    if args.chinese:
        # If -c is used, translate Chinese text to English and Japanese
        chinese_input = args.chinese
        translation_data = translate_text(chinese_input)

        # Extract the data
        original_text = translation_data["original_text"]
        translated_text = translation_data["translated_text"]
        english_grammar = translation_data.get("english_grammar", "")
        japanese_text = translation_data.get("japanese_text", "")
        hiragana_pronunciation = translation_data.get("hiragana_pronunciation", "")
        japanese_grammar = translation_data.get("japanese_grammar", "")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Store the translation in the database
        store_translation(original_text, translated_text, english_grammar, japanese_text, hiragana_pronunciation, japanese_grammar, timestamp)

        # Output the structured response
        print(f"Original (Chinese): {original_text}")
        print(f"Translated (English): {translated_text}")
        if args.grammar:
            print(f"English Grammar Explanation: {english_grammar}")
        print(f"Japanese Translation: {japanese_text}")
        print(f"Hiragana Pronunciation: {hiragana_pronunciation}")
        if args.grammar:
            print(f"Japanese Grammar Explanation: {japanese_grammar}")
        print(f"Timestamp: {timestamp}")
    
    elif args.english:
        # If -e is used, correct the English grammar and store it in the database
        english_input = args.english
        corrected_english_data = correct_english_grammar(english_input)

        # Extract the data
        original_text = corrected_english_data["original_text"]
        translated_text = corrected_english_data["translated_text"]
        english_grammar = corrected_english_data.get("english_grammar", "")
        japanese_text = corrected_english_data.get("japanese_text", "")
        hiragana_pronunciation = corrected_english_data.get("hiragana_pronunciation", "")
        japanese_grammar = corrected_english_data.get("japanese_grammar", "")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Store the corrected English translation in the database
        store_translation(original_text, translated_text, english_grammar, japanese_text, hiragana_pronunciation, japanese_grammar, timestamp)

        # Output the corrected English and related information
        print(f"Original (English): {original_text}")
        print(f"Corrected English: {translated_text}")
        if args.grammar:
            print(f"English Grammar Explanation: {english_grammar}")
        print(f"Japanese Translation: {japanese_text}")
        print(f"Hiragana Pronunciation: {hiragana_pronunciation}")
        if args.grammar:
            print(f"Japanese Grammar Explanation: {japanese_grammar}")
        print(f"Timestamp: {timestamp}")
    
    else:
        print("Please provide either a Chinese sentence (-c) or an English sentence (-e) to process.")

if __name__ == "__main__":
    main()
