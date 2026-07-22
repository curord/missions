👨‍👩‍👧 Família

Crear família. 

Crear fins a 5 fills. 

Crear perfils de pares. 

📚 Escola

Assignatura. 

Llibre. 

Tema. 

Pàgines. 

Exercicis. 

Data límit. 

Prioritat. 

🏠 Casa

Tasques recurrents. 

Tasques puntuals. 

Calendari. 

👦 El nen

Quan entra veu:

Avui tens:

Matemàtiques 

Anglès 

Fer el llit 

Posar el rentaplats 

Cada tasca té un botó "Completa".

Quan la marca:

Escriu què ha fet. 

Pàgina inicial. 

Pàgina final. 

Temps dedicat. 

Pot adjuntar una foto. 

👩 El pare

Rep una notificació.

Pot:

Aprovar. 

Rebutjar. 

Escriure comentaris. 

Donar punts. 

🪙 Recompenses

Els punts serveixen per comprar:

Escollir sopar. 

Cinema. 

Temps extra de consola. 

Dormir a casa d'un amic. 

Diners. 

Sortides. 

📈 Estadístiques

Dies seguits complint. 

Temps d'estudi. 

Assignatura més treballada. 

Tasques de casa. 

Percentatge de compliment. 

Tasques de casa

Fer llit. 

Aspirar. 

Posar rentadora. 

Estendre. 

Rentar plats. 

Doblegar roba. 

Treure escombraries. 

Recurrència:

Cada dia 

Dilluns 

Caps de setmana 

etc. 

Rutines

Matí

Rentar dents. 

Esmorzar. 

Preparar motxilla. 

Donar menjar al gos. 

Nit

Dutxa. 

Preparar roba. 

Llegir. 

Dormir abans de les 22:30. 

Hàbits

Llegir 20 minuts. 

Fer esport. 

Practicar anglès. 

Tocar guitarra. 

Meditar. 

Recompenses

Els punts es converteixen en monedes.

Botiga:

🍕 Escollir sopar → 120 monedes 

🎬 Cinema → 500 

🎮 1 hora consola → 180 

🍦 Gelat → 90 

🛍️ 15 € → 800 

Estadístiques

Cada fill veu:

Tasques completades. 

Tasques pendents. 

Dies seguits. 

Punts. 

Nivell. 

Insígnies. 

Els pares veuen també:

Temps dedicat als estudis. 

Assignatures treballades. 

Evolució setmanal. 

Repartiment de les tasques de casa. 

Tecnologies

Perquè sigui fàcil de mantenir i no dependre de ningú:

🐍 Python 3.13+ 

🌐 Flask 

💾 SQLite 

🎨 HTML + CSS 

⚡ JavaScript 

📦 Sense frameworks complicats 

Estructura del projecte

MISSIONS/

│

├── app.py                 # Punt d'entrada

├── config.py              # Configuració

├── database.py            # Connexió SQLite

├── init_db.py             # Crea la BD

├── requirements.txt

│

├── models/

│   ├── family.py

│   ├── user.py

│   ├── mission.py

│   ├── reward.py

│   ├── category.py

│

├── templates/

│   ├── login.html

│   ├── dashboard_parent.html

│   ├── dashboard_child.html

│

├── static/

│   ├── css/

│   ├── js/

│   ├── img/

│

├── uploads/

│

└── data/

    └── missions.db

Aquesta estructura és escalable i ens permetrà créixer sense haver de reorganitzar-ho tot.

La base de dades (primera versió)

Jo començaria amb només 8 taules.

1. families

Una família pot tenir diversos adults i diversos fills.

id

nom

data_creacio

2. users

id

family_id

nom

email

password

rol

avatar

punts

nivell

actiu

Rol

pare 

mare 

fill 

3. categories

id

nom

icona

color

ordre

Exemple:

Casa 

Escola 

Mascotes 

Piscina 

Hàbits 

Extraescolars 

4. missions

id

categoria_id

titol

descripcio

tipus

punts

xp

validacio

repeticio

activa

5. mission_assignments

Aquesta és molt important.

