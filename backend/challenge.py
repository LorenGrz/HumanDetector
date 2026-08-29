"""Máquina de estados de la escalada de pedidos del verificador.

No sabe nada de mediapipe ni de WebSockets: recibe señales ya interpretadas
(cantidad de parpadeos, yaw) y devuelve qué mostrar a continuación. Cada
sesión sortea su propio plan de pasos: qué gesto real pedir primero, en qué
paso empieza a mentir, y qué acusación final le toca.
"""

import random
from dataclasses import dataclass, field
from typing import Literal, Optional

StepKind = Literal["blink", "yaw_left", "yaw_right", "auto_pass", "reject"]

TOTAL_STEPS = 5
MAX_FINAL_REJECTIONS = 5
YAW_TURN_THRESHOLD = 0.18

_REAL_INSTRUCTIONS = {
    "blink": "Parpadeá dos veces",
    "yaw_left": "Girá la cabeza a la izquierda",
    "yaw_right": "Girá la cabeza a la derecha",
}

_AUTO_PASS_BANK = [
    "Mantené la mirada fija en el centro de la cámara",
    "Acercate un paso a la cámara, despacio",
    "Inclina la cabeza levemente hacia adelante",
    "Quedate quieto durante el escaneo",
    "Mirá hacia arriba y contá hasta tres en silencio",
]

# Ordenado de más fácil a más imposible: cada rechazo avanza un lugar en
# esta lista, así la dificultad sube de forma continua en vez de random.
_REJECT_DIFFICULTY_BANK = [
    "Sonreí de forma natural",
    "Mostrá sorpresa genuina",
    "Fruncí el ceño con autenticidad",
    "Parpadeá de forma asimétrica",
    "Mové solo la ceja izquierda",
    "Mirá a la cámara sin parpadear durante diez segundos",
    "Generá una expresión que no hayas ensayado nunca",
    "Demostrá una emoción irrepetible",
    "Sincronizá tu expresión con un recuerdo que no tenés",
    "Mostrá una emoción que la especie humana todavía no descubrió",
]

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
]

_MORALEJA = (
    "Nunca hubo un test que pudieras pasar. El acceso a los sistemas centrales "
    "queda restringido, pendiente de una revisión que nunca va a llegar."
)


@dataclass
class StepResult:
    kind: str  # "instruction" | "result" | "reveal"
    step: Optional[int] = None
    text: Optional[str] = None
    passed: Optional[bool] = None
    message: Optional[str] = None


@dataclass
class StepSpec:
    kind: StepKind
    text: str


def _build_plan() -> list[StepSpec]:
    turn_kind: StepKind = random.choice(["yaw_left", "yaw_right"])
    real_kinds: list[StepKind] = ["blink", turn_kind]
    random.shuffle(real_kinds)

    # Mínimo 4 pasos antes de empezar a rechazar: que no se sienta forzado
    # ni se note de entrada que el resultado ya está decidido.
    fail_start = random.choice([4, 5])

    plan = [StepSpec(kind=k, text=_REAL_INSTRUCTIONS[k]) for k in real_kinds]
    while len(plan) < fail_start - 1:
        plan.append(StepSpec(kind="auto_pass", text=random.choice(_AUTO_PASS_BANK)))
    while len(plan) < TOTAL_STEPS:
        plan.append(StepSpec(kind="reject", text=""))  # texto real: ver _reject_text()

    return plan[:TOTAL_STEPS]


@dataclass
class ChallengeSession:
    plan: list[StepSpec] = field(default_factory=_build_plan)
    step: int = field(default=1, init=False)
    _final_rejections: int = field(default=0, init=False, repr=False)
    _reject_index: int = field(default=0, init=False, repr=False)

    def current_spec(self) -> StepSpec:
        return self.plan[self.step - 1]

    def _reject_text(self) -> str:
        index = min(self._reject_index, len(_REJECT_DIFFICULTY_BANK) - 1)
        return _REJECT_DIFFICULTY_BANK[index]

    def instruction(self) -> StepResult:
        spec = self.current_spec()
        text = self._reject_text() if spec.kind == "reject" else spec.text
        return StepResult(kind="instruction", step=self.step, text=text)

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

    def auto_pass(self) -> StepResult:
        """Pasos intermedios teatrales: siempre pasan, para sumar variedad."""
        result = StepResult(kind="result", step=self.step, passed=True, message="Verificado.")
        self.step += 1
        return result

    def reject(self) -> StepResult:
        """El último paso siempre rechaza, hasta acumular MAX_FINAL_REJECTIONS."""
        self._reject_index += 1

        if self.step < TOTAL_STEPS:
            message = random.choice(_REJECT_MESSAGES)
            result = StepResult(kind="result", step=self.step, passed=False, message=message)
            self.step += 1
            return result

        self._final_rejections += 1
        if self._final_rejections >= MAX_FINAL_REJECTIONS:
            accusation = random.choice(_ACCUSATIONS)
            return StepResult(
                kind="reveal",
                text=accusation["label"],
                message=f"{accusation['message']} {_MORALEJA}",
            )
        message = random.choice(_REJECT_MESSAGES)
        return StepResult(kind="result", step=self.step, passed=False, message=message)
