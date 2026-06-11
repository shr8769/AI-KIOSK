import { OrbStateConfig } from './orbStates';

/* ─────────────────────────────────────────────
   GLSL source strings
───────────────────────────────────────────── */
const VERTEX_SHADER = /* glsl */`
  attribute vec2 a_pos;
  void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }
`;

const FRAGMENT_SHADER = /* glsl */`
precision highp float;

uniform vec2  u_res;
uniform float u_time;
uniform float u_energy;
uniform float u_speed;
uniform float u_convergence;
uniform float u_expansion;
uniform float u_turb;
uniform float u_membrane;
uniform float u_hueA;
uniform float u_hueB;
uniform float u_hueC;
uniform float u_sat;
uniform float u_lum;
uniform float u_mode;
// mode: 0=circulate, 1=converge/inward, 2=expand, 3=receive, 4=oscillate
uniform float u_voice;

#define PI 3.14159265359

/* ── HSL → RGB ── */
vec3 hsl2rgb(float h, float s, float l) {
  h = mod(h, 360.0);
  float c = (1.0 - abs(2.0 * l - 1.0)) * s;
  float x = c * (1.0 - abs(mod(h / 60.0, 2.0) - 1.0));
  float m = l - c * 0.5;
  vec3 rgb;
  if      (h < 60.0)  rgb = vec3(c, x, 0.0);
  else if (h < 120.0) rgb = vec3(x, c, 0.0);
  else if (h < 180.0) rgb = vec3(0.0, c, x);
  else if (h < 240.0) rgb = vec3(0.0, x, c);
  else if (h < 300.0) rgb = vec3(x, 0.0, c);
  else                rgb = vec3(c, 0.0, x);
  return rgb + m;
}

/* ── Hash + Noise ── */
float hash(float n) { return fract(sin(n) * 43758.5453); }
float hash2(vec2 p)  { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(hash2(i),             hash2(i + vec2(1.0, 0.0)), u.x),
    mix(hash2(i + vec2(0.0, 1.0)), hash2(i + vec2(1.0, 1.0)), u.x),
    u.y
  ) * 2.0 - 1.0;
}

/* ── Fractional Brownian Motion ── */
float fbm(vec2 p, int oct) {
  float v = 0.0, a = 0.5, s = 0.0, f = 1.8;
  for (int i = 0; i < 6; i++) {
    if (i >= oct) break;
    v += noise(p * f) * a;
    s += a;
    a *= 0.52;
    f *= 2.05;
  }
  return v / s;
}

void main() {
  vec2 fc  = gl_FragCoord.xy;
  vec2 uv  = (fc - u_res * 0.5) / min(u_res.x, u_res.y);
  float dist  = length(uv);
  float R     = 0.42;

  if (dist > R + 0.012) { discard; }

  float nd    = dist / R;
  float angle = atan(uv.y, uv.x);
  float ts    = u_time * u_speed;

  float edgeFade = nd > 0.82 ? pow((1.0 - nd) / 0.18, 2.2) : 1.0;
  float depthFade = 1.0 - nd * nd * 0.55;

  vec2 st = uv * 3.2;

  /* ── Mode-driven fluid warp ── */
  if (u_mode < 1.5) {
    /* converge / inward: pull toward center */
    float pull = (1.0 - nd) * u_convergence * 0.55;
    st += uv * pull * 1.5;
  } else if (u_mode < 2.5) {
    /* expand: push outward */
    float push = nd * u_expansion * 0.28;
    st -= uv * push;
  } else if (u_mode < 3.5) {
    /* receive: voice ripple inward */
    float sr = u_voice * sin(dist * 38.0 - ts * 4.0) * 0.04;
    st += uv * sr;
  } else if (u_mode < 4.5) {
    /* oscillate: dual competing fields */
    float osc = sin(u_time * 1.4) * 0.5;
    st += vec2(osc, -osc) * u_convergence * 0.25;
  }

  /* ── Voice membrane ripple ── */
  float vRipple = u_voice * u_membrane * sin(dist * 30.0 - ts * 3.5) * sin(angle * 3.0 + ts * 2.0);
  st += vec2(vRipple * 0.022);

  /* ── Layered fluid FBM ── */
  float f1 = fbm(st + vec2(ts * 0.22, ts * 0.16), 5);
  float f2 = fbm(st + vec2(ts * 0.14 + f1 * 0.55, ts * 0.18 + f1 * 0.45), 4);
  float f3 = fbm(st + vec2(-ts * 0.10 + f2 * 0.4,  ts * 0.12 + f2 * 0.35), 3);
  float fluid = f1 * 0.48 + f2 * 0.33 + f3 * 0.19;

  /* ── Caustic highlights ── */
  float cU = fbm(uv * 2.2 + vec2(ts * 0.28 + fluid * 0.7, ts * 0.22), 3);
  float cV = fbm(uv * 2.2 + vec2(ts * 0.22, ts * 0.28 + fluid * 0.6), 3);
  float caustic = pow(max(0.0, (cU * 0.5 + cV * 0.5 + 1.0) * 0.5), 3.5) * u_energy;

  /* ── Aurora filaments ── */
  float aw  = sin(fluid * PI * 2.5 + ts * 0.6) * 0.5 + 0.5;
  float al  = sin(fluid * PI * 5.0 + ts * 0.3) * 0.5 + 0.5;
  float aurora = aw * 0.65 + al * 0.35;

  /* ── Color mapping ── */
  float tParam = clamp(fluid * 0.45 + aurora * 0.35 + nd * 0.2, 0.0, 1.0);
  float hShift = sin(angle * 2.0 + ts * 0.4) * 8.0 + sin(ts * 0.25 + fluid * 3.0) * 5.0;
  float hue = u_hueA + (u_hueB - u_hueA) * tParam + (u_hueC - u_hueA) * aurora * 0.3 + hShift;

  float sat = clamp(u_sat + aurora * 0.18 * u_energy + caustic * 0.10 + u_voice * 0.08, 0.0, 0.95);
  float lum = clamp(
    (u_lum * depthFade * (0.4 + edgeFade * 0.6) + caustic * 0.32 + aurora * 0.08 * u_energy + u_voice * 0.06) * edgeFade,
    0.0, 0.88
  );

  /* ── Sphere normal → Phong specular ── */
  vec3 N = normalize(vec3(uv * 2.5, sqrt(max(0.0, 1.0 - dot(uv * 2.5, uv * 2.5)))));
  vec3 L = normalize(vec3(-0.6, 0.7, 0.8));
  float spec  = pow(max(0.0, dot(reflect(-L, N), vec3(0.0, 0.0, 1.0))), 18.0) * 0.55;
  float spec2 = pow(max(0.0, dot(reflect(-L, N), vec3(0.0, 0.0, 1.0))), 80.0) * 0.35;

  vec3 col = hsl2rgb(hue, sat, lum);
  col += vec3(spec + spec2);
  col *= mix(1.0, 0.4, pow(nd, 3.5)); // depth rim darkening

  float alpha = smoothstep(R + 0.012, R - 0.016, dist) * edgeFade;
  gl_FragColor = vec4(col, alpha);
}
`;

