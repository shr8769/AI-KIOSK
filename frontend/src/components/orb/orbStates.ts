export type OrbState =
  | 'idle' | 'detected' | 'greeting' | 'listening'
  | 'thinking' | 'retrieving' | 'clarifying' | 'speaking' | 'error';

export type AuraMode =
  | 'breathe' | 'expand' | 'warmPulse' | 'ripple'
  | 'contract' | 'stream' | 'split' | 'radiate' | 'stabilize';

export type FluidMode =
  | 'circulate' | 'converge' | 'expand' | 'receive' | 'inward' | 'oscillate';

export interface OrbStateConfig {
  id: OrbState;
  label: string;
  desc: string;
  /** Overall brightness/intensity 0–1 */
  energy: number;
  /** Fluid animation speed multiplier */
  speed: number;
  /** How strongly currents pull toward center 0–1 */
  convergence: number;
  /** How strongly energy expands outward 0–1 */
  expansion: number;
  /** Turbulence amount 0–1 */
  turb: number;
  /** Membrane deformation amount 0–1 */
  membrane: number;
  /** Primary hue (degrees) */
  hueA: number;
  /** Secondary hue */
  hueB: number;
  /** Accent hue */
  hueC: number;
  /** Saturation 0–1 */
  sat: number;
  /** Base luminance 0–1 */
  lum: number;
  /** Aura animation mode */
  aura: AuraMode;
  /** Internal fluid current mode */
  mode: FluidMode;
}

export const ORB_STATES: OrbStateConfig[] = [
  {
    // Deep Indigo / Midnight Slate breathing
    id: 'idle', label: 'Idle', desc: 'Waiting for you',
    energy: .05, speed: .02, convergence: 0.0, expansion: 0.02, turb: .01, membrane: .01,
    hueA: 240, hueB: 230, hueC: 220, sat: .20, lum: .10,
    aura: 'breathe', mode: 'circulate',
  },
  {
    // Soft Cyan expansion
    id: 'detected', label: 'User Detected', desc: 'I see you approaching',
    energy: .15, speed: .04, convergence: 0.0, expansion: 0.10, turb: .03, membrane: .02,
    hueA: 190, hueB: 200, hueC: 210, sat: .40, lum: .18,
    aura: 'expand', mode: 'circulate',
  },
  {
    // Gentle Cyan/Violet welcoming ripple
    id: 'greeting', label: 'Greeting', desc: 'Welcome to VidyaSahayak',
    energy: .20, speed: .06, convergence: 0.0, expansion: 0.15, turb: .05, membrane: .04,
    hueA: 200, hueB: 230, hueC: 250, sat: .50, lum: .25,
    aura: 'warmPulse', mode: 'expand',
  },
  {
    // Soft glowing Cyan with audio-reactive membrane
    id: 'listening', label: 'Listening', desc: "Go ahead, I'm listening",
    energy: .25, speed: .08, convergence: .15, expansion: .10, turb: .08, membrane: .15,
    hueA: 185, hueB: 195, hueC: 205, sat: .60, lum: .30,
    aura: 'ripple', mode: 'receive',
  },
  {
    // Deep Violet/Indigo slow orbiting
    id: 'thinking', label: 'Thinking', desc: 'Processing your query',
    energy: .15, speed: .08, convergence: .40, expansion: 0.0, turb: .10, membrane: .02,
    hueA: 255, hueB: 265, hueC: 275, sat: .40, lum: .20,
    aura: 'contract', mode: 'converge',
  },
  {
    // Elegant scanning ring (Cyan to Violet)
    id: 'retrieving', label: 'Retrieving', desc: 'Searching knowledge base',
    energy: .25, speed: .12, convergence: .50, expansion: 0.0, turb: .12, membrane: .05,
    hueA: 190, hueB: 220, hueC: 260, sat: .50, lum: .25,
    aura: 'stream', mode: 'inward',
  },
  {
    // Dual phase glow (Cyan/Indigo)
    id: 'clarifying', label: 'Clarifying', desc: 'Could you clarify that?',
    energy: .18, speed: .06, convergence: .15, expansion: .15, turb: .05, membrane: .05,
    hueA: 200, hueB: 230, hueC: 260, sat: .40, lum: .22,
    aura: 'split', mode: 'oscillate',
  },
  {
    // Ice White / Slate pulsing waveform synchronized breathing
    id: 'speaking', label: 'Speaking', desc: 'Here is what I found',
    energy: .40, speed: .10, convergence: 0.0, expansion: .25, turb: .15, membrane: .20,
    hueA: 220, hueB: 230, hueC: 240, sat: .10, lum: .50,
    aura: 'radiate', mode: 'expand',
  },
  {
    // Calm amber/red warning state
    id: 'error', label: 'Recovering', desc: 'Give me a moment',
    energy: .08, speed: .03, convergence: .10, expansion: 0.0, turb: .02, membrane: .02,
    hueA: 10, hueB: 20, hueC: 30, sat: .30, lum: .15,
    aura: 'stabilize', mode: 'circulate',
  },
];

/** Demo auto-play sequence */
export const STATE_SEQUENCE: { id: OrbState; duration: number }[] = [
  { id: 'idle',       duration: 2400 },
  { id: 'detected',   duration: 1800 },
  { id: 'greeting',   duration: 2200 },
  { id: 'listening',  duration: 2800 },
  { id: 'thinking',   duration: 3000 },
  { id: 'retrieving', duration: 2800 },
  { id: 'clarifying', duration: 2400 },
  { id: 'speaking',   duration: 3000 },
  { id: 'error',      duration: 2200 },
];
