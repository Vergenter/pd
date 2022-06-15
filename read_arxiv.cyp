LOAD CSV FROM 'file:///arxiv/num-node-list.csv' AS line
UNWIND range(0,toInteger(line[0])) AS id
CREATE (:Article{id:id});
// Added 169344 labels, created 169344 nodes, set 169344 properties, completed after 597 ms.

CREATE INDEX FOR (a:Article) ON (a.id)
// Added 1 index, completed after 21 ms.

// //skip null values
// LOAD CSV WITH HEADERS FROM 'file:///companies.csv' AS row
// WITH row WHERE row.Id IS NOT NULL
// MERGE (c:Company {companyId: row.Id});
// arxiv
// // clear data
// MATCH (n:Company) DELETE n;

LOAD CSV FROM 'file:///arxiv/edge.csv' AS line
MATCH (a1:Article{id:toInteger(line[0])})
MATCH (a2:Article{id:toInteger(line[1])})
CREATE (a1)-[:COAUTORED]->(a2)
// Created 1166243 relationships, completed after 15250 ms.

LOAD CSV FROM 'file:///arxiv/num-edge-list.csv' AS line
return line[0]
//  "1166243"

match (a1:Article)-->(a2:Article),(a2)-->(a1)
return a1,a2
LIMIT 3
// Success relationships are in two ways

MATCH (a1:Article)-[r]->(a2:Article)
WITH a1,a2,count(r) as rel_count
WHERE rel_count > 1
RETURN a1,a2
//(no changes, no records)

match (a1:Article)-[r1:COAUTORED]->(a2:Article),(a2)-[r2:COAUTORED]->(a1)
DELETE r2
// Deleted 16888 relationships, completed after 5185 ms.

PROFILE LOAD CSV FROM 'file:///arxiv/node_year.csv' AS line
WITH line LIMIT 0
MERGE (a1:Article{id:(linenumber()-1)})
ON CREATE SET a1.year = toInteger(line[0])
ON MATCH SET a1.year = toInteger(line[0])

:auto USING PERIODIC COMMIT 1000
LOAD CSV FROM 'file:///arxiv/node_year.csv' AS line
MERGE (a1:Article{id:(linenumber()-1)})
ON CREATE SET a1.year = toInteger(line[0])
ON MATCH SET a1.year = toInteger(line[0])
// Set 169343 properties, completed after 1654 ms.

:auto USING PERIODIC COMMIT 1000
LOAD CSV FROM 'file:///arxiv/node-label.csv' AS line
MERGE (a1:Article{id:(linenumber()-1)})
ON CREATE SET a1.label = toInteger(line[0])
ON MATCH SET a1.label = toInteger(line[0])
// Set 169343 properties, completed after 1369 ms.

:auto USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///arxiv/nodeidx2paperid.csv' AS line
match (a1:Article{id:toInteger(line.`node idx`)})
SET a1.paper_id = toInteger(line.`paper id`)
// Set 169343 properties, completed after 1501 ms.

CREATE INDEX FOR (a:Article) ON (a.paper_id)

LOAD CSV FROM 'file:///arxiv/titleabs.tsv' AS line
FIELDTERMINATOR '\t'
return count(line)
// At /var/lib/neo4j/import/arxiv/titleabs.tsv @ position 421556 -  there's a field starting with a quote and whereas it ends that quote there seems to be characters in that field after that ending quote. That isn't supported. This is what I read: 'How well connected is the network?" '

// file fixed with regular expression replace (?<!\\)" to \"

LOAD CSV FROM 'file:///arxiv/titleabs_fixed_quotes.tsv' AS line
FIELDTERMINATOR '\t'
return count(line)
// 179719

:auto USING PERIODIC COMMIT 1000
LOAD CSV FROM 'file:///arxiv/titleabs_fixed_quotes.tsv' AS line
FIELDTERMINATOR '\t'
match (a1:Article{paper_id:toInteger(line[0])})
SET a1.title = line[1]
SET a1.abstract = line[2]
// Set 338686 properties, completed after 2567 ms.

LOAD CSV WITH HEADERS FROM 'file:///arxiv/labelidx2arxivcategeory.csv' AS line
CREATE (:Category{id:toInteger(line.`label idx`), name:line.`arxiv category`})

CREATE INDEX FOR (c:Category) ON (c.id)

MATCH (a1:Article),(c:Category)
where a1.label = c.id
CREATE (a1)-[:OF_CATEGORY]->(c)


MATCH (a1:Article)-[r]-(c:Category)
return a1,r,c
limit 100


match path = (a1:Article)-[r]-(c:Category)
WITH path LIMIT 1000
with collect(path) as paths
call apoc.gephi.add("http://192.168.0.178:8080",'workspace1', paths) yield nodes, relationships, time
return nodes, relationships, time

match path = (a1:Article)-[r]-(a2:Article)
with collect(path) as paths
call apoc.gephi.add("http://192.168.0.178:8080",'workspace1', paths,"weight",['type','category', 'year']) yield nodes, relationships, time
return nodes, relationships, time

:auto USING PERIODIC COMMIT 1000
match (a:Article) 
SET a.category = a.label 
REMOVE a.label 