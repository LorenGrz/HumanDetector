# Deck — pitch de HumanDetector

Presentación de 7 slides para la antihackathon. Hecha con [Marp](https://marp.app/).

## Archivos

| | |
|---|---|
| `deck.md` | Fuente (Markdown + HTML). Editás acá. |
| `theme.css` | Tema Marp `humandetector` (estética terminal negro/verde). |
| `assets/qr.png` · `qr.svg` | QR a `https://lorengrz.github.io/HumanDetector/` (generado con `qrencode`). |
| `dist/humandetector.pptx` | Cada slide como imagen — se proyecta exacto. |
| `dist/humandetector-editable.pptx` | Texto editable (conversión vía LibreOffice; el layout puede correrse un poco). |
| `dist/humandetector.pdf` | Para proyectar sin PowerPoint. |
| `dist/humandetector.html` | Self-contained, se presenta desde el browser. |

## Regenerar

```sh
cd deck
npx @marp-team/marp-cli deck.md --theme theme.css --html --allow-local-files \
  --pptx --pdf -o dist/humandetector.pptx
npx @marp-team/marp-cli deck.md --theme theme.css --html --allow-local-files \
  --pptx --pptx-editable -o dist/humandetector-editable.pptx
```

Regenerar el QR si cambia la URL:

```sh
qrencode -t PNG -o assets/qr.png -s 30 -m 2 -l M "https://lorengrz.github.io/HumanDetector/"
```
