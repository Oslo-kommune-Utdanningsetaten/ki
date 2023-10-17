from .. import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import StreamingHttpResponse
import openai
import os

openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.api_version = os.environ.get('OPENAI_API_VERSION')
openai.api_base = os.environ.get('OPENAI_API_BASE')
openai.api_type = os.environ.get('OPENAI_API_TYPE')
deployment_name = os.environ.get('OPENAI_API_DEPLOYMENT')


@api_view(["POST"])
def start_message(request, bot_nr):
    bot = models.Bot.objects.get(bot_nr=bot_nr)
    if not bot:
        # abort(404)
        return Response(status=404)

    return Response({'bot': {
        'bot_nr': bot.bot_nr,
        'title': bot.title,
        'ingress': bot.ingress,
        'prompt': bot.prompt,
    }})


@api_view(["POST"])
def send_message(request):
    bot_nr = request.data.get('bot_nr')
    messages = request.data.get('messages')
    if not bot_nr in request.g.get('bots', []):
        return Response(status=403)
    bot = models.Bot.objects.get(bot_nr=bot_nr)
    if not bot:
        return Response(status=404)

    async def stream():
        completion = await openai.ChatCompletion.acreate(
            model=bot.model,
            messages=messages,
            deployment_id=deployment_name,
            stream=True)
        async for line in completion:
            chunk = line['choices'][0].get('delta', {}).get('content', '')
            if chunk:
                yield chunk

    return StreamingHttpResponse(stream(), content_type='text/event-stream')
