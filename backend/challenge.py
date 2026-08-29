"""Máquina de estados de la escalada de pedidos del verificador.

No sabe nada de mediapipe ni de WebSockets: recibe señales ya interpretadas
(cantidad de parpadeos, yaw, energía de movimiento) y devuelve qué mostrar a
continuación. Cada sesión sortea su propio plan de hasta 10 pasos: qué
gesto real pedir primero, en qué paso empieza a mentir, y qué acusación
final le toca si no logra seguirle el ritmo al reloj.

A partir del paso 3 aparece un contador que se achica en cada intento (más
presión, menos tiempo). Si el movimiento facial durante ese intento supera
el umbral, el paso se aprueba de verdad — es difícil a propósito, pero no
es un engaño total: si lo lográs, el sistema lo reconoce.
"""

import random
from dataclasses import dataclass, field
from typing import Literal, Optional

StepKind = Literal[
    "blink", "yaw_left", "yaw_right", "mouth_open", "tilt_left", "tilt_right", "auto_pass", "reject"
]

TOTAL_STEPS = 10
YAW_TURN_THRESHOLD = 0.18
TILT_THRESHOLD_DEGREES = 12.0
MOUTH_OPEN_THRESHOLD = 0.5

# El contador arranca en el paso 3 (recién después del 2do paso real) y se
# achica en cada intento siguiente, hasta un piso, para que la presión
# suba de forma exponencial en vez de aparecer de golpe.
PRESSURE_START_SECONDS = 9.0
PRESSURE_STEP_SECONDS = 1.0
PRESSURE_FLOOR_SECONDS = 3.0

# Energía de movimiento (suma de desplazamientos de landmarks normalizados
# durante la ventana del intento) necesaria para que "siga el ritmo". No
# alcanza por sí sola: además hay que ganar el sorteo de CONFIRM_PROBABILITY
# — así es difícil que pase incluso moviéndose mucho, y casi imposible que
# pase dos veces seguidas. Ajustar umbral según cámara/luz del evento.
MOTION_PASS_THRESHOLD = 10.0
CONFIRM_PROBABILITY = 1 / 6

_REAL_INSTRUCTIONS = {
    "blink": "Parpadeá dos veces",
    "yaw_left": "Girá la cabeza a la izquierda",
    "yaw_right": "Girá la cabeza a la derecha",
    "mouth_open": "Abrí la boca",
    "tilt_left": "Inclina la cabeza hacia tu hombro izquierdo",
    "tilt_right": "Inclina la cabeza hacia tu hombro derecho",
}

# Familias de gestos reales: cada sesión elige REAL_STEP_COUNT familias al
# azar (sin repetir) y, si la familia tiene variantes (izquierda/derecha),
# sortea cuál. Así los primeros pasos varían de sesión a sesión en vez de
# ser siempre "parpadeá y girá la cabeza".
_REAL_FAMILIES: list[list[StepKind]] = [
    ["blink"],
    ["yaw_left", "yaw_right"],
    ["mouth_open"],
    ["tilt_left", "tilt_right"],
]
REAL_STEP_COUNT = 3


def _pick_real_kinds() -> list[StepKind]:
    families = random.sample(_REAL_FAMILIES, k=REAL_STEP_COUNT)
    kinds = [random.choice(family) for family in families]
    random.shuffle(kinds)
    return kinds

_AUTO_PASS_BANK = [
    "Mantené la mirada fija en el centro de la cámara",
    "Acercate un paso a la cámara, despacio",
    "Inclina la cabeza levemente hacia adelante",
    "Quedate quieto durante el escaneo",
    "Mirá hacia arriba y contá hasta tres en silencio",
]

