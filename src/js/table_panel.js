

// --- Constants
const containerTable = document.getElementById('container_table');

// --- Functions
function renderTable(){
    // flush
    containerTable.innerHTML = '';
    // render every table inside alasql.tables
    for (let table in alasql.tables){
        // - Table
        var tableElement = document.createElement('table');
        tableElement.classList.add('sql_table');
        tableElement.id = "table_" + table;
        tableElement.setAttribute('name', table);

        // pk
        var pk = alasql.tables[table].pk;
        if (pk){
            var pk_column = pk.columns;
        } else {
            var pk_column = null;
        }
        
        // - Table head (columns) + table name
        var thead = document.createElement('thead');
        var tr_name = document.createElement('tr');
        var th_name = document.createElement('th');
        th_name.textContent = table;
        th_name.setAttribute('colspan', alasql.tables[table].columns.length);
        th_name.classList.add('table_name');
        th_name.setAttribute('name', table);
        tr_name.appendChild(th_name);
        thead.appendChild(tr_name);

        var tr = document.createElement('tr');
        for (let column of alasql.tables[table].columns){
            var th = document.createElement('th');
            th.textContent = column.columnid;
            th.classList.add('table_column');
            th.setAttribute('name', column.columnid);
            tr.appendChild(th);
            // pk (pk_column is an array)
            if (pk_column && pk_column.includes(column.columnid)){
                th.classList.add('pk');
                th.setAttribute('pk', 'true');
            }

        }
        thead.appendChild(tr);
        tableElement.appendChild(thead);
        
        // - Table body (rows)
        var tbody = document.createElement('tbody');
        for (let row of alasql.tables[table].data){
            var tr = document.createElement('tr');
            Object.values(row).forEach(value => {
                var td = document.createElement('td');
                td.textContent = value;
                td.classList.add('table_cell');
                td.setAttribute('name', value);
                td.setAttribute('table_name', table);
                tr.appendChild(td);
                // pk
                if (pk_column && pk_column.includes(Object.keys(row)[Object.values(row).indexOf(value)])){
                    td.classList.add('pk');
                    td.setAttribute('pk', 'true');
                };
            }
        );
            tbody.appendChild(tr);
        }
        tableElement.appendChild(tbody);
        // - Append table to container
        containerTable.appendChild(tableElement);
    }
}




setTimeout(renderTable, 500);