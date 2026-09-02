// Web Audio API visualizer, recorder, and playback with real audio reactivity

// Browser Web Speech API SpeechRecognition wrapper
class BrowserSpeechRecognizer {
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.isSupported = !!SpeechRecognition;
    this.recognition = null;
    this.isActive = false;
    this.onInterim = null;
    this.onFinal = null;
    this.onError = null;
    this.onEnd = null;

    if (this.isSupported) {
      try {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false; // Turn-based command listening
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        this.recognition.onresult = (event) => {
          let interimTranscript = "";
          let finalTranscript = "";

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            const result = event.results[i];
            const text = result[0].transcript;
            if (result.isFinal) {
              finalTranscript += text;
            } else {
              interimTranscript += text;
            }
          }

          if (interimTranscript && this.onInterim) {
            this.onInterim(interimTranscript);
          }
          if (finalTranscript && this.onFinal) {
            this.onFinal(finalTranscript.trim());
          }
        };

        this.recognition.onerror = (event) => {
          this.isActive = false;
          if (this.onError) {
            this.onError(event.error);
          }
        };

        this.recognition.onend = () => {
          this.isActive = false;
          if (this.onEnd) {
            this.onEnd();
          }
        };
      } catch (err) {
        console.warn("SpeechRecognition initialization failed:", err);
        this.isSupported = false;
      }
    }
  }

  start(lang = "en-US", onInterim = null, onFinal = null, onError = null, onEnd = null) {
    if (!this.isSupported || !this.recognition) return false;
    this.onInterim = onInterim;
    this.onFinal = onFinal;
    this.onError = onError;
    this.onEnd = onEnd;

    try {
      this.recognition.lang = lang;
      this.recognition.start();
      this.isActive = true;
      return true;
    } catch (e) {
      console.warn("SpeechRecognition start warning:", e);
      return false;
    }
  }

  stop() {
    if (!this.recognition || !this.isActive) return;
    try {
      this.recognition.stop();
    } catch (e) {}
    this.isActive = false;
  }

  abort() {
    if (!this.recognition) return;
    try {
      this.recognition.abort();
    } catch (e) {}
    this.isActive = false;
  }
}

class AudioSystem {
  constructor() {
    this.audioCtx = null;
    this.analyser = null;
    this.micStream = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.currentAudioElement = null;
    this.currentAudioUrl = null;
    this.sourceNodesMap = new WeakMap();
    this.isRecording = false;
    this.speechRecognizer = new BrowserSpeechRecognizer();
    this.animationId = null;
    this.cadenceInterval = null;
    this.canvas = null;
    this.canvasCtx = null;
  }

  initVisualizer(canvasElement) {
    this.canvas = canvasElement;
    this.canvasCtx = canvasElement.getContext("2d");
    this.resizeCanvas();
    window.addEventListener("resize", () => this.resizeCanvas());
    this.drawIdleWave();
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const parent = this.canvas.parentElement;
    const dpr = window.devicePixelRatio || 1;
    const rect = parent.getBoundingClientRect();
    const w = rect.width || 400;
    const h = rect.height || 48;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.canvas.style.width = `${w}px`;
    this.canvas.style.height = `${h}px`;
    if (this.canvasCtx) {
      this.canvasCtx.scale(dpr, dpr);
    }
  }

