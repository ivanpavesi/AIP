# Verifiche dello STEP 1

Eseguite il **14 ottobre 2026** nel repository AIP, con Python **3.12.14**.
Nessun database di produzione, nessun dato reale, nessuna pubblicazione o servizio a pagamento.

## Dipendenze e avvio

- Installazione Python con `uv lock` e `uv sync --extra dev`; lockfile conservato.
- Installazione asset con `npm ci`; compilazione con `npm run build:assets`.
- Avvio reale Uvicorn su `127.0.0.1:8000`, senza database né chiave.
- Compilazione Python con `python -m compileall -q app migrations scripts tests`.
- Controllo dei diff con `git diff --check`.

## Pytest: 25 test passati

L’ultima esecuzione completa ha restituito **25 passed**, senza warning.
Il database PostgreSQL **16.2** è stato avviato localmente con `pgserver 0.1.4`,
un’utility installata solo per la verifica e non inclusa nelle dipendenze dell’app.
È stato creato un database vuoto `aip_test`, eliminato dopo i test; server poi fermato.
Le chiavi dei test sono generate in memoria e i contenuti sono dichiaratamente sintetici.

Sono stati verificati:

- Configurazione senza credenziali, URL PostgreSQL, mascheramento dei segreti e host consentiti.
- Cifratura/decifratura Unicode, token diversi per lo stesso contenuto, chiave mancante/errata,
  token alterati e conversione automatica del tipo SQLAlchemy.
- Homepage, asset locali, quattro aree informative, rifiuto dei POST e risposta parziale HTMX.
- Header CSP e sicurezza, liveness senza database, assenza di API di autenticazione.
- Migrazione PostgreSQL offline, separazione degli schemi e cifratura dei campi sensibili.
- Upgrade e downgrade su PostgreSQL reale locale; `alembic check` senza differenze rispetto
  ai modelli; roundtrip ORM; lettura SQL grezza con contenuto cifrato; vincoli sui ruoli
  e protezione referenziale delle cartelle.

L’esecuzione senza `AIP_TEST_DATABASE_URL` restituisce **24 passed, 1 skipped**:
la verifica PostgreSQL è stata comunque eseguita separatamente e ha superato il controllo.

## Chromium, Playwright e axe-core

Comando: `python scripts/verify_homepage.py --chromium /usr/bin/chromium`.

| Larghezza | Layout | Violazioni axe WCAG rilevate | Overflow orizzontale |
| --- | --- | --- | --- |
| 1440 px | Desktop, due card affiancate | 0 | Assente |
| 390 px | Mobile, card impilate | 0 | Assente |
| 320 px | Reflow, card impilate | 0 | Assente |

Controllati anche ordine Tab, collegamenti alle quattro aree, avviso HTMX nel contenitore
`role=status`, assenza di trasmissione del valore digitato, fallback senza JavaScript,
assenza di cookie e di errori JavaScript. I collegamenti hanno un focus visibile;
le azioni principali e i collegamenti del footer hanno un’altezza di almeno 44 px.
Il bordo del campo usa un colore con contrasto superiore a 3:1 sul bianco.
La homepage usa asset locali, testo etichettato, landmark semantici e skip link.

Le schermate desktop/mobile e `browser-report.json` sono in `artifacts/`, ignorata da Git.
Sono state anche ispezionate visivamente le schermate desktop e mobile.
Axe è eseguito tramite DevTools per il test, senza indebolire la CSP della pagina.
I controlli automatici non costituiscono una certificazione WCAG: non sono stati eseguiti
un audit completo con screen reader, test su Safari/Firefox o una valutazione con utenti.

## Limiti noti e attività successive

- Logo ufficiale da fornire; segnaposto esplicito già predisposto.
- Accessi e funzioni cliniche intenzionalmente non operativi.
- Dockerfile preparato ma container non costruito o avviato.
- Nessuna verifica Supabase o hosting remoto, nessuna connessione di produzione.
- Workflow GitHub avviato sulla [PR #1](https://github.com/ivanpavesi/AIP/pull/1).
  Il blocco iniziale di autorizzazione è stato risolto dal committente; il commit
  `3c9d0ab` è conservato sul branch remoto. Corrette le virgolette del comando
  di health check del servizio PostgreSQL, richieste dal runner GitHub Actions.
  L’esito aggiornato del workflow è consultabile nella PR.
- Gestione dei permessi clinici, autenticazione, audit e ciclo di vita delle chiavi richiedono
  le fasi successive. Nessuna di queste funzionalità è stata avviata.

## Revisione della homepage su richiesta del committente

Rimosse dalla homepage le indicazioni sullo stato di sviluppo, lo slogan e l’avviso
sul campo codice. Titolo centrato senza interruzioni su desktop; sottotitolo
“Artificial Intelligence Platform” e sigla “AIP” su righe distinte. Card e footer
ridisposti secondo il riferimento visivo. Su schermi piccoli il titolo può andare
a capo per mantenere leggibilità e assenza di overflow.

Gli accessi continuano a non eseguire autenticazione: dopo un clic appare soltanto
un messaggio neutro “Accesso non disponibile.”, senza riferimenti a fasi future.
Non sono state aggiunte dichiarazioni su 2FA o funzioni cliniche inesistenti.

Verifiche della revisione: **24 test passati, 1 test PostgreSQL saltato** perché il
database locale non era configurato per questa esecuzione. Il codice di database
non è stato modificato. Rieseguiti build degli asset e controllo browser completo:
zero violazioni axe a 1440/390/320 px, ordine Tab, HTMX, mancata trasmissione del
codice, collegamenti e fallback senza JavaScript verificati.
