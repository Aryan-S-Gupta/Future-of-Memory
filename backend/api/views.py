import json
import os
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'data/static_questions.json'), 'r', encoding='utf-8') as f:
    STATIC_QUESTIONS = json.load(f)

with open(os.path.join(BASE_DIR, 'data/static_stories.json'), 'r', encoding='utf-8') as f:
    STATIC_STORIES = json.load(f)

@csrf_exempt
def get_static_question(request):
    q = random.choice(STATIC_QUESTIONS)
    return JsonResponse(q)

@csrf_exempt
def get_static_story(request):
    year = int(request.GET.get('year', 2071))
    story = next((s for s in STATIC_STORIES if s['year'] == year), None)
    return JsonResponse(story or {'year': year, 'story': '暂无故事数据'})