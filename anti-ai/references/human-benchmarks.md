# Benchmark-uri pe texte umane (calibrare anonima)

Blocklist-ul a fost calibrat pe patru corpusuri: un draft scris de model (AI) si trei
texte scrise de oameni, independent intre ele. Toate numerele de mai jos sunt masurate;
sursele nu sunt citate si nu se atribuie. Lectia de pipeline: FAIL = telluri grele
(aproape sigur text AI); REVIEW poate fi text uman bun. La REVIEW nu taia mecanic.

## Corpus AI (draft de model)

FAIL. 3 HIGH intr-un draft de ~1.000 de cuvinte (sablon-paralel, "a mere", metafora
"fara sens literal"). Ipoteza de plecare a intregului proiect.

## Corpus uman A: blog personal (90 de posturi, 2008-2025, 55.7k cuvinte)

Vezi house-style.md. 14 PASS / 38 REVIEW / 25 FAIL, cele mai multe HIGH in era veche.
Singurele tipare HIGH din vocea recenta: binarul "not only...but", binarul "is not X. It
is Y", o metafora moarta unica si un adverb de sinceritate unic. Densitate umana, doua
clauze concrete. Tellul de AI e ACELASI sablon la densitate mare si cu a doua clauza
goala; densitatea e discriminatorul, nu aparitia izolata.

## Corpus uman B: memo intern de management (alt autor, ~5.100 cuvinte)

- 404 propozitii, medie 12,7 cuvinte, mediana 11; doar 8 peste 35 de cuvinte.
- Adresare directa dominanta (raport you:I aproximativ 14:1), multe intrebari retorice,
  exclamatii putine, paranteze pentru asideri, colon ca pauza, zero em-dash.
- Zero cuvinte din blocklist in toata pagina: niciunul dintre "delves", "crucial",
  "pivotal", "robust", "seamless", "leverage", "foster", "journey", "landscape",
  "navigate", "unlock", "harness", "elevate", "empower", "moreover", "furthermore",
  "stakeholder", "synergy" nu apare.
- Intensificatorii simpli sunt firesti, nu hedge: "very" x13, "really" x8.
- ALL-CAPS pentru accent si 3 smileys in 5.100 de cuvinte: om care scrie lejer, nu asistent.
- Scanner: REVIEW (0 HIGH, 29 MEDIUM, 35 LOW).
- Ce calibreaza: (1) "genuinely" despre PERSOANE e permis (extensia logica a exceptiei
  de la "honest"); (2) calificativele emotionale sunt CASTIGATE daca clauza urmatoare
  explica mecanismul concret; (3) verbele latine firesti unui memo cad LOW, nu sunt
  tell; (4) analogiile introduse EXPLICIT cu "like / think of" trec proba la dictionar:
  banul e pe metaforele moarte, nu pe figuri de limbaj; (5) finalul fara rezumat si fara
  maxima e semnal de om.
- Schimbare de scanner rezultata: tiparul earns-its nu mai prinde folosirile concrete si
  castigate ale verbului "earn" (a castiga un drept prin fapte); tellul ramane "earns its
  place/complexity/stripes".

## Corpus uman C: document de lucru intern (~1.500 de cuvinte, cu comentarii in margine)

- 81 propozitii, medie 18,4, mediana 15; doar 5 peste 35 de cuvinte.
- Registru normativ: "we" 14,4/k, "should" 7,8/k, dar "must" doar 0,7/k. Persuasiunea
  prin norme impartasite si opinie marcata ("I believe", "I feel", "To me"), nu prin
  comenzi. Expresii "we don't want to X".
- Intrebarile ca structura de argument (7,8/k), documentul organizat pe intrebari.
- Zero exclamatii, zero em-dash adevarat, 10 linii "termen - explicatie" in rol de
  colon, un singur smiley dupa autoironie, "he/she" inclusiv, contractii
  normale, typos lasate in text (proza needitata).
- CAPS ca operatori logici deliberati si acronime de lucru, nu ca emotie.
- Conceptele iau nume cu imagine concreta, definite in aceeasi fraza.
- Scanner: REVIEW (0 HIGH, 11 MEDIUM, 24 LOW), zero la metaphor, weight, chat, honesty,
  hedge, list; cuvintele-blocklist care ies natural la densitate umana: "holistic",
  "cutting edge", "important".
- Ce calibreaza: (1) la work-docs, categoriile complex-LOW sunt zgomot de registru;
  (2) "termen - explicatie" nu e em-dash, e sintaxa de lista; (3) proza needitata
  castiga REVIEW, nu FAIL: FAIL-ul apare la sabloane, nu la imperfectiune.

## Tabel verdicturi

| Corpus | Natura | Verdict | HIGH/k |
|---|---|---|---|
| Draft AI | model | FAIL | ~3 intr-un singur text |
| Uman A (blog) | om, publicat | 9 REVIEW / 4 FAIL in era recenta | 0,4 |
| Uman B (memo) | om, intern | REVIEW | 0 |
| Uman C (work doc) | om, intern, needitat | REVIEW | 0 |
