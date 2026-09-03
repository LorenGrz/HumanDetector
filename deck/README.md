# Deck — pitch de HumanDetector

Presentación de 7 slides para la antihackathon. Hecha con [Marp](https://marp.app/).

## Archivos

| | |
|---|---|
| `deck.md` | Fuente (Markdown + HTML). Editás acá. |
| `theme.css` | Tema Marp `humandetector` (estética terminal negro/verde). |
| `assets/qr.png` · `qr.svg` | QR a `https://lorengrz.github.io/HumanDetector/` (generado con `qrencode`). Van embebidos como data URI en `deck.md` para que el `.html` sea self-contained. |
| `dist/humandetector.pptx` | Cada slide como imagen — se proyecta exacto. |
| `dist/humandetector-editable.pptx` | Texto editable (conversión vía LibreOffice; el layout puede correrse un poco). |
| `dist/humandetector.pdf` | Para proyectar sin PowerPoint. |
| `dist/humandetector.html` | Self-contained, se presenta desde el browser. |

## Regenerar

```sh
cd deck
# --pptx / --pdf / --html son mutuamente exclusivos: una corrida por formato.
npx @marp-team/marp-cli deck.md --theme theme.css --html --allow-local-files \
  --pptx -o dist/humandetector.pptx
npx @marp-team/marp-cli deck.md --theme theme.css --html --allow-local-files \
  --pdf -o dist/humandetector.pdf
npx @marp-team/marp-cli deck.md --theme theme.css --html --allow-local-files \
  -o dist/humandetector.html
npx @marp-team/marp-cli deck.md --theme theme.css --html --allow-local-files \
  --pptx --pptx-editable -o dist/humandetector-editable.pptx
```

Cerrá el `.pptx` en LibreOffice/PowerPoint antes de regenerar (si no, queda un
`.~lock` y marp no puede sobrescribir).

Regenerar el QR si cambia la URL:

```sh
qrencode -t PNG -o assets/qr.png -s 30 -m 2 -l M "https://lorengrz.github.io/HumanDetector/"
```

Después de regenerar un QR hay que volver a embeberlo en `deck.md` (el `<img src>`
usa `data:image/png;base64,…`, no la ruta al archivo):

```sh
python3 - <<'PY'
import base64, re
md = open('deck.md', encoding='utf-8').read()
for png, alt in [('assets/qr.png', 'QR a HumanDetector'),
                 ('assets/qr-portfolio.png', 'QR al portfolio')]:
    uri = 'data:image/png;base64,' + base64.b64encode(open(png, 'rb').read()).decode()
    md = re.sub(rf'<img src="[^"]*" alt="{alt}" />', f'<img src="{uri}" alt="{alt}" />', md)
open('deck.md', 'w', encoding='utf-8').write(md)
PY
```
