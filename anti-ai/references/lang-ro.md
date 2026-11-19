# Anexa RO - registru vorbit

Regula universală (regula 2 din anti-ai-prompt.md): propoziția scrisă trebuie să sune
ca una rostită. O spui cu voce tare, unui prieten, în bucătărie; dacă sună ca un
comunicat de presă, o rescrii. Probează fiecare verb: l-ai folosi vorbind? Nu ->
înlocuiește-l. Latinismul e semnalul clasic al draftului de model în română.

## Cuvinte umflate -> echivalent vorbit

| Scris de comunicat | Vorbit |
|---|---|
| "în vederea" | pentru |
| "în momentul de față" | acum |
| "în consecință" | de aceea |
| "a furniza" | a da |
| "a efectua" | a face |
| "a utiliza" | a folosi |
| "a implementa" | a pune în aplicare |
| "a finaliza" | a termina |
| "a solicita" | a cere |
| "a achiziționa" | a cumpăra |
| "a beneficia de" | a avea |
| "posibilitatea de a X" | poate X |
| "ulterior" | apoi |

Toate sunt în patterns.json (categoria complex, lang ro), așa că check_tells.py le prinde.

## Prost -> bine

- Prost: "În vederea finalizării implementării soluției, echipa va efectua o analiză."
  Bine: "Ca să terminăm, echipa se uită întâi la numere."
- Prost: "Clienții beneficiază de posibilitatea de a opta pentru livrare gratuită."
  Bine: "Livrarea e gratuită dacă comanzi până vineri."
- Prost: "Este important de menționat că termenul s-a schimbat."
  Bine: "Termenul s-a schimbat."

## Ritm: cum recalibrezi numerele

Numerele din house-style.md (nucleu de 12-22 de cuvinte, media de litere sub 4.8,
cuvinte lungi sub 12%) sunt calibrate pe text englezesc. Nucleul propoziției se
transferă și în română. Lungimea cuvântului nu se transferă: sufixele românești merg
natural mai lung și nu e nicio vină de stil acolo.

Rețeta de măsurare: ia 2.000+ de cuvinte dintr-o proză de-a ta care îți place. Numără
media de litere pe cuvânt și proporția cuvintelor de 10+ litere. Pune numerele tale
în locul celor din house-style.md și ține-le pe ale tale de-acum încolo.

Zero em-dash rămâne universal, în orice limbă.
