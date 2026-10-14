"""Informazioni delle aree future: nessuna autenticazione o attività clinica."""
from pydantic import BaseModel, ConfigDict


class AreaInfo(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    description: str


AREAS = {
    "paziente": AreaInfo(title="Accesso Paziente", description="Accesso ai questionari."),
    "terapeuta": AreaInfo(title="Area Terapeuta", description="Area riservata ai professionisti."),
    "ricercatore": AreaInfo(title="Accesso Ricercatore", description="Area riservata alla ricerca."),
    "amministratore": AreaInfo(title="Accesso Amministratore", description="Area riservata all’amministrazione."),
}
