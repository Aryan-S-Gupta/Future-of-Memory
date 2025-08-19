
"""
Django's command-line utility for administrative tasks.

This module provides the main entry point for Django management commands.
It sets up the Django environment and delegates to Django's built-in
command-line utility for tasks like running the development server,
creating migrations, running tests, etc.

Usage:
    python manage.py <command> [options]
    
Common commands:
    - runserver: Start the development server
    - migrate: Apply database migrations
    - makemigrations: Create new database migrations
    - shell: Start an interactive Python shell with Django loaded
    - test: Run the test suite
"""
import os
import sys

def main():
    """
    Run administrative tasks.
    
    This function sets up the Django settings module and executes
    command-line management commands.
    """
    # Set the default Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_sim.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # Execute the command-line management utility
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()