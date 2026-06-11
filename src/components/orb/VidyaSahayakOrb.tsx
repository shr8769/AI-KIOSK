'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { OrbState, OrbStateConfig, ORB_STATES, STATE_SEQUENCE } from './orbStates';
import { initWebGL, updateUniforms, WebGLContext } from './orbWebGL';
import { drawGlassShell, drawAura } from './orbCanvas2D';
import { startMicAnalysis, stopMicAnalysis, MicHandle } from './orbAudio';

interface VidyaSahayakOrbProps {
  /** Controlled state from parent (optional) */
  state?: OrbState;
  /** Called when orb wants to change state internally */
  onStateChange?: (state: OrbState) => void;
  /** Show demo auto-sequence on mount */
  autoDemo?: boolean;
  /** Show state label + description below orb */
  showLabels?: boolean;
  /** Show state control buttons */
  showControls?: boolean;
  /** Show microphone button */
  showMic?: boolean;
  /** Orb diameter in px */
  size?: number;
}

/** Linearly interpolate between a and b by k */
function lerp(a: number, b: number, k: number) {
  return a + (b - a) * k;
}

/** Ease-in-out cubic */
function eio(t: number) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

const LERP_FIELDS: (keyof OrbStateConfig)[] = [
  'energy', 'speed', 'convergence', 'expansion',
  'turb', 'membrane', 'hueA', 'hueB', 'hueC', 'sat', 'lum',
];

const TRANS_DUR = 1600; // ms

