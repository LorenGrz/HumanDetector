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

<p class="dim">Cada vez te lo van a preguntar más seguido. Y con menos paciencia.</p>

---

<!-- _class: center -->

## Verificar tu humanidad ya es rutina

<div class="recaptcha">
  <div class="box err"></div>
  <div class="label">No soy un robot</div>
  <div class="brand"><b>reCAPTCHA</b>Privacidad · Términos</div>
</div>

<p class="dim" style="margin-top:22px">Semáforos, bicicletas, "seleccioná todas las imágenes con un colectivo". Un trámite.</p>

<p class="statement" style="margin-top:22px">¿Y si dejara de ser un trámite<br>y pasara a ser un <strong>juicio</strong>?</p>

---

# <strong>HumanDetector</strong>

<div class="drake">
  <div class="cell no face"><span class="ico">🙅</span></div>
  <div class="cell no">"Marcá la casilla: no soy un robot."</div>
  <div class="cell yes face"><span class="ico">🙆</span></div>
  <div class="cell yes">"Demostralo. Con la cara. En vivo."</div>
</div>

<p class="statement" style="margin-top:28px">Un sistema que te <strong>presiona</strong> a demostrar tu humanidad — en un mundo donde cada vez más nos reemplazan.</p>

---

## Cómo funciona

<div class="steps">
  <div class="step"><span class="n">01</span><span>Escaneás el QR — se abre en tu teléfono.</span></div>
  <div class="step"><span class="n">02</span><span>Le das acceso a la cámara. Todo pasa en el momento; nada se guarda.</span></div>
  <div class="step"><span class="n">03</span><span>Te pide un gesto. Lo hacés. <strong>MediaPipe te lee la cara de verdad</strong> — parpadeo, giro, inclinación.</span></div>
  <div class="step"><span class="n">04</span><span>Pasás ese paso → el siguiente es más exigente. Y así.</span></div>
</div>

<p class="statement" style="margin-top:24px">No está hecho para que apruebes.<br>Está hecho para que <strong>te lo preguntes</strong>.</p>

---

## Primeras reacciones

<div class="reviews">
  <div class="rev">
    <div class="stars">★☆☆☆☆</div>
    <div class="q">"Hice todo lo que me pidió. Sigo sin ser humano oficialmente."</div>
    <div class="who">— usuario #2213</div>
  </div>
  <div class="rev">
    <div class="stars">★★★★★</div>
    <div class="q">"La mejor crisis existencial que tuve este año."</div>
    <div class="who">— anónimo</div>
  </div>
  <div class="rev">
    <div class="stars">★☆☆☆☆</div>
    <div class="q">"Se lo pasé a mi jefe. Tampoco aprobó. Ahora nos llevamos mejor."</div>
    <div class="who">— RR.HH.</div>
  </div>
  <div class="rev">
    <div class="stars">★★★☆☆</div>
    <div class="q">"Llegué lejos. Nadie llega lo suficiente."</div>
    <div class="who">— un tester</div>
  </div>
</div>

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

## ¿Y si el sistema <strong>realmente</strong> te juzgara?

<ul>
  <li>Bancos que te piden una selfie para abrir una cuenta.</li>
  <li>"Liveness detection": girá la cabeza, parpadeá, seguí el punto con la mirada.</li>
  <li>Cada año, más gates de "probá que sos humano" — y más difíciles.</li>
</ul>

<p class="statement" style="margin-top:24px">HumanDetector solo lleva esa lógica <strong>hasta el final</strong>. La parte incómoda es que ya la viste antes.</p>

---

<div class="kicker">Moraleja</div>

# Le pedimos a las máquinas que nos <strong>distingan</strong> de las máquinas.

<p class="big-note">El sistema no está roto: hace exactamente lo que promete — no confiar en nadie.</p>

<p class="dim">Vos, mientras tanto, seguís con la mano levantada.<br>github.com/LorenGrz/HumanDetector</p>

---

<!-- _class: center -->

# CONECTEMOS

<div class="qr-wrap">
  <img src="assets/qr-portfolio.png" alt="QR al portfolio" />
  <div class="url">lorengrz.github.io</div>
</div>

<p class="dim">Mi portfolio. Acá <strong>sí</strong> te dejan pasar.</p>
