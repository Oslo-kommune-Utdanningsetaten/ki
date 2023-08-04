from flask import Blueprint, g, abort, redirect, request, session, url_for, jsonify, current_app
import random
import time
import openai
from app import db
from app.main import models


api = Blueprint('api', __name__, url_prefix='/api')

openai.api_key = current_app.config['OPENAI_API_KEY']
openai.organization = current_app.config['OPENAI_ORG_ID']


# define a retry decorator, 
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (openai.error.RateLimitError,),
):
    """Retry a function with exponential backoff."""
 
    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay
 
        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)
 
            # Retry on specific errors
            except errors as e:
                # Increment retries
                num_retries += 1
 
                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )
 
                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())
 
                # Sleep for the delay
                time.sleep(delay)
 
            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e
 
    return wrapper
    
@api.route('/bot/<bot_nr>', methods=['POST'])
def start_message(bot_nr):

    bot = models.Bot.query.get(bot_nr)
    if not bot:
        abort(404)

    return jsonify({'bot': {
        'bot_nr': bot.bot_nr,
        'title': bot.title,
        'ingress': bot.ingress,
        'prompt': bot.prompt,
        }})


@api.route('/send_message', methods=['POST'])
def send_message():

    bot_nr = request.json.get('bot_nr')
    if not bot_nr in g.bots:
        abort(403)
    bot = models.Bot.query.get(bot_nr)
    if not bot:
        abort(404)
    messages = request.json.get('messages')
    return_messages = send_to_openai(bot, messages)

    return jsonify({'messages': return_messages})


@retry_with_exponential_backoff
def send_to_openai(bot, messages):
    response = openai.ChatCompletion.create(
      model=bot.model,
      messages=messages
    )

    if response['choices'][0]['finish_reason'] == 'stop':
        return_messages = response['choices'][0]['message']
        return return_messages

