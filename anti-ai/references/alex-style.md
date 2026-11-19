# Stilul lui Alexandru Gris (Alex) - masurat de pe blog

Sursa: alexandrugris.ro (home, projects.html, from-the-edges, org-beneath-org) si
blog.alexandrugris.ro (postul Some Leadership Principles, 28 oct 2025).
Corpus 2 de calibrare (text uman asemanator, alt autor): profilul anonymizat e in
human-benchmarks.md; profilul cu surse rămâne privat.

## Masuratori

from-the-edges: 29 propozitii, medie 12.1 cuvinte, 0 em-dash, 2 aparitii de I, 5 colonuri.
projects.html: 8 propozitii, medie 22.0, 0 em-dash.
leadership principles: 24 propozitii, medie 28.5, 1 em-dash.
on-leadership-meditation.md (local): 466 linii, 0 bullet points, 1 header.
"curated-reading-recommendations.md": lista scrisa cu titlu ingrosat, linie Prioritate,
apoi un paragraf care spune DE CE. Asa arata lista lui.

## Reguli de casa

1. Daca e lista, e lista. Bullet points cu lead ingrosat. Nu trei propozitii paralele mascate in proza.
   (Alex, 19 nov 2026: If it is bullet points, make it bullet points, if not, write the idea.)
2. Daca nu e lista, scrie ideea. Propozitii pline, nu bullet points.
3. Fara moralitate la final. Textul se termina pe o imagine sau pe un fapt, nu pe o maxima.
4. Heading = propozitie declarativa cu punct final. Europe wrote the answer down two centuries ago.
5. Nucleu de 12-22 de cuvinte. Enumararile pot alerga lung (postul de leadership: medie 28.5), dar nu
   peste tot; clauzele din enumerate raman scurte. Zero em-dash. Colon ca pauza de apoteza.
6. Prima persoana, rar: the one I can point to, 2 ori in 29 de propozitii.
7. Substantiv concret, nu categorie: freedom has a flag.
8. Zero vorbire de model, zero hedge-uri in grup.
9. Fara "honest" despre propria vorbire. Interzis, exceptie: referinta la o persoana.
10. Verbele de greutate sunt interzise: "load-bearing", "carries weight" in orice forma
    ("carries the weight of", "carries enormous weight"), "anchors", "underpins",
    "grants", "fosters", "fuels", "earns its".

## Ce nu apare niciodata pe blog

lead-inuri de umpluturare, hedge-uri grupate, moralitati de inchidere, triade paralele
fara bullet, "a mere X", "it genuinely earns its complexity", em-dash ca semn de pauza.

Verificare: python3 check_tells.py fisier.txt (scannerul sta in rădăcina anti-ai/,
langă references/).

## Vocabular masurat - blogul complet (19 nov 2026)

Corpus: 90 de posturi blog.alexandrugris.ro (2008-2025), 55.700 cuvinte, extractie din
post-body. Textul extractat (feed-ul blogului, 55.700 cuvinte) nu e publicat; regenerabil oricând
din arhiva blog.alexandrugris.ro. Doua ere care nu se amesteca in profile: 2008-2013
(jurnal, 45.200 cuv) si 2014-2025 (eseuri, 10.400 cuv). Proba recenta e VOCEA CURENTA.

Era recenta (vocea curenta, fata de era de inceput):
- am inversat persoana: I scade de la 13,4/k la 8,4/k; you/your creste la 10,7/k.
- exclamarile aproape dispar: 58 in prima era, 1 in 10.400 cuvinte.
- coloana creste la ~10,7/k (pauza de apoteza, ca regula 5).
- "very" scade de la 2,3/k la 1,0/k. Intensificator folosit econom: nu-l largi.
- propozitia scurteaza: medie 19,8 -> 15,0 cuvinte.
- "not only...but": 26 de aparitii in prima era, 2 in era recenta.
- "to be honest/honestly" despre propria vorbire: prima era; in 2025 apare o singura
  data (flagged corect de scanner). Regula 9 masoara vocea curenta, nu mostenirea.

Confirmari dure:
- em-dash adevarat: 1 in 55.700 cuvinte (post din 2017). Regula "zero em-dash" tine.
  Cele 266 de " - " NU sunt pauze: sintaxa lui de lista "termen - explicatie" (lead
  ingrosat apoi cratima, ca in postul din 2014/2015 despre lideri).
- CAPS nu sunt emoționale: sunt acronime tehnice (PM x40, IDEO, OK, PMP, TDD...).
  Zero smileys.
- bullet-uri si linii "term - descriere": ~200; listele sunt dovezi de casa, nu exceptii.

Verbe permise (masurate intreaga pagina): do(193), need(126), think(94), make(79), get(67),
know(60), start, take, trust(55), help, believe, ask. Adjective: good(77), "important"(63),
clear(50), great, hard, simple, bad, small.
Cuvinte interzise care totusi apar in blog (aproape toate in era veche, densitate umana
~0,5/k): "strategic" x8, "empowering" x7, "crucial" x2, "synergy" x2, "stakeholder" x2,
"optimize" x2, "leveraging" x2, "foster" x1, "cornerstone" x1. In era recenta: doar
"strategic" x2 si "comprehensive" x2 (ambele in titluri/citate); zero aparitii la restul:
"delve", "pivotal", "robust", "seamless", "holistic", "harness", "elevate", "meticulous",
"moreover", "furthermore", "myriad", "realm".

Scanner v0.11.1 pe blog: 55,7k cuvinte -> 48 HIGH (0,9/k; era veche 1,0/k, recenta 0,4/k).
Verdicturi: 14 PASS, 38 REVIEW, 25 FAIL in 2008-2013; 9 REVIEW, 4 FAIL in 2014-2025;
singurele HIGH din vocea curenta: "binary_not_but" (1), "binary_is_is" (1),
"cornerstone" (1), "honestly" adverb (1, postul 2025). Toate citibile ca fapte, nu ca
telluri de AI: densitatea umana e pe masura. Tellul de AI e ACELASI sablon la densitate
mare si cu a doua clauza goala.
Postul 2025 e FAIL doar pe "looking under the hood honestly" - regula 9 face exact ce trebuie.

## Regula 11 - fiecare cuvant are sens literal

Nicio metafora. "weapons" despre strategie e interzis: cuvantul nu are sens in propozitie.

Proba: dicționar, in context. Daca sensul nu rezista, cuvantul se rescrie concret.
Excepție: citatele intre ghilimele, pastrate ca citate, cu atribuire explicita.

## Regula 12 - engleza simpla

Alex nu e vorbitor nativ de engleza. Cuvinte de 1-2 silabe, sens literal, propozitii de
12-22 de cuvinte. Media de litere pe cuvant sub 4.8. Cuvinte de 10+ litere sub 12%.
Fara nominalizari si fara latinisme care nu se traduc bine.

## Regula 13 - calificative emotionale

Interzise in general: "uncomfortable", "striking", "fascinating", "troubling",
"remarkable", "compelling", "intriguing", "disturbing", "alarming", "insightful",
"fascinating", "elegant", "profound" si restul listei din anti-ai-prompt.md, sectiunea
Empty emotional adjectives. Exceptie: daca descriu ceva fizic (scaun, caldura, zgomot).
Altfel: tai cuvantul sau explica concret ce reactioneaza la fapt.

## Regula 14 - fara registru noir la fapte simple

Daca faptul e mic, scrie-l mic. Fara teaser, fara suspense, fara punchline, fara decor de
scena ("waiting on your desk tonight", "the plot thickens", "here's the twist"). Suspense doar
la fapte care il merita, si doar cu concrete.