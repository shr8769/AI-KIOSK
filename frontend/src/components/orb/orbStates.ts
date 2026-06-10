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
    id: 'idle', label: 'Idle', desc: 'Waiting for you',
    energy: .10, speed: .08, convergence: 0,   expansion: .05, turb: .04, membrane: .03,
    hueA: 220, hueB: 230, hueC: 240, sat: .20, lum: .15,
    aura: 'breathe', mode: 'circulate',
  },
  {
    id: 'detected', label: 'User Detected', desc: 'I see you approaching',
    energy: .25, speed: .12, convergence: 0,   expansion: .15, turb: .08, membrane: .08,
    hueA: 210, hueB: 220, hueC: 230, sat: .30, lum: .25,
    aura: 'expand', mode: 'circulate',
  },
  {
    id: 'greeting', label: 'Greeting', desc: 'Welcome to VidyaSahayak',
    energy: .40, speed: .18, convergence: 0,   expansion: .25, turb: .12, membrane: .15,
    hueA: 190, hueB: 210, hueC: 220, sat: .40, lum: .35,
    aura: 'warmPulse', mode: 'expand',
  },
  {
    id: 'listening', label: 'Listening', desc: "Go ahead, I'm listening",
    energy: .45, speed: .20, convergence: .15, expansion: .10, turb: .30, membrane: .35,
    hueA: 180, hueB: 200, hueC: 210, sat: .50, lum: .45,
    aura: 'ripple', mode: 'receive',
  },
  {
    id: 'thinking', label: 'Thinking', desc: 'Processing your query',
    energy: .35, speed: .15, convergence: .60, expansion: 0,   turb: .20, membrane: .10,
    hueA: 250, hueB: 270, hueC: 290, sat: .45, lum: .40,
    aura: 'contract', mode: 'converge',
  },
  {
    id: 'retrieving', label: 'Retrieving', desc: 'Searching knowledge base',
    energy: .50, speed: .35, convergence: .70, expansion: 0,   turb: .25, membrane: .15,
    hueA: 230, hueB: 250, hueC: 270, sat: .55, lum: .45,
    aura: 'stream', mode: 'inward',
  },
  {
    id: 'clarifying', label: 'Clarifying', desc: 'Could you clarify that?',
    energy: .30, speed: .15, convergence: .25, expansion: .25, turb: .15, membrane: .15,
    hueA: 35, hueB: 45, hueC: 55, sat: .45, lum: .40,
    aura: 'split', mode: 'oscillate',
  },
  {
    id: 'speaking', label: 'Speaking', desc: 'Here is what I found',
    energy: .60, speed: .30, convergence: 0,   expansion: .40, turb: .20, membrane: .25,
    hueA: 210, hueB: 220, hueC: 230, sat: .15, lum: .65, // Pulsing white/slate
    aura: 'radiate', mode: 'expand',
  },
  {
    id: 'error', label: 'Recovering', desc: 'Give me a moment',
    energy: .15, speed: .10, convergence: .20, expansion: 0,   turb: .05, membrane: .05,
    hueA: 0, hueB: 10, hueC: 20, sat: .35, lum: .25,
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
