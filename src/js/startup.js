console.log('startup script loaded');
alasql("CREATE TABLE cities (city string, pop number)");
alasql("INSERT INTO cities VALUES ('Paris',2249975),('Berlin',3517424),('Madrid',3041579)");

alasql("CREATE TABLE cities2 (city string, pop number)");
alasql("INSERT INTO cities2 VALUES ('Paris',2249975),('Berlin',3517424),('Madrid',3041579)");