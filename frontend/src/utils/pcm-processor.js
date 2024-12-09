class PCMProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0]
    if (input && input[0]) {
      // Mono channel data
      const channelData = input[0]

      // Resample to 16kHz
      const resampledData = this.resample(channelData, sampleRate, 16000)

      // Convert Float32 to Int16 PCM
      const pcmData = this.float32ToInt16(resampledData)

      // Post PCM data to the main thread
      this.port.postMessage(pcmData.buffer)
    }

    return true // Keep processor alive
  }

  resample(buffer, inputSampleRate, outputSampleRate) {
    const sampleRateRatio = inputSampleRate / outputSampleRate
    const newLength = Math.round(buffer.length / sampleRateRatio)
    const resampledBuffer = new Float32Array(newLength)
    for (let i = 0; i < newLength; i++) {
      const originalIndex = i * sampleRateRatio
      const lowerIndex = Math.floor(originalIndex)
      const upperIndex = Math.ceil(originalIndex)
      const interpolation = originalIndex - lowerIndex
      resampledBuffer[i] = (1 - interpolation) * buffer[lowerIndex] + interpolation * buffer[upperIndex]
    }
    return resampledBuffer
  }

  float32ToInt16(buffer) {
    const int16Array = new Int16Array(buffer.length)
    for (let i = 0; i < buffer.length; i++) {
      int16Array[i] = Math.min(1, Math.max(-1, buffer[i])) * 0x7FFF // Clamp and scale
    }
    return int16Array
  }
}

registerProcessor('pcm-processor', PCMProcessor)
