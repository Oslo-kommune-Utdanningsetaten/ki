# ki - backend

Some notes/documentation on the communication going on across the websocket in audio mode.

## Messages from the client

When the user presses the record button, a websocket connection is opened, and the client sends a config message to the server, it typically looks like this:

```json
{
  "type": "websocket.text",
  "selected_language": "nb-NO",
  "selected_voice": "nb-NO-IselinNeural",
  "bot_uuid": "some-uuid",
  "bot_model": "gpt-4o-mini"
}
```

It then follows up with a message containing the initial dialog (between user and chatbot)

```json
{
  "type": "websocket.text",
  "messages": [{ "role": "system", "content": "You are a nice bot" }]
}
```

## Messages from the server

The server will report on its status using the `serverStatus`. Such messages look like:

```json
{
  "type": "websocket.text",
  "serverStatus": "idle"
}
```

Server status may be one of:

```js
;[
  'websocketOpened', // the websocket connection was just opened
  'websocketClosed', // the websocket connection closed
  'initializing', // initializing serverside config (language, voice, azure connection etc)
  'streamingAudioToAzure', // audio (received from the client) is now being streamed from the server to azure
  'streamingTextToClient', // sending text update to client
  'generatingChatResponse', // azure chat completion is currently in progress
  'generatingAudioResponse', // azure is working on speech synthesis
  'streamingAudioToClient', // audio (received from azure) is being streamed from the server to the client
  'idle', // server is chilling and ready for duty
]
```

When streaming audio, the server will begin the stream with this message:

```json
{
  "type": "websocket.audio",
  "command": "audio-stream-begin"
}
```

When streaming audio, the server will signal that the stream is finished with this message:

```json
{
  "type": "websocket.audio",
  "command": "audio-stream-end"
}
```

A `ping` command sent to the server will be returned with as similar message containing `pong`

```json
{
  "type": "websocket.text",
  "command": "ping"
}
```
