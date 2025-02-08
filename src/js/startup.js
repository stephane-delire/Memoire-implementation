console.log('startup script loaded');
alasql("CREATE TABLE cities (city string, pop number, PRIMARY KEY(city))");
alasql("INSERT INTO cities VALUES ('Paris',2249975),('Berlin',3517424),('Madrid',3041579)");

alasql("CREATE TABLE cities2 (city string, pop number)");
alasql("INSERT INTO cities2 VALUES ('Paris',2249975),('Berlin',3517424),('Madrid',3041579)");



alasql("CREATE TABLE one (id NVARCHAR(3));")
alasql("CREATE TABLE two (id NVARCHAR(3));")
alasql("CREATE TABLE three (id NVARCHAR(3));")

alasql("INSERT INTO one VALUES ('A'),('AB'),('AC'),('ABC');")
alasql("INSERT INTO two VALUES ('B'),('AB'),('BC'),('ABC');")
alasql("INSERT INTO three VALUES ('C'),('BC'),('AC'),('ABC');")


setTimeout(() => {
    sqlTextarea.value = "SELECT * FROM cities;";
    executeSQL();
    // sqlTextarea.value = "Insert into cities value ('Paris', 4000000);";
    // executeSQL();
    sqlTextarea.value = "select sum(pop) as population, city as ville from cities group by city;";
    executeSQL();
}, 1000);