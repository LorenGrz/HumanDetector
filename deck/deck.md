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

<p class="dim" style="margin-top:22px">Semáforos, bicicletas, "seleccioná todas las imágenes con un colectivo".</p>
<p class="meme mid" style="margin-top:18px">¿y si el sistema<br>simplemente nunca te cree?</p>

---

## <strong>HumanDetector</strong>: un verificador que no aprueba a nadie

<div class="drake">
  <div class="cell no face"><span class="ico">🙅</span></div>
  <div class="cell no">CAPTCHA: "seleccioná las fotos con semáforos"</div>
  <div class="cell yes face"><span class="ico">🙆</span></div>
  <div class="cell yes">HUMANDETECTOR: "mostrá desconfianza genuina a cámara"</div>
</div>

<p class="dim center" style="margin-top:26px">Una instalación satírica: te pide gestos por la webcam, los detecta de verdad, y va subiendo la apuesta.</p>

---

## Cómo lo vas a usar

<div class="steps">
  <div class="step"><span class="n">01</span><span>Escaneás el QR — se abre en tu teléfono.</span></div>
  <div class="step"><span class="n">02</span><span>Le das acceso a la cámara. Todo pasa en el momento; nada se guarda.</span></div>
  <div class="step"><span class="n">03</span><span>El sistema te pide un gesto. Lo hacés. Lo detecta de verdad.</span></div>
  <div class="step"><span class="n">04</span><span>Pasás ese paso → el siguiente es más exigente. Y así.</span></div>
</div>

<p class="meme mid" style="margin-top:26px">🪤 es una trampa &nbsp;·&nbsp; probala igual</p>

---

## La detección es real

<div class="brain">
  <div class="row"><span class="b">🧠</span><span>MediaPipe te lee la cara: parpadeo, giro, inclinación, boca</span></div>
  <div class="row"><span class="b">🧠</span><span>Los primeros gestos son normales — los pasás sin drama</span></div>
  <div class="row"><span class="b">🤯</span><span>Después, los pedidos se vuelven... creativos</span></div>
  <div class="row"><span class="b">🌌</span><span>Cuánto aguantás antes de que sea imposible: averigualo vos</span></div>
</div>

<p class="dim center" style="margin-top:22px">No spoileamos los pedidos finales. Se disfrutan más en vivo.</p>

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
- **Transporte** — un WebSocket manda los frames de la cámara y recibe la escalada
- **Deploy** — imagen construida en AWS CodeBuild, backend <strong>on-demand</strong> (se prende para el evento)
- **Estado** — sin base de datos: todo vive en memoria por conexión

<div class="stack-tags">
  <span>Next.js</span><span>TypeScript</span><span>Tailwind</span><span>Python</span><span>FastAPI</span><span>MediaPipe</span><span>WebSockets</span><span>Docker</span><span>AWS EC2</span><span>CodeBuild</span><span>Caddy</span>
</div>

---

<!-- _class: center -->

<div class="kicker">RESULTADO DE LA VERIFICACIÓN</div>

# HUMANO <strong style="color:#b23b3b">NO CONFIRMADO</strong>

<p class="meme mid">🔥 🐶 🔥 &nbsp; todo bien &nbsp; 🔥</p>

<p class="dim">Intentá de nuevo. El resultado va a ser el mismo.</p>

---

<div class="kicker">Moraleja</div>

# Le pedimos a las máquinas que nos <strong>distingan</strong> de las máquinas.

<p class="big-note">El sistema no está roto: hace exactamente lo que promete — no confiar en nadie.</p>

<p class="dim">Vos, mientras tanto, seguís con la mano levantada.<br>github.com/LorenGrz/HumanDetector</p>
