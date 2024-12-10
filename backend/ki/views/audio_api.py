import os
import asyncio
import json
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, SpeechSynthesizer, AudioDataStream, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import PushAudioInputStream
from channels.generic.websocket import AsyncWebsocketConsumer

# consider using a websocket connection to Azure
# https://github.com/Azure-Samples/cognitive-services-speech-sdk/blob/master/samples/python/tts-text-stream/text_stream_sample.py

voices = ['nb-NO-PernilleNeural', 'nb-NO-FinnNeural', 'nb-NO-IselinNeural']

class AudioConsumer(AsyncWebsocketConsumer):

    # Called when the WebSocket connection is opened
    async def connect(self):
        await self.accept()

        # Create a push stream
        self.push_stream_audio = PushAudioInputStream()

        # Create an audio configuration using the push stream
        self.audio_input_config = AudioConfig(stream=self.push_stream_audio)

        # Initialize speech recognizer with retries
        retries = 3
        while retries > 0:
            try:
                # Configure recognizer
                self.speech_config = SpeechConfig(subscription=os.environ.get('AZURE_SPEECH_KEY'), region=os.environ.get('AZURE_SPEECH_REGION'))
                self.speech_config.speech_recognition_language="nb-NO"
                self.speech_recognizer = SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_input_config)

                # Register callbacks
                self.speech_recognizer.recognized.connect(self.recognized_callback)
                self.speech_recognizer.session_stopped.connect(self.stop_callback)
                self.speech_recognizer.session_started.connect(self.start_callback)
                self.speech_recognizer.canceled.connect(self.canceled_callback)

                # Start recognition immediately
                self.speech_recognizer.start_continuous_recognition()

                # Configure synthesizer
                self.speech_config.speech_synthesis_voice_name=voices[1]
                self.speech_config.set_speech_synthesis_output_format(
                    SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
                )
                self.speech_synthesizer = SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
                break

            except Exception as e:
                print(f"Error initializing speech recognizer: {e}")
                retries -= 1
                if retries == 0:
                    await self.close()

    # Called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        self.speech_recognizer.stop_continuous_recognition()
        self.push_stream_audio.close()
        self.speech_synthesizer.stop_speaking()
        await self.close()

    # Called when the WebSocket receives a message
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            # client is sending text data, synthesize and stream
            textInput = json.loads(text_data)['message']
            await self.synthesize_and_stream(textInput)
        if bytes_data:
            # client is sending audio data, write to stream for transcription
            self.push_stream_audio.write(bytes_data)


    async def synthesize_and_stream(self, textInput):
        result = self.speech_synthesizer.speak_text_async(textInput).get()
        audio_stream = AudioDataStream(result)

        # send start signal to client
        await self.send(text_data=json.dumps({
            "type": "websocket.audio",
            "status": "start"
        }))
        
        # Stream until no more data
        try:
            buffer = bytes(16000)
            filled_size = audio_stream.read_data(buffer)
            while filled_size > 0:
                await self.send(bytes_data=buffer[:filled_size])
                filled_size = audio_stream.read_data(buffer)
        except Exception as e:
            print(f"Error while streaming audio to client: {e}")

        # send stop signal to client
        await self.send(text_data=json.dumps({
            "type": "websocket.audio",
            "status": "stop"
        }))


    def recognized_callback(self, evt):
        recognized_text = evt.result.text
        if recognized_text:
            asyncio.run(self.send(text_data=json.dumps({
                "type": "websocket.text",
                "transcript": recognized_text
            })))

    def stop_callback(self, evt):
        print("Recognition stopped.")

    def start_callback(self, evt):
        print("Recognition started!")

    def canceled_callback(self, evt):
        print(f"Recognition canceled: {evt.reason}")