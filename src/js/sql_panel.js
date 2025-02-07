
// Constants
const sqlBtnExecute = document.getElementById('sql_btn_execute');
const sqlBtnClear = document.getElementById('sql_btn_trash');

// Event listeners
sqlBtnExecute.addEventListener('click', executeSQL);
sqlBtnClear.addEventListener('click', clearSQL);