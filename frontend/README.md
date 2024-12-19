# ki - backend

Some notes/documentation on the communication going on across the websocket in audio mode\_

On start, the client sends a config message to the server, it typically looks like this:

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

The data stream from the server to the client is also either text or audio binary. An example of the former:

```json
{
  "type": "websocket.text",
  "serverStatus": "ready",
  "messages": [
    { "role": "system", "content": "You are a nice bot" },
    { "role": "user", "content": "What is sugar" },
    { "role": "assistant", "content": "Sugar is sweet" }
  ]
}
```

The `serverStatus` field reports what the server is currently up to. This can be one of

```json
[
  "websocketOpened",
  "websocketClosed",
  "initializing",
  "streamingAudioToAzure",
  "streamingTextToClient",
  "generatingChatResponse",
  "generatingAudioResponse",
  "streamingAudioToClient",
  "ready"
]
```

The `command` field flags the beginning or end of an audio stream