# Agrupado en secciones de dificultad (leve -> media -> imposible). Cada
# sesión recorre las secciones en ese orden, pero DENTRO de cada sección la
# instrucción elegida es al azar — así dos personas no hacen la misma
# secuencia exacta, aunque la curva de dificultad sea la misma. Cada
# instrucción tiene su propio banco de sospechas ("suspicion_bank") que
# comenta específicamente por qué "falla" justo en ese gesto.
_REJECT_TIER_MILD = [
    {
        "text": "Sonreí de forma natural",
        "suspicion_bank": [
            "Esa sonrisa se ve calculada.",
            "Los músculos faciales se activaron en un orden sospechoso.",
            "¿Por qué le cuesta tanto sonreír 'sin querer'?",
        ],
    },
    {
        "text": "Mostrá sorpresa genuina",
        "suspicion_bank": [
            "La sorpresa llegó medio segundo tarde.",
            "Un humano real no necesitaría pensar la sorpresa.",
            "Cejas levantadas, pero sin el sobresalto real detrás.",
        ],
    },
    {
        "text": "Fruncí el ceño con autenticidad",
        "suspicion_bank": [
            "El ceño se frunce, pero los ojos no acompañan.",
            "Autenticidad del gesto: baja.",
            "Parece más un tic que un sentimiento.",
        ],
    },
]

_REJECT_TIER_MEDIUM = [
    {
        "text": "Parpadeá de forma asimétrica",
        "suspicion_bank": [
            "Mmm... qué raro que le cueste tanto pestañear asimétricamente.",
            "Ambos ojos insisten en moverse igual. Muy poco humano.",
            "Un ojo se resiste a cooperar por separado. Anómalo.",
        ],
    },
    {
        "text": "Mové solo la ceja izquierda",
        "suspicion_bank": [
            "La ceja derecha sigue moviéndose sola. Sospechoso.",
            "El control muscular independiente no es su fuerte.",
            "¿Un humano puede aislar un solo músculo facial? Dudoso.",
        ],
    },
    {
        "text": "Mirá a la cámara sin parpadear",
        "suspicion_bank": [
            "El parpadeo reflejo sigue activo. Muy humano, en realidad.",
            "Los ojos se resecan. Reacción demasiado biológica.",
            "Este comportamiento no ayuda a descartar la sospecha.",
        ],
    },
    {
        "text": "Generá una expresión que no hayas ensayado nunca",
        "suspicion_bank": [
            "Toda expresión humana ya fue ensayada alguna vez.",
            "El sistema no puede confirmar espontaneidad real.",
            "Se detecta duda, no autenticidad.",
        ],
    },
]

_REJECT_TIER_IMPOSSIBLE = [
    {
        "text": "Demostrá una emoción irrepetible",
        "suspicion_bank": [
            "Las emociones humanas se repiten estadísticamente.",
            "Nada en este rostro es, en rigor, irrepetible.",
            "Contradicción lógica detectada en el pedido y en la respuesta.",
        ],
    },
    {
        "text": "Sincronizá tu expresión con un recuerdo que no tenés",
        "suspicion_bank": [
            "Pedido lógicamente imposible. El sujeto lo sigue intentando.",
            "Persistencia sospechosa ante un pedido sin sentido.",
            "Eso, en rigor, no se puede hacer. Y sin embargo lo intenta.",
        ],
    },
    {
        "text": "Mostrá una emoción que la especie humana todavía no descubrió",
        "suspicion_bank": [
            "Definición pendiente. El sistema tampoco sabe qué buscar.",
            "El sujeto sigue esforzándose por algo indefinible.",
            "Ni el protocolo sabe cómo se vería eso. Igual, insiste.",
        ],
    },
]

_REJECT_TIERS = [_REJECT_TIER_MILD, _REJECT_TIER_MEDIUM, _REJECT_TIER_IMPOSSIBLE]


def _pick_reject_entries(count: int) -> list[dict]:
    """Arma `count` pasos de rechazo en secciones de dificultad crecientes,
    pero la instrucción elegida dentro de cada sección es al azar."""
    boundaries = [round(count * (i + 1) / len(_REJECT_TIERS)) for i in range(len(_REJECT_TIERS))]
    entries: list[dict] = []
    start = 0
    for tier, end in zip(_REJECT_TIERS, boundaries):
        section_size = end - start
        start = end
        pool: list[dict] = []
        for _ in range(section_size):
            if not pool:
                pool = list(tier)
                random.shuffle(pool)
            entries.append(pool.pop())
    return entries[:count]

