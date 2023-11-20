from .. import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponseForbidden
import openai
import os
import json
# from ..mock import mock_acreate

openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.api_base = os.environ.get('OPENAI_API_BASE')
openai.api_type = os.environ.get('OPENAI_API_TYPE')


@api_view(["POST"])
def start_message(request, bot_nr):
    try:
        bot = models.Bot.objects.get(bot_nr=bot_nr)
    except models.Bot.DoesNotExist:
        return Response(status=404)

    return Response({'bot': {
        'bot_nr': bot.bot_nr,
        'title': bot.title,
        'ingress': bot.ingress,
        'prompt': bot.prompt,
    }})


async def send_message(request):
    body = json.loads(request.body)
    bot_nr = body.get('bot_nr')
    messages = body.get('messages')
    if not bot_nr in request.g.get('bots', []):
        return HttpResponseForbidden()
    try:
        bot = await models.Bot.objects.aget(bot_nr=bot_nr)
    except models.Bot.DoesNotExist:
        return HttpResponseNotFound()

    async def stream():
        completion = await openai.ChatCompletion.acreate(
            engine=bot.model,
            messages=messages,
            stream=True,
            )
        # Mock function for loadtesting etc.:
        # completion = await mock_acreate()
        async for line in completion:
            if line['choices']:
                chunk = line['choices'][0].get('delta', {}).get('content', '')
                if chunk:
                    yield chunk

    return StreamingHttpResponse(stream(), content_type='text/event-stream')
