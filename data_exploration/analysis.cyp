// Number of nodes and edges
match (a:Article)
return count(*) as Article_Count
// Article_Count
// 169344
// Started streaming 1 records after 1 ms and completed after 1 ms.

match (:Article)<-[rel:CITES]-(:Article)
return count(rel) as CITES_Count
// CITES_Count
// 1166243
// Started streaming 1 records in less than 1 ms and completed after 796 ms.

// MAXDENSITY = n*(n-1) for directed and n*(n-1)/2 for undirected
// precentile density = connections/(n*(n-1))
// 1166243/(169344 * 169343) = 0.000040668 <=>sparseness,
// 1166243/169344 = 6.886827995
match (c:Category)
return count(*) as Category_Count
// nodes per category and per time
match (c:Category)<-[:OF_CATEGORY]-(a:Article)
return c.name, count(a) as Article_Count

match (c:Category)<-[:OF_CATEGORY]-(a:Article)
return c.name, a.year, count(a) as Article_Count

// single articles
match (a:Article)
where NOT (a)-[:CITES]-(:Article)
return count(a)


// for arxiv and edge per category

// how much article is cited
match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)<-[rel:CITES]-(:Article)
return c1.name, count(rel) as CITES_Count
// how much article cites
match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)-[rel:CITES]->(:Article)
return c1.name, count(rel) as CITES_Count

match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)<-[rel:CITES]-(a2:Article)
where a1.year>=a2.year
return c1.name, a1.year, count(rel) as CITES_Count

match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)<-[rel:CITES]-(a2:Article)
return c1.name, a1.year,a2.year, count(rel) as CITES_Count

// cross category neighbours


match (c1:Category)<-[:OF_CATEGORY]-(:Article)<-[:CITES]-(:Article)-[:OF_CATEGORY]->(c2:Category)
where id(c1) <> id(c2)
return c1.name,c2.name, count(*) as Article_Count

// for year
match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)<-[:CITES]-(a2:Article)-[:OF_CATEGORY]->(c2:Category)
where id(c1) <>  id(c2)
return c1.name,c2.name,a1.year, count(*) as Article_Count

// between years
match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)-[:CITES]-(a2:Article)-[:OF_CATEGORY]->(c2:Category)
where id(c1) <>  id(c2)
return c1.name,c2.name,a1.year,a2.year, count(*) as Article_Count

// get node with most categories neighbours
match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)<-[:CITES]-(a2:Article)-[:OF_CATEGORY]->(c2:Category)
where id(c1) <>  id(c2)
return a1.title,count(distinct c2) as connected_categories
ORDER BY connected_categories DESC

// get node with most categories neighbours
match (c1:Category)<-[:OF_CATEGORY]-(a1:Article)-[:CITES]->(a2:Article)-[:OF_CATEGORY]->(c2:Category)
where id(c1) <>  id(c2)
return a1.title,count(distinct c2) as connected_categories
ORDER BY connected_categories DESC


// // set degree
// MATCH (p:Article)
// SET p.degree = apoc.node.degree(p, "CITES")


CALL gds.graph.project('graph', 'Article', 'CITES')

CALL gds.graph.list('graph')
YIELD graphName, degreeDistribution;

// CENTRALITIES


// degree centrality

// get outDegree 
CALL gds.degree.write('graph', { writeProperty: 'outDegree',orientation: 'REVERSE' })
YIELD centralityDistribution, nodePropertiesWritten
RETURN centralityDistribution.min AS minimumScore, centralityDistribution.mean AS meanScore, nodePropertiesWritten
// minimumScore	meanScore	nodePropertiesWritten
// 0.0	6.88684698788397	169344
// Started streaming 1 records after 1 ms and completed after 2371 ms.

// get degree distribution
MATCH (n:Article) WITH n RETURN n.outDegree ,count(n.outDegree) as count ORDER BY n.outDegree

// get inDegree 
CALL gds.degree.write('graph', { writeProperty: 'inDegree',orientation: 'NATURAL' })
YIELD centralityDistribution, nodePropertiesWritten
RETURN centralityDistribution.min AS minimumScore, centralityDistribution.mean AS meanScore, nodePropertiesWritten
// minimumScore	meanScore	nodePropertiesWritten
// 0.0	6.886847502295032	169344
// Started streaming 1 records after 1 ms and completed after 1208 ms.

