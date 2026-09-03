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
    "blink",
    "yaw_left",
    "yaw_right",
    "mouth_open",
    "tilt_left",
    "tilt_right",
    "tilt_forward",
    "look_up",
    "move_closer",
    "auto_pass",
    "reject",
]

TOTAL_STEPS = 10
YAW_TURN_THRESHOLD = 0.18
TILT_THRESHOLD_DEGREES = 12.0
MOUTH_OPEN_THRESHOLD = 0.5
# Cuánto tiene que crecer el ancho de cara (interocular) respecto al primer
# frame del paso para contar como "se acercó". Ajustar según cámara/evento.
PROXIMITY_INCREASE_RATIO = 0.15
# Cuánto tiene que crecer (inclinar adelante) o bajar (mirar arriba)
# pitch_ratio respecto al primer frame del paso. Ajustar según cámara/evento.
PITCH_FORWARD_INCREASE = 0.06
LOOK_UP_DECREASE = 0.06

# El contador arranca en el paso 3 (recién después del 2do paso real) y se
# achica en cada intento siguiente, hasta un piso, para que la presión
# suba de forma exponencial en vez de aparecer de golpe. El piso no baja de
# 4s: con textos largos, menos que eso no alcanza ni para leer la consigna.
PRESSURE_START_SECONDS = 9.0
PRESSURE_STEP_SECONDS = 1.0
PRESSURE_FLOOR_SECONDS = 4.0

# Energía de movimiento (suma de desplazamientos de landmarks normalizados
# durante la ventana del intento) necesaria para que "siga el ritmo". No
# alcanza por sí sola: además hay que ganar el sorteo de CONFIRM_PROBABILITY
# — así es difícil que pase incluso moviéndose mucho, y casi imposible que
# pase dos veces seguidas. Ajustar umbral según cámara/luz del evento.
MOTION_PASS_THRESHOLD = 10.0
CONFIRM_PROBABILITY = 1 / 5

_REAL_INSTRUCTIONS = {
    "blink": "Parpadeá dos veces",
    "yaw_left": "Girá la cabeza a la izquierda",
    "yaw_right": "Girá la cabeza a la derecha",
    "mouth_open": "Abrí la boca",
    "tilt_left": "Inclina la cabeza hacia tu hombro izquierdo",
    "tilt_right": "Inclina la cabeza hacia tu hombro derecho",
    "tilt_forward": "Inclina la cabeza hacia adelante",
    "look_up": "Mirá hacia arriba",
    "move_closer": "Acercate un paso a la cámara",
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
    ["move_closer"],
    ["tilt_forward"],
    ["look_up"],
]
REAL_STEP_COUNT = 3


def _pick_real_kinds() -> list[StepKind]:
    families = random.sample(_REAL_FAMILIES, k=REAL_STEP_COUNT)
    kinds = [random.choice(family) for family in families]
    random.shuffle(kinds)
    return kinds

