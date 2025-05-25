/*
Charge les divers exemples de raccourcis pour utiliser dans
l'éditeur directement
*/

const Editor = document.getElementById("editor_input");

const btnShrt1 = document.getElementById("exemple_1");
const btnShrt2 = document.getElementById("exemple_2");
const btnShrt3 = document.getElementById("exemple_3");
const btnShrt4 = document.getElementById("exemple_4");
const btnShrt5 = document.getElementById("exemple_5");
const btnShrt6 = document.getElementById("exemple_6");

// ----------------------------------------------------------------------------
// event listeners
btnShrt1.addEventListener("click", function () {
  Editor.value = `# Exemple de base
# Reçu par mail

@database
Likes(John, Paris;)
Lives(John; London)
Mayor(Paris; Hidalgo)
Mayor(London; Khan)

@query
Likes(p,t;)
not Lives(p;t)
not Mayor(t;p)`;
});

btnShrt2.addEventListener("click", function () {
  Editor.value = `# Exemple 4.5 de l'article
# Mais pas certain

@database
P(1; A)
P(1; B)
N(C; A)

@query
P(x; y)
Not N(C; y)

# Doit etre clique guarded
# et réécrit`;
});

btnShrt3.addEventListener("click", function () {
    Editor.value = `# Exemple 4.5 de l'article
# certain

@database
P(1; A)
N(C; B)

@query
P(x; y)
Not N(C; y)

# Doit etre clique guarded
# et réécrit`;
});

btnShrt4.addEventListener("click", function () {
    Editor.value = `# Weakly guarded

@database
P(a, b;)
Q(a, c;)
R(c, b;)

@query
P(x, y;)
Q(x, z;)
R(z, y;)
not S(x, y, z)`;
});

btnShrt5.addEventListener("click", function () {
    Editor.value = `# Conflit

@database
Lives(John; London)
Lives(John; Paris) # duplicata sur la clé p
Visited(John, Paris;)

@query
Lives(p; t)
Visited(p, t;)
not Banned(t;)`;
});

btnShrt6.addEventListener("click", function () {
    Editor.value = `@database
P(a; b)
Q(b; c)
R(c; a)
D(a, b, c;)
@query
P(x; y)
Q(y; z)
R(z; x)
not D(x, y, z)
`;
});