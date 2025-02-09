//
//
//
// - Global
var statements = [];
var statements_index = 1;
// - Constants
const containerRes = document.getElementById('container_res');

// - Functions
// ---------------------------------------------------------------------------------------- resParse
function resParse(sql, res) {

    // - Statements
    var parsed = alasql.parse(sql).statements;


    for (const element of parsed) {
        var type = "undefined";
        var normalize_query = String(element);

        // ---------------------------------------------------------------------
        // On split la query normalisée
        var query = String(element).split(' ');

        // Si le premier mot est SELECT
        if (query[0] == 'SELECT') {
            type = 'SELECT';
        }
        // Si le premier mot est INSERT
        if (query[0] == 'INSERT') {
            type = 'INSERT';
        }
        // Si le premier mot est CREATE
        if (query[0] == 'CREATE') {
            type = 'CREATE';
        }
        // Si le premier mot est DROP
        if (query[0] == 'DROP') {
            type = 'DROP';
        }
        // Si le premier mot est DELETE
        if (query[0] == 'DELETE') {
            type = 'DELETE';
        }
        // Si le premier mot est UPDATE
        if (query[0] == 'UPDATE') {
            type = 'UPDATE';
        }
        // Si le premier mot est ALTER
        if (query[0] == 'ALTER') {
            type = 'ALTER';
        }

        // ---------------------------------------------------------------------
        // On vérifie si la query est exprimable en FO
        var [isFO, reason] = isFOExpressible(normalize_query, type);
        // ---------------------------------------------------------------------
        // Table cible : 
        // on récupère le nom de la table cible
        var target_table = '';
        if (type == 'SELECT') {
            for (const word of query) {
                if (word == 'FROM') {
                    target_table = query[query.indexOf(word) + 1];
                    break;
                }
            }
        }
        // Récupère la table cible, et vérifie qu'elle n'a pas d'erreur
        // récupère la table dom dont le nom est target_table
        var target_table_dom = document.getElementById('table_' + target_table);
        if (target_table_dom) {
            pk_error = target_table_dom.getAttribute('error');
            if (pk_error == 'true' || pk_error == true || pk_error == 'True' || pk_error == 'TRUE') {
                pk_error = true;
            } else {
                pk_error = false;
            }
        } else {
            pk_error = false;
        }
        // ---------------------------------------------------------------------
        // Colonne cible (id)
        // On récupère la colonne cible
        var target_column = '';
        if (type == 'SELECT') {
            target_column = target_table_dom.querySelector('.pk').getAttribute('name');
        }

        // ---------------------------------------------------------------------
        // Certainty
        // On vérifie la certitude de la query
        var certainty_res = certainty(normalize_query, type, target_table, res, pk_error, isFO, target_column);

        // ---------------------------------------------------------------------
        // On push dans statements :
        var new_statement = {
            id: statements_index,
            type: type,
            query: normalize_query,
            isFO: isFO,
            reason: reason,
            res: res,
            table: target_table,
            column_id: target_column,
            pk_error: pk_error,
            certainty: certainty_res
        };

        statements.push(new_statement);
        statements_index++;

        // ---------------------------------------------------------------------
        // render
        renderNewStatement(new_statement);
    }
};

// --------------------------------------------------------------------------------- isFOExpressible
function isFOExpressible(query, type) {
    var isFO = false;

    // Si le type n'est pas SELECT alors c'est d'office faux
    if (type != 'SELECT') {
        return [false, 'Not a SELECT statement'];
    }
    // Si le type est SELECT
    // mais que la query contient un group by
    if (query.includes('GROUP BY')) {
        return [false, 'Group by'];
    }
    // mais que la query contient un having
    if (query.includes('HAVING')) {
        return [false, 'Having'];
    }
    // mais que la query contient un order by
    if (query.includes('ORDER BY')) {
        return [false, 'Order by'];
    }
    // mais que la query contient un limit
    if (query.includes('LIMIT')) {
        return [false, 'Limit'];
    }
    // mais que la query contient un with
    if (query.includes('WITH')) {
        return [false, 'With'];
    }
    // mais que la query contient une fonction d'agrégation
    if (query.includes('COUNT') || query.includes('SUM') || query.includes('AVG') || query.includes('MIN') || query.includes('MAX')) {
        return [false, 'Aggregation'];
    }
    return [true, ''];
}




