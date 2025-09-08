from django.db import models

class WorldBackground(models.Model):
    """
    Stores static world story background that can be reused across sessions.
    """
    content = models.TextField() # The static world background story

    def __str__(self):
        return f'WorldBackground: {self.content[:50]}...'

class Session(models.Model):
    """
    Stores a game session and its evolving world state.
    """
    world_background = models.ForeignKey(WorldBackground, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Session {self.id}'

class Turn(models.Model):
    """
    Core model: stores all data for a specific turn/year in the game.
    Uses year as primary key for easy lookup.
    """
    year = models.IntegerField(primary_key=True) # Year as primary key (e.g., 2035, 2036...)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='turns')
    
    # Question phase data
    question = models.TextField(blank=True) # Generated question text
    question_generated_at = models.DateTimeField(null=True, blank=True)
    
    # Description phase data  
    description = models.TextField(blank=True) # Generated description/scenario text
    description_generated_at = models.DateTimeField(null=True, blank=True)
    
    # RAG and LLM interaction data
    query_text = models.TextField(blank=True) # Latest query_text (updated in description phase)
    context_block = models.TextField(blank=True) # RAG retrieved context
    
    # User interaction (for shared session voting/consensus)
    user_choice = models.CharField(max_length=1, blank=True) # A, B, C, or D - final chosen option
    
    # Image management (preserved from teammate's design)
    displayed_image_rel = models.CharField(max_length=512, blank=True) # revealed image rel path for this turn/question

    class Meta:
        ordering = ['year']

    def __str__(self):
        return f'Turn {self.year} (Session {self.session_id})'

class Option(models.Model):
    """
    Stores individual options for a specific turn.
    Each turn has exactly 4 options (A, B, C, D) with corresponding image prompts.
    """
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=1) # A, B, C, D
    option_text = models.TextField(blank=True) # The actual option text displayed to user (may be empty initially)
    image_text = models.TextField(blank=True) # LLM generated prompt for image generation (added later)

    class Meta:
        ordering = ['label']
        unique_together = ['turn', 'label'] # Ensure one option per label per turn

    def __str__(self):
        return f'Option {self.label} for Turn {self.turn.year}'

class ImageRender(models.Model):
    """
    Records image generation attempts for a given option.
    """
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('ready', 'ready'),
        ('failed', 'failed'),
    ]
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='renders')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    image_rel = models.CharField(max_length=512, blank=True)
    last_turn_image_rel = models.CharField(max_length=512, blank=True) # image of the last turn, as a fallback

    def __str__(self):
        return f'Render {self.id} ({self.status}) for Option {self.option.label}'

class DefaultQueryList(models.Model):
    """
    Stores the initial query keywords list for year 2035 (when year-1 == 2034).
    """
    keyword = models.CharField(max_length=255)

    def __str__(self):
        return f'Default Query: {self.keyword}'
