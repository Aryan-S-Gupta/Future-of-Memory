from django.contrib import admin
from .models import WorldBackground, Session, Turn, Option, ImageRender, DefaultQueryList

@admin.register(WorldBackground)
class WorldBackgroundAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview']
    search_fields = ['content']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'world_background', 'created_at', 'turn_count']
    list_filter = ['created_at', 'world_background']
    
    def turn_count(self, obj):
        return obj.turns.count()
    turn_count.short_description = 'Turn Count'

@admin.register(Turn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ['year', 'session', 'has_question', 'has_description', 'user_choice', 'question_generated_at', 'description_generated_at']
    list_filter = ['session', 'user_choice', 'question_generated_at', 'description_generated_at']
    search_fields = ['question', 'description', 'query_text']
    ordering = ['year']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('year', 'session')
        }),
        ('Question Phase', {
            'fields': ('question', 'question_generated_at'),
            'classes': ('collapse',)
        }),
        ('Description Phase', {
            'fields': ('description', 'description_generated_at', 'user_choice'),
            'classes': ('collapse',)
        }),
        ('RAG & LLM Data', {
            'fields': ('query_text', 'context_block'),
            'classes': ('collapse',)
        }),
        ('Image Management', {
            'fields': ('displayed_image_rel',),
            'classes': ('collapse',)
        }),
    )
    
    def has_question(self, obj):
        return bool(obj.question)
    has_question.boolean = True
    has_question.short_description = 'Has Question'
    
    def has_description(self, obj):
        return bool(obj.description)
    has_description.boolean = True
    has_description.short_description = 'Has Description'

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['turn_year', 'label', 'has_option_text', 'has_image_text', 'render_count']
    list_filter = ['label', 'turn__session']
    search_fields = ['option_text', 'image_text', 'turn__year']
    ordering = ['turn__year', 'label']
    
    def turn_year(self, obj):
        return obj.turn.year
    turn_year.short_description = 'Year'
    
    def has_option_text(self, obj):
        return bool(obj.option_text)
    has_option_text.boolean = True
    has_option_text.short_description = 'Has Text'
    
    def has_image_text(self, obj):
        return bool(obj.image_text)
    has_image_text.boolean = True
    has_image_text.short_description = 'Has Image Prompt'
    
    def render_count(self, obj):
        return obj.renders.count()
    render_count.short_description = 'Renders'

@admin.register(ImageRender)
class ImageRenderAdmin(admin.ModelAdmin):
    list_display = ['id', 'option_info', 'status', 'has_image', 'has_fallback']
    list_filter = ['status', 'option__turn__session', 'option__label']
    search_fields = ['image_rel', 'last_turn_image_rel']
    
    def option_info(self, obj):
        return f"Year {obj.option.turn.year} - Option {obj.option.label}"
    option_info.short_description = 'Option Info'
    
    def has_image(self, obj):
        return bool(obj.image_rel)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    def has_fallback(self, obj):
        return bool(obj.last_turn_image_rel)
    has_fallback.boolean = True
    has_fallback.short_description = 'Has Fallback'

@admin.register(DefaultQueryList)
class DefaultQueryListAdmin(admin.ModelAdmin):
    list_display = ['keyword']
    search_fields = ['keyword']
