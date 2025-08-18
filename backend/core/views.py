# Views for the core application
# This module contains view functions that handle HTTP requests for the core app

from django.http import HttpResponse

def index(request):
    """
    Simple index view that returns a status message.
    
    Args:
        request: The HTTP request object
        
    Returns:
        HttpResponse: A simple text response indicating the backend is running
    """
    return HttpResponse("MemorySim backend is running.")