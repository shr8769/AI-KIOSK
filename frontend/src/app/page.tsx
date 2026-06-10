'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { VidyaSahayakOrb } from '@/components/orb';
import type { OrbState } from '@/components/orb/orbStates';

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
    <main style={{
      minHeight: '100vh',
      background: '#060810',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 20px',
    }}>
      {/* ── Wordmark ── */}
      <p style={{
        fontSize: 10,
        letterSpacing: '0.22em',
        color: 'rgba(255,255,255,0.14)',
        textTransform: 'uppercase',
        fontWeight: 500,
        marginBottom: 32,
      }}>
        VidyaSahayak · PES University
      </p>

      {/* ── Orb ───────────────────────────────────────── */}
      <VidyaSahayakOrb
        state={orbState}
        onStateChange={setOrbState}
        autoDemo={false}
        showLabels={true}
        showControls={true}
        showMic={true}
        size={300}
      />

      <p style={{
        marginTop: 40,
        fontSize: 9,
        letterSpacing: '0.12em',
        color: 'rgba(255,255,255,0.08)',
        textTransform: 'uppercase',
      }}>
        Fluid Intelligence · Academic AI · GPU Accelerated
      </p>
    </main>
  );
}
