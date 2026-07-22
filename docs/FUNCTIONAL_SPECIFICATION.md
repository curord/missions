Missions App 

Especificació Funcional v1.0

1. Objectiu de l'aplicació

L'aplicació permet gestionar les tasques domèstiques d'una família mitjançant un sistema de missions, punts, monedes, recompenses i validacions.

L'objectiu és fomentar els bons hàbits, la responsabilitat i la col·laboració familiar.

No és un gestor de tasques convencional; és un sistema gamificat.

2. Tipus d'usuaris

👦 Gamer (Nen/Nena)

Pot:

Veure les seves missions. 

Completar missions. 

Consultar el seu historial. 

Comprar recompenses. 

Veure el seu nivell. 

Veure XP. 

Veure monedes. 

Veure la seva ratxa. 

No pot:

Crear missions. 

Validar missions. 

Modificar recompenses. 

Configurar la família. 

👨 Admin (mare, pare , tutor)

A més de tot l'anterior pot:

Crear missions. 

Editar missions. 

Assignar missions. 

Validar missions. 

Rebutjar missions. 

Crear recompenses. 

Lliurar recompenses. 

Gestionar membres. 

Configurar la família. 

Els administradors també poden tenir missions personals.

Validador Gamer

Les tasques dels administradors, les poden validar els validadors, q son els nens, avaluant progenitors/adults

3. Cicle de vida d'una missió

Estat 1

Esborrany

Només visible durant la creació.

Estat 2

Assignada

La missió apareix al Dashboard del membre.

Encara no dona:

XP 

Monedes 

Estat 3

En curs

Estat 4

Esperant validació

El membre l'ha completada.

Desapareix de "Pendents".

Apareix a:

Esperant validació (membre) 

Pendents de validar (administrador) 

Encara NO suma:

XP 

Monedes 

Estat 5

Aprovada

L'administrador valida.

En aquest moment:

✔ suma XP

✔ suma monedes

✔ recalcula nivell

✔ recalcula barra XP

✔ actualitza ratxa

✔ entra a l'historial

Estat 6

Rebutjada

L'administrador rebutja.

El sistema desa:

motiu 

data 

administrador 

El membre veu:

❌ Revisió no superada

Comentari

[Tornar a completar]

La missió torna a Pendents.

No crea una nova assignació.

Estat 7

Cancel·lada

Per administració.

Només apareix a l'historial.

4. Flux de validació

Administrador crea missió

↓

Assigna membres

↓

Els membres la veuen

↓

Completen

↓

Esperant validació

↓

Administrador

↓

Aprovar

↓

XP

Monedes

Historial

5. Tipus de missió

Individual

Només la veu el membre assignat.

Quan la completa:

Només desapareix del seu Dashboard.

Col·laborativa

Diversos membres tenen la mateixa missió.

Cada membre té el seu propi progrés.

Cada validació és independent.

Compartida

Una sola missió.

Quan un membre la completa:

Desapareix per a tots.

Només hi ha una validació.

6. Dashboard Gamer

Hauria de tenir únicament:

📋 Les meves missions

Pendents de fer.

⏳ Esperant validació

Ja completades.

Esperant aprovació.

❌ Revisió no superada

Rebutjades.

Amb comentari.

Botó:

"Tornar a completar"

🏆 Perfil

Nivell

XP

Monedes

Ratxa

Barra progrés

📜 Historial

Només missions finalitzades.

7. Dashboard Administrador

🔴 Validacions pendents

Missions esperant aprovació.

Botons:

✔ Aprovar

✖ Rebutjar

🎯 Les meves missions

Si també en té assignades.

🎁 Recompenses pendents

Pendents de lliurar.

⚙ Gestió

Missions

Recompenses

Família

Configuració