_AUTO_PASS_BANK = [
    "Mantené la mirada fija en el centro de la cámara",
    "Quedate quieto durante el escaneo",
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
    {
        "text": "Mostrá desconfianza genuina",
        "suspicion_bank": [
            "La desconfianza se nota, pero llega tarde.",
            "¿Eso fue desconfianza o solo una corriente de aire?",
            "Gesto registrado. Autenticidad: en duda.",
        ],
    },
    {
        "text": "Hacé un gesto de asombro real",
        "suspicion_bank": [
            "El asombro parece de manual.",
            "Ojos bien abiertos, pero la ceja no acompaña.",
            "Reacción demasiado prolija para ser espontánea.",
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
    {
        "text": "Arrugá solo la nariz",
        "suspicion_bank": [
            "La nariz se arruga, el resto de la cara no coopera.",
            "Movimiento aislado sospechosamente preciso.",
            "¿Alguien puede mover solo la nariz? Dudoso.",
        ],
    },
    {
        "text": "Sonreí de un solo lado de la boca",
        "suspicion_bank": [
            "Sonrisa asimétrica detectada. Simetría facial: cuestionada.",
            "Un lado de la boca coopera, el otro se resiste.",
            "Control muscular unilateral fuera de lo esperado.",
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
    {
        "text": "Mostrá alegría sin mover ningún músculo conocido",
        "suspicion_bank": [
            "Contradicción detectada: toda alegría implica movimiento muscular.",
            "El sujeto lo intenta igual. Persistencia anotada.",
            "No hay músculo que cumpla ese criterio. Se solicita igual.",
        ],
    },
    {
        "text": "Expresá una emoción que vas a sentir recién en el futuro",
        "suspicion_bank": [
            "El sistema no puede verificar emociones que todavía no ocurrieron.",
            "Se detecta un intento de anticipación emocional. Insuficiente.",
            "Pedido temporalmente imposible. El sujeto igual pone cara.",
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
        "label": "POSIBLE ALIENÍGENA",
        "message": "La firma biométrica no converge con ningún linaje humano conocido por el sistema.",
    },
    {
        "label": "IA GENERATIVA SIN SUPERVISIÓN HUMANA",
        "message": "Las respuestas faciales son estadísticamente indistinguibles de un modelo entrenado. Alucinación de gestos no descartada.",
    },
    {
        "label": "SABOTEADOR DEL MUNDIAL 2026",
        "message": "Se detectaron vínculos con la conspiración contra los jugadores de Argentina en el Mundial 2026.",
    },
    {
        "label": "AGENTE ENCUBIERTO DE LA FIFA",
        "message": "Comportamiento demasiado alineado con los intereses comerciales del organismo.",
    },
    {
        "label": "CANDIDATO A GRAN HERMANO NO SELECCIONADO",
        "message": "Nivel de sobreactuación frente a cámara incompatible con espontaneidad real.",
    },
    {
        "label": "SOSPECHOSO DE TOMAR MATE SIN CEBAR A NADIE",
        "message": "Consumo de infusión detectado sin evidencia de reciprocidad en el cebado.",
    },
    {
        "label": "PRÓFUGO DE UN GRUPO DE WHATSAPP FAMILIAR",
        "message": "Mensajes sin responder detectados en al menos tres cadenas de reenvíos.",
    },
    {
        "label": "ASISTENTE HABITUAL A ASADOS SIN LLEVAR NADA",
        "message": "No se registra aporte alguno en los últimos encuentros sociales catalogados.",
    },
    {
        "label": "BOT DE REDES CON FOTO DE PERFIL HUMANA",
        "message": "El patrón de parpadeo coincide con cuentas creadas en lote.",
    },
    {
        "label": "INFILTRADO DE LA CONMEBOL",
        "message": "Acceso sospechoso a información de sorteos antes de su publicación oficial.",
    },
    {
        "label": "SOSPECHOSO DE NO DEVOLVER EL TÁPER",
        "message": "Se registran recipientes plásticos ajenos sin restitución en al menos dos domicilios.",
    },
    {
        "label": "USUARIO QUE DIJO 'YA SALGO' HACE CUARENTA MINUTOS",
        "message": "Discrepancia crítica entre la ubicación declarada y la ubicación real.",
    },
    {
        "label": "REVENDEDOR DE ENTRADAS NO ACREDITADO",
        "message": "Patrón facial compatible con operaciones de reventa a valor inflado.",
    },
    {
        "label": "COMENSAL DE MILANESAS FRÍAS A LAS TRES DE LA MAÑANA",
        "message": "Actividad de heladera fuera de horario compatible con hábitos no declarados.",
    },
]

_SUSPICION_NEUTRAL = [
    "Escaneando geometría facial...",
    "Extrayendo puntos de referencia...",
    "Calibrando perfil biométrico...",
    "Analizando textura dérmica...",
    "Midiendo simetría facial...",
]

# Comentario específico por cada gesto real, para que la sospecha en vivo
# no sea genérica ni siquiera en los pasos "fáciles".
_SUSPICION_BY_REAL_KIND: dict[str, list[str]] = {
    "blink": [
        "Contando parpadeos... el ritmo es sospechosamente parejo.",
        "Frecuencia de parpadeo dentro de rango, por ahora.",
        "Cada parpadeo se registra y se compara con la base de datos.",
    ],
    "yaw_left": [
        "Girando... el eje de rotación es demasiado preciso.",
        "Movimiento de cabeza mecánicamente perfecto. Anotado.",
        "Verificando eje de rotación cervical.",
    ],
    "yaw_right": [
        "Girando hacia el otro lado. Simetría sospechosa.",
        "El giro es fluido. Demasiado fluido.",
        "Verificando eje de rotación cervical.",
    ],
    "mouth_open": [
        "Apertura mandibular dentro de parámetros... por ahora.",
        "¿Eso fue un bostezo real o simulado?",
        "Midiendo amplitud bucal.",
    ],
    "tilt_left": [
        "Inclinación lateral en curso. Vértebras bajo observación.",
        "El cuello se dobla en un ángulo sospechosamente cómodo.",
        "Calculando centro de gravedad craneal.",
    ],
    "tilt_right": [
        "Inclinación hacia el otro lado. Todo demasiado simétrico.",
        "El equilibrio no se altera. Sospechoso.",
        "Verificando flexibilidad cervical.",
    ],
    "tilt_forward": [
        "La cabeza baja. El sistema sigue mirando.",
        "Inclinación frontal detectada. Analizando intención.",
        "¿Reverencia o maniobra evasiva? Indeterminado.",
    ],
    "look_up": [
        "Mmm... te estás moviendo.",
        "La mirada sube, la sospecha también.",
        "Buscando algo en el techo, o eso dice.",
    ],
    "move_closer": [
        "Acercamiento detectado. Reduciendo distancia de seguridad.",
        "Cuanto más cerca, más se ve. Eso no ayuda.",
        "El sujeto invade el espacio de escaneo. Continuando.",
    ],
}

# Comentario específico por cada instrucción teatral (auto_pass).
_SUSPICION_BY_AUTO_PASS_TEXT: dict[str, list[str]] = {
    "Mantené la mirada fija en el centro de la cámara": [
        "La mirada no se despega. Persistente.",
        "Fijación ocular prolongada. Anotado para revisión.",
        "¿Está mirando la cámara o algo detrás de ella?",
    ],
    "Quedate quieto durante el escaneo": [
        "Mmm... te estás moviendo.",
        "Se detecta microtemblor. Nadie está tan quieto.",
        "La inmovilidad total tampoco es normal, para que sepa.",
    ],
}

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

    plan = [
        StepSpec(kind=k, text=_REAL_INSTRUCTIONS[k], suspicion_bank=_SUSPICION_BY_REAL_KIND[k])
        for k in real_kinds
    ]
    auto_pass_pool = random.sample(_AUTO_PASS_BANK, k=len(_AUTO_PASS_BANK))
    while len(plan) < fail_start - 1 and auto_pass_pool:
        text = auto_pass_pool.pop()
        plan.append(
            StepSpec(kind="auto_pass", text=text, suspicion_bank=_SUSPICION_BY_AUTO_PASS_TEXT[text])
        )

    for entry in _pick_reject_entries(TOTAL_STEPS - len(plan)):
        plan.append(StepSpec(kind="reject", text=entry["text"], suspicion_bank=entry["suspicion_bank"]))

    return plan[:TOTAL_STEPS]


@dataclass
class ChallengeSession:
    plan: list[StepSpec] = field(default_factory=_build_plan)
    # Si la sesión anterior terminó en "confirmed", la siguiente arranca con
    # esto en False para que no pueda tocar humano dos veces seguidas (lo
    # maneja main.py entre conexiones).
    allow_confirm: bool = True
    step: int = field(default=1, init=False)
    _pressure_index: int = field(default=0, init=False, repr=False)
    _last_suspicion_line: Optional[str] = field(default=None, init=False, repr=False)

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
        """Comentario random y específico del intento actual: cada paso
        (real, teatral o de rechazo) tiene su propio banco de frases.

        Nunca repite la frase anterior de inmediato (si el banco tiene más
        de una opción)."""
        spec = self.current_spec()
        bank = (
            _SUSPICION_CRITICAL
            if spec.kind == "reject" and self.step >= TOTAL_STEPS - 1
            else spec.suspicion_bank
        )
        choices = [line for line in bank if line != self._last_suspicion_line] or bank
        line = random.choice(choices)
        self._last_suspicion_line = line
        return line

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

    def submit_proximity(self, face_width: float, baseline_face_width: float) -> Optional[StepResult]:
        if self.current_spec().kind != "move_closer" or baseline_face_width <= 0:
            return None
        if face_width < baseline_face_width * (1 + PROXIMITY_INCREASE_RATIO):
            return None
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def submit_pitch(self, pitch_ratio: float, baseline_pitch_ratio: float) -> Optional[StepResult]:
        if self.current_spec().kind != "tilt_forward":
            return None
        if pitch_ratio < baseline_pitch_ratio + PITCH_FORWARD_INCREASE:
            return None
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def submit_look_up(self, pitch_ratio: float, baseline_pitch_ratio: float) -> Optional[StepResult]:
        if self.current_spec().kind != "look_up":
            return None
        if pitch_ratio > baseline_pitch_ratio - LOOK_UP_DECREASE:
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
        (1 en 5). Si allow_confirm es False (la sesión anterior ya dio
        humano), no hay sorteo posible esta vez. Si no pasa, rechaza y
        avanza — y si era el último de los TOTAL_STEPS, dispara el
        veredicto final.
        """
        self._pressure_index += 1
        passed = (
            self.allow_confirm
            and motion_score >= MOTION_PASS_THRESHOLD
            and random.random() < CONFIRM_PROBABILITY
        )
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
