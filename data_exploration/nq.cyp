['id', 'lemmas', 'embeddings', 'keywords']

EXPLAIN UNWIND $events AS event
match (a:Article{id:event.id})
set a.embeddings=event.embeddings
with a
UNWIND event.lemmas as lemma
MERGE (l:Lemma{word:lemma})
with (a,lemma)
MERGE (a)-[rel:CONTAINS]->(l)
ON CREATE SET rel.weight = 1
ON MATCH SET rel.weight +=1
with (a)
UNWIND event.keywords as keyword
MERGE (k:Keyword{word:keyword[0]})
with (a,k)
MERGE (a)-[rel:ABOUT]->(k)
ON CREATE SET rel.score = keyword[1]
ON MATCH SET rel.score = CASE WHEN rel.score > keyword[0] THEN rel.score ELSE keyword[0] END;

// CHECK FOR EMBEDINGS FORMAT

UNWIND $events AS event
match (a:Article{id:event.id})
set a.embeddings=event.embeddings

CREATE CONSTRAINT IF NOT EXISTS FOR (n:Stem) REQUIRE n.word IS UNIQUE

explian
UNWIND $events AS event
match (a:Article{id:event.id})
with a
UNWIND event.lemmas as lemma
MERGE (l:Lemma{word:lemma})
with (a,lemma)
MERGE (a)-[rel:CONTAINS]->(l)
ON CREATE SET rel.weight = 1
ON MATCH SET rel.weight +=1



CREATE CONSTRAINT IF NOT EXISTS FOR (n:Keyword) REQUIRE n.word IS UNIQUE

explain 
UNWIND $events as event
match (a:Article{id:event.id})
with a,event
UNWIND event.result as stem
MERGE (s:Stem{word:stem})
with a,s
MERGE (a)-[rel:CONTAINS]->(s)
ON CREATE SET rel.weight = 1
ON MATCH SET rel.weight = rel.weight+1


CREATE CONSTRAINT IF NOT EXISTS FOR (n:Article) REQUIRE n.id IS UNIQUE
CREATE CONSTRAINT IF NOT EXISTS FOR (n:Category) REQUIRE n.id IS UNIQUE

explain
UNWIND $events as event
match (a:Article{id:event.id})
with a,event
UNWIND event.keywords as keyword
MERGE (k:Keyword{word:keyword.`1`})
with a,k,toInteger(keyword.`0`) as score
MERGE (a)-[rel:ABOUT]->(k)
ON CREATE SET rel.score = score
ON MATCH SET rel.score = CASE WHEN rel.score > score THEN rel.score ELSE score END


UNWIND $events as event
UNWIND event.keywords as keyword
MERGE (k:Keyword{word:keyword.`1`})

explain 
UNWIND $events as event
match (a:Article{id:event.id})
UNWIND event.keywords as keyword
match (k:Keyword{word:keyword.`1`})
with a,k,toInteger(keyword.`0`) as score
MERGE (a)-[rel:ABOUT]->(k)
ON CREATE SET rel.score = score
ON MATCH SET rel.score = CASE WHEN rel.score > score THEN rel.score ELSE score END


match (:Article)-[c:CONTAINS]->(:Stem) with c LIMIT 10000 delete c



match (:Stem)<-[c:CONTAINS]-(a:Article) with a,sum(c.weight) as terms SET a.terms = terms


match (:Stem)<-[c:CONTAINS]-(a:Article) SET c.tf = c.weight/a.terms

explain
match (a1:Article) 
with count(a1) as documents 
match (s:Stem)<-[c:CONTAINS]-(a2:Article)
with documents,s,count(a2) as termSpecificity
set s.idf = 1+ log(documents/(1+termSpecificity))

match (s:Stem)<-[c:CONTAINS]-(:Article) SET c.tfidf = s.idf*c.tf



match (:Keyword)<-[c:ABOUT]-(a:Article) with a,count(c) as keywords SET a.keywords = keywords

match (:Keyword)<-[c:ABOUT]-(a:Article) SET c.tf = 1/a.keywords

match (a1:Article) 
with count(a1) as documents 
match (k:Keyword)<-[c:ABOUT]-(a2:Article)
with documents,k,count(a2) as keywordSpecificity
set k.idf = 1+ log(documents/(1+keywordSpecificity))

match (k:Keyword)<-[c:ABOUT]-(:Article) SET c.tfidf = s.idf*c.tf
match (k:Keyword)<-[c:ABOUT]-(:Article) SET c.wtfidf = c.score*c.tfidf


most pupular tags

most popular tags in category

match (a:Article)-->(k:Keyword) return k.word,count(a) as degree order by degree desc  




explain
UNWIND $events as event
match (a:Article{id:event.id}),(s:Stem{word:event.result})
with a,s,event
MERGE (a)-[rel:CONTAINS{weight:event.count}]->(s)






// Mapper for ar



MATCH (:Stem)-[r:COOCURES]->(:Stem)
CALL { WITH r
DELETE r
} IN TRANSACTIONS OF 10000 ROWS;

MATCH (s:Steam)
CALL { WITH s
DETACH DELETE s
} IN TRANSACTIONS OF 10000 ROWS;