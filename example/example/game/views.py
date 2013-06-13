from django.template.response import TemplateResponse


def index(request):
    return TemplateResponse(request, 'game/index.html')


def battle(request, battle_id):
    context = {
        'battle_id': battle_id
    }
    return TemplateResponse(request, 'game/battle.html', context)