_REJECT_MESSAGES = [
    "Patrón facial demasiado uniforme. Reintentá.",
    "Expresión clasificada como ensayada. Reintentá.",
    "No se detectó espontaneidad suficiente. Reintentá.",
    "El gesto coincide con registros previos. Reintentá.",
    "Autenticidad emocional insuficiente. Reintentá.",
    "Microexpresión fuera de rango humano conocido. Reintentá.",
    "Se detectaron inconsistencias térmicas faciales. Reintentá.",
]

_ACCUSATIONS = [
    {
        "label": "POSIBLE REPTILIANO",
        "message": "Se detectó parpadeo nictitante incompatible con la fisiología humana estándar.",
    },
    {
        "label": "ENTIDAD SINTÉTICA NO REGISTRADA",
        "message": "Los patrones faciales no coinciden con ningún registro biológico catalogado.",
    },
    {
        "label": "REPLICANTE NIVEL 3",
        "message": "Respuesta emocional excesivamente consistente para tratarse de un sujeto orgánico.",
    },
    {
        "label": "ANOMALÍA DIMENSIONAL",
        "message": "La firma biométrica no converge con ningún linaje humano conocido por el sistema.",
    },
    {
        "label": "RESIDUO ECTOPLÁSMICO",
        "message": "Se detectaron fluctuaciones faciales sin correlato térmico. Posible entidad no física.",
    },
    {
        "label": "UNIDAD DE VIGILANCIA NO HUMANA",
        "message": "El patrón de parpadeo es demasiado regular para tratarse de un sistema nervioso biológico.",
    },
    {
        "label": "VIAJERO TEMPORAL NO REGISTRADO",
        "message": "El patrón de envejecimiento facial no coincide con la edad declarada.",
    },
    {
        "label": "PROTOTIPO DE IA FUGADO",
        "message": "Las respuestas son demasiado consistentes con un modelo entrenado. Posible fuga de laboratorio.",
    },
    {
        "label": "DOBLE DE CUERPO NO ACREDITADO",
        "message": "Coincidencia biométrica parcial con una identidad ya registrada. Posible sustitución.",
    },
    {
        "label": "MIEMBRO DE SOCIEDAD SECRETA NIVEL MEDIO",
        "message": "Se detectaron gestos faciales compatibles con protocolos de reconocimiento no públicos.",
    },
]

_SUSPICION_NEUTRAL = [
    "Escaneando geometría facial...",
    "Extrayendo puntos de referencia...",
    "Calibrando perfil biométrico...",
    "Analizando textura dérmica...",
    "Midiendo simetría facial...",
]

_SUSPICION_CRITICAL = [
    "Sospecha de origen no humano: alta...",
    "Iniciando protocolo de reclasificación...",
    "Posible entidad no catalogada...",
    "Coincidencias con registros anómalos previos...",
    "Preparando dictamen final...",
]

_MORALEJA = (
    "El acceso a los sistemas centrales queda restringido, pendiente de una "
    "revisión que nunca va a llegar."
)

_CONFIRMED_MESSAGE = (
    "Le ganaste al cronómetro y al protocolo. Rarísimo — casi nadie lo logra. "
    "Quedás acreditado como humano, al menos por ahora."
)


@dataclass
class StepResult:
    kind: str  # "instruction" | "result" | "reveal" | "confirmed"
    step: Optional[int] = None
    text: Optional[str] = None
    passed: Optional[bool] = None
    message: Optional[str] = None
    duration: Optional[float] = None


@dataclass
class StepSpec:
    kind: StepKind
    text: str
    suspicion_bank: list[str] = field(default_factory=lambda: _SUSPICION_NEUTRAL)


def _build_plan() -> list[StepSpec]:
    real_kinds = _pick_real_kinds()

    # Mínimo 4 pasos antes de empezar a rechazar: que no se sienta forzado
    # ni se note de entrada que el resultado ya está decidido. Con 3 pasos
    # reales de base, fail_start >= 5 asegura ese mínimo de 4.
    fail_start = random.choice([5, 6])

    plan = [StepSpec(kind=k, text=_REAL_INSTRUCTIONS[k]) for k in real_kinds]
    while len(plan) < fail_start - 1:
        plan.append(StepSpec(kind="auto_pass", text=random.choice(_AUTO_PASS_BANK)))

    for entry in _pick_reject_entries(TOTAL_STEPS - len(plan)):
        plan.append(StepSpec(kind="reject", text=entry["text"], suspicion_bank=entry["suspicion_bank"]))

    return plan[:TOTAL_STEPS]


