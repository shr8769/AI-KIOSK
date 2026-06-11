import { OrbStateConfig } from './orbStates';

function hsl(h: number, s: number, l: number, a = 1): string {
  return `hsla(${h},${(s * 100).toFixed(1)}%,${(l * 100).toFixed(1)}%,${a})`;
}

function noise1(x: number): number {
  const i = Math.floor(x);
  const f = x - i;
  const u = f * f * (3 - 2 * f);
  const a = (Math.sin(i * 127.1) * 43758.5453) % 1;
  const b = (Math.sin((i + 1) * 127.1) * 43758.5453) % 1;
  return (a + (b - a) * u) * 2 - 1;
}

function lerp(a: number, b: number, k: number) { return a + (b - a) * k; }

/* ─────────────────────────────────────────────
   Glass Shell + Membrane
───────────────────────────────────────────── */
export function drawGlassShell(
  ctx: CanvasRenderingContext2D,
  e: OrbStateConfig,
  t: number,
  voiceAmp: number,
) {
  const { width: W, height: H } = ctx.canvas;
  const cx = W / 2, cy = H / 2;
  const R  = W * 0.42;

  ctx.clearRect(0, 0, W, H);

  /* clip to orb */
  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI * 2);
  ctx.clip();

  /* ── Rim conic gradient (light wrapping around glass) ── */
  const rimGrad = (ctx as any).createConicGradient(t * e.speed * 0.12, cx, cy);
  const ra = e.energy * 0.12 + 0.04;
  rimGrad.addColorStop(0.00, hsl(e.hueA, e.sat * 0.8, e.lum + 0.15, ra * 1.3));
  rimGrad.addColorStop(0.30, hsl(e.hueB, e.sat * 0.7, e.lum + 0.06, ra * 0.3));
  rimGrad.addColorStop(0.60, hsl(e.hueC, e.sat * 0.75, e.lum + 0.10, ra * 0.7));
  rimGrad.addColorStop(1.00, hsl(e.hueA, e.sat * 0.8, e.lum + 0.15, ra * 1.3));
  ctx.globalCompositeOperation = 'screen';
  ctx.fillStyle = rimGrad;
  ctx.fillRect(0, 0, W, H);

  /* ── Primary specular highlight ── */
  const specGrad = ctx.createRadialGradient(
    cx - R * 0.30, cy - R * 0.35, 0,
    cx - R * 0.10, cy - R * 0.08, R * 0.52,
  );
  specGrad.addColorStop(0.00, `rgba(255,255,255,${0.44 + e.energy * 0.10})`);
  specGrad.addColorStop(0.10, `rgba(255,255,255,${0.18 + e.energy * 0.06})`);
  specGrad.addColorStop(0.28, 'rgba(255,255,255,0.04)');
  specGrad.addColorStop(0.50, 'rgba(255,255,255,0)');
  ctx.fillStyle = specGrad;
  ctx.fillRect(0, 0, W, H);

  /* ── Edge depth darkening ── */
  ctx.globalCompositeOperation = 'source-over';
  const edgeGrad = ctx.createRadialGradient(cx, cy, R * 0.68, cx, cy, R);
  edgeGrad.addColorStop(0.00, 'rgba(0,0,0,0)');
  edgeGrad.addColorStop(0.70, 'rgba(0,4,18,0.16)');
  edgeGrad.addColorStop(1.00, 'rgba(0,4,20,0.70)');
  ctx.fillStyle = edgeGrad;
  ctx.fillRect(0, 0, W, H);

  ctx.restore();

  /* ── Liquid membrane boundary ── */
  const pts    = 64;
  const ts     = t * e.speed;
  const mAmp   = voiceAmp * e.membrane * 22 + e.membrane * 3.5;

  ctx.beginPath();
  for (let i = 0; i <= pts; i++) {
    const a = (i / pts) * Math.PI * 2;
    const w = (
      noise1(a * 3.0 + ts * 2.0) * mAmp +
      noise1(a * 2.1 - ts * 1.6) * mAmp * 0.45 +
      voiceAmp * Math.sin(a * 4 - ts * 5) * 14
    );
    const rx = cx + (R + w) * Math.cos(a);
    const ry = cy + (R + w) * Math.sin(a);
    i === 0 ? ctx.moveTo(rx, ry) : ctx.lineTo(rx, ry);
  }
  ctx.closePath();
  ctx.strokeStyle = hsl(
    e.hueA, e.sat * 0.7, e.lum + 0.28,
    Math.min(0.6, 0.12 + e.membrane * 0.38 + voiceAmp * 0.30),
  );
  ctx.lineWidth = 1.4;
  ctx.stroke();
}

