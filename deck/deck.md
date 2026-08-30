---
marp: true
theme: humandetector
paginate: false
html: true
size: 16:9
title: ¿Sos humano?
---

<!-- _class: lead -->

<div class="kicker">Levantá la mano</div>

# ¿SOS <strong>HUMANO</strong>?

<p class="dim">Nadie baja la mano. El sistema tampoco les cree.</p>

---

<!-- _class: center -->

## Todos los días te piden que lo demuestres

<div class="recaptcha">
  <div class="box err"></div>
  <div class="label">No soy un robot</div>
  <div class="brand"><b>reCAPTCHA</b>Privacidad · Términos</div>
</div>

<p class="meme mid" style="margin-top:36px">¿y si el sistema<br>simplemente nunca te cree?</p>

---

## <strong>HumanDetector</strong>: un verificador que no aprueba a nadie

<div class="drake">
  <div class="cell no face"><span class="ico">🙅</span></div>
  <div class="cell no">CAPTCHA: "seleccioná las fotos con semáforos"</div>
  <div class="cell yes face"><span class="ico">🙆</span></div>
  <div class="cell yes">HUMANDETECTOR: "mostrá desconfianza genuina a cámara"</div>
</div>

<p class="dim center" style="margin-top:28px">Pide gestos reales por la webcam · escala los pedidos hasta lo imposible · nunca confirma</p>

---

## Cómo escala el interrogatorio

<div class="brain">
  <div class="row"><span class="b">🧠</span><span>Paso 01 — "Parpadeá tres veces"</span></div>
  <div class="row"><span class="b">🧠</span><span>Paso 03 — "Girá la cabeza hacia la izquierda"</span></div>
  <div class="row"><span class="b">🤯</span><span>Paso 06 — "Arrugá solo la nariz"</span></div>
  <div class="row"><span class="b">🌌</span><span>Paso 10 — "Expresá una emoción que vas a sentir recién en el futuro"</span></div>
</div>

<p class="dim center" style="margin-top:24px">Detección real con <strong>MediaPipe</strong> (parpadeo, giro, inclinación, boca). Los primeros pasos se pasan. El resto, no.</p>

---

<!-- _class: center -->

<div class="kicker">ESCANEÁ · REQUIERE CÁMARA · NO VAS A APROBAR</div>

# PROBALO AHORA

<div class="qr-wrap">
  <img src="assets/qr.png" alt="QR a HumanDetector" />
  <div class="url">lorengrz.github.io/HumanDetector</div>
</div>

---

## Cómo está hecho

- **Frontend** — Next.js export estático en <strong>GitHub Pages</strong>
- **Backend** — FastAPI + MediaPipe en contenedor, <strong>AWS EC2</strong> + Caddy (TLS automático)
- **Transporte** — un WebSocket manda frames de la cámara y recibe la escalada
- **Estado** — sin base de datos: todo vive en memoria por conexión

<div class="stack-tags">
  <span>Next.js</span><span>TypeScript</span><span>Tailwind</span><span>Python</span><span>FastAPI</span><span>MediaPipe</span><span>WebSockets</span><span>Docker</span><span>AWS EC2</span><span>Caddy</span>
</div>

---

<!-- _class: center -->

<div class="kicker">RESULTADO DE LA VERIFICACIÓN</div>

# HUMANO <strong style="color:#b23b3b">NO CONFIRMADO</strong>

<p class="meme mid">🔥 🐶 🔥 &nbsp; todo bien &nbsp; 🔥</p>

<p class="dim">Bienvenido a la gobernanza algorítmica.<br>github.com/LorenGrz/HumanDetector</p>
