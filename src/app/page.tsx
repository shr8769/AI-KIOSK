'use client';

/**
 * Example integration page for VidyaSahayak Orb
 * Drop this into your Next.js / Vite app.
 *
 * Minimal usage:
 *   import { VidyaSahayakOrb } from '@/components/orb';
 *   <VidyaSahayakOrb />
 *
 * Controlled usage (your backend drives the state):
 *   <VidyaSahayakOrb state={currentState} onStateChange={setCurrentState} autoDemo={false} />
 */

import React, { useState } from 'react';
import { VidyaSahayakOrb } from '@/components/orb';
import type { OrbState } from '@/components/orb';

export default function KioskPage() {
  // Optional: control state from your own logic
  const [orbState, setOrbState] = useState<OrbState>('idle');

  // Example: connect to your LLM pipeline
  async function handleUserQuery(transcript: string) {
    setOrbState('thinking');
    // ... call your LLM / RAG backend
    // setOrbState('retrieving');  ← while fetching docs
    // setOrbState('speaking');    ← while TTS plays
    // setOrbState('idle');        ← when done
  }

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

      {/* ── Orb ─────────────────────────────────────────
          Props reference:
          state        – controlled OrbState (optional)
          onStateChange – callback when orb transitions
          autoDemo     – run demo sequence on mount (default true)
          showLabels   – show state name + description (default true)
          showControls – show manual state buttons (default true)
          showMic      – show microphone toggle (default true)
          size         – orb diameter in px (default 300)
      ─────────────────────────────────────────────── */}
      <VidyaSahayakOrb
        state={orbState}
        onStateChange={setOrbState}
        autoDemo={false}       // set true for kiosk attract-loop
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
