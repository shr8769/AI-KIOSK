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
    energy: .16, speed: .18, convergence: 0,   expansion: .10, turb: .08, membrane: .08,
    hueA: 215, hueB: 235, hueC: 250, sat: .50, lum: .22,
    aura: 'breathe', mode: 'circulate',
  },
  {
    id: 'detected', label: 'User Detected', desc: 'I see you approaching',
    energy: .42, speed: .32, convergence: 0,   expansion: .35, turb: .14, membrane: .20,
    hueA: 218, hueB: 242, hueC: 258, sat: .60, lum: .34,
    aura: 'expand', mode: 'circulate',
  },
  {
    id: 'greeting', label: 'Greeting', desc: 'Welcome to VidyaSahayak',
    energy: .68, speed: .48, convergence: 0,   expansion: .72, turb: .20, membrane: .38,
    hueA: 220, hueB: 248, hueC: 265, sat: .68, lum: .44,
    aura: 'warmPulse', mode: 'expand',
  },
  {
    id: 'listening', label: 'Listening', desc: "Go ahead, I'm listening",
    energy: .58, speed: .38, convergence: .25, expansion: .20, turb: .55, membrane: .72,
    hueA: 205, hueB: 235, hueC: 258, sat: .65, lum: .40,
    aura: 'ripple', mode: 'receive',
  },
  {
    id: 'thinking', label: 'Thinking', desc: 'Processing your query',
    energy: .52, speed: .28, convergence: .85, expansion: 0,   turb: .35, membrane: .18,
    hueA: 228, hueB: 255, hueC: 275, sat: .58, lum: .38,
    aura: 'contract', mode: 'converge',
  },
  {
    id: 'retrieving', label: 'Retrieving', desc: 'Searching knowledge base',
    energy: .78, speed: .72, convergence: .92, expansion: 0,   turb: .45, membrane: .32,
    hueA: 200, hueB: 238, hueC: 262, sat: .72, lum: .50,
    aura: 'stream', mode: 'inward',
  },
  {
    id: 'clarifying', label: 'Clarifying', desc: 'Could you clarify that?',
    energy: .44, speed: .30, convergence: .45, expansion: .45, turb: .28, membrane: .28,
    hueA: 232, hueB: 262, hueC: 278, sat: .55, lum: .38,
    aura: 'split', mode: 'oscillate',
  },
  {
    id: 'speaking', label: 'Speaking', desc: 'Here is what I found',
    energy: .88, speed: .68, convergence: 0,   expansion: .95, turb: .38, membrane: .55,
    hueA: 210, hueB: 245, hueC: 268, sat: .78, lum: .56,
    aura: 'radiate', mode: 'expand',
  },
  {
    id: 'error', label: 'Recovering', desc: 'Give me a moment',
    energy: .22, speed: .18, convergence: .35, expansion: 0,   turb: .10, membrane: .12,
    hueA: 238, hueB: 252, hueC: 265, sat: .35, lum: .24,
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
