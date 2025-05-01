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
  Editor.value = `# NGFO, mais pas certaine

@database
Parent(John, Mary;)
Parent(Mary, Alice;)
Teacher(Mary;)
Student(Alice;)

@query
Parent(x, y;)
Teacher(x;)
not Student(y;)`;
});

btnShrt3.addEventListener("click", function () {
    Editor.value = `# pas SJF

@database
Friend(John, Mary;)
Friend(Mary, Bob;)
Enemy(Bob, John;)

@query
Friend(x, y;)
Friend(y, z;) # SJF...
Enemy(z, x;)`;
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
    Editor.value = `# A priori correct

@database
Parent(John, Mary;)
Parent(Mary, Alice;)
Teacher(Mary;)
Student(Bob;)

@query
Parent(x, y;)
Teacher(x;)
not Student(y;)`;
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