from django.http import StreamingHttpResponse, JsonResponse
from openai import AsyncAzureOpenAI, BadRequestError
import os
import json

default_model = 'gpt-4o-mini'
DEFAULT_TEMPERATURE = 0.7

azureClient = AsyncAzureOpenAI(
    azure_endpoint=os.environ.get('OPENAI_API_BASE'),
    api_key=os.environ.get('OPENAI_API_KEY'),
    api_version=os.environ.get('OPENAI_API_VERSION'),
)


async def chat_completion_azure(chat_parameters):
    try:
        completion = await azureClient.chat.completions.create(
            **chat_parameters
        )
    except BadRequestError as e:
        if e.code == "content_filter":
            return "Dette er ikke et passende emne. Start samtalen på nytt."
        else:
            return "Noe gikk galt. Prøv igjen senere?"
    except Exception as e:
        return "Noe gikk galt. Kanskje du kan prøve igjen?"

    if completion.choices:
        message = completion.choices[0].message.content or ""
        finish_reason = completion.choices[0].finish_reason

        if finish_reason == "content_filter":
            return "Beklager, vi stopper her! Dette er ikke passende innhold å vise. Start samtalen på nytt."
        elif finish_reason == "length":
            return "Grensen for antall tegn i samtalen er nådd."
        return message
    else:
        return "Noe gikk galt. Mulig det hjelper å prøve igjen, men det er ikke sikkert."


async def chat_completion_azure_streamed(chat_parameters):
    async def stream():
        try:
            completion = await azureClient.chat.completions.create(
                stream=True,
                **chat_parameters,
            )
        except BadRequestError as e:
            if e.code == "content_filter":
                yield "Dette er ikke et passende emne. Start samtalen på nytt."
            else:
                yield "Noe gikk galt. Prøv igjen senere."
            return
        async for line in completion:
            if line.choices:
                chunk = line.choices[0].delta.content or ""
                if line.choices[0].finish_reason == "content_filter":
                    yield "Beklager, vi stopper her! Dette er ikke passende innhold å vise. Start samtalen på nytt."
                    break
                if line.choices[0].finish_reason == "length":
                    yield "Grensen for antall tegn i samtalen er nådd."
                    break
                if chunk:
                    yield chunk
    return StreamingHttpResponse(stream(), content_type='text/event-stream')


async def generate_image_azure(parameters):
    try:
        response = await azureClient.images.generate(
            **parameters,
            response_format='url',
            size='1024x1024',
            quality='standard',
            n=1,
        )
        json_response = json.loads(response.model_dump_json())
        data = json_response['data'][0]
    except BadRequestError as e:
        if e.code == "content_policy_violation":
            data = {'system_message': "Jeg klarte ikke å lage et bilde av den instruksen. Prøv igjen med en annen?"}
        else:
            data = {'system_message': "Noe gikk galt. Prøv igjen senere."}
    return JsonResponse(data)
