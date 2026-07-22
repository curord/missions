CONTEXT DEL PROJECTE ANTIGRAVITY
Projecte

Nom: Missions

Aquesta és una aplicació EXISTENT.

NO és un projecte nou.

L'objectiu és fer evolucionar l'aplicació existent sense reescriure-la.

Tecnologia
Python 3
Flask
SQLite
Jinja2
HTML
CSS
JavaScript Vanilla

No React.

No Angular.

No Vue.

No TypeScript.

No Node.js.

No npm.

Arquitectura

L'arquitectura actual segueix una migració incremental cap a l'Arquitectura v2.

Presentació

↓

Rutes (Blueprints)

↓

Serveis

↓

Repositoris

↓

Base de dades (SQLite)

↓

Models de domini

Tota funcionalitat nova ha de respectar aquesta arquitectura.

Carpetes existents
app.py
config.py
database.py
routes/
templates/
static/
models/
repositories/
services/
tests/
docs/

No creïs mai una altra aplicació.

No creïs mai un altre projecte.

No creïs mai projectes de prova ("scratch projects").

Filosofia de desenvolupament

Migració incremental.

Compatibilitat amb versions anteriors.

Canvis petits.

Un Sprint cada vegada.

No reescriguis mai tota l'aplicació.

No canviïs mai les tecnologies.

Abans d'implementar

Analitza sempre el codi existent.

Reutilitza el codi existent sempre que sigui possible.

Només crea fitxers nous si és estrictament necessari.

Explica quins fitxers es modificaran.

No inventis mai fitxers que no pertanyin a aquest projecte.

Patró Repository

Els repositoris accedeixen a SQLite.

Els serveis contenen la lògica de negoci.

Les rutes només processen les peticions HTTP.

Les plantilles només renderitzen les dades.

No posis SQL dins de les rutes.

No posis lògica de negoci dins de les plantilles.

Interfície d'usuari (UI)

Responsiva.

Mobile First.

Compatible amb Bootstrap.

Targetes (Cards) en dispositius mòbils.

Taules en ordinadors d'escriptori.

Evita el desplaçament horitzontal.

Dissenys compactes.

Estil del codi

Funcions petites.

Noms descriptius i llegibles.

Sense codi duplicat.

Sense números màgics.

Sense configuració codificada ("hardcoded").

La configuració ha de provenir de Config o de la base de dades.

Flux de treball dels Sprints

Cada Sprint ha de seguir aquesta seqüència:

Anàlisi
Pla d'implementació
Esperar l'aprovació
Implementació
Verificació
Explicar els fitxers modificats
Proposar proves manuals

No ometis mai el pas d'aprovació.

Flux de treball amb Git

Una branca per Sprint.

Fes commits amb freqüència.

No modifiquis fitxers que no estiguin relacionats amb el Sprint.

Allò que no ha de passar mai

NO creïs:

Projectes Node.js
Aplicacions React
Projectes TypeScript
Aplicacions de prova ("scratch applications")
Demostracions externes
Aplicacions temporals
Arquitectures alternatives

No substitueixis Flask.

No substitueixis SQLite.

No reescriguis l'aplicació.

Limita't a millorar el projecte actual.

Format de la resposta

Proporciona sempre:

Resum
Fitxers modificats
Motiu de cada modificació
Passos de verificació
Possibles riscos