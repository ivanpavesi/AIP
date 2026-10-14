# Scuole di Psicoterapia Cognitiva — AIP

Prima versione Python dell’**Artificial Intelligence Platform**, limitata allo STEP 1.
La homepage funziona senza database, chiavi o credenziali di produzione.
Gli accessi paziente, terapeuta, ricercatore e amministratore mostrano pagine informative:
**non eseguono autenticazione e non raccolgono dati clinici**.

## Avvio locale, passo per passo

Occorre **Python 3.12**. Dal terminale, dentro il repository AIP:

```bash
python3.12 -m venv .venv
```

Attivare l’ambiente virtuale:

```bash
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: usare invece
# .venv\Scripts\Activate.ps1
```

Installare le versioni bloccate e avviare il sito:

```bash
python -m pip install --require-hashes -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Aprire <http://127.0.0.1:8000>. Per fermare il server: **Ctrl+C**.
Su Windows, se `python3.12` non è disponibile, il primo comando è `py -3.12 -m venv .venv`.
CSS e HTMX sono già inclusi: Node.js non serve per avviare la homepage.
Non occorre creare `.env` per vedere il sito.

In alternativa, con [uv](https://docs.astral.sh/uv/):

```bash
uv sync --frozen --extra dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Dove modificare il progetto

| Percorso | A cosa serve |
| --- | --- |
| `app/core/config.py` | Configurazione Pydantic da variabili d’ambiente |
| `app/db/` | Modelli SQLAlchemy, connessioni lazy e tipo di testo cifrato |
| `app/security/encryption.py` | Cifratura autenticata Fernet, senza chiave predefinita |
| `app/routes/pages.py` | Homepage e quattro percorsi predisposti |
| `app/services/areas.py` | Titoli e descrizioni delle aree future |
| `app/templates/` | Contenuti Jinja2; `home.html` contiene le due card |
| `app/static/css/source.css` | Stili Tailwind e colori |
| `migrations/` | Migrazione Alembic iniziale |
| `tests/` | Verifiche automatiche e integrazione PostgreSQL locale |

Il logo è un segnaposto dichiarato. Sostituirlo in `base.html` quando sarà disponibile
un file ufficiale utilizzabile, con un testo alternativo appropriato.

## Modificare l’aspetto della homepage

Per modificare template o CSS occorre Node.js 20 o successivo:

```bash
npm ci
npm run build:assets
```

`app.css` è il CSS compilato da Tailwind; `htmx.min.js` è una copia locale della
libreria. Entrambi sono tracciati in Git e funzionano senza CDN, font remoti o analytics.
Dopo una modifica ai template che introduce nuove classi Tailwind, ricompilare il CSS.
`package-lock.json` blocca le dipendenze degli asset; `uv.lock` quelle Python.

## Database e cifratura: configurazione facoltativa nello STEP 1

La homepage e `/health` non aprono connessioni al database. Per lavorare sui modelli,
creare **un PostgreSQL locale vuoto** e copiare `.env.example` in `.env`.
Inserire in `.env`, mai in file tracciati:

- `AIP_DATABASE_URL`: URL con driver `postgresql+psycopg`, del proprio PostgreSQL locale.
- `AIP_ENCRYPTION_KEY`: chiave Fernet generata localmente.

Per generare una chiave da copiare nel file locale ignorato da Git:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Non condividere la chiave e conservarne una copia protetta: perderla rende i dati
illeggibili. Non rigenerarla dopo aver cifrato dati che si desidera conservare.
La cifratura non parte se la chiave manca o non è valida.

Applicare la migrazione **solo al proprio database locale**:

```bash
python -m alembic upgrade head
python -m alembic check
```

Compilare SQL senza collegarsi a un database:

```bash
python -m alembic upgrade head --sql
```

