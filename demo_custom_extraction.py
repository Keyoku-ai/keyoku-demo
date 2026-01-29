#!/usr/bin/env python3
"""
Demo script for Keyoku Custom Schema Extraction.

This script demonstrates how to use custom schemas to extract structured
data from conversations alongside the default memory extraction.

Usage:
    export KEYOKU_API_KEY="your-api-key"
    export KEYOKU_BASE_URL="http://localhost:8080"  # or your API URL
    python demo_custom_extraction.py
"""

import os
import sys
import json
from pprint import pprint

# Add parent directory to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'keyoku-python', 'src'))

try:
    from keyoku import Keyoku, KeyokuError
except ImportError:
    print("Error: Could not import keyoku. Make sure keyoku-python is installed.")
    print("Run: pip install -e ../keyoku-python")
    sys.exit(1)


def get_client():
    """Initialize Keyoku client from environment."""
    api_key = os.environ.get("KEYOKU_API_KEY")
    base_url = os.environ.get("KEYOKU_BASE_URL", "http://localhost:8080")

    if not api_key:
        print("Error: KEYOKU_API_KEY environment variable not set")
        sys.exit(1)

    return Keyoku(api_key=api_key, base_url=base_url)


def demo_mental_health_schema():
    """Demo: Create and use a mental health assessment schema."""
    print("\n" + "="*60)
    print("Demo: Mental Health Assessment Schema")
    print("="*60)

    client = get_client()

    # Step 1: Create the custom schema
    print("\n1. Creating custom extraction schema...")

    schema_definition = {
        "type": "object",
        "properties": {
            "mood_state": {
                "type": "string",
                "enum": ["depressed", "anxious", "neutral", "positive", "mixed"],
                "description": "The overall mood state expressed"
            },
            "mood_intensity": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Intensity of the mood (0.0 to 1.0)"
            },
            "symptoms": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of symptoms mentioned"
            },
            "triggers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "What triggered these feelings"
            },
            "risk_level": {
                "type": "string",
                "enum": ["none", "low", "medium", "high", "crisis"],
                "description": "Risk assessment level"
            },
            "coping_strategies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Coping strategies mentioned"
            },
            "social_support": {
                "type": "boolean",
                "description": "Whether social support was mentioned"
            }
        },
        "required": ["mood_state", "risk_level"]
    }

    try:
        # Check if schema already exists
        existing_schemas = client.schemas.list()
        schema = None
        for s in existing_schemas.schemas:
            if s.name == "Mental Health Assessment":
                schema = s
                print(f"   Found existing schema: {schema.id}")
                break

        if not schema:
            schema = client.schemas.create(
                name="Mental Health Assessment",
                schema=schema_definition,
                description="Extract mental health indicators from patient conversations"
            )
            print(f"   Created schema: {schema.id}")

    except KeyokuError as e:
        print(f"   Error creating schema: {e}")
        return

    # Step 2: Test with sample conversations
    print("\n2. Processing sample conversations...")

    test_cases = [
        {
            "content": "I've been feeling really anxious about work lately. I can't sleep well and my mind keeps racing at night. My boss has been putting a lot of pressure on the team. I've been trying to exercise more to help.",
            "expected": "anxious mood, work trigger, insomnia symptom"
        },
        {
            "content": "Today was actually a pretty good day. I met up with my friends for coffee and we had a great conversation. I've been feeling more positive lately since I started that new hobby.",
            "expected": "positive mood, social support present"
        },
        {
            "content": "I don't know what to do anymore. Everything feels hopeless. I haven't talked to anyone in weeks and I just stay in bed most days. Sometimes I wonder if things will ever get better.",
            "expected": "depressed mood, isolation, possible elevated risk"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n   Test Case {i}: {case['expected']}")
        print(f"   Input: \"{case['content'][:60]}...\"")

        try:
            # Use remember with schema_id
            job = client.remember(
                case["content"],
                schema_id=schema.id
            )

            # Wait for processing
            result = job.wait(timeout=30.0)
            print(f"   Job completed: {result.id}")

            # Check for custom extraction data
            if hasattr(result, 'custom_extracted_data') and result.custom_extracted_data:
                print("   Extracted data:")
                for key, value in result.custom_extracted_data.items():
                    print(f"     - {key}: {value}")
            else:
                print("   (No custom extraction data in job result, checking extractions endpoint...)")

                # Try getting extractions by job
                extractions = client.extractions.get_by_job(result.id)
                if extractions:
                    for ext in extractions:
                        print(f"   Extraction {ext.id}:")
                        print(f"     Confidence: {ext.confidence}")
                        for key, value in ext.extracted_data.items():
                            print(f"     - {key}: {value}")
                else:
                    print("   No extractions found for this job")

        except TimeoutError:
            print("   Job timed out")
        except KeyokuError as e:
            print(f"   Error: {e}")

    # Step 3: Query all extractions
    print("\n3. Listing all extractions for this schema...")

    try:
        extractions_response = client.extractions.list(schema_id=schema.id, limit=10)
        print(f"   Found {extractions_response.total} extractions")

        for ext in extractions_response.extractions:
            print(f"\n   Extraction: {ext.id}")
            print(f"   Confidence: {ext.confidence}")
            print(f"   Data: {json.dumps(ext.extracted_data, indent=6)}")

    except KeyokuError as e:
        print(f"   Error listing extractions: {e}")

    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)


def demo_product_feedback_schema():
    """Demo: Create and use a product feedback schema."""
    print("\n" + "="*60)
    print("Demo: Product Feedback Schema")
    print("="*60)

    client = get_client()

    # Create product feedback schema
    print("\n1. Creating product feedback schema...")

    schema_definition = {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral", "mixed"]
            },
            "features_mentioned": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Product features discussed"
            },
            "pain_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Issues or frustrations mentioned"
            },
            "feature_requests": {
                "type": "array",
                "items": {"type": "string"},
                "description": "New features requested"
            },
            "satisfaction_score": {
                "type": "number",
                "minimum": 1,
                "maximum": 10
            },
            "would_recommend": {
                "type": "boolean"
            }
        },
        "required": ["sentiment"]
    }

    try:
        existing_schemas = client.schemas.list()
        schema = None
        for s in existing_schemas.schemas:
            if s.name == "Product Feedback":
                schema = s
                print(f"   Found existing schema: {schema.id}")
                break

        if not schema:
            schema = client.schemas.create(
                name="Product Feedback",
                schema=schema_definition,
                description="Extract product feedback insights from customer conversations"
            )
            print(f"   Created schema: {schema.id}")

    except KeyokuError as e:
        print(f"   Error: {e}")
        return

    # Test with feedback
    print("\n2. Processing product feedback...")

    feedback = """
    I've been using your app for about 3 months now. Overall I really like the search
    feature - it's super fast and accurate. However, the mobile app crashes sometimes
    when I try to export data. It would be great if you could add dark mode and
    offline support. Despite these issues, I'd still recommend it to my colleagues.
    I'd rate it about 7 out of 10.
    """

    try:
        job = client.remember(feedback, schema_id=schema.id)
        result = job.wait(timeout=30.0)
        print(f"   Job completed: {result.id}")

        extractions = client.extractions.get_by_job(result.id)
        if extractions:
            for ext in extractions:
                print("\n   Extracted feedback insights:")
                print(f"   {json.dumps(ext.extracted_data, indent=4)}")

    except (TimeoutError, KeyokuError) as e:
        print(f"   Error: {e}")

    print("\n" + "="*60)


def cleanup_schemas():
    """Cleanup: Delete demo schemas."""
    print("\nCleaning up demo schemas...")

    client = get_client()

    schema_names = ["Mental Health Assessment", "Product Feedback"]

    try:
        schemas = client.schemas.list()
        for schema in schemas.schemas:
            if schema.name in schema_names:
                client.schemas.delete(schema.id)
                print(f"   Deleted schema: {schema.name}")
    except KeyokuError as e:
        print(f"   Error during cleanup: {e}")


def main():
    print("="*60)
    print("Keyoku Custom Schema Extraction Demo")
    print("="*60)

    # Run demos
    demo_mental_health_schema()
    demo_product_feedback_schema()

    # Optional cleanup
    response = input("\nCleanup demo schemas? (y/N): ").strip().lower()
    if response == 'y':
        cleanup_schemas()

    print("\nDone!")


if __name__ == "__main__":
    main()
