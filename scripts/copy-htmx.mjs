// HTMX è servito localmente: nessuna dipendenza da CDN nella homepage.
import { copyFileSync } from 'node:fs';
copyFileSync('node_modules/htmx.org/dist/htmx.min.js', 'app/static/js/htmx.min.js');
