# Annexe FR - registre parlé

Règle universelle (règle 2 de anti-ai-prompt.md) : la phrase écrite doit sonner comme
une phrase dite. Tu la dis à voix haute, à un ami, dans la cuisine ; si elle sonne
comme un communiqué de presse, tu la réécris. Teste chaque verbe : tu l'utiliserais
en parlant ? Non -> remplace-le. Le latinisme administratif est le signal classique
du brouillon de modèle en français.

## Mots enflés -> équivalent parlé

| Écrit administrative | Parlé |
|---|---|
| subséquemment | après |
| il convient de | il faut |
| effectuer | faire |
| en termes de | pour |
| en vue de | pour |
| de par | par |
| pérenniser | faire durer |
| en adéquation avec | adapté à |
| une myriade de | beaucoup de |
| une pléthore de | beaucoup de |
| un éventail de | plusieurs |
| nous souhaitons | nous voulons |
| davantage | plus |

Tous sont dans patterns.json (catégorie complex, lang fr), donc check_tells.py les repère.

## Mauvais -> bien

- Mauvais : Il convient de noter que nous souhaitons effectuer une analyse des coûts.
  Bien : Nous allons regarder les coûts.
- Mauvais : Il existe une myriade de solutions dans le paysage actuel.
  Bien : Il y a plein de solutions aujourd'hui.
- Mauvais : En conclusion, il est important de comprendre le budget.
  Bien : Le budget est serré ; voici pourquoi.

## Rythme : recalibrer les chiffres

Les chiffres de house-style.md (noyau de 12-22 mots, moyenne de lettres sous 4.8,
mots longs sous 12%) sont calibrés sur du texte anglais. Le noyau de phrase passe en
français. La longueur des mots ne passe pas : les suffixes français courent plus long,
et ce n'est pas une faute de style.

Recette de mesure : prends 2.000+ mots d'une prose à toi que tu aimes. Compte la
moyenne de lettres par mot et la part des mots de 10+ lettres. Mets tes chiffres à la
place de ceux de house-style.md et garde les tiens ensuite.

Zéro em-dash reste universel, dans toutes les langues.
