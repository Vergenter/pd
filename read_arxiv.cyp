LOAD CSV FROM 'file:///arxiv/num-node-list.csv' AS line
UNWIND range(0,toInteger(line[0])) AS id
CREATE (:Article{id:id});
// Added 169344 labels, created 169344 nodes, set 169344 properties, completed after 597 ms.

CREATE CONSTRAINT IF NOT EXISTS FOR (a:Article) REQUIRE a.id IS UNIQUE

CREATE INDEX FOR (a:Article) ON (a.id)
// Added 1 index, completed after 21 ms.
// No error no duplicate nodes

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
CREATE (a1)-[:CITES]->(a2)
// Created 1166243 relationships, completed after 15250 ms.

LOAD CSV FROM 'file:///arxiv/num-edge-list.csv' AS line
return line[0]
//  "1166243"

match (a1:Article)-->(a2:Article),(a2)-->(a1)
return a1,a2
LIMIT 3
// Success relationships are in two ways

// check for duplicate links
MATCH (a1:Article)-[r]->(a2:Article)
WITH a1,a2,count(r) as rel_count
WHERE rel_count > 1
RETURN a1,a2
//(no changes, no records)

// check for self loop
MATCH (a:Article)-[r]->(a:Article)
RETURN a1,r,a2
// (no changes, no records) Completed after 768 ms.

// It's not problem that relationship are in two ways
// match (a1:Article)-[r1:CITES]->(a2:Article),(a2)-[r2:CITES]->(a1)
// DELETE r2
// // Deleted 16888 relationships, completed after 5185 ms.

// check for isolated nodes
MATCH (a1:Article)
where NOT (a1)-->(:Article)
RETURN count(a1)
// 17441 completed after 302 ms.

// check for isolated nodes
MATCH (a1:Article)
where NOT (a1)<--(:Article)
RETURN count(a1)
// 62007 completed after 311 ms.

MATCH (a1:Article)
where NOT (a1)--(:Article)
RETURN count(a1)
// 1 completed after 281 ms.

MATCH (a1:Article)
where NOT (a1)--(:Article)
delete a1
//  Deleted 1 nodes, completed after 221 ms.

MATCH (a:Article) WHERE NOT EXISTS(a.year) delete a
// Deleted 2 nodes, completed after 221 ms.

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

MATCH (a:Article) WHERE NOT EXISTS(a.year) delete a
// Deleted 2 nodes, completed after 221 ms.

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
toInteger(line[0])
// 179719 completed after 1378 ms.

:auto USING PERIODIC COMMIT 1000
LOAD CSV FROM 'file:///arxiv/titleabs_fixed_quotes.tsv' AS line
FIELDTERMINATOR '\t'
match (a1:Article{paper_id:toInteger(line[0])})
SET a1.title = line[1]
SET a1.abstract = line[2]
// Set 338686 properties, completed after 2567 ms.

LOAD CSV WITH HEADERS FROM 'file:///arxiv/labelidx2arxivcategeory.csv' AS line
CREATE (:Category{id:toInteger(line.`label idx`), name:line.`arxiv category`})
// Added 40 labels, created 40 nodes, set 80 properties, completed after 21 ms.

CREATE INDEX FOR (c:Category) ON (c.id)

MATCH (a1:Article),(c:Category)
where a1.category = c.id
CREATE (a1)-[:OF_CATEGORY]->(c)
// Created 169343 relationships, completed after 718 ms.

MATCH (a1:Article)-[r]-(c:Category)
return a1,r,c
limit 100




// match (a:Article) 
// SET a.category = a.label 
// REMOVE a.label 
// // Set 338686 properties, completed after 725 ms.

// VISUALIZE IN GEPHI

match path = (a1:Article)-[r]-(a2:Article)
with collect(path) as paths
call apoc.gephi.add("http://192.168.0.178:8080",'workspace1', paths,"weight",['type','category', 'year']) yield nodes, relationships, time
return nodes, relationships, time



// fix typo in relation name
MATCH (n:Article)-[rel:>OLD_NAME]->(m:Article) WITH rel
CALL apoc.refactor.setType(rel, 'NEW_NAME') YIELD input, output RETURN *


// map categories
MATCH (c:Category)
set c.humanName =CASE 
WHEN c.name='arxiv cs ai' THEN 'Artificial Intelligence'
WHEN c.name='arxiv cs cl' THEN 'Computation and Language'
WHEN c.name='arxiv cs cc' THEN 'Computational Complexity'
WHEN c.name='arxiv cs ce' THEN 'Computational Engineering, Finance, and Science'
WHEN c.name='arxiv cs cg' THEN 'Computational Geometry'
WHEN c.name='arxiv cs gt' THEN 'Computer Science and Game Theory'
WHEN c.name='arxiv cs cv' THEN 'Computer Vision and Pattern Recognition'
WHEN c.name='arxiv cs cy' THEN 'Computers and Society'
WHEN c.name='arxiv cs cr' THEN 'Cryptography and Security'
WHEN c.name='arxiv cs ds' THEN 'Data Structures and Algorithms'
WHEN c.name='arxiv cs db' THEN 'Databases'
WHEN c.name='arxiv cs dl' THEN 'Digital Libraries'
WHEN c.name='arxiv cs dm' THEN 'Discrete Mathematics'
WHEN c.name='arxiv cs dc' THEN 'Distributed, Parallel, and Cluster Computing'
WHEN c.name='arxiv cs et' THEN 'Emerging Technologies'
WHEN c.name='arxiv cs fl' THEN 'Formal Languages and Automata Theory'
WHEN c.name='arxiv cs gl' THEN 'General Literature'
WHEN c.name='arxiv cs gr' THEN 'Graphics'
WHEN c.name='arxiv cs ar' THEN 'Hardware Architecture'
WHEN c.name='arxiv cs hc' THEN 'Human-Computer Interaction'
WHEN c.name='arxiv cs ir' THEN 'Information Retrieval'
WHEN c.name='arxiv cs it' THEN 'Information Theory'
WHEN c.name='arxiv cs lo' THEN 'Logic in Computer Science'
WHEN c.name='arxiv cs lg' THEN 'Machine Learning'
WHEN c.name='arxiv cs ms' THEN 'Mathematical Software'
WHEN c.name='arxiv cs ma' THEN 'Multiagent Systems'
WHEN c.name='arxiv cs mm' THEN 'Multimedia'
WHEN c.name='arxiv cs ni' THEN 'Networking and Internet Architecture'
WHEN c.name='arxiv cs ne' THEN 'Neural and Evolutionary Computing'
WHEN c.name='arxiv cs na' THEN 'Numerical Analysis'
WHEN c.name='arxiv cs os' THEN 'Operating Systems'
WHEN c.name='arxiv cs oh' THEN 'Other Computer Science'
WHEN c.name='arxiv cs pf' THEN 'Performance'
WHEN c.name='arxiv cs pl' THEN 'Programming Languages'
WHEN c.name='arxiv cs ro' THEN 'Robotics'
WHEN c.name='arxiv cs si' THEN 'Social and Information Networks'
WHEN c.name='arxiv cs se' THEN 'Software Engineering'
WHEN c.name='arxiv cs sd' THEN 'Sound'
WHEN c.name='arxiv cs sc' THEN 'Symbolic Computation'
WHEN c.name='arxiv cs sy' THEN 'Systems and Control'
ELSE "UNDEFINED"
END



Added
match (a:Article)
where a.year<=2017
set a.known_category = a.category