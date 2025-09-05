from django.db import models

class Session(models.Model):
    """
    Stores a game session and its evolving world state.
    """
    world_state = models.TextField(blank=True) # current world description
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Session {self.id}'

class Turn(models.Model):
    """
    One question/response cycle in a session.
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='turns')
    question_json = models.JSONField() # question with options
    user_choice = models.ForeignKey('Option', on_delete=models.SET_NULL, null=True, blank=True, related_name='chosen') # final choice
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Turn {self.id} (Session {self.session_id})'

class Option(models.Model):
    """
    Possible choice for a turn, with its text and image prompt.
    """
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE, related_name='options')
    label = models.TextField() # e.g. A, B, C, D
    image_text = models.TextField() # LLM generated prompts for image generation for this option
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Option {self.label} (Turn {self.turn_id})'

class ImageRender(models.Model):
    """
    Records image generation attempts for a given option.
    """
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('ready', 'ready'),
        ('failed', 'failed'),
    ]
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='renders') # 1-n for retries
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    filename = models.CharField(max_length=512, blank=True)
    last_render_filename = models.CharField(max_length=512, blank=True) # image of the last turn, as a fallback
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Render {self.id} ({self.status})'
