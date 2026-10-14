"""Pagine pubbliche. Il codice paziente non viene inviato né memorizzato."""
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.areas import AREAS

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")


@router.get("/", name="home")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@router.get("/paziente", name="patient_area")
def patient_area(request: Request):
    # HTMX migliora l'interazione senza trasmettere il campo codice.
    template = "partials/unavailable.html" if request.headers.get("HX-Request") == "true" else "area.html"
    return templates.TemplateResponse(request=request, name=template, context={"area": AREAS["paziente"]}, headers={"Vary": "HX-Request"})


@router.get("/terapeuta", name="therapist_area")
def therapist_area(request: Request):
    return area_page(request, "terapeuta")


@router.get("/ricercatore", name="researcher_area")
def researcher_area(request: Request):
    return area_page(request, "ricercatore")


@router.get("/amministratore", name="administrator_area")
def administrator_area(request: Request):
    return area_page(request, "amministratore")


def area_page(request: Request, key: str):
    return templates.TemplateResponse(request=request, name="area.html", context={"area": AREAS[key]})