Una mateixa missió pot estar assignada a diferents fills.

id

mission_id

user_id

estat

comentari

data_limit

data_finalitzacio

6. rewards

id

nom

cost

imatge

activa

7. reward_history

id

user_id

reward_id

data

estat

8. settings

Configuració general.

tema

idioma

logo

nom_familia

El primer usuari

Quan instal·lis l'app, ja vindrà amb:

Família

Casa Roig

-------------

Laura

Administrador

-------------

Iris

Fill

-------------

Roc

Fill

Només hauràs de canviar les dades si vols.

Pantalla inicial

No vull una pantalla avorrida.

Vull una cosa així:

MISSIONS

Bon dia Laura ☀️

Avui tens:

📚 4 missions escolars

🏠 5 missions de casa

🐶 2 missions mascotes

🏊 1 piscina

⏳ 3 pendents de validar

------------------

Iris ⭐ 520

Roc ⭐ 480

La nostra metodologia

Cada fase tindrà aquest ordre:

📝 Dissenyem (sense programar). 

🗄️ Creem la base de dades. 

💻 Programem. 

🧪 Ho provem. 

✨ Ho millorem. 

No avançarem fins que l'anterior estigui bé.

Objectiu del MVP (versió 0.1)

Quan acabem la primera versió, tu ja podràs:

Crear una família. 

Tenir 2 fills. 

Crear missions. 

Assignar-les. 

Que els nens les completin. 

Validar-les. 

Donar punts. 

Bescanviar recompenses.

La idea

Una app perquè els pares puguin gestionar:

🏠 Tasques de casa. 

📚 Deures escolars. 

🎯 Hàbits. 

📅 Rutines. 

💰 Recompenses. 

📈 Evolució. 

I que els nens només vegin el que els toca fer.

Perfils

👨‍👩‍👧 Pare/Mare

Pot:

Crear tasques. 

Crear deures. 

Assignar-los a un fill. 

Aprovar o rebutjar tasques. 

Donar punts. 

Crear recompenses. 

Veure estadístiques. 

👦 Fill

Pot:

Veure les tasques del dia. 

Marcar-les com iniciades. 

Escriure què ha fet. 

Posar: 

pàgina inicial 

pàgina final 

exercicis fets 

Adjuntar una foto. 

Demanar revisió. 

Jo afegiria un camp nou a les missions:

Tipus de missió

Com funciona

Individual

Un únic nen la fa.

Compartida

Qualsevol dels assignats la pot completar; el primer s'endú els punts.

Col·laborativa

Tots els assignats han de completar la seva part.

Rotativa

Es va alternant automàticament entre els assignats.

Lliure

Qualsevol membre de la família la pot fer.

1. Obre Git CMD

Veuràs una finestra negra.

2. Ves a la carpeta del projecte

Si el teu projecte és a D:\missions, escriu:

cd /d D:\missions

Després comprova que hi ets:

dir

Hauries de veure fitxers com:

app.py 

README.md 

requirements.txt 

carpetes templates, static, ... 

Si no els veus, para i m'ho dius.

3. Inicialitza Git

Només la primera vegada:

git init

4. Afegeix tots els fitxers

git add .

5. Fes el primer commit

git commit -m "v0.0.1 - Projecte inicial"

Si surt un error com aquest:

Please tell me who you are...

És normal. Només cal configurar Git una vegada:

git config --global user.name "El teu nom"

git config --global user.email "el_teu_correu@example.com"

Després repeteixes:

git commit -m "v0.0.1 - Projecte inicial"

💡 A partir d'aquí, cada vegada que acabem una funcionalitat només hauràs de fer:

git add .

git commit -m "Missatge"

git push

dependencies projecte

pip install -r requirements.txt

executa githup i conecta

github cmd

d:

cd /d D:\sistemes\missions

git init

git add .

git commit -m "Missatge"

git push

executar app:

accedir cmd de la carpeta on esta app.py

python -m pip install flask

python app.py

navegador : 

http://127.0.0.1:5000/

antigravity

"Read docs/ANTIGRAVITY_CONTEXT.md before doing anything."

