export interface MicHandle {
  analyser: AnalyserNode;
  freqData: Uint8Array;
  stream: MediaStream;
  audioCtx: AudioContext;
}

/**
 * Request microphone access and set up Web Audio analysis.
 * Returns null if permission denied or API unavailable.
 */
export async function startMicAnalysis(): Promise<MicHandle | null> {
  try {
    const AudioContextClass =
      window.AudioContext ?? (window as any).webkitAudioContext;
    if (!AudioContextClass) return null;

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: false,
    });

    const audioCtx = new AudioContextClass() as AudioContext;
    const source   = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();

    // 256 bins → good frequency resolution without heavy CPU cost
    analyser.fftSize = 256;
    // 0.72 smoothing: fast enough to feel reactive, slow enough to look fluid
    analyser.smoothingTimeConstant = 0.72;

    source.connect(analyser);

    const freqData = new Uint8Array(analyser.frequencyBinCount);

    return { analyser, freqData, stream, audioCtx };
  } catch {
    return null;
  }
}

/**
 * Stop microphone analysis and release all resources.
 */
export function stopMicAnalysis(handle: MicHandle | null | undefined) {
  if (!handle) return;
  handle.stream.getTracks().forEach(t => t.stop());
  handle.audioCtx.close().catch(() => {});
}

/**
 * Read the current RMS voice amplitude (0–1) from an active handle.
 * Call this every frame inside your render loop.
 */
export function readVoiceAmplitude(handle: MicHandle): number {
  handle.analyser.getByteFrequencyData(handle.freqData as any);
  let sum = 0;
  const n = Math.min(80, handle.freqData.length);
  for (let i = 0; i < n; i++) sum += handle.freqData[i];
  return (sum / n) / 255;
}