  ensureAudioContext() {
    if (!this.audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioCtxClass();
      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 64;
      this.analyser.smoothingTimeConstant = 0.82;
    }
    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }
  }

  // 1. Microphone recording
  async startRecording() {
    this.ensureAudioContext();
    this.audioChunks = [];
    try {
      this.micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = this.audioCtx.createMediaStreamSource(this.micStream);
      source.connect(this.analyser);
      
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") 
        ? "audio/webm;codecs=opus" 
        : (MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "");

      this.mediaRecorder = mimeType ? new MediaRecorder(this.micStream, { mimeType }) : new MediaRecorder(this.micStream);
      
      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) this.audioChunks.push(e.data);
      };

      this.mediaRecorder.start(250);
      this.isRecording = true;
      appState.setState(AssistantState.LISTENING);
      this.startVisualizerLoop();
      return true;
    } catch (err) {
      console.error("Microphone access error:", err);
      appState.setState(AssistantState.ERROR);
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        if (window.showToast) window.showToast("Microphone permission denied. You can type your query below.");
      } else {
        if (window.showToast) window.showToast("Microphone unavailable.");
      }
      setTimeout(() => appState.setState(AssistantState.IDLE), 2500);
      throw err;
    }
  }

  stopRecording() {
    return new Promise((resolve) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === "inactive") {
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        const mime = this.mediaRecorder.mimeType || "audio/webm";
        const blob = new Blob(this.audioChunks, { type: mime });
        this.isRecording = false;
        if (this.micStream) {
          this.micStream.getTracks().forEach(t => t.stop());
          this.micStream = null;
        }
        this.resetAudioAmplitude();
        resolve(blob);
      };

      this.mediaRecorder.stop();
    });
  }

  // Connect mic stream to visualizer during speech recognition
  async startMicVisualizer() {
    this.ensureAudioContext();
    try {
      if (!this.micStream) {
        this.micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const source = this.audioCtx.createMediaStreamSource(this.micStream);
        source.connect(this.analyser);
      }
      this.startVisualizerLoop();
      return true;
    } catch (err) {
      console.warn("Could not attach mic stream to visualizer:", err);
      return false;
    }
  }

  stopMicVisualizer() {
    if (this.micStream) {
      this.micStream.getTracks().forEach(t => t.stop());
      this.micStream = null;
    }
    this.resetAudioAmplitude();
    this.drawIdleWave();
  }

  cancelRecording() {
    if (this.speechRecognizer && this.speechRecognizer.isActive) {
      this.speechRecognizer.abort();
    }
    if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
      this.mediaRecorder.stop();
    }
    this.stopMicVisualizer();
    this.isRecording = false;
    this.audioChunks = [];
    this.resetAudioAmplitude();
    appState.setState(AssistantState.IDLE);
    this.drawIdleWave();
  }

  // 2. Assistant speech playback & interruption
  speakText(text, onEnded = null) {
    this.stopAudio();
    if (!text) {
      if (onEnded) onEnded();
      return;
    }

    // If browser supports SpeechSynthesis and user preference is speech or auto
    if ("speechSynthesis" in window) {
      try {
        window.speechSynthesis.cancel(); // clean slate
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = appState.settings.voice_speed || 1.0;
        utterance.pitch = 1.0;

        // Try selecting matching voice or pleasant voice
        const voices = window.speechSynthesis.getVoices() || [];
        const lang = appState.settings.language || "en";
        const matchedVoice = voices.find(v => v.lang && v.lang.startsWith(lang)) || voices[0];
        if (matchedVoice) utterance.voice = matchedVoice;

        appState.setState(AssistantState.SPEAKING);
        this.startCadenceLoop();

        utterance.onend = () => {
          this.stopCadenceLoop();
          this.resetAudioAmplitude();
          appState.setState(AssistantState.IDLE);
          this.drawIdleWave();
          if (onEnded) onEnded();
          if (appState.handsFree) {
            setTimeout(() => appState.emit("handsFreeNextTurn"), 600);
          }
        };

        utterance.onerror = (err) => {
          console.warn("Speech synthesis notice:", err);
          this.stopCadenceLoop();
          this.resetAudioAmplitude();
          appState.setState(AssistantState.IDLE);
          this.drawIdleWave();
        };

        window.speechSynthesis.speak(utterance);
        return;
      } catch (err) {
        console.warn("SpeechSynthesis error, falling back to audio chime:", err);
      }
    }

    // Fallback to audio chime if available
    if (this.currentAudioUrl) {
      this.playAudio(this.currentAudioUrl, onEnded);
    }
  }

  playAudio(audioUrl, onEnded = null) {
    this.ensureAudioContext();
    this.stopAudio(); // Interrupt any ongoing speech
    
    this.currentAudioUrl = audioUrl;
    const audio = new Audio(audioUrl);
    this.currentAudioElement = audio;
    
    // Connect audio to analyser without duplicate source node errors
    try {
      let source = this.sourceNodesMap.get(audio);
      if (!source) {
        source = this.audioCtx.createMediaElementSource(audio);
        this.sourceNodesMap.set(audio, source);
      }
      source.connect(this.analyser);
      this.analyser.connect(this.audioCtx.destination);
    } catch (e) {
      // Audio element may already be connected
    }

    appState.setState(AssistantState.SPEAKING);
    this.startVisualizerLoop();

    audio.onended = () => {
      this.resetAudioAmplitude();
      appState.setState(AssistantState.IDLE);
      this.drawIdleWave();
      if (onEnded) onEnded();
      if (appState.handsFree) {
        setTimeout(() => {
          appState.emit("handsFreeNextTurn");
        }, 500);
      }
    };

    audio.onerror = (e) => {
      console.error("Audio playback error:", e);
      this.resetAudioAmplitude();
      appState.setState(AssistantState.IDLE);
      this.drawIdleWave();
    };

    audio.play().catch(err => {
      console.warn("Autoplay was blocked or interrupted:", err);
      this.resetAudioAmplitude();
      appState.setState(AssistantState.IDLE);
    });
  }

  stopAudio() {
    // 1. Stop HTML5 audio element
    if (this.currentAudioElement) {
      this.currentAudioElement.pause();
      this.currentAudioElement.currentTime = 0;
      this.currentAudioElement = null;
    }
    // 2. Stop browser speech synthesis
    if ("speechSynthesis" in window && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }
    // 3. Abort speech recognition if active
    if (this.speechRecognizer && this.speechRecognizer.isActive) {
      this.speechRecognizer.abort();
    }
    // 4. Release any active microphone streams
    this.stopMicVisualizer();
    this.stopCadenceLoop();
    this.resetAudioAmplitude();
    if (appState.getState() === AssistantState.SPEAKING || appState.getState() === AssistantState.LISTENING) {
      appState.setState(AssistantState.IDLE);
      this.drawIdleWave();
    }
  }

  replayAudio() {
    if (this.currentAudioUrl) {
      this.playAudio(this.currentAudioUrl);
    }
  }

  startCadenceLoop() {
    if (this.cadenceInterval) clearInterval(this.cadenceInterval);
    let step = 0;
    this.cadenceInterval = setInterval(() => {
      if (appState.getState() !== AssistantState.SPEAKING) {
        this.stopCadenceLoop();
        return;
      }
      step += 0.2;
      // Synthesize rhythmic speech volume modulation between 0.15 and 0.75
      const mod = 0.45 + Math.sin(step * 3) * 0.2 + Math.cos(step * 5) * 0.1;
      const amp = Math.max(0.1, Math.min(0.85, mod));
      document.documentElement.style.setProperty("--audio-amp", amp.toFixed(3));
      this.drawSyntheticWave(amp);
    }, 50);
  }

  stopCadenceLoop() {
    if (this.cadenceInterval) {
      clearInterval(this.cadenceInterval);
      this.cadenceInterval = null;
    }
  }

  drawSyntheticWave(amp) {
    if (!this.canvasCtx || !this.canvas) return;
    const width = this.canvas.parentElement ? this.canvas.parentElement.clientWidth : 400;
    const height = this.canvas.parentElement ? this.canvas.parentElement.clientHeight : 48;
    this.canvasCtx.clearRect(0, 0, width, height);

    const bars = 24;
    const barWidth = width / bars;
    for (let i = 0; i < bars; i++) {
      const h = Math.sin((i / bars) * Math.PI) * (height * amp * 0.8);
      const grad = this.canvasCtx.createLinearGradient(0, height, 0, 0);
      grad.addColorStop(0, "rgba(0, 242, 254, 0.4)");
      grad.addColorStop(1, "rgba(127, 0, 255, 0.9)");
      this.canvasCtx.fillStyle = grad;
      const y = (height - h) / 2;
      this.canvasCtx.fillRect(i * barWidth + 2, y, barWidth - 4, Math.max(2, h));
    }
  }

  resetAudioAmplitude() {
    document.documentElement.style.setProperty("--audio-amp", "0");
  }

  // 3. Audio visualizer loop
  startVisualizerLoop() {
    if (this.animationId) cancelAnimationFrame(this.animationId);

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const draw = () => {
      const state = appState.getState();
      if (state !== AssistantState.LISTENING && state !== AssistantState.SPEAKING) {
        this.resetAudioAmplitude();
        this.drawIdleWave();
        return;
      }

      this.animationId = requestAnimationFrame(draw);
      this.analyser.getByteFrequencyData(dataArray);

      // Compute normalized audio volume amplitude (0.0 to 1.0)
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i];
      }
      const avg = sum / (bufferLength * 255);
      const amp = Math.min(1.0, avg * 1.5);
      document.documentElement.style.setProperty("--audio-amp", amp.toFixed(3));

      // Draw onto canvas
      const width = this.canvas.parentElement.clientWidth || 400;
      const height = this.canvas.parentElement.clientHeight || 48;
      this.canvasCtx.clearRect(0, 0, width, height);

      const barWidth = (width / bufferLength) * 1.8;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const val = dataArray[i] / 255;
        const barHeight = val * (height * 0.85);
        
        const grad = this.canvasCtx.createLinearGradient(0, height, 0, 0);
        if (state === AssistantState.LISTENING) {
          grad.addColorStop(0, "rgba(0, 242, 254, 0.35)");
          grad.addColorStop(1, "rgba(0, 242, 254, 0.95)");
        } else {
          grad.addColorStop(0, "rgba(79, 172, 254, 0.35)");
          grad.addColorStop(1, "rgba(127, 0, 255, 0.95)");
        }

        this.canvasCtx.fillStyle = grad;
        const y = (height - barHeight) / 2;
        this.canvasCtx.fillRect(x, y, barWidth - 1, Math.max(2, barHeight));
        x += barWidth;
      }
    };

    draw();
  }

  drawIdleWave() {
    if (this.animationId) cancelAnimationFrame(this.animationId);
    if (!this.canvasCtx || !this.canvas) return;
    
    this.resetAudioAmplitude();
    const width = this.canvas.parentElement ? this.canvas.parentElement.clientWidth : 400;
    const height = this.canvas.parentElement ? this.canvas.parentElement.clientHeight : 48;
    this.canvasCtx.clearRect(0, 0, width, height);
    
    const midY = height / 2;
    this.canvasCtx.beginPath();
    this.canvasCtx.moveTo(0, midY);
    this.canvasCtx.lineTo(width, midY);
    this.canvasCtx.strokeStyle = "rgba(255, 255, 255, 0.1)";
    this.canvasCtx.lineWidth = 1.5;
    this.canvasCtx.stroke();
  }
}

const audioSystem = new AudioSystem();
