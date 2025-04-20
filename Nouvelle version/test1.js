// Exemple d'input au format CQA
const input = `
@database
Likes(John, Paris;)
Lives(John; London)
Mayor(Paris; Hidalgo)
Mayor(London; Khan)

@query
Likes(p,t;)
not Lives(p;t)
not Mayor(t;p)
`;

// Fonction pour parser la section de la base de données
function parseDatabase(dbSection) {
  const relations = {};
  // On sépare les lignes, on élimine les espaces inutiles et les lignes vides
  const lines = dbSection.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('@'));
  lines.forEach(line => {
    // Exemple d'une ligne : "Likes(John, Paris;)"
    const match = line.match(/^(\w+)\((.*)\)$/);
    if (match) {
      const relationName = match[1];
      const content = match[2];
      // Le point-virgule sépare la clé (ou les clés) des autres attributs
      const [keysPart, nonKeysPart] = content.split(';');
      const keys = keysPart.split(',').map(s => s.trim()).filter(s => s);
      const nonKeys = nonKeysPart ? nonKeysPart.split(',').map(s => s.trim()).filter(s => s) : [];
      // Ajout du tuple dans la relation correspondante
      if (!relations[relationName]) {
        relations[relationName] = [];
      }
      relations[relationName].push({ keys, attributes: nonKeys });
    }
  });
  return relations;
}

// Fonction pour parser la section de la requête
function parseQuery(querySection) {
  const atoms = [];
  const lines = querySection.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('@'));
  lines.forEach(line => {
    // Détection d'une négation (préfixe "not")
    let isNegated = false;
    if (line.startsWith('not ')) {
      isNegated = true;
      line = line.substring(4).trim();
    }
    const match = line.match(/^(\w+)\((.*)\)$/);
    if (match) {
      const relationName = match[1];
      const content = match[2];
      const [keysPart, nonKeysPart] = content.split(';');
      const keys = keysPart.split(',').map(s => s.trim()).filter(s => s);
      const nonKeys = nonKeysPart ? nonKeysPart.split(',').map(s => s.trim()).filter(s => s) : [];
      atoms.push({
        relation: relationName,
        keys,
        attributes: nonKeys,
        negated: isNegated
      });
    }
  });
  return atoms;
}

// Fonction principale pour parser l'input complet
function parseInput(input) {
  // On découpe l'input en sections en se basant sur les marqueurs "@"
  const sections = input.split(/@(\w+)/).map(s => s.trim()).filter(s => s);
  const result = {};
  for (let i = 0; i < sections.length; i += 2) {
    const sectionName = sections[i].toLowerCase();
    const sectionContent = sections[i + 1];
    if (sectionName === 'database') {
      result.database = parseDatabase(sectionContent);
    } else if (sectionName === 'query') {
      result.query = parseQuery(sectionContent);
    }
  }
  return result;
}

// Utilisation de la fonction de parsing
const parsed = parseInput(input);
console.log("Base de données :", parsed.database);
console.log("Requête :", parsed.query);

// Exemple d'affichage simple pour chaque atome de la requête
parsed.query.forEach(atom => {
  console.log(`Atome ${atom.negated ? 'négatif' : 'positif'} : ${atom.relation} avec clés [${atom.keys.join(', ')}] et attributs [${atom.attributes.join(', ')}]`);
});