// get degree distribution
MATCH (n:Article) WITH n RETURN n.inDegree ,count(n.inDegree) as count ORDER BY inDegree


// closeness centrality
CALL gds.beta.closeness.stats('graph')
YIELD centralityDistribution,computeMillis,postProcessingMillis,preProcessingMillis,configuration
// Started streaming 1 records in less than 1 ms and completed after 266034 ms.

CALL gds.beta.closeness.write('graph', { writeProperty: 'closenessCentrality'})
YIELD centralityDistribution, nodePropertiesWritten
RETURN centralityDistribution.min AS minimumScore, centralityDistribution.mean AS meanScore, nodePropertiesWritten
// minimumScore	meanScore	nodePropertiesWritten
// 0.0	0.30212856283466294	169344
// Started streaming 1 records after 1 ms and completed after 258632 ms.

// betweenness centrality
CALL gds.beta.closeness.write('graph', { writeProperty: 'closenessCentrality'})
YIELD centralityDistribution, nodePropertiesWritten
RETURN centralityDistribution.min AS minimumScore, centralityDistribution.mean AS meanScore, nodePropertiesWritten



CALL gds.betweenness.write.estimate('stemGraph', { writeProperty: 'betweenness' })
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory

match (s:Stem) return count(s)
// 262775
CALL gds.betweenness.stats('stemGraph',{samplingSize:10000})
YIELD centralityDistribution,computeMillis,postProcessingMillis,preProcessingMillis,configuration

CALL gds.beta.graph.project.subgraph(
  graphName: String,
  fromGraphName: String,
  nodeFilter: String,
  relationshipFilter: String,
  configuration: Map
) YIELD
  graphName: String,
  fromGraphName: String,
  nodeFilter: String,
  relationshipFilter: String,
  nodeCount: Integer,
  relationshipCount: Integer,
  projectMillis: Integer


// Wasserman and Faust and Harmonic are upgrade of this


CALL gds.betweenness.stats('graph')
YIELD centralityDistribution,computeMillis,postProcessingMillis,preProcessingMillis,configuration

// Bad result -> "p99": 3968479.9999999404,
// Started streaming 1 records after 1 ms and completed after 984329 ms.
// It's good result :D



CALL gds.betweenness.stats('graph', {samplingSize: 2, samplingSeed: 42})
YIELD centralityDistribution,computeMillis,postProcessingMillis,preProcessingMillis,configuration

// "p99": 42.285888612270355,
// Started streaming 1 records after 1 ms and completed after 497 ms.

// moemory estimation
CALL gds.betweenness.write.estimate('myGraph', { writeProperty: 'betweenness' })
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory
// nodeCount	relationshipCount	bytesMin	bytesMax	requiredMemory
// 169344	1166243	74513048	74513048	"71 MiB"
// Started streaming 1 records after 1 ms and completed after 2 ms.

