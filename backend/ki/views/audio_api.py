import os
import asyncio
import json
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer
from azure.cognitiveservices.speech.audio import PushAudioInputStream
from channels.generic.websocket import AsyncWebsocketConsumer

class AudioConsumer(AsyncWebsocketConsumer):

    # Called when the WebSocket connection is opened
    async def connect(self):
        await self.accept()

        # Create a push stream
        self.push_stream = PushAudioInputStream()

        # Create an audio configuration using the push stream
        self.audio_config = AudioConfig(stream=self.push_stream)

        # Initialize speech recognizer with retries
        retries = 3
        while retries > 0:
            try:
                self.speech_config = SpeechConfig(subscription=os.environ.get('AZURE_SPEECH_KEY'), region=os.environ.get('AZURE_SPEECH_REGION'))
                self.speech_config.speech_recognition_language="nb-NO"
                self.speech_recognizer = SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)

                #self.speech_recognizer.recognizing.connect(self.recognizing_callback)
                self.speech_recognizer.recognized.connect(self.recognized_callback)
                self.speech_recognizer.session_stopped.connect(self.stop_callback)
                self.speech_recognizer.session_started.connect(self.start_callback)
                self.speech_recognizer.canceled.connect(self.canceled_callback)

                # Start recognition immediately
                self.speech_recognizer.start_continuous_recognition()
                print("Speech recognizer started.")
                break
            except Exception as e:
                print(f"Error initializing speech recognizer: {e}")
                retries -= 1
                if retries == 0:
                    await self.close()

    # Called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        print("WebSocket disconnected")
        self.speech_recognizer.stop_continuous_recognition()
        self.push_stream.close()
        await self.close()

    def recognized_callback(self, evt):
        recognized_text = evt.result.text
        print(f"->Recognized: {recognized_text}")
        if recognized_text:
            asyncio.run(self.send(text_data=json.dumps({
                "type": "websocket.send",
                "transcription": recognized_text
            })))

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            self.push_stream.write(bytes_data)

    def stop_callback(self, evt):
        print("Recognition stopped.")

    def start_callback(self, evt):
        print("Recognition started!")

    def canceled_callback(self, evt):
        print(f"Recognition canceled: {evt.reason}")