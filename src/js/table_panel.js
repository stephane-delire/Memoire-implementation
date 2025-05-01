

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
                // add svg before textContent
                var svg = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-key-round"><path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"/><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/></svg>
                `;
                th.innerHTML = svg + th.textContent;
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

        // check pk contraint, need to verify if pk is unique, otherwise add error class on the tds
        const pk_tds = document.querySelectorAll(`#table_${table} td[pk=true]`);
        const pk_values = [];
        pk_tds.forEach(td => {
            pk_values.push(td.getAttribute('name'));
        });
        // check if pk_values contains duplicates
        const duplicates = pk_values.filter((value, index) => pk_values.indexOf(value) !== index);
        if (duplicates.length > 0){
            var i = 1;
            pk_tds.forEach(td => {
                if (duplicates.includes(td.getAttribute('name'))){
                    td.classList.add('error');
                    td.setAttribute('error', 'duplicate PK');
                    td.innerHTML = td.textContent + ' <span class="errorIndex">(' + i + ')</span>';
                    i++;
                    // insert an attribute to the table
                    tableElement.setAttribute('error', 'True');
                }
            });
        }
        

    }
}




setTimeout(renderTable, 500);