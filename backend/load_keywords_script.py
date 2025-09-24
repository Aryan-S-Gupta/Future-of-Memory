#!/usr/bin/env python
"""
Quick script to load keywords from keywords.txt into DefaultQueryList model
Run this from the backend directory: python load_keywords_script.py
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
django.setup()

from shared.models import DefaultQueryList


def load_keywords():
    """Load keywords from keywords.txt file into database"""
    
    # Path to keywords file
    keywords_file = 'rag/cleaned_data/keywords/keywords.txt'
    
    if not os.path.exists(keywords_file):
        print(f"Keywords file not found: {keywords_file}")
        return
    
    # Read keywords
    try:
        with open(keywords_file, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        
        print(f"Found {len(keywords)} keywords in file")
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Load into database
    created_count = 0
    skipped_count = 0
    
    for keyword in keywords:
        if not DefaultQueryList.objects.filter(keyword=keyword).exists():
            DefaultQueryList.objects.create(keyword=keyword)
            created_count += 1
            print(f"Added: {keyword}")
        else:
            skipped_count += 1
            print(f"Skipped (duplicate): {keyword}")
    
    # Summary
    total_count = DefaultQueryList.objects.count()
    print(f"""
Loading completed!
  - Created: {created_count}
  - Skipped: {skipped_count}
  - Total in database: {total_count}
    """)


if __name__ == '__main__':
    load_keywords()