I dati identificativi sono nello schema `identity_data`; le cartelle nello schema
`clinical_data`, collegate mediante UUID pseudonimi. I campi sensibili vengono cifrati
prima della scrittura SQL. Non esistono route CRUD né account di esempio.
La migrazione revoca gli accessi impliciti a `PUBLIC` per schemi e tabelle AIP.
Il downgrade cancella tabelle e dati: usarlo esclusivamente su database sacrificabili.

## Test

Con uv, dopo `uv sync --frozen --extra dev`:

```bash
uv run pytest -q
```

Senza uv, installare anche gli strumenti di sviluppo con `python -m pip install -e '.[dev]'`,
poi eseguire `python -m pytest -q`.
Il test PostgreSQL viene saltato se `AIP_TEST_DATABASE_URL` non è impostata.
Per eseguirlo, usare **un database locale vuoto il cui nome termina in `_test`**:

```bash
# Esempio solo locale, senza password; adattare al proprio PostgreSQL di test.
export AIP_TEST_DATABASE_URL='postgresql+psycopg://localhost/aip_test'
uv run pytest -q
```

Il test rifiuta host remoti e database non vuoti. Crea/rimuove solo lo schema AIP,
verifica upgrade/downgrade, coerenza con i modelli, vincoli e cifratura a livello SQL.

Per la verifica browser, avviare prima il server locale e installare gli asset:

```bash
npm ci
uv run playwright install chromium
uv run python scripts/verify_homepage.py
# Con Chromium già installato su Linux:
# uv run python scripts/verify_homepage.py --chromium /usr/bin/chromium
```

Lo script salva schermate e report in `artifacts/`, esclusa da Git.
Controlla WCAG con axe-core, layout a 1440/390/320 px, ordine Tab, collegamenti,
HTMX e fallback senza JavaScript. Il codice nel campo paziente non è trasmesso.
I test automatici non equivalgono a una certificazione completa di accessibilità;
prima dell’uso pubblico servirà anche una verifica con tecnologie assistive.

## Hosting futuro (nessuna pubblicazione eseguita)

Per un servizio compatibile con Python 3.12:

- Installazione: `python -m pip install --require-hashes -r requirements.txt`.
- Avvio: `uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --no-access-log`.
- Endpoint liveness: `/health` (verifica l’app, non la disponibilità del database).
- Impostare `AIP_ENVIRONMENT=production` e `AIP_ALLOWED_HOSTS` con una lista JSON
  degli host effettivi. Terminare HTTPS sul servizio di hosting.
- Fornire chiave e URL attraverso il gestore di segreti del servizio, senza commetterli.
- Eseguire Alembic come operazione separata e verificata, mai all’avvio di ogni worker.

È incluso anche un `Dockerfile` con utente non privilegiato e asset già compilati;
non è stato costruito né pubblicato un container in questo STEP.
Per Supabase, usare in futuro una connessione PostgreSQL con TLS e un ruolo dedicato;
le migrazioni richiederanno un ruolo distinto con i permessi DDL necessari.
Non sono state richieste credenziali Supabase o effettuate connessioni di produzione.

## Confini della versione

Non sono implementati autenticazione, autorizzazione per ruolo, questionari, gestione
clinica, ricerca, amministrazione o funzionalità AI. L’UUID del paziente è un riferimento,
non una credenziale; non esistono PIN utilizzabili per accedere.
Il campo codice è dimostrativo, senza form o nome trasmesso. Il relativo collegamento
mostra solo un avviso, anche senza JavaScript.
La separazione degli schemi non è anonimizzazione e non sostituisce permessi applicativi,
ruoli database e politiche di accesso. La gestione e rotazione delle chiavi, RLS/permessi
per Supabase, audit, backup e conservazione saranno progettati prima dell’uso clinico.
Le connessioni hanno i parametri SQL nascosti nei log; la cifratura Fernet protegge
il contenuto ma rende visibili la lunghezza approssimativa e il timestamp del token.

Vedere [verifiche effettivamente eseguite](docs/verification.md).
**Lo sviluppo si ferma allo STEP 1.**
