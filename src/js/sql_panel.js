
// --- Constants
// btns
const sqlBtnExecute = document.getElementById('sql_btn_execute');
const sqlBtnClear = document.getElementById('sql_btn_trash');
// textareas
const sqlTextarea = document.getElementById('sql_textarea');

// --- Event listeners
sqlBtnExecute.addEventListener('click', executeSQL);
sqlBtnClear.addEventListener('click', clearSQL);


// --- Functions
function executeSQL() {
    let sql = sqlTextarea.value;
    try {
        // Certainty ?
        var res = alasql(sql); // ! retour en cas de SELECT
        successSQL();
        renderTable(); // rendre la table (table_panel.js)
        resParse(sql, res); // Vers le JS res_panel.js
    } catch (error) {
        console.error(error);
        errorSQL();
    }
}

function clearSQL() {
    sqlTextarea.value = '';
    resetSQL();
    sqlTextarea.focus();
}

// styling the textarea
function successSQL() {
    // add class to the textarea
    sqlTextarea.classList.add('sql-success');
}
function errorSQL() {
    sqlTextarea.classList.add('sql-error');
}
function resetSQL() {
    sqlTextarea.classList.remove('sql-success');
    sqlTextarea.classList.remove('sql-error');
}
// eventlistener for the textarea
sqlTextarea.addEventListener('keydown', function (event) {
    resetSQL();
    
    if (event.key === 'Enter' && event.ctrlKey || event.key == 'F8') {
        executeSQL();
    }
    
    if (event.key === 'Escape' || event.key === 'F9') {
        clearSQL();
    }

});