/* ─────────────────────────────────────────────
   Types & helpers
───────────────────────────────────────────── */
export interface WebGLContext {
  gl: WebGLRenderingContext;
  program: WebGLProgram;
  uniforms: Record<string, WebGLUniformLocation | null>;
}

function compileShader(gl: WebGLRenderingContext, type: number, src: string): WebGLShader {
  const shader = gl.createShader(type)!;
  gl.shaderSource(shader, src);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    throw new Error(`Shader compile error: ${gl.getShaderInfoLog(shader)}`);
  }
  return shader;
}

/* ─────────────────────────────────────────────
   Public API
───────────────────────────────────────────── */
export function initWebGL(canvas: HTMLCanvasElement): WebGLContext | null {
  const gl = canvas.getContext('webgl', {
    antialias: true,
    premultipliedAlpha: false,
    alpha: true,
  });
  if (!gl) return null;

  const prog = gl.createProgram()!;
  gl.attachShader(prog, compileShader(gl, gl.VERTEX_SHADER, VERTEX_SHADER));
  gl.attachShader(prog, compileShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    throw new Error(`Program link error: ${gl.getProgramInfoLog(prog)}`);
  }
  gl.useProgram(prog);

  /* Full-screen quad */
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
    gl.STATIC_DRAW,
  );
  const aPos = gl.getAttribLocation(prog, 'a_pos');
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

  const uNames = [
    'u_res','u_time','u_energy','u_speed','u_convergence','u_expansion',
    'u_turb','u_membrane','u_hueA','u_hueB','u_hueC','u_sat','u_lum','u_mode','u_voice',
  ];
  const uniforms: Record<string, WebGLUniformLocation | null> = {};
  uNames.forEach(n => { uniforms[n] = gl.getUniformLocation(prog, n); });

  return { gl, program: prog, uniforms };
}

const modeIndex: Record<string, number> = {
  circulate: 0, converge: 1, expand: 2, receive: 3, inward: 1, oscillate: 4,
};

export function updateUniforms(
  ctx: WebGLContext,
  time: number,
  state: OrbStateConfig,
  voice: number,
) {
  const { gl, uniforms } = ctx;
  const { width, height } = (gl.canvas as HTMLCanvasElement);

  gl.viewport(0, 0, width, height);
  gl.clearColor(0, 0, 0, 0);
  gl.clear(gl.COLOR_BUFFER_BIT);

  gl.uniform2f(uniforms['u_res'],         width, height);
  gl.uniform1f(uniforms['u_time'],        time);
  gl.uniform1f(uniforms['u_energy'],      state.energy);
  gl.uniform1f(uniforms['u_speed'],       state.speed);
  gl.uniform1f(uniforms['u_convergence'], state.convergence);
  gl.uniform1f(uniforms['u_expansion'],   state.expansion);
  gl.uniform1f(uniforms['u_turb'],        state.turb);
  gl.uniform1f(uniforms['u_membrane'],    state.membrane);
  gl.uniform1f(uniforms['u_hueA'],        state.hueA);
  gl.uniform1f(uniforms['u_hueB'],        state.hueB);
  gl.uniform1f(uniforms['u_hueC'],        state.hueC);
  gl.uniform1f(uniforms['u_sat'],         state.sat);
  gl.uniform1f(uniforms['u_lum'],         state.lum);
  gl.uniform1f(uniforms['u_mode'],        modeIndex[state.mode] ?? 0);
  gl.uniform1f(uniforms['u_voice'],       voice);

  gl.drawArrays(gl.TRIANGLES, 0, 6);
}
