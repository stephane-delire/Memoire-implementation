//
//
//
// - Global
var statements = [];
var statements_index = 1;
// - Constants
const containerRes = document.getElementById('container_res');

// - Functions
function resParse(sql, res){

    // - Statements
    var parsed = alasql.parse(sql).statements;
    

    for (const element of parsed) {
        var type = "undefined";
        var normalize_query = String(element);

        // ---------------------------------------------------------------------
        // On split la query normalisée
        var query = String(element).split(' ');
        
        // Si le premier mot est SELECT
        if(query[0] == 'SELECT'){
            type = 'SELECT';
        }
        // Si le premier mot est INSERT
        if(query[0] == 'INSERT'){
            type = 'INSERT';
        }
        // Si le premier mot est CREATE
        if(query[0] == 'CREATE'){
            type = 'CREATE';
        }
        // Si le premier mot est DROP
        if(query[0] == 'DROP'){
            type = 'DROP';
        }
        // Si le premier mot est DELETE
        if(query[0] == 'DELETE'){
            type = 'DELETE';
        }
        // Si le premier mot est UPDATE
        if(query[0] == 'UPDATE'){
            type = 'UPDATE';
        }
        // Si le premier mot est ALTER
        if(query[0] == 'ALTER'){
            type = 'ALTER';
        }

        // ---------------------------------------------------------------------
        // On vérifie si la query est exprimable en FO
        var [isFO, reason] = isFOExpressible(normalize_query, type);

        // ---------------------------------------------------------------------
        // On push dans statements :
        statements.push({
            id: statements_index,
            type: type,
            query: normalize_query,
            isFO: isFO,
            reason: reason,
            res: res
        });
        statements_index++;
    }
};


function isFOExpressible(query, type){
    var isFO = false;

    // Si le type n'est pas SELECT alors c'est d'office faux
    if(type != 'SELECT'){
        return [false, 'Not a SELECT statement'];
    }
    // Si le type est SELECT
    // mais que la query contient un group by
    if(query.includes('GROUP BY')){
        return [false, 'Group by'];
    }
    // mais que la query contient un having
    if(query.includes('HAVING')){
        return [false, 'Having'];
    }
    // mais que la query contient un order by
    if(query.includes('ORDER BY')){
        return [false, 'Order by'];
    }
    // mais que la query contient un limit
    if(query.includes('LIMIT')){
        return [false, 'Limit'];
    }
    // mais que la query contient un with
    if(query.includes('WITH')){
        return [false, 'With'];
    }
    // mais que la query contient une fonction d'agrégation
    if(query.includes('COUNT') || query.includes('SUM') || query.includes('AVG') || query.includes('MIN') || query.includes('MAX')){
        return [false, 'Aggregation'];
    }
    return [true, ''];
}