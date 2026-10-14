Lo STEP 1 introduce la homepage istituzionale di AIP e la struttura Python 3.12 con FastAPI, SQLAlchemy 2, Alembic e PostgreSQL. La homepage funziona senza credenziali, database o chiavi configurate; i quattro percorsi di accesso mostrano esplicitamente che le aree non sono ancora operative.

## Modifiche

- Homepage Jinja2 responsive, palette richiesta, spazio per il logo ufficiale, card paziente/terapeuta e collegamenti ricerca/amministrazione.
- Tailwind compilato e HTMX serviti localmente; il campo codice paziente non viene inviato né memorizzato. Fallback informativo anche senza JavaScript.
- Moduli distinti per configurazione Pydantic, database, sicurezza, route, servizi, template e test.
- Modelli utenti, identità pazienti e cartelle cliniche; identità e dati clinici in schemi PostgreSQL distinti, con riferimenti UUID pseudonimi.
- Tipo SQLAlchemy per cifratura autenticata Fernet dei campi sensibili, con chiave esterna e nessun valore predefinito.
- Migrazione Alembic iniziale, connessioni lazy, parametri SQL nascosti nei log e header di sicurezza.
- Dipendenze bloccate, guida italiana per l’avvio, Dockerfile per hosting futuro e workflow di test su PostgreSQL effimero.

## Validazione eseguita

- **25 test Pytest passati**, inclusa integrazione con PostgreSQL 16.2 locale: upgrade/downgrade, coerenza dei modelli, cifratura effettiva nel database e vincoli.
- Avvio reale Uvicorn senza database/chiave; compilazione asset Tailwind/HTMX.
- Chromium + Playwright + axe-core: **0 violazioni rilevate** alle larghezze di 1440, 390 e 320 px; nessun overflow orizzontale.
- Ordine Tab, collegamenti, avviso HTMX, mancata trasmissione del codice, assenza di cookie/errori JavaScript e funzionamento senza JavaScript verificati.
- Ispezione visiva desktop/mobile, compilazione Python e controllo dei diff.

Dettagli riproducibili in `README.md`, `scripts/verify_homepage.py` e `docs/verification.md`.

## Confini e limiti

Il logo ufficiale resta da fornire. Autenticazione, autorizzazione, funzioni cliniche e AI sono fuori scope; non sono simulati accessi, account o PIN funzionanti. Nessun dato reale o database di produzione è stato usato; nessun sito è stato pubblicato. Il Dockerfile non è stato costruito e l’accessibilità non è stata certificata con un audit completo. Le fasi successive richiedono approvazione del committente.