Llegeix docs/ANTIGRAVITY_CONTEXT.md abans de fer res.

Segueix totes les normes definides en aquest document.

No incompleixis cap restricció del projecte.

Espera l'aprovació abans de començar la implementació.

…aquí el q ha de fer spring xxxx……….

Per cada Sprint:

1. Crear una branca

git checkout architecture-v2

git pull

git checkout -b sprint-21

2. Desenvolupar

Antigravity treballa sobre sprint-21.

3. Quan acabis

git add .

git commit -m "Sprint 21 - Sistema de recompenses pendents"

git push -u origin sprint-21

4. Validar

Passar el teu checklist. 

Fer proves manuals. 

Executar pytest si hi ha tests. 

5. Fusionar

Quan estiguis satisfet:

git checkout architecture-v2

git merge sprint-21

git push

I després pots eliminar la branca si ja no la necessites:

git branch -d sprint-21

git push origin --delete sprint-21

tasques pendents:

admin/missions : m.sort_order, peta en el con.excecute. ( si esta bd)

21/07/2026 pendent :

M'agrada molt la direcció que està agafant el projecte. Jo ho convertiria en una Roadmap v3, amb sprints petits (1-3 hores de feina cadascun) perquè Antigravity no intenti fer massa coses de cop.

🎯 Sprint 5.1 - Configuració familiar

Objectiu:

Crear un nou apartat "Configuració familiar" dins del panell d'administració.

Primers paràmetres:

- Autoaprovar missions dels administradors (Sí/No)

- Les recompenses requereixen lliurament (Sí/No)

- Comptar caps de setmana a les ratxes (Sí/No)

Requisits:

- Crear la pantalla de configuració.

- Desar els valors a la base de dades.

- Llegir la configuració des dels Services.

- No utilitzar valors hardcoded.

Restriccions:

- No modificar altres funcionalitats.

- Utilitzar arquitectura Repository + Service.

Al final:

- Explica el model utilitzat.

- Mostra els fitxers modificats.

🎯 Sprint 5.2 - Autoaprovació d'administradors

Objectiu:

Implementar el comportament configurable de les missions assignades als administradors.

Funcionament:

Si "Autoaprovar administradors" està activat:

Administrador

↓

Completa missió

↓

Aprovada automàticament

Si està desactivat:

Administrador

↓

Completa

↓

Pendent de validació

↓

Un altre administrador la valida.

Requisits:

- Utilitzar la configuració familiar.

- No duplicar codi.

- Actualitzar XP, monedes i historial correctament.

Al final:

- Explica el flux implementat.

🎯 Sprint 5.3 - Recompenses pendents de lliurament

Objectiu:

Crear el sistema de lliurament físic de recompenses.

Flux:

Nen

↓

Compra recompensa

↓

Pendent de lliurament

↓

Administrador

↓

Marca com "Lliurada"

↓

Historial

Requisits:

- Crear un nou apartat "Recompenses pendents".

- Mostrar:

    - Nen

    - Recompensa

    - Data

    - Estat

- Botó "Marcar com lliurada".

No eliminar l'historial.

Explica els fitxers modificats.

🎯 Sprint 5.4 - Centre de notificacions

Objectiu:

Crear un centre de notificacions per als administradors.

Mostrar notificacions quan:

- Un nen completa una missió.

- Es compra una recompensa.

- Una missió és rebutjada.

- Una recompensa està pendent de lliurar.

Mostrar un badge amb el nombre de notificacions pendents.

No implementar notificacions push.

Només dins de l'aplicació.

🎯 Sprint 5.5 - Ratxes intel·ligents

Objectiu:

Millorar el càlcul de les ratxes.

Requisits:

No trencar una ratxa si aquell dia no existia cap missió obligatòria.

Respectar la configuració familiar:

- Comptar caps de setmana.

- Ignorar caps de setmana.

Crear una funció calculate_streak() totalment reutilitzable.

Explicar l'algoritme.

🎯 Sprint 5.6 - Historial complet

Objectiu:

Crear una línia temporal completa de totes les activitats.

