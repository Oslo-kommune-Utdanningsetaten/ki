from django.http import StreamingHttpResponse, JsonResponse
from openai import AsyncAzureOpenAI
from openai import AsyncAzureOpenAI
import openai
import azure.cognitiveservices.speech as speechsdk
import os
import json

azureClient = AsyncAzureOpenAI(
    azure_endpoint=os.environ.get('OPENAI_API_BASE'),
    api_key=os.environ.get('OPENAI_API_KEY'),
    api_version=os.environ.get('OPENAI_API_VERSION'),
)

async def chat_completion_azure(messages, options=None):
    if options is None:
        options = {}

    bot_model = options.get('bot_model', 'gpt-4o-mini')
    temperature = options.get('temperature', 0.7)

    try:
        completion = await azureClient.chat.completions.create(
            model=bot_model,
            messages=messages,
            temperature=float(temperature),
        )
    except openai.BadRequestError as e:
        if e.code == "content_filter":
            return "Dette er ikke et passende emne. Start samtalen på nytt."
        else:
            return "Noe gikk galt. Prøv igjen senere."

    if completion.choices:
        message = completion.choices[0].message.content or ""
        finish_reason = completion.choices[0].finish_reason

        if finish_reason == "content_filter":
            return "Beklager, vi stopper her! Dette er ikke passende innhold å vise. Start samtalen på nytt."
        elif finish_reason == "length":
            print(completion.choices[0].content_filter_results)
            return "Grensen for antall tegn i samtalen er nådd."

        return message
    else:
        return "Noe gikk galt. Prøv igjen senere."


async def chat_completion_azure_streamed(messages, options=None):
    if options is None:
        options = {}

    bot_model = options.get('bot_model', 'gpt-4o-mini')
    temperature = options.get('temperature', 0.7)

    async def stream():
        try:
            completion = await azureClient.chat.completions.create(
                model=bot_model,
                messages=messages,
                temperature=float(temperature),
                stream=True,
            )
        except openai.BadRequestError as e:
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
                    print(line.choices[0].content_filter_results)
                    yield "Grensen for antall tegn i samtalen er nådd."
                    break
                if chunk:
                    yield chunk

    return StreamingHttpResponse(stream(), content_type='text/event-stream')


async def generate_image_azure(prompt, options=None):
    if options is None:
        options = {}

    bot_model = options.get('bot_model', 'dall-e-3')
    size = options.get('size', '1024x1024')
    quality = options.get('quality', 'standard')
    number_of_images = options.get('n', 1)

    try:
        response = await azureClient.images.generate(
            model=bot_model,
            size=size,
            quality=quality,
            prompt=prompt,
            response_format='url',
            n=number_of_images,
        )
        json_response = json.loads(response.model_dump_json())
        data = json_response['data'][0]
    except openai.BadRequestError as e:
        if e.code == "content_policy_violation":
            data = {'msg': "Dette er ikke et passende emne. Velg noe annet å lage bilde av."}
        else:
            data = {'msg': "Noe gikk galt. Prøv igjen senere."}
    return JsonResponse(data)


