
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
        alasql(sql);
        successSQL();
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