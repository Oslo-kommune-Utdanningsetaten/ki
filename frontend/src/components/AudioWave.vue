<template>
  <span class="audioWave">
    <span></span>
    <span></span>
    <span></span>
    <span></span>
    <span></span>
  </span>
</template>

<style>
.audioWave {
  display: inline-flex;
  align-items: flex-end;
  vertical-align: middle;
  justify-content: center;
  height: 80%;
  width: 80%;
  padding: 0px;
}

.audioWave span {
  display: inline-block;
  width: 15%;
  background-color: rgba(45, 45, 45, 0.5);
  margin-right: 2px;
  animation: sound 0.8s infinite;
  animation-timing-function: ease-out;
}

.audioWave span:nth-child(1) {
  animation-delay: 0.1s;
}

.audioWave span:nth-child(2) {
  animation-delay: 0s;
}

.audioWave span:nth-child(3) {
  animation-delay: 0.15s;
}

.audioWave span:nth-child(4) {
  animation-delay: 0.3s;
}

.audioWave span:nth-child(5) {
  animation-delay: 0.2s;
  margin-right: 0px;
}

@keyframes sound {
  0% {
    height: 1px;
  }
  1% {
    height: 100%;
  }
  100% {
    height: 1px;
  }
}
</style>
