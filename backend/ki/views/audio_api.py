import os
import asyncio
import json
import uuid
import logging
import datetime
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, SpeechSynthesizer, AudioDataStream, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import PushAudioInputStream
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from ki.ai_providers.azure import chat_completion_azure
from ki.utils import use_log

# Raise the root logger threshold to WARNING
logging.basicConfig(level=logging.WARNING)
# Create a dedicated logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AudioConsumer(AsyncWebsocketConsumer):

    # Called when the WebSocket connection is opened
    async def connect(self):
        await self.accept()

        # Initialize vars
        self.connection_id = str(uuid.uuid4())
        self.messages = []
        self.bot_model = None
        self.bot_uuid = None
        self.user_level = None
        self.user_role = None
        self.user_schools = None
        self.selected_language = None
        self.selected_voice = None
        self.selected_speech_rate = None
        self.current_server_status = None
        self.speech_recognizer = None
        self.speech_synthesizer = None
        await self.send_server_status("websocketOpened")

        # Define speech config
        self.speech_config = SpeechConfig(subscription=os.environ.get('AZURE_SPEECH_KEY'), region=os.environ.get('AZURE_SPEECH_REGION'))

        # Create a push stream
        self.push_stream_audio = PushAudioInputStream()

        # Create an audio configuration using the push stream
        self.audio_input_config = AudioConfig(stream=self.push_stream_audio)


    # Override disconnect method to handle graceful cleanup
    async def websocket_disconnect(self, message):
        self.log(f"Disconnect because: {message["code"]}")
        try:
            self.push_stream_audio.close()
            self.speech_recognizer.stop_continuous_recognition()
            self.speech_synthesizer.stop_speaking()
        except Exception as e:
            self.log(f"Error during cleanup: {e}")
        raise StopConsumer()


    # Fires when the WebSocket receives a message from the client
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            # Client is sending text data. This usually happens at init and when language/voice is changed
            data = json.loads(text_data)

            # Handle ping command
            if data.get("type") == "websocket.text" and data.get("command") == "ping":
                await self.send(text_data=json.dumps({
                    "type": "websocket.text",
                    "command": "pong"
                }))
                return

            # Record bot model, bot UUID, messages, language and voice
            if data.get('bot_uuid'):
                self.bot_uuid = data.get('bot_uuid')
            if data.get('bot_model'):
                self.bot_model = data.get('bot_model')
            if data.get('messages'):
                self.messages = data.get('messages')
            if data.get('selected_language'):
                self.selected_language = data.get('selected_language')
            if data.get('selected_voice'):
                self.selected_voice = data.get('selected_voice')
            if data.get('selected_speech_rate'):
                self.selected_speech_rate = data.get('selected_speech_rate')
            if data.get('user_info'):
                self.user_role = data.get('user_info', {}).get('role', None)
                self.user_level = data.get('user_info', {}).get('level', None)
                self.user_schools = data.get('user_info', {}).get('schools', [])
                self.log(f"User info: role: {self.user_role}, level: {self.user_level}, schools: {self.user_schools}")

            # Initialize speech recognizer if client made changes
            if self.selected_language != self.speech_config.speech_recognition_language:
                await self.initialize_speech_recognizer()
            # Initialize speech synthesizer if client made changes
            if self.selected_language != self.speech_config.speech_recognition_language or self.selected_voice != self.speech_config.speech_synthesis_voice_name:
                await self.initialize_speech_synthesizer()

        elif bytes_data:
            # We're receiving audio from the client and passing it on to Azure
            await self.send_server_status("receivingAudioFromClient")
            try:
                # Write to outbound stream for transcription by Azure
                self.push_stream_audio.write(bytes_data)
            except Exception as e:
                self.log(f"Error while processing audio data: {e}")
                # Re-create a push stream
                self.push_stream_audio = PushAudioInputStream()
                # Create an audio configuration using the new push stream
                self.audio_input_config = AudioConfig(stream=self.push_stream_audio)
                # Reinitialize speech recognizer
                await self.initialize_speech_recognizer()


    async def create_completion_from_transcript(self, recognized_text):
        # For cosmetic reasons, if recognized_text includes only one period, remove it
        if recognized_text.count('.') == 1:
            recognized_text = recognized_text.strip('.')

        self.messages.append({
            "role": "user",
            "content": recognized_text
        })

        await self.send_server_status("sendingTextToClient")

        # Send updated messages to client
        await self.send(text_data=json.dumps({
            "type": "websocket.text",
            "messages": self.messages
        }))

        # Log usage
        try:
            await use_log(self.bot_uuid, role=self.user_role, level=self.user_level, schools=self.user_schools, message_length=len(self.messages), interaction_type='audio')
        except Exception as e:
            self.log(f"Error while logging usage: {e}")

        await self.send_server_status("generatingChatResponse")

        # Request completion based on messages
        completion = await chat_completion_azure(self.messages, self.bot_model)

        # Append completion to messages
        self.messages.append({
            "role": "assistant",
            "content": completion
        })

        await self.send_server_status("sendingTextToClient")

        # Send updated messages to client
        await self.send(text_data=json.dumps({
            "type": "websocket.text",
            "messages": self.messages
        }))

        # Synthesize completion and stream audio to client
        await self.synthesize_and_stream(completion)


    # Synthesize speech from text and stream audio to client
    async def synthesize_and_stream(self, textInput):
        await self.send_server_status("generatingAudioResponse")

        try:
            input_ssml = self.assemble_ssml(textInput)
            result = self.speech_synthesizer.speak_ssml_async(input_ssml).get()
            audio_stream = AudioDataStream(result)
        except Exception as e:
            self.log(f"Error during speech synthesis: {e}")
            return

        # send start signal to client
        await self.send(text_data=json.dumps({
            "type": "websocket.audio",
            "command": "audio-stream-begin"
        }))

        # Stream until no more data
        await self.send_server_status("streamingAudioToClient")
        try:
            buffer = bytes(16000)
            filled_size = audio_stream.read_data(buffer)
            while filled_size > 0:
                await self.send(bytes_data=buffer[:filled_size])
                filled_size = audio_stream.read_data(buffer)
        except Exception as e:
            self.log(f"Error while streaming audio to client: {e}")

        # send stop signal to client
        await self.send(text_data=json.dumps({
            "type": "websocket.audio",
            "command": "audio-stream-end"
        }))
        await self.send_server_status("idle")


    async def initialize_speech_recognizer(self):
        self.log(f"Initializing speech recognizer [{self.selected_language}]")
        await self.send_server_status("initializing")
        # Stop any existing recognition
        if self.speech_recognizer:
            self.speech_recognizer.stop_continuous_recognition()
        # Initialize speech recognizer
        self.speech_config.speech_recognition_language=self.selected_language
        self.speech_recognizer = SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_input_config)
        # Register speech recognizer callbacks
        self.speech_recognizer.recognized.connect(self.recognized_callback)
        self.speech_recognizer.session_stopped.connect(self.stop_callback)
        self.speech_recognizer.session_started.connect(self.start_callback)
        self.speech_recognizer.canceled.connect(self.canceled_callback)
        self.speech_recognizer.speech_start_detected.connect(self.speech_start_callback)
        self.speech_recognizer.speech_end_detected.connect(self.speech_end_callback)
        # Start recognition immediately
        self.speech_recognizer.start_continuous_recognition()
        await self.send_server_status("idle")


    async def initialize_speech_synthesizer(self):
        self.log(f"Initializing speech synthesizer [{self.selected_language}, {self.selected_voice}]")
        await self.send_server_status("initializing")
        # Stop any existing synthesis
        if self.speech_synthesizer:
            self.speech_synthesizer.stop_speaking()
        # Initialize speech synthesizer
        self.speech_config.speech_synthesis_voice_name=self.selected_voice
        self.speech_config.set_speech_synthesis_output_format(
            SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
        )
        self.speech_synthesizer = SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
        await self.send_server_status("idle")


    # Wrapper for easy sending of server status to websocket client
    async def send_server_status(self, status):
        if self.current_server_status == status:
            return
        self.log(f"Status: {status}")
        self.current_server_status = status
        await self.send(text_data=json.dumps({
            "type": "websocket.text",
            "serverStatus": status,
            "connectionId": self.connection_id
        }))


    # Use SSML in order to control speech rate
    def assemble_ssml(self, text):
        return f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{self.selected_language}'><voice name='{self.selected_voice}'><prosody rate='{self.selected_speech_rate}'>{text}</prosody></voice></speak>"


    # Wrapper for easy logging with connection_id prefix
    def log(self, message):
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        logger.debug(f"{utc_time.strftime("%Y-%m-%dT%H:%M:%S")} :: {self.connection_id} :: {message}")


    # Speech recognizer callback which fires whenever Azure recognizes speech
    def recognized_callback(self, evt):
        recognized_text = evt.result.text
        if recognized_text:
            asyncio.run(self.create_completion_from_transcript(recognized_text))

    # The following callbacks are not used, but implemented to get a sense of what happens when
    def speech_start_callback(self, evt):
        self.log(f"Recognition start")

    def speech_end_callback(self, evt):
        self.log(f"Recognition end")

    def stop_callback(self, evt):
        self.log(f"Recognition stopped")

    def start_callback(self, evt):
        self.log("Ready and awaiting audio stream from client")

    def canceled_callback(self, evt):
        self.log(f"Recognition canceled: {evt.reason}")

