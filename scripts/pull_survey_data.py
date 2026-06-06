#!/usr/bin/env python3
"""
Pull survey responses from Typeform and save to CSV
Run this script anytime to get the latest responses
"""

import requests
import json
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Typeform credentials (from .env file)
TYPEFORM_TOKEN = os.getenv("TYPEFORM_TOKEN")
FORM_ID = "f1FkXdTE"
API_URL = f"https://api.typeform.com/forms/{FORM_ID}/responses"

if not TYPEFORM_TOKEN:
    raise ValueError("TYPEFORM_TOKEN not found. Create a .env file with your token.")

# Question field references (will be populated from form metadata)
QUESTIONS = {}

def get_form_metadata():
    """Fetch form structure to map question IDs to labels"""
    url = f"https://api.typeform.com/forms/{FORM_ID}"
    headers = {"Authorization": f"Bearer {TYPEFORM_TOKEN}"}

    response = requests.get(url, headers=headers)
    form_data = response.json()

    # Extract questions
    for field in form_data.get("fields", []):
        field_ref = field.get("ref")
        title = field.get("title", "Unknown")
        QUESTIONS[field_ref] = title

    return form_data

def fetch_responses():
    """Fetch all responses from Typeform"""
    headers = {"Authorization": f"Bearer {TYPEFORM_TOKEN}"}

    print(f"Fetching responses from Typeform...")
    response = requests.get(API_URL, headers=headers)
    data = response.json()

    return data.get("items", [])

def parse_response(response_item):
    """Convert Typeform response to flat dict"""
    parsed = {
        "submission_id": response_item.get("response_id"),
        "submitted_at": response_item.get("submitted_at"),
    }

    # Extract answers
    for answer in response_item.get("answers", []):
        field_ref = answer.get("field", {}).get("ref", "unknown")
        question = QUESTIONS.get(field_ref, field_ref)

        # Handle different answer types
        answer_type = answer.get("type")
        if answer_type == "text":
            value = answer.get("text", "")
        elif answer_type == "number":
            value = answer.get("number", "")
        elif answer_type == "choice":
            value = answer.get("choice", {}).get("label", "")
        elif answer_type == "choices":
            value = ", ".join([c.get("label", "") for c in answer.get("choices", [])])
        else:
            value = str(answer)

        parsed[question] = value

    return parsed

def save_to_csv(responses):
    """Save responses to CSV file"""
    if not responses:
        print("No responses to save.")
        return

    filename = f"data/survey_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # Get all unique keys
    all_keys = set()
    for resp in responses:
        all_keys.update(resp.keys())

    fieldnames = sorted(list(all_keys))

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(responses)

    print(f"✅ Saved {len(responses)} responses to: {filename}")
    return filename

def main():
    print("=" * 60)
    print("Youth Soccer Survey - Data Extraction")
    print("=" * 60)

    # Get form metadata
    print("\n1. Loading form structure...")
    get_form_metadata()
    print(f"   Found {len(QUESTIONS)} questions")

    # Fetch responses
    print("\n2. Fetching responses...")
    raw_responses = fetch_responses()
    print(f"   Found {len(raw_responses)} responses")

    if not raw_responses:
        print("\n   No responses yet. Survey is live at:")
        print("   https://easydoesit.github.io/youth-soccer-analysis/survey.html")
        return

    # Parse responses
    print("\n3. Parsing responses...")
    parsed_responses = [parse_response(r) for r in raw_responses]

    # Save to CSV
    print("\n4. Saving to CSV...")
    csv_file = save_to_csv(parsed_responses)

    # Show summary
    print("\n" + "=" * 60)
    print(f"Total responses: {len(parsed_responses)}")
    print(f"Questions collected: {len(QUESTIONS)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