export const VidyaSahayakOrb: React.FC<VidyaSahayakOrbProps> = ({
  state: controlledState,
  onStateChange,
  autoDemo = true,
  showLabels = true,
  showControls = true,
  showMic = true,
  size = 300,
}) => {
  const glCanvasRef  = useRef<HTMLCanvasElement>(null);
  const glassCanvasRef = useRef<HTMLCanvasElement>(null);
  const auraCanvasRef  = useRef<HTMLCanvasElement>(null);

  const webglCtxRef  = useRef<WebGLContext | null>(null);
  const micHandleRef = useRef<MicHandle | null>(null);
  const rafRef       = useRef<number>(0);

  const prevStateRef  = useRef<OrbStateConfig>({ ...ORB_STATES[0] });
  const curRef        = useRef<OrbStateConfig>({ ...ORB_STATES[0] });
  const targetRef     = useRef<OrbStateConfig>(ORB_STATES[0]);
  const transStartRef = useRef<number>(0);
  const timeRef       = useRef<number>(0);
  const lastTSRef     = useRef<number>(0);
  const voiceAmpRef   = useRef<number>(0);
  const demoTimerRef  = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [activeId, setActiveId]   = useState<OrbState>('idle');
  const [label, setLabel]         = useState('Idle');
  const [desc, setDesc]           = useState('Waiting for you');
  const [micOn, setMicOn]         = useState(false);
  const [micAvail, setMicAvail]   = useState(true);

  /* ─── set state ─── */
  const applyState = useCallback((id: OrbState) => {
    const cfg = ORB_STATES.find(s => s.id === id) ?? ORB_STATES[0];
    prevStateRef.current = { ...curRef.current };
    targetRef.current    = cfg;
    transStartRef.current = performance.now();
    setActiveId(id);
    setLabel(cfg.label);
    setDesc(cfg.desc);
    onStateChange?.(id);
  }, [onStateChange]);

  /* ─── demo sequence ─── */
  const runDemo = useCallback(() => {
    let si = 0;
    function next() {
      if (si >= STATE_SEQUENCE.length) { si = 0; return; }
      const { id, duration } = STATE_SEQUENCE[si++];
      applyState(id);
      if (duration > 0) demoTimerRef.current = setTimeout(next, duration);
    }
    demoTimerRef.current = setTimeout(next, 500);
  }, [applyState]);

  const stopDemo = useCallback(() => {
    if (demoTimerRef.current) clearTimeout(demoTimerRef.current);
  }, []);

  /* ─── mic ─── */
  const toggleMic = useCallback(async () => {
    stopDemo();
    if (micOn) {
      stopMicAnalysis(micHandleRef.current);
      micHandleRef.current = null;
      setMicOn(false);
      applyState('idle');
    } else {
      const handle = await startMicAnalysis();
      if (!handle) { setMicAvail(false); return; }
      micHandleRef.current = handle;
      setMicOn(true);
      applyState('listening');
    }
  }, [micOn, applyState, stopDemo]);

  /* ─── render loop ─── */
  useEffect(() => {
    const glCanvas    = glCanvasRef.current!;
    const glassCanvas = glassCanvasRef.current!;
    const auraCanvas  = auraCanvasRef.current!;

    const glCtx = initWebGL(glCanvas);
    if (!glCtx) { console.error('WebGL not supported'); return; }
    webglCtxRef.current = glCtx;

    function frame(ts: number) {
      const dt = Math.min(ts - lastTSRef.current, 50);
      lastTSRef.current = ts;
      timeRef.current += dt * 0.001;

      /* transition */
      const tk = eio(Math.min(1, (performance.now() - transStartRef.current) / TRANS_DUR));
      const prev = prevStateRef.current;
      const tgt  = targetRef.current;
      const next: any = {};
      LERP_FIELDS.forEach(f => {
        next[f] = lerp(prev[f] as number, tgt[f] as number, tk);
      });
      next.aura = tk > 0.5 ? tgt.aura : prev.aura;
      next.mode = tk > 0.5 ? tgt.mode : prev.mode;
      curRef.current = next as OrbStateConfig;

      /* voice */
      const handle = micHandleRef.current;
      if (handle?.analyser && handle?.freqData) {
        handle.analyser.getByteFrequencyData(handle.freqData);
        let sum = 0;
        const n = Math.min(80, handle.freqData.length);
        for (let i = 0; i < n; i++) sum += handle.freqData[i];
        voiceAmpRef.current = lerp(voiceAmpRef.current, (sum / n) / 255, 0.2);
      } else {
        voiceAmpRef.current = lerp(voiceAmpRef.current, 0, 0.07);
      }

      const v = voiceAmpRef.current;
      const c = curRef.current;
      const eff = {
        ...c,
        energy:   Math.min(1, c.energy   + v * 0.3),
        membrane: Math.min(1, c.membrane + v * 0.5),
        turb:     Math.min(1, c.turb     + v * 0.25),
        sat:      Math.min(0.95, c.sat   + v * 0.08),
        lum:      Math.min(0.88, c.lum   + v * 0.07),
      };

      /* WebGL core */
      updateUniforms(glCtx, timeRef.current, eff, v);

      /* 2D overlays */
      const gCtx2d = glassCanvas.getContext('2d')!;
      const aCtx2d = auraCanvas.getContext('2d')!;
      drawGlassShell(gCtx2d, eff, timeRef.current, v);
      drawAura(aCtx2d, eff, timeRef.current, v);

      rafRef.current = requestAnimationFrame(frame);
    }

    if (autoDemo) runDemo();
    rafRef.current = requestAnimationFrame(frame);

    return () => {
      cancelAnimationFrame(rafRef.current);
      stopDemo();
      stopMicAnalysis(micHandleRef.current);
    };
  }, []);

  /* sync controlled state */
  useEffect(() => {
    if (controlledState) {
      stopDemo();
      applyState(controlledState);
    }
  }, [controlledState]);

  const canvasSize = size * 2; // HiDPI
  const auraSize   = Math.round(size * 1.34);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {/* ── Orb stage ── */}
      <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
        {/* Layer 5: Aura */}
        <canvas
          ref={auraCanvasRef}
          width={auraSize * 2}
          height={auraSize * 2}
          style={{
            position: 'absolute',
            width: auraSize,
            height: auraSize,
            top: -(auraSize - size) / 2,
            left: -(auraSize - size) / 2,
            pointerEvents: 'none',
            borderRadius: 0,
          }}
        />
        {/* Layer 1–3: WebGL fluid core */}
        <canvas
          ref={glCanvasRef}
          width={canvasSize}
          height={canvasSize}
          style={{ position: 'absolute', top: 0, left: 0, width: size, height: size, borderRadius: '50%' }}
        />
        {/* Layer 4: Glass shell + membrane */}
        <canvas
          ref={glassCanvasRef}
          width={canvasSize}
          height={canvasSize}
          style={{ position: 'absolute', top: 0, left: 0, width: size, height: size, borderRadius: '50%', pointerEvents: 'none' }}
        />
      </div>

      {/* ── Labels ── */}
      {showLabels && (
        <>
          <p style={{ fontSize: 10, letterSpacing: '0.18em', color: 'rgba(255,255,255,0.22)', textTransform: 'uppercase', fontWeight: 500, marginTop: 22, transition: 'all 0.6s ease' }}>
            {label}
          </p>
          <p style={{ fontSize: 12.5, color: 'rgba(255,255,255,0.38)', marginTop: 8, textAlign: 'center', fontWeight: 400, letterSpacing: '0.015em', transition: 'all 0.6s ease' }}>
            {desc}
          </p>
        </>
      )}

      {/* ── Mic button ── */}
      {showMic && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 18 }}>
          <button
            onClick={toggleMic}
            title={micOn ? 'Stop listening' : 'Start listening'}
            style={{
              width: 44, height: 44, borderRadius: '50%',
              border: `0.5px solid ${micOn ? 'rgba(100,160,255,0.4)' : 'rgba(255,255,255,0.14)'}`,
              background: micOn ? 'rgba(80,140,255,0.2)' : 'rgba(255,255,255,0.05)',
              color: micOn ? 'rgba(160,200,255,0.9)' : 'rgba(255,255,255,0.5)',
              cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 0.25s', outline: 'none',
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="2" width="6" height="11" rx="3"/>
              <path d="M5 10a7 7 0 0014 0"/>
              <line x1="12" y1="21" x2="12" y2="17"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
            </svg>
          </button>
          <span style={{ fontSize: 10, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.2)', textTransform: 'uppercase' }}>
            {!micAvail ? 'Mic unavailable' : micOn ? 'Listening…' : 'Tap to listen'}
          </span>
        </div>
      )}

      {/* ── State controls ── */}
      {showControls && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, justifyContent: 'center', marginTop: 18, maxWidth: 520 }}>
          {ORB_STATES.map(s => (
            <button
              key={s.id}
              onClick={() => { stopDemo(); if (micOn) { stopMicAnalysis(micHandleRef.current); micHandleRef.current = null; setMicOn(false); } applyState(s.id as OrbState); }}
              style={{
                fontSize: 10, fontWeight: 500, letterSpacing: '0.07em',
                padding: '6px 13px', borderRadius: 100,
                border: `0.5px solid ${activeId === s.id ? 'rgba(90,145,255,0.3)' : 'rgba(255,255,255,0.09)'}`,
                background: activeId === s.id ? 'rgba(70,120,255,0.14)' : 'rgba(255,255,255,0.035)',
                color: activeId === s.id ? 'rgba(160,195,255,0.88)' : 'rgba(255,255,255,0.32)',
                cursor: 'pointer', textTransform: 'uppercase', transition: 'all 0.2s', outline: 'none',
              }}
            >
              {s.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default VidyaSahayakOrb;
