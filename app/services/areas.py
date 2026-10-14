"""Informazioni delle aree future: nessuna autenticazione o attività clinica."""
from pydantic import BaseModel, ConfigDict


class AreaInfo(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    description: str


AREAS = {
    "paziente": AreaInfo(title="Accesso Paziente", description="I questionari saranno disponibili dopo l'attivazione del sistema di accesso sicuro."),
    "terapeuta": AreaInfo(title="Area Terapeuta", description="L'area professionale sarà disponibile dopo l'attivazione del sistema di accesso sicuro."),
    "ricercatore": AreaInfo(title="Accesso Ricercatore", description="L'area dedicata alla ricerca è prevista in una fase successiva."),
    "amministratore": AreaInfo(title="Accesso Amministratore", description="L'area di amministrazione è prevista in una fase successiva."),
}
