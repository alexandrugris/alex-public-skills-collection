# House style - masurat pe un corpus personal (blog, 2008-2025)

Acest fisier e UN exemplu de house style calibrat pe vocea lui Alexandru Gris
(blog.alexandrugris.ro si alexandrugris.ro, 90 de posturi, 2008-2025, ~55.700 cuvinte;
profilul complet, cu masuratorile pe pagina si pe vocabular: `alex-style.md`).
Nu e un standard universal: copiaza-l, masoara-ti propriul text si inlocuieste
numerele cu ale tale.

Doua ere, doua voci (nu le amesteca in profil): 2008-2013 (jurnal personal, ~45.200
cuvinte) si 2014-2025 (eseuri, ~10.400 cuvinte). Vocea curenta = era recenta:
- persoana se inverseaza cu timpul: I scade de la 13,4/k la 8,4/k; you/your creste la 10,7/k
- exclamarile aproape dispar (58 in prima era, 1 in era recenta)
- coloana (:) ajunge la ~10,7/k: pauza de apoteza, inainte de faptul sec
- "very" scade de la 2,3/k la 1,0/k; intensificatorii se folosesc economic
- propozitia scurteaza: medie 19,8 -> 15,0 cuvinte
- "not only...but": 26 de aparitii in prima era, 2 in era recenta
- "to be honest / honestly" despre propria vorbire: numai in prima era

## Reguli de casa (calibrate)

1. Daca e lista, e lista. Bullet points cu lead ingrosat. Nu trei propozitii paralele
   mascate in proza. ("If it is bullet points, make it bullet points, if not, write the idea.")
2. Daca nu e lista, scrie ideea. Propozitii pline, nu bullet points.
3. Fara moralitate la final. Se termina pe imagine sau fapt, nu pe maxima.
4. Heading = propozitie declarativa cu punct final.
5. Nucleu de 12-22 de cuvinte. Enumararile pot alerga lung, dar nu peste tot; clauzele din
   enumeratii raman scurte (max 22). Zero em-dash. Colon ca pauza de apoteza.
6. Prima persoana, rara.
7. Substantiv concret, nu categorie.
8. Zero vorbire de model, zero hedge-uri in grup.
9. Fara "honest" despre propria vorbire. Exceptie: referinta la o persoana.
10. Verbele de greutate sunt interzise: load-bearing, carries weight in orice forma
    (carries the weight of, carries enormous weight), anchors, underpins, grants, fosters,
    fuels, earns its.
11. Fiecare cuvant are sens literal. Nicio metafora: daca sensul de dictionar nu rezista
    in context, cuvantul se rescrie concret. Excepție: citatele, pastrate ca citate, cu
    atribuire explicita.
12. Engleza simpla (cu atat mai mult daca engleza nu e prima ta limba): cuvinte de 1-2
    silabe, sens literal, propozitii de 12-22 de cuvinte. Media de litere pe cuvant sub
    4.8. Cuvinte de 10+ litere sub 12%. Fara latinisme care nu se traduc bine.
    Numerele de litere sunt calibrate pe text englezesc; pentru romana si franceza
    sufixele merg natural mai lung. Reteta de recalibrare: `lang-ro.md` si `lang-fr.md`.
13. Calificativele emotionale (uncomfortable, striking, fascinating, troubling, remarkable,
    compelling, intriguing) sunt interzise, exceptand descrierea fizica. Altfel: taie
    cuvantul sau explica concret ce anume produce reactia.
14. Fara registru noir la fapte simple: daca faptul e mic, scrie-l mic. Fara teaser, fara
    suspense, fara punchline, fara decor de scena.

## Confirmari dure din corpus

- em-dash adevarat: 1 in 55.700 de cuvinte. Regula "zero em-dash" tine.
  Liniile " - " nu sunt pauze: sunt sintaxa de lista "termen - explicatie".
- CAPS nu sunt emotionale: sunt acronime de lucru.
- Verbe permise (masurate): do (193), need (126), think (94), make (79), get (67),
  know (60), start, take, trust (55), help, believe, ask.
  Adjective: good (77), important (63), clear (50), great (49), hard (47), simple, bad, small.
- Cuvintele din blocklist apar la densitate umana (~0,5/k) si aproape dispar in era
  recenta: strategic x8, empowering x7, crucial x2, synergy x2, stakeholder x2, optimize x2.
  Zero aparitii: delve, pivotal, robust, seamless, holistic, harness, elevate, meticulous,
  moreover, furthermore, myriad, realm.
- Scanner v0.11.x pe corpus: 48 HIGH / 55,7k cuvinte (0,9/k; 1,0/k prima era, 0,4/k recenta).
  Verdicturi pe 90 de posturi: 14 PASS, 38 REVIEW, 25 FAIL (2008-2013);
  9 REVIEW, 4 FAIL (2014-2025).

Verificare: python3 check_tells.py fisier.txt
