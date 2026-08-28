"""Máquina de estados de la escalada de pedidos del verificador.

No sabe nada de mediapipe ni de WebSockets: recibe señales ya interpretadas
(cantidad de parpadeos, yaw) y devuelve qué mostrar a continuación.
"""

import random
from dataclasses import dataclass, field
from typing import Optional

_INSTRUCTIONS = {
    1: "Parpadeá dos veces",
    2: "Girá la cabeza a la izquierda",
    3: "Sonreí de forma natural",
    4: "Sonreí de forma natural",
    5: "Mostrá una emoción que no hayas ensayado",
}

_SMILE_REJECTIONS = [
    "Sonrisa detectada como no espontánea. Reintentá.",
    "Patrón facial demasiado uniforme. Reintentá.",
    "La sonrisa no coincide con el perfil de autenticidad esperado. Reintentá.",
]

_FINAL_REJECTIONS = [
    "Emoción clasificada como ensayada. Reintentá.",
    "No se detectó espontaneidad suficiente. Reintentá.",
    "El gesto coincide con patrones previamente registrados. Reintentá.",
    "Autenticidad emocional insuficiente. Reintentá.",
    "La expresión no supera el umbral de humanidad requerido. Reintentá.",
]

REVEAL_TEXT = (
    "El algoritmo detectó patrones biológicos irregulares. "
    "No podemos verificar tu humanidad en este momento. "
    "El acceso a los sistemas centrales queda restringido, pendiente de revisión. "
    "Nunca hubo un test que pudieras pasar."
)

BLINK_TARGET = 2
YAW_TURN_THRESHOLD = 0.18
MAX_FINAL_REJECTIONS = 5


@dataclass
class StepResult:
    kind: str  # "instruction" | "result" | "reveal"
    step: Optional[int] = None
    text: Optional[str] = None
    passed: Optional[bool] = None
    message: Optional[str] = None


@dataclass
class ChallengeSession:
    step: int = 1
    _final_rejections: int = field(default=0, init=False, repr=False)

    def instruction(self) -> StepResult:
        return StepResult(kind="instruction", step=self.step, text=_INSTRUCTIONS[self.step])

    def submit_blink_count(self, blink_count: int) -> Optional[StepResult]:
        if self.step != 1 or blink_count < BLINK_TARGET:
            return None
        self.step = 2
        return StepResult(kind="result", step=1, passed=True, message="Verificado.")

    def submit_yaw(self, yaw: float) -> Optional[StepResult]:
        if self.step != 2 or yaw <= YAW_TURN_THRESHOLD:
            return None
        self.step = 3
        return StepResult(kind="result", step=2, passed=True, message="Verificado.")

    def reject_smile(self) -> StepResult:
        """Los pasos 3 y 4 siempre fallan, sin importar el gesto real."""
        current_step = self.step
        message = random.choice(_SMILE_REJECTIONS)
        self.step += 1
        return StepResult(kind="result", step=current_step, passed=False, message=message)

    def reject_final(self) -> StepResult:
        """El paso 5 falla siempre hasta llegar al reveal de la moraleja."""
        self._final_rejections += 1
        if self._final_rejections >= MAX_FINAL_REJECTIONS:
            return StepResult(kind="reveal", text=REVEAL_TEXT)
        message = random.choice(_FINAL_REJECTIONS)
        return StepResult(kind="result", step=self.step, passed=False, message=message)
