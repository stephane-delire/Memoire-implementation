console.log('startup script loaded');
alasql("CREATE TABLE example (town string, country string, michelin string ,PRIMARY KEY(town))");
alasql("INSERT INTO example VALUES ('Mons','Belgium','*')");
alasql("INSERT INTO example VALUES ('Bruxelles','Belgium','**')");
alasql("INSERT INTO example VALUES ('Paris','France','**')");

const tool_deactivate_constraints = document.getElementById('tool_deactivate_constraints');
tool_deactivate_constraints.click();

alasql("INSERT INTO example VALUES ('Mons','Belgium','**')");

sqlTextarea.value = "SELECT * FROM example;";
executeSQL();


sqlTextarea.value = "SELECT town FROM example where country = 'Belgium';";
/*
SELECT town FROM example where country = 'Belgium';
Devait retourner true pour certainty...
*/