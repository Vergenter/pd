
// remove relationships without year

match (a:Article)
MATCH (a:Article) WHERE NOT EXISTS(a.year) delete a
match (a:Article) return a.year,count(a) order by a.year asc
//  a.year	count(a)
//  1971	1
//  1986	1
//  1987	1
//  1988	1
//  1990	3
//  1991	3
//  1992	1
//  1993	8
//  1994	19
//  1995	25
//  1996	31
//  1997	33
//  1998	123
//  1999	165
//  2000	261
//  2001	248
//  2002	355
//  2003	387
//  2004	415
//  2005	629
//  2006	968
//  2007	1302
//  2008	1931
//  2009	2499
//  2010	3564
//  2011	4427
//  2012	6435
//  2013	8135
//  2014	9154
//  2015	12035
//  2016	16339
//  2017	21442
//  2018	29799
//  2019	39711
//  2020	8892
//  null	2

CALL gds.graph.project(
  'allArticlesDirected',                    
  {Article:{properties: 'year'}},                             
  'CITES'  
)
YIELD
  graphName AS graph,
  relationshipProjection AS knowsProjection,
  nodeCount AS nodes,
  relationshipCount AS rels
// nodes rels 
// 169343	1166243



CALL gds.graph.project(
  'allArticlesUndirected',                    
  {Article:{properties: 'year'}},                             
  {CITES: {orientation: 'UNDIRECTED'}}  
)
YIELD
  graphName AS graph,
  relationshipProjection AS knowsProjection,
  nodeCount AS nodes,
  relationshipCount AS rels
// nodes rels 
// 69343	2332486

CALL gds.beta.graph.project.subgraph('2003ArticlesDirected','allArticlesDirected','n.year <= 2003','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2007ArticlesDirected','allArticlesDirected','n.year <= 2007','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2010ArticlesDirected','allArticlesDirected','n.year <= 2010','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2013ArticlesDirected','allArticlesDirected','n.year <= 2013','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2016ArticlesDirected','allArticlesDirected','n.year <= 2016','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2018ArticlesDirected','allArticlesDirected','n.year <= 2018','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2020ArticlesDirected','allArticlesDirected','n.year <= 2020','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;

CALL gds.beta.graph.project.subgraph('2003ArticlesUndirected','allArticlesUndirected','n.year <= 2003','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2007ArticlesUndirected','allArticlesUndirected','n.year <= 2007','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2010ArticlesUndirected','allArticlesUndirected','n.year <= 2010','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2013ArticlesUndirected','allArticlesUndirected','n.year <= 2013','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2016ArticlesUndirected','allArticlesUndirected','n.year <= 2016','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2018ArticlesUndirected','allArticlesUndirected','n.year <= 2018','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;
CALL gds.beta.graph.project.subgraph('2020ArticlesUndirected','allArticlesUndirected','n.year <= 2020','*') YIELD graphName, fromGraphName, nodeCount, relationshipCount;


// page rank memory

CALL gds.pageRank.write.estimate('2003ArticlesDirected', { writeProperty: 'pageRank'}) YIELD nodeCount, relationshipCount, requiredMemory return nodeCount, relationshipCount, requiredMemory UNION ALL
CALL gds.pageRank.write.estimate('2007ArticlesDirected', { writeProperty: 'pageRank'}) YIELD nodeCount, relationshipCount, requiredMemory return nodeCount, relationshipCount, requiredMemory UNION ALL
CALL gds.pageRank.write.estimate('2010ArticlesDirected', { writeProperty: 'pageRank'}) YIELD nodeCount, relationshipCount, requiredMemory return nodeCount, relationshipCount, requiredMemory UNION ALL
CALL gds.pageRank.write.estimate('2013ArticlesDirected', { writeProperty: 'pageRank'}) YIELD nodeCount, relationshipCount, requiredMemory return nodeCount, relationshipCount, requiredMemory UNION ALL
CALL gds.pageRank.write.estimate('2016ArticlesDirected', { writeProperty: 'pageRank'}) YIELD nodeCount, relationshipCount, requiredMemory return nodeCount, relationshipCount, requiredMemory UNION ALL
CALL gds.pageRank.write.estimate('2018ArticlesDirected', { writeProperty: 'pageRank'}) YIELD nodeCount, relationshipCount, requiredMemory return nodeCount, relationshipCount, requiredMemory UNION ALL
CALL gds.pageRank.write.estimate('2020ArticlesDirected', { writeProperty: 'pageRank'}) YIELD nodeCount, relationshipCount, requiredMemory return nodeCount, relationshipCount, requiredMemory
// nodeCount	relationshipCount	requiredMemory
// 1666	1855	"40 KiB"
// 4980	6103	"118 KiB"
// 12974	21090	"306 KiB"
// 31971	71669	"753 KiB"
// 69499	237163	"1638 KiB"
// 120740	622466	"2845 KiB"
// 169343	1166243	"3990 KiB"

CALL gds.pageRank.stats('2003ArticlesDirected') YIELD ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis return ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis UNION ALL
CALL gds.pageRank.stats('2007ArticlesDirected') YIELD ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis return ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis UNION ALL
CALL gds.pageRank.stats('2010ArticlesDirected') YIELD ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis return ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis UNION ALL
CALL gds.pageRank.stats('2013ArticlesDirected') YIELD ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis return ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis UNION ALL
CALL gds.pageRank.stats('2016ArticlesDirected') YIELD ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis return ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis UNION ALL
CALL gds.pageRank.stats('2018ArticlesDirected') YIELD ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis return ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis UNION ALL
CALL gds.pageRank.stats('2020ArticlesDirected') YIELD ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis return ranIterations, didConverge, preProcessingMillis, computeMillis, postProcessingMillis 
// ranIterations	didConverge	preProcessingMillis	computeMillis	postProcessingMillis
// 20	false	0	59	0
// 20	false	0	53	0
// 20	false	0	97	0
// 20	false	0	95	0
// 20	false	0	349	0
// 20	false	0	291	0
// 20	false	0	326	0