@dataclass
class ChallengeSession:
    plan: list[StepSpec] = field(default_factory=_build_plan)
    step: int = field(default=1, init=False)
    _pressure_index: int = field(default=0, init=False, repr=False)

    def current_spec(self) -> StepSpec:
        return self.plan[self.step - 1]

    def current_duration(self) -> Optional[float]:
        """None para los pasos reales (1-2): esos no tienen límite de tiempo."""
        if self.current_spec().kind not in ("auto_pass", "reject"):
            return None
        return max(
            PRESSURE_FLOOR_SECONDS,
            PRESSURE_START_SECONDS - self._pressure_index * PRESSURE_STEP_SECONDS,
        )

    def suspicion_line(self) -> str:
        """Comentario random y específico del intento actual."""
        spec = self.current_spec()
        if spec.kind == "reject" and self.step >= TOTAL_STEPS - 1:
            return random.choice(_SUSPICION_CRITICAL)
        if spec.kind == "reject":
            return random.choice(spec.suspicion_bank)
        return random.choice(_SUSPICION_NEUTRAL)

    def instruction(self) -> StepResult:
        spec = self.current_spec()
        return StepResult(
            kind="instruction", step=self.step, text=spec.text, duration=self.current_duration()
        )

    def submit_blink_count(self, blink_count: int) -> Optional[StepResult]:
        if self.current_spec().kind != "blink" or blink_count < 2:
            return None
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def submit_yaw(self, yaw: float) -> Optional[StepResult]:
        spec = self.current_spec()
        if spec.kind == "yaw_left" and yaw > YAW_TURN_THRESHOLD:
            pass
        elif spec.kind == "yaw_right" and yaw < -YAW_TURN_THRESHOLD:
            pass
        else:
            return None
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def submit_tilt(self, roll_degrees: float) -> Optional[StepResult]:
        spec = self.current_spec()
        if spec.kind == "tilt_left" and roll_degrees < -TILT_THRESHOLD_DEGREES:
            pass
        elif spec.kind == "tilt_right" and roll_degrees > TILT_THRESHOLD_DEGREES:
            pass
        else:
            return None
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def submit_mouth_open(self, mouth_aspect_ratio: float) -> Optional[StepResult]:
        if self.current_spec().kind != "mouth_open" or mouth_aspect_ratio < MOUTH_OPEN_THRESHOLD:
            return None
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def auto_pass(self) -> StepResult:
        """Pasos intermedios teatrales: siempre pasan, para sumar variedad."""
        self._pressure_index += 1
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def resolve_reject(self, motion_score: float) -> StepResult:
        """Paso contra reloj, cada vez más corto.

        Moverse lo suficiente (MOTION_PASS_THRESHOLD) es necesario pero no
        alcanza: además hay que ganar un sorteo de CONFIRM_PROBABILITY
        (1 en 6). Así es raro que un intento pase, y mucho más raro que
        pasen dos seguidos. Si no pasa, rechaza y avanza — y si era el
        último de los TOTAL_STEPS, dispara el veredicto final.
        """
        self._pressure_index += 1
        passed = motion_score >= MOTION_PASS_THRESHOLD and random.random() < CONFIRM_PROBABILITY
        is_last_step = self.step >= TOTAL_STEPS

        if passed:
            if is_last_step:
                return StepResult(kind="confirmed", text="HUMANO CONFIRMADO", message=_CONFIRMED_MESSAGE)
            result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
            self.step += 1
            return result

        if is_last_step:
            accusation = random.choice(_ACCUSATIONS)
            return StepResult(
                kind="reveal",
                text=accusation["label"],
                message=f"{accusation['message']} {_MORALEJA}",
            )

        message = random.choice(_REJECT_MESSAGES)
        result = StepResult(kind="result", step=self.step, passed=False, message=message)
        self.step += 1
        return result