/* ─────────────────────────────────────────────
   Aura Field
───────────────────────────────────────────── */
export function drawAura(
  ctx: CanvasRenderingContext2D,
  e: OrbStateConfig,
  t: number,
  voiceAmp: number,
) {
  const { width: AW, height: AH } = ctx.canvas;
  const cx = AW / 2, cy = AH / 2;
  ctx.clearRect(0, 0, AW, AH);

  const ts   = t * e.speed;
  const bE   = e.energy + voiceAmp * e.energy * 0.45;

  /** Soft radial glow helper */
  function sc(
    x: number, y: number, r0: number, r1: number,
    h: number, s: number, l: number, a: number,
  ) {
    const g = ctx.createRadialGradient(x, y, r0, x, y, r1);
    g.addColorStop(0, hsl(h, s, l, a));
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, AW, AH);
  }

  switch (e.aura) {
    case 'breathe': {
      const b = 0.5 + Math.sin(ts * 0.6) * 0.5;
      sc(cx, cy, 100, 195, e.hueA, e.sat * 0.7, e.lum + 0.08, bE * 0.18 + b * 0.04);
      break;
    }
    case 'expand': {
      const b = 0.5 + Math.sin(ts * 0.9) * 0.5;
      sc(cx, cy, 100, 175 + b * 28, e.hueB, e.sat * 0.8, e.lum + 0.10, bE * 0.30);
      sc(cx, cy, 128, 185 + b * 18, e.hueA, e.sat * 0.6, e.lum + 0.06, bE * 0.14 * (1 + b * 0.25));
      break;
    }
    case 'warmPulse': {
      const p  = 0.5 + Math.sin(ts * 1.2) * 0.5;
      const p2 = 0.5 + Math.sin(ts * 1.2 + Math.PI * 0.5) * 0.5;
      sc(cx, cy, 88, 182 + p * 26,  e.hueB, e.sat * 0.85, e.lum + 0.12, bE * 0.38 * (1 + p * 0.2));
      sc(cx, cy, 100, 158 + p2 * 18, e.hueA, e.sat * 0.70, e.lum + 0.08, bE * 0.20 * p2);
      break;
    }
    case 'ripple': {
      [0, 0.33, 0.66].forEach(ph => {
        const rp = ((ts * 0.8 + ph) % 1);
        sc(cx, cy, 128 + rp * 75, 148 + rp * 78, e.hueA, e.sat * 0.8, e.lum + 0.10,
          Math.pow(1 - rp, 2) * bE * 0.32 + voiceAmp * 0.14);
      });
      sc(cx, cy, 90, 150, e.hueA, e.sat * 0.7, e.lum + 0.08, bE * 0.18);
      break;
    }
    case 'contract': {
      const c = 0.5 + Math.sin(ts * 0.5) * 0.5;
      sc(cx, cy, 80,  148 - c * 18, e.hueC, e.sat * 0.65, e.lum + 0.10, bE * 0.28);
      sc(cx, cy, 88, 118,           e.hueB, e.sat * 0.70, e.lum + 0.12, bE * 0.22 * (1 + c * 0.15));
      break;
    }
    case 'stream': {
      sc(cx, cy, 78, 140, e.hueA, e.sat * 0.8, e.lum + 0.12, bE * 0.30);
      for (let a = 0; a < Math.PI * 2; a += Math.PI / 3) {
        const rx = cx + Math.cos(a + ts * 0.4) * 38;
        const ry = cy + Math.sin(a + ts * 0.4) * 38;
        const g = ctx.createRadialGradient(rx, ry, 0, cx, cy, 155);
        g.addColorStop(0, hsl(e.hueB, e.sat * 0.9, e.lum + 0.15, bE * 0.12));
        g.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g; ctx.fillRect(0, 0, AW, AH);
      }
      break;
    }
    case 'split': {
      const s = Math.sin(ts * 0.7) * 22;
      sc(cx - s, cy, 88, 152, e.hueA, e.sat * 0.70, e.lum + 0.10, bE * 0.22);
      sc(cx + s, cy, 88, 152, e.hueC, e.sat * 0.65, e.lum + 0.08, bE * 0.20);
      break;
    }
    case 'radiate': {
      const p  = 0.5 + Math.sin(ts * 1.8) * 0.5;
      const p2 = 0.5 + Math.sin(ts * 1.8 + Math.PI * 0.4) * 0.5;
      sc(cx, cy, 98,  188 + p * 30,  e.hueA, e.sat * 0.85, e.lum + 0.12, bE * 0.42 * (1 + p * 0.18) + voiceAmp * 0.18);
      sc(cx, cy, 112, 172 + p2 * 22, e.hueB, e.sat * 0.75, e.lum + 0.10, bE * 0.28 * p2);
      for (let a = 0; a < Math.PI * 2; a += Math.PI * 0.4) {
        const rx = cx + Math.cos(a + ts * 0.3) * 52;
        const ry = cy + Math.sin(a + ts * 0.3) * 52;
        const g = ctx.createRadialGradient(rx, ry, 0, rx, ry, 68 + p * 22);
        g.addColorStop(0, hsl(e.hueC, e.sat * 0.9, e.lum + 0.15, bE * 0.10 + voiceAmp * 0.07));
        g.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = g; ctx.fillRect(0, 0, AW, AH);
      }
      break;
    }
    case 'stabilize': {
      const s = 0.5 + Math.sin(ts * 0.35) * 0.5;
      sc(cx, cy, 93, 148, e.hueA, e.sat * 0.5, e.lum + 0.08, bE * 0.18 + s * 0.03);
      break;
    }
  }

  /* Vignette — fade aura at outer edge so it blends into background */
  const fade = ctx.createRadialGradient(cx, cy, 0, cx, cy, AW * 0.5);
  fade.addColorStop(0.70, 'rgba(0,0,0,0)');
  fade.addColorStop(1.00, 'rgba(6,8,16,0.97)');
  ctx.fillStyle = fade;
  ctx.fillRect(0, 0, AW, AH);
}