Registrar:

✔ Missió aprovada

❌ Missió rebutjada

🚫 Missió cancel·lada

🎁 Recompensa reclamada

📦 Recompensa lliurada

⭐ Pujada de nivell

💰 Monedes guanyades

Cada registre ha de mostrar:

- Data

- Usuari

- Estat

- Comentaris

No eliminar informació.

🎯 Sprint 5.7 - Comentaris del pare

Objectiu:

Permetre als administradors escriure un comentari quan aproven o rebutgen una missió.

Si és rebutjada:

El nen ha de veure:

⚠️ Revisió no superada

Comentari:

"La fotografia està borrosa."

Botó:

[Tornar a completar]

Guardar els comentaris a la base de dades.

Mostrar-los també a l'historial.

🎯 Sprint 5.8 - Evidències

Objectiu:

Permetre adjuntar evidències quan es completa una missió.

Tipus:

- Fotografia

- Vídeo

- Àudio

- Text

Cada missió podrà definir quin tipus d'evidència necessita.

Els administradors podran veure l'evidència durant la validació.

No modificar les missions existents.

🎯 Sprint 5.9 - Calendari

Objectiu:

Crear una vista calendari de les missions.

Mostrar:

- Missions programades.

- Missions completades.

- Missions pendents.

- Missions rebutjades.

Utilitzar un calendari responsive.

No modificar la lògica de les missions.

🎯 Sprint 6.0 - Missions recurrents

Objectiu:

Permetre crear missions recurrents.

Opcions:

- Cada dia

- Dilluns-divendres

- Caps de setmana

- Dies personalitzats

La generació de missions ha de ser automàtica.

No duplicar codi.

🎯 Sprint 6.1 - Estadístiques

Objectiu:

Crear un dashboard d'estadístiques.

Mostrar:

- Missions completades.

- Percentatge d'èxit.

- XP guanyada.

- Monedes guanyades.

- Ratxa més llarga.

- Recompenses reclamades.

Permetre filtrar:

- Aquesta setmana

- Aquest mes

- Aquest any

🎯 Sprint 6.2 - IA per generar missions

Objectiu:

Preparar la infraestructura perquè una IA pugui generar missions.

Crear un MissionGeneratorService.

Inicialment:

Només definir la interfície.

No connectar encara cap model d'IA.

Exemple:

generate_missions(age, interests, objectives)

La implementació real es farà en futurs Sprints.

⭐ Un Sprint que jo afegiria i considero dels més importants

🎯 Sprint 5.0 - Sistema d'auditoria (abans de continuar desenvolupant)

Objectiu:

Implementar un sistema complet d'auditoria de totes les accions importants de l'aplicació.

Registrar:

- Login

- Logout

- Crear missió

- Editar missió

- Eliminar missió

- Completar missió

- Aprovar

- Rebutjar

- Comprar recompensa

- Lliurar recompensa

- Canvis de configuració

Cada registre ha de guardar:

- Data i hora

- Usuari

- Acció

- Entitat afectada

- Identificador

- Valor anterior (si existeix)

- Valor nou (si existeix)

Crear una pantalla d'administració per consultar aquest registre amb filtres per data, usuari i tipus d'acció.

No modificar el funcionament actual de l'aplicació; només registrar les accions.

👉 Aquest sprint sembla poc "visible", però és el que després et permetrà saber qui ha fet què i quan, facilitarà la depuració de problemes i serà molt útil quan la família o el nombre d'usuaris creixi. És una característica molt pròpia d'aplicacions professionals.

. Futur (molt interessant)

Aquestes funcionalitats les deixaria preparades:

⭐ Bonus per ratxa (7 dies seguits) 

🔥 Multiplicador de caps de setmana 

🎯 Bonus si es completa abans d'una hora 

💥 Penalització si caduca 

🎁 Recompensa sorpresa 

🔊 So en completar 

🎉 Animació

Fase 8

Aplicación móvil

Fase 9

Publicación

Aquí sí:

Docker 

PostgreSQL 

Gunicorn 

Nginx 

Cloud