#!/usr/bin/env python
"""
Script to create initial world background for memory policy simulation
Run this from the backend directory: python create_background.py
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
django.setup()

from shared.models import WorldBackground


def create_background():
    """Create initial world background focused on memory policy making"""
    
    background_content = """The year is 2035. Breakthrough advances in neurotechnology have made human memory manipulation not just possible, but precise and reliable. Memory editing, enhancement, and storage technologies have matured from experimental procedures to commercially viable solutions.

    Global governments now face unprecedented policy decisions that will fundamentally reshape human society. Memory modification technologies can eliminate traumatic experiences, enhance learning capabilities, allow perfect recall of any information, and even enable memory sharing between individuals. These capabilities present both extraordinary opportunities and profound risks.

    The international community stands at a crossroads. Some nations advocate for unrestricted access to memory technologies, viewing them as the next step in human evolution. Others call for strict regulation, warning of potential misuse and the erosion of human authenticity. Meanwhile, private corporations have developed sophisticated memory storage systems, creating new questions about data ownership, privacy, and commercial exploitation of human consciousness.

    Early adopter regions have already begun implementing pilot programs: therapeutic memory editing for trauma victims, cognitive enhancement for students and professionals, and memory preservation systems for the elderly. The results are promising but controversial, with reports of both miraculous recoveries and unexpected psychological complications.

    As policymakers worldwide prepare to establish the regulatory framework that will govern memory technologies for generations to come, each decision carries the weight of human history. The choices made in the coming years will determine whether these technologies become tools of liberation or instruments of control, whether they preserve human dignity or fundamentally alter what it means to be human.

    The future of memory - and humanity itself - hangs in the balance of legislative chambers and policy councils around the globe."""

    # Check if background already exists
    if WorldBackground.objects.exists():
        print("Updating existing world background...")
        bg = WorldBackground.objects.first()
        bg.content = background_content
        bg.save()
    else:
        print("Creating new world background...")
        bg = WorldBackground.objects.create(content=background_content)

    print(f"Background content saved successfully!")
    print(f"Content length: {len(background_content)} characters")
    print(f"Background ID: {bg.id}")


if __name__ == '__main__':
    create_background()