// ------------------------------------------------------------------------------ renderNewStatement
function renderNewStatement(statement) {
    //hide the no result message
    document.getElementById('res_null').style.display = 'none';
    //rendering
    var div = document.createElement('div');
    div.classList.add('res_content');
    div.setAttribute('id', 'res_' + statement.id);
    div.setAttribute('type', statement.type);
    div.setAttribute('isFO', statement.isFO);

    // top bar
    var top_bar = document.createElement('div');
    top_bar.classList.add('res_top_bar');
    div.appendChild(top_bar);
    // badge
    var badge = document.createElement('div');
    badge.classList.add('res_badge');
    badge.innerHTML = statement.type;
    if (statement.type == 'SELECT') {
        badge.classList.add('badge_select');
    }
    if (statement.type == 'INSERT') {
        badge.classList.add('badge_insert');
    }
    if (statement.type == 'CREATE') {
        badge.classList.add('badge_create');
    }
    if (statement.type == 'DROP') {
        badge.classList.add('badge_drop');
    }
    if (statement.type == 'DELETE') {
        badge.classList.add('badge_delete');
    }
    if (statement.type == 'UPDATE') {
        badge.classList.add('badge_update');
    }
    if (statement.type == 'ALTER') {
        badge.classList.add('badge_alter');
    }
    top_bar.appendChild(badge);

    // query content
    var div_query = document.createElement('div');
    div_query.classList.add('res_query');
    div_query.innerHTML = statement.query;
    top_bar.appendChild(div_query);

    // close button
    var close_btn = document.createElement('div');
    close_btn.classList.add('res_close');
    close_btn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-x"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>
    `;
    close_btn.addEventListener('click', function () {
        document.getElementById('res_' + statement.id).remove();
        if (containerRes.childElementCount == 1) {
            document.getElementById('res_null').style.display = 'block';
        }
    });
    top_bar.appendChild(close_btn);

    // -------------------------------------------------------------------------
    // render select result
    if (statement.type == 'SELECT') {
        //FO
        var div_isFO = document.createElement('div');
        div_isFO.classList.add('res_isFO');
        if (statement.isFO) {
            div_isFO.innerHTML = 'Exprimable en FO';
            div_isFO.classList.add('isFO_true');
        } else {
            div_isFO.innerHTML = 'Non exprimable en FO';
            div_isFO.classList.add('isFO_false');
        }
        div.appendChild(div_isFO);


        //res (table) -- Uniquement si Certainty...
        var table_container = document.createElement('div');
        table_container.classList.add('res_table_container');
        div.appendChild(table_container);
        var table = document.createElement('table');
        table.classList.add('res_table');
        var thead = document.createElement('thead');
        var tr = document.createElement('tr');
        for (const key in statement.res[0]) {
            var th = document.createElement('th');
            th.innerHTML = key;
            tr.appendChild(th);
        }
        thead.appendChild(tr);
        table.appendChild(thead);
        var tbody = document.createElement('tbody');
        for (const row of statement.res) {
            var tr = document.createElement('tr');
            for (const key in row) {
                var td = document.createElement('td');
                td.innerHTML = row[key];
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
        table.appendChild(tbody);
        table_container.appendChild(table);
    }


    containerRes.appendChild(div);
}

// --------------------------------------------------------------------------------------- certainty
function certainty(query, type, target_table, res, pk_error, isFO, target_column) {
    /*
    */
    if (type != 'SELECT') {
        return true;
    }
    // Si la table cible n'a pas d'erreur
    if (!pk_error) {
        return true;
    }
    // Si c'est pas exprimable en FO
    if (!isFO) {
        return false;
    }
    // Il faut générer les tables avec le moins possibles de réparations
    repair_table = generateRepairTable(target_table, res, target_column);
    console.log(repair_table);

    return true;
}

// ----------------------------------------------------------------------------- generateRepairTable
function generateRepairTable(target_table, res, target_column) {

    // Note : les réparations doivent se faire avant la query donnée donc...
    // il faut récupérer les données avant la query
    //res = alasql('SELECT * FROM ' + target_table);
    // Ou pas ???? TODO

    let grouped = {};
    res.forEach((item, index) => {
        if (!grouped[item[target_column]]) {
            grouped[item[target_column]] = [];
        }
        grouped[item[target_column]].push(index);
    });
    // Trouver les éléments ayant plusieurs occurrences
    let duplicates = Object.values(grouped).filter(indices => indices.length > 1);

    // Générer les listes en supprimant un élément dupliqué à la fois
    let results = [];
    duplicates.forEach(indices => {
        indices.forEach(indexToRemove => {
            let newList = res.filter((_, idx) => idx !== indexToRemove);
            results.push(newList);
        });
    });
    return results;
}

// ----------------------------------------------------------------------------- isAllListsIdentical
function isAllListsIdentical(lists) {
    if (lists.length === 0) return true;
    // Fonction de normalisation : trie les objets et les transforme en string JSON
    const normalize = list => JSON.stringify(
        list.map(obj => JSON.stringify(obj)).sort()
    );
    // Prendre la version normalisée de la première liste comme référence
    const reference = normalize(lists[0]);
    // Vérifier que toutes les autres listes sont identiques à la référence
    return lists.every(list => normalize(list) === reference);
}