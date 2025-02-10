# Implémentation du mémoire

<div style='text-align:center;'>
    <img src="src/img/umons.png" width="200"/>
</div>

# Certainty Algorithm for Consistent Query Answering

## Description

Ce projet implémente l'algorithme *CERTAINTY(q)* dans le contexte des bases de données, en lien avec le *Consistent Query Answering (CQA)*. L'objectif est d'étudier l'expressivité de cet algorithme dans le cadre de la logique du premier ordre. 

L'implémentation repose sur les travaux de Jef Wijsen et Paraschos Koutris, détaillés dans l'article :
> *Consistent Query Answering for Primary Keys and Conjunctive Queries with Negated Atoms* (2018)

L'ensemble du code est mis à disposition sous une licence ouverte afin de favoriser l'expérimentation.

## Objectifs

Todo

## Stack Technique

Ce projet repose sur une stack web pour assurer une portabilité maximale :

- **Langage :** JavaScript (vanilla)
- **Base de données :** AlaSQL (interprétation SQL en JavaScript)
- **Interface :** HTML/CSS pour l'affichage des résultats
- **Exécution :** Fonctionne directement dans un navigateur sans dépendances externes.

## Installation et Usage

Aucune installation n'est requise. Il suffit de cloner le dépôt et d'ouvrir `main.html` dans un navigateur :

```sh
git clone https://github.com/stephane-delire/Memoire-implementation.git
cd Memoire-implementation
open main.html   # ou double-cliquer sur index.html
````

## Structure
```
📂 src
├── 📂 css
│   ├── 📄 fonts.css
│   ├── 📄 main.css
│   ├── 📄 res_panel.css
│   ├── 📄 scroll_bar.css
│   ├── 📄 sql_panel.css
│   └── 📄 toolbar.css
├── 📂 fonts
│   ├── Roboto-Regular.ttf
│   └── RobotoMono-Medium.ttf
├── 📂 img
│   └── ...
├── 📂 js
│   ├── 📄 alasql_beautified.js
│   ├── 📄 main.js
│   ├── 📄 res_panel.js
│   ├── 📄 sql_panel.js
│   ├── 📄 startup.js
│   ├── 📄 table_panel.js
│   └── 📄 toolbar.js
└── 📂 svg
📄 main.html                               # Interface principale
📄 README.md                               # Documentation du projet (ce fichier)
```