CALL gds.pageRank.write.estimate('graph', {
  writeProperty: 'pageRank',
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory
// nodeCount	relationshipCount	bytesMin	bytesMax	requiredMemory
// 169344	1166243	4086208	4086208	"3990 KiB"
// Started streaming 1 records after 1 ms and completed after 3 ms.

CALL gds.pageRank.stats('graph',{
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD centralityDistribution,computeMillis,postProcessingMillis,preProcessingMillis,configuration

// centralityDistribution	computeMillis	postProcessingMillis	preProcessingMillis	configuration
// "p99": 5.187560081481934,
// Started streaming 1 records in less than 1 ms and completed after 972 ms.

// possible use of scaler scaler: "L1Norm"
// Personalized PageRank for ego analysis
// ArticleRank as alternative 

// eigenvector
CALL gds.eigenvector.write.estimate('graph', {
  writeProperty: 'centrality',
  maxIterations: 20
})
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory
// nodeCount	relationshipCount	bytesMin	bytesMax	requiredMemory
// 169344	1166243	4086208	4086208	"3990 KiB"
// Started streaming 1 records after 1 ms and completed after 2 ms.

CALL gds.eigenvector.stats('graph',{
  maxIterations: 20
})
YIELD ranIterations,
  didConverge,
  preProcessingMillis,
  computeMillis,
  postProcessingMillis,
  centralityDistribution
  
//   Started streaming 1 records in less than 1 ms and completed after 1107 ms.
// "Error": "Unable to create histogram due to range of scores exceeding implementation limits."}
// But it's not a problem :)



// HITS

CALL gds.alpha.hits.stats('graph', {hitsIterations: 20})
YIELD ranIterations,  didConverge,  preProcessingMillis,  computeMillis
// ranIterations	didConverge	preProcessingMillis	computeMillis
// 81	false	0	3507
// Started streaming 1 records after 1 ms and completed after 3751 ms.

CALL gds.alpha.hits.write('graph', {
    authProperty:"autority",
    hubProperty:"hub"
})

// Mention Influence maximization but skip cause no usefull info


// Community detection


// https://neo4j.com/docs/graph-data-science/current/algorithms/triangle-count/ skip it but mention
// https://neo4j.com/docs/graph-data-science/current/algorithms/local-clustering-coefficient/ same
// strongly connected components

CALL gds.louvain.stats('graph')
YIELD preProcessingMillis,
  computeMillis,
  postProcessingMillis,
  communityCount,
  ranLevels,
  modularity,
  modularities,
  communityDistribution
// preProcessingMillis	computeMillis	postProcessingMillis	communityCount	ranLevels	modularity	modularities	communityDistribution
// 0	2444	49	6842	2	0.5780849234313209	[0.43336651177054625, 0.5780849234313209]	"p99": 231,
// Started streaming 1 records after 1 ms and completed after 2506 ms.



CALL gds.labelPropagation.stats('graph')
YIELD preProcessingMillis,
  computeMillis,
  postProcessingMillis,
  communityCount,
  ranIterations,
  didConverge,
  communityDistribution
// preProcessingMillis	computeMillis	postProcessingMillis	communityCount	ranIterations	didConverge	communityDistribution
// 0	514	24	18110	10	false	"p99": 69,
// Started streaming 1 records after 1 ms and completed after 544 ms.

// semantci brand score
// PREVALENCE

match (s:Stem)<-[c:CONTAINS]-(a:Article)
with s,a,sum(c.weight) as prevalence
return s,a.year,prevalence

CREATE CONSTRAINT IF NOT EXISTS FOR (y:Year) REQUIRE y.year IS UNIQUE

match (a:Article)
with collect(distinct a.year) as years
unwind years as year
create (:Year{year:year})

match (s:Stem)<-[c:CONTAINS]-(a:Article)
with s,a.year as year,sum(c.weight) as prevalence
match (y:Year{year:year})
with y,s,prevalence
merge (s)-[:PREVALENCE{value:prevalence}]->(y)
// Set 671524 properties, created 671524 relationships, completed after 37245 ms.

match (y:Year)<-[p:PREVALENCE]-(:Stem) 
with y,stDevP(p.value) as std,avg(p.value) as avg
set y.avgYearlyPrevalence = avg
set y.stdYearlyPrevalence = std
// Set 70 properties, completed after 857 ms.

// DIVERSITY FROM NETWORKX
match (y:Year)<-[p:DISTINCTIVENESS]-(:Stem) 
with y,stDevP(p.value) as std,avg(p.value) as avg
set y.avgYearlydistinctiveness = avg
set y.stdYearlydistinctiveness = std

// BETWEENNESS FROM NETWORKX
match (y:Year)<-[p:BETWEENNESS]-(:Stem) 
with y,stDevP(p.value) as std,avg(p.value) as avg
set y.avgYearlybetweenness = avg
set y.stdYearlybetweenness = std


// Get result

match (s:Stem{word:"spark"})-[prevalence:PREVALENCE]->(y:Year),(s)-[distincitveness:DISTINCTIVENESS]->(y),(s)-[betweenness:BETWEENNESS]->(y)
with s.word as word,y.year as year,
(prevalence.value/y.avgYearlyPrevalence)/y.stdYearlyPrevalence as normalizedPrevalence,
(distincitveness.value/y.avgYearlydistinctiveness)/y.stdYearlydistinctiveness as normalizedDistincitveness,
(betweenness.value/y.avgYearlybetweenness)/y.stdYearlybetweenness as normalizedBetweenness
return word,year,normalizedPrevalence+normalizedDistincitveness+normalizedBetweenness as semanticBrandScore
order by year ASC

// some analysis
match (s:Stem)-[prevalence:PREVALENCE]->(y:Year),(s)-[distincitveness:DISTINCTIVENESS]->(y),(s)-[betweenness:BETWEENNESS]->(y)
with s.word as word,y.year as year,
(prevalence.value/y.avgYearlyPrevalence)/y.stdYearlyPrevalence as normalizedPrevalence,
(distincitveness.value/y.avgYearlydistinctiveness)/y.stdYearlydistinctiveness as normalizedDistincitveness,
(betweenness.value/y.avgYearlybetweenness)/y.stdYearlybetweenness as normalizedBetweenness
with word,year,normalizedPrevalence+normalizedDistincitveness+normalizedBetweenness as semanticBrandScore
return word,year,semanticBrandScore
order by semanticBrandScore DESC
limit 10

match (s:Stem)-[prevalence:PREVALENCE]->(y:Year{year:2019}),(s)-[distincitveness:DISTINCTIVENESS]->(y),(s)-[betweenness:BETWEENNESS]->(y)
with s.word as word,y.year as year,
(prevalence.value/y.avgYearlyPrevalence)/y.stdYearlyPrevalence as normalizedPrevalence,
(distincitveness.value/y.avgYearlydistinctiveness)/y.stdYearlydistinctiveness as normalizedDistincitveness,
(betweenness.value/y.avgYearlybetweenness)/y.stdYearlybetweenness as normalizedBetweenness
with word,year,normalizedPrevalence+normalizedDistincitveness+normalizedBetweenness as semanticBrandScore
return word,year,semanticBrandScore
order by semanticBrandScore DESC
limit 10


// DIVERSITY
// distincitveness centrality

match (a1:Stem)-->(a2:Stem) return count(*)

MATCH (a1:Stem)-[c:COOCURES]-(:Stem)
with a1,c.


MATCH (a1:Stem)--(a2:Stem)
with a1,collect(a2.inDegree) as indeg,collect(a2.outDegree)as outdeg
SET a1.neighboursDegree = toInteger(apoc.coll.sum(indeg) + apoc.coll.sum(outdeg))
// Set 169343 properties, completed after 7205 ms.

match (s:Stem)-[distincitveness:DISTINCTIVENESS]->(y:Year)
with distincitveness limit 1000000
delete distincitveness


CALL gds.degree.write('stemGraph', { writeProperty: 'inDegree',orientation: 'NATURAL' })
YIELD centralityDistribution, nodePropertiesWritten
RETURN centralityDistribution.min AS minimumScore, centralityDistribution.mean AS meanScore, nodePropertiesWritten


// generate graph
CALL gds.graph.project('stemGraph','Stem',{COOCURES: { orientation: 'NATURAL'}})
// Started streaming 1 records in less than 1 ms and completed after 4933 ms.

// calculate degree for later propagation
CALL gds.degree.write('stemGraph', { writeProperty: 'degree',orientation: 'UNDIRECTED' })
YIELD centralityDistribution, nodePropertiesWritten
RETURN centralityDistribution.min AS minimumScore, centralityDistribution.mean AS meanScore, nodePropertiesWritten
// Started streaming 1 records in less than 1 ms and completed after 1776 ms.

// slightly modified because I have coocurence to itself inf oposite situaiotn stemCount should be reduces by one
MATCH (s:Stem)
with count(s) as stemCount
MATCH (a1:Stem)
set a1.selfDistinctivenessFactor = log10(stemCount/a1.degree)
// Set 262775 properties, completed after 691 ms.

MATCH (a1:Stem)--(a2:Stem)
with a1,collect(a2.selfDistinctivenessFactor) as factors
SET a1.DistinctivenessCentrality = apoc.coll.sum(factors) 
// Set 262774 properties, completed after 123351 ms.

 
MATCH (s:Stem)
return stDevP(s.DistinctivenessCentrality)as std,avg(s.DistinctivenessCentrality) as avg
// std	avg
// 2492.7310950976243	335.20050363722856
// Started streaming 1 records after 18 ms and completed after 189 ms.

CALL gds.beta.closeness.write('graph', { writeProperty: 'closenessCentrality'})
YIELD centralityDistribution, nodePropertiesWritten
RETURN centralityDistribution.min AS minimumScore, centralityDistribution.mean AS meanScore, nodePropertiesWritten

// get link weights for future filtering
MATCH (a1:Stem)-[rel:COOCURES]-(:Stem)
with a1,collect(rel.weight) as weights
SET a1.linkWeight = apoc.coll.sum(weights)
// Set 262774 properties, completed after 221548 ms.

// find distribution to find when to filter
MATCH (a1:Stem) 
with a1.linkWeight as linkWeight,collect(a1.linkWeight) as linkWeights
return linkWeight,apoc.coll.sum(LinkWeights) as weightDistribution
ORDER BY weightDistribution












CALL gds.alpha.scc.write('graph', {
  writeProperty: 'componentId'
})
YIELD setCount, maxSetSize, minSetSize;

match (a:Article) 
return a.componentId,count(distinct a.category) as cat, count(a.componentId) as cnt
ORDER BY cnt DESC

// shortest paths
CALL gds.alpha.allShortestPaths.stream('graph', null)
YIELD sourceNodeId, targetNodeId, distance

WITH sourceNodeId, targetNodeId, distance
WHERE gds.util.isFinite(distance) = true
MATCH (source:Article) WHERE id(source) = sourceNodeId
MATCH (target:Article) WHERE id(target) = targetNodeId

WITH source, target, distance WHERE source <> target
RETURN source.name AS source, target.name AS target, distance
ORDER BY distance DESC, source ASC, target ASC
LIMIT 10

// calculate diameter
MATCH (n:Article)
WITH collect(n) AS nodes
UNWIND nodes AS a
UNWIND nodes AS b
WITH a, b
WHERE id(a) < id(b)
MATCH path=shortestPath((a)-[:Cites]-(b))
RETURN length(path) AS diameter
ORDER BY diameter
DESC LIMIT 1










match (c:Category)<-[:OF_CATEGORY]-(a:Article) 
with c.humanName as category,collect(a.id) as articles
with category, apoc.coll.randomItems(articles, 100) AS articlesSample
unwind articlesSample as article
with collect(article) as ids
match (a1:Article),(a2:Article) where a1.id<>a2.id and a1.id in ids and a2.id in ids 
return a1.id,gds.similarity.cosine(a1.embeddings,a2.embeddings),a2.id


gds.similarity.cosine

match (c:Category)<-[:OF_CATEGORY]-(a:Article)
where a.embeddings
with c.humanName as category,collect(a.id) as articles
with category, apoc.coll.randomItems(articles, 50) AS articlesSample
unwind articlesSample as article
with collect(article) as ids
unwind apoc.coll.combinations(ids,2,2) as pair
match (a1:Article{id:pair[0]}),(a2:Article{id:pair[1]})
CREATE (a1)-[:SIMILARITY{cosine:toFloat(gds.similarity.cosine(a1.embeddings,a2.embeddings))}]->(a2)
// Set 1957231 properties, created 1957231 relationships, completed after 230853 ms.
match (c1:Category)<-[:OF_CATEGORY]-(:Article)-[r:SIMILARITY]-(:Article)-[:OF_CATEGORY]->(c2:Category)
return c1.humanName,avg(r.cosine) as similarity,c2.humanName
order by similarity desc

match (c1:Category)<-[:OF_CATEGORY]-(:Article)-[sr:SIMILARITY]->(:Article)-[:OF_CATEGORY]->(c2:Category)
with c1,avg(sr.cosine) as similarity,c2
create (c1)-[:SIMILARITY{value:similarity}]->(c2)
// Set 1600 properties, created 1600 relationships, completed after 18269 ms.
match (c1:Category)-[sr:SIMILARITY]-(c2:Category)
return c1,sum(sr.value) as similarity,count(c2) as count
create (c1)-[:SIMILARITY{value:similarity}]->(c2)

match (c:Category)<-[:OF_CATEGORY]-(:Article)-[sr:SIMILARITY]->(:Article)-[:OF_CATEGORY]->(c:Category)
with avg(sr.cosine) as selfsimilarity
match (c1:Category)<-[:OF_CATEGORY]-(:Article)-[r:SIMILARITY]->(:Article)-[:OF_CATEGORY]->(c2:Category)
with c1,sum(r.cosine) as similarity,count(c2) as categoriesCount,c2,selfsimilarity
CREATE (c1)-[:DIFFERENCE{value:(similarity-2*selfsimilarity)/(categoriesCount-1)}]->(c2)

match (c1:Category)-[r:DIFFERENCE]->(c2:Category)
return c1.humanName,r.value,c2.humanName

match (c1:Category)-[sr:SIMILARITY]-(c2:Category)
with c1,avg(sr.value) as avg
set sr.avg = avg

// mean difference
match (c:Category)-[sr:SIMILARITY]->(c:Category)
with sr.value as selfsimilarity,c
match (c)-[sr:SIMILARITY]-(c2:Category) where c<>c2
with c,avg(sr.value) as similarity,count(c2) as categoriesCount,selfsimilarity
return c.humanName,(similarity-selfsimilarity)/(categoriesCount) as meanDifference
order by meanDifference asc

// set in gephi http://192.168.0.178:7687/
match path = (c1:Category)-[sr:SIMILARITY]-(c2:Category)
with collect(path) as paths
call apoc.gephi.add("http://192.168.0.178:8080",'workspace1', paths,"deavgsimilarity",['type','humanName']) yield nodes, relationships, time
return nodes, relationships, time


match (c1:Category)-[sr:SIMILARITY]-(c2:Category)
set sr.deavgsimilarity = sr.simic1.avgSimilarity

match (c1:Category)-[sr:SIMILARITY]-(c2:Category)
set sr.deavgsimilarity = sr.value - c1.avgSimilarity

// Most cited article
match (:Article)-[r:CITES]->(a :Article) with a,count(r) as count return a.title,count order by count desc limit 1

// Citation from which year
match (a1:Article)-[c:CITES]->(a2:Article{id:1353}) with a2,a1.year as year ,count(a1) as citations return a2.title as title, year ,citations

// 
match (c:Category)<-[:OF_CATEGORY]-(a1:Article)-[:CITES]->(a2:Article{id:1353})
with a2,count(a1) as count,c  
create (a2)-[:CITED_IN_CATEGORY{weight:count}]->(c)


match path = (a1:Article)-[c:CITED_IN_CATEGORY]->(cc:Category)

// set in gephi http://192.168.0.178:7687/
match path = (a1:Article)-[c:CITED_IN_CATEGORY]->(cc:Category)
with collect(path) as paths
call apoc.gephi.add("http://192.168.0.178:8080",'workspace1', paths,"weight",['type','title','humanName']) yield nodes, relationships, time
return nodes, relationships, time


// page rank on articles
CALL gds.graph.project(
  'articleGraph',
  'Article',
  'CITES',
)

CALL gds.pageRank.write.estimate('articleGraph', {
  writeProperty: 'pageRank',
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory

CALL gds.pageRank.write('articleGraph',{writeProperty:"pageRank"})
YIELD centralityDistribution, nodePropertiesWritten

match (a:Article) return a.title,a.year, a.pageRank, a.inDegree, a.betweenness  order by a.pageRank desc limit 3


CALL gds.betweenness.write.estimate('articleGraph', { writeProperty: 'betweenness' })
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory

CALL gds.betweenness.write('articleGraph', { writeProperty: 'betweenness', samplingSize: 10000, samplingSeed: 42})
YIELD centralityDistribution, nodePropertiesWritten

match (a:Article) return a.title,a.year, a.pageRank,a.inDegree, a.betweenness order by a.betweenness desc limit 3


CALL gds.degree.write('articleGraph', { writeProperty: 'inDegree', orientation:"REVERSE" })
YIELD centralityDistribution, nodePropertiesWritten

match (a:Article) return a.title,a.year, a.pageRank,a.inDegree, a.betweenness order by a.inDegree desc limit 3

CALL gds.graph.project(
  'keywordArticleGraph',
  ['Article',"Keyword"],
  ['CITES','ABOUT']
)

CALL gds.pageRank.write('keywordArticleGraph',{writeProperty:"keywordArticlePageRank"})
YIELD centralityDistribution, nodePropertiesWritten

CALL gds.degree.write('keywordArticleGraph', { writeProperty: 'keywordArticleInDegree', orientation:"REVERSE" })
YIELD centralityDistribution, nodePropertiesWritten

match (k:Keyword) return k  order by k.keywordArticlePageRank desc limit 3

match (k:Keyword) return k  order by k.keywordArticleInDegree desc limit 3