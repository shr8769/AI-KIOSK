'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { VidyaSahayakOrb } from '@/components/orb';
import type { OrbState } from '@/components/orb/orbStates';
import { TextParticle } from '@/components/ui/text-particle';
import { Typewriter } from '@/components/ui/typewriter-text';

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/session';

export default function KioskPage() {
  const [orbState, setOrbState] = useState<OrbState>('idle');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  
  // Hardcoded session ID for demo purposes until orchestration is complete
  const sessionId = 'demo_session_id';

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = `${WS_BASE_URL}/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`[WS] Connected to ${wsUrl}`);
      reconnectAttempts.current = 0;
      setOrbState('idle'); // Recovered connection
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        console.log('[WS] Message received:', msg);

        // State Mapping Logic
        switch (msg.type) {
          case 'session_start':
          case 'greeting':
            setOrbState('greeting');
            break;
          case 'audio_chunk':
          case 'listening':
            setOrbState('listening');
            break;
          case 'transcript':
          case 'thinking':
            setOrbState('thinking');
            break;
          case 'retrieving':
            setOrbState('retrieving');
            break;
          case 'clarifying':
            setOrbState('clarifying');
            break;
          case 'answer':
          case 'tts_chunk':
          case 'speaking':
            setOrbState('speaking');
            break;
          case 'detection':
            if (msg.payload?.person_detected) {
              setOrbState('detected');
            } else {
              setOrbState('idle');
            }
            break;
          case 'error':
            console.error('[WS] Backend Error:', msg.payload);
            setOrbState('error');
            break;
          default:
            console.warn('[WS] Unknown message type:', msg.type);
            break;
        }
      } catch (err) {
        console.error('[WS] Failed to parse message', err);
      }
    };

    ws.onclose = (event) => {
      console.warn(`[WS] Disconnected (code: ${event.code}). Attempting reconnect...`);
      setOrbState('error'); // Fallback state when connection drops
      
      // Exponential backoff reconnection (max 30s)
      const timeout = Math.min(1000 * Math.pow(1.5, reconnectAttempts.current), 30000);
      reconnectAttempts.current += 1;
      
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, timeout);
    };

    ws.onerror = (err) => {
      console.error('[WS] Connection error', err);
      ws.close(); // Force close to trigger onclose and reconnect
    };

    wsRef.current = ws;
  }, [sessionId]);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null; // Prevent reconnect loop on unmount
        wsRef.current.close();
      }
    };
  }, [connectWebSocket]);

  return (
    <main className="min-h-screen bg-[#060810] flex flex-col items-center justify-between py-16 px-4 relative overflow-hidden">
      
      {/* ── Top Magical Wordmark ── */}
      <div className="w-full h-32 flex items-center justify-center relative z-10 mb-8">
        <TextParticle
          text="VIDYASAHAYAK"
          fontSize={100}
          fontFamily="system-ui, -apple-system, sans-serif"
          particleColor="#38bdf8" // Glowing cyan/blue
          particleSize={1.5}
          particleDensity={4}
          className="w-full h-full cursor-crosshair opacity-80"
        />
      </div>

      {/* ── Orb ───────────────────────────────────────── */}
      <div className="relative z-20 flex-1 flex items-center justify-center">
        <VidyaSahayakOrb
          state={orbState}
          onStateChange={setOrbState}
          autoDemo={false}
          showLabels={true}
          showControls={true}
          showMic={true}
          size={500}
        />
      </div>

      {/* ── Dynamic Footer ── */}
      <div className="h-16 mt-16 relative z-10 flex items-center justify-center text-center">
        <Typewriter
          text={[
            "PES University",
            "Fluid Intelligence",
            "Academic AI",
            "GPU Accelerated"
          ]}
          speed={70}
          deleteSpeed={40}
          delay={2500}
          loop={true}
          className="font-sans text-sm tracking-[0.2em] text-white/40 uppercase font-medium"
          cursor="|"
        />
      </div>
    </main>
  );
}
