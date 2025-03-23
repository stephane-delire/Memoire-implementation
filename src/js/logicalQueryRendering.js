/*
Rendu logique des requêtes SQL (uniquement SELECT et FO
*/
//

function logicalQueryRendering(query) {
    const input = query.toLowerCase().trim();

    // Parsing très simple (uniquement SELECT x FROM T WHERE condition)
    const selectMatch = input.match(/select\s+(.*?)\s+from\s+/i);
    const fromMatch = input.match(/from\s+(\w+)/i);
    const whereMatch = input.match(/where\s+(.*)/i);

    if (!selectMatch || !fromMatch) {
        document.getElementById("foFormula").innerHTML = "$$\\text{Format non reconnu}$$";
        MathJax.typesetPromise();
        return;
    }

    const selectVar = selectMatch[1].trim();
    const relation = fromMatch[1].trim();
    const condition = whereMatch ? whereMatch[1].trim().replace(";", "") : null;

    // On suppose que chaque attribut est binaire : relation(x, a)
    let formula = "";

    if (condition) {
        formula = `\\ Q( ${selectVar} ) : \\exists a\\ ${relation}(${selectVar}, a) \\land ${escapeLatex(condition)} `;
    } else {
        formula = `\\ Q( ${selectVar} ) : ${relation}(${selectVar}) `;
    }

    // document.getElementById("foFormula").innerHTML = `$$${formula}$$`;
    // console.log(formula);
    return formula;
    
}

function escapeLatex(str) {
    // Remplacer les opérateurs pour LaTeX
    return str
        .replace(/</g, "<")
        .replace(/>/g, ">")
        .replace(/=/g, "=")
        .replace(/and/gi, "\\land")
        .replace(/or/gi, "\\lor")
        .replace(/<>/g, "\\neq");
}