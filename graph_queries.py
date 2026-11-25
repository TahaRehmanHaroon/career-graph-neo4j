import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


class CareerGraphEngine:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_all_skills(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                RETURN s.name AS name, s.category AS category
                ORDER BY s.category, s.name
            """)
            return result.data()

    def get_all_roles(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Role)
                RETURN r.name AS name, r.domain AS domain,
                       r.avg_salary AS avg_salary, r.demand_level AS demand_level,
                       r.roadmap_url AS roadmap_url
                ORDER BY r.name
            """)
            return result.data()

    def get_sample_candidates(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:Candidate)-[:HAS_SKILL]->(s:Skill)
                RETURN u.name AS name, u.current_role AS current_role,
                       collect(s.name) AS skills
                ORDER BY u.name
            """)
            return result.data()

    # 1. Weighted Role Compatibility Scoring
    def recommend_roles(self, user_skills):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Role)-[req:REQUIRES]->(s:Skill)
                WITH r,
                     sum(CASE WHEN req.importance = 'Core' THEN 2 ELSE 1 END) AS total_weight,
                     sum(CASE WHEN s.name IN $user_skills
                              THEN (CASE WHEN req.importance = 'Core' THEN 2 ELSE 1 END)
                              ELSE 0 END) AS earned_weight,
                     collect(CASE WHEN s.name IN $user_skills THEN s.name END) AS matched_skills,
                     collect(CASE WHEN NOT s.name IN $user_skills THEN s.name END) AS missing_skills
                RETURN r.name AS role,
                       r.domain AS domain,
                       r.avg_salary AS avg_salary,
                       r.demand_level AS demand_level,
                       round(toFloat(earned_weight) / total_weight * 100, 1) AS match_score,
                       [x IN matched_skills WHERE x IS NOT NULL] AS matched_skills,
                       [x IN missing_skills WHERE x IS NOT NULL] AS missing_skills
                ORDER BY match_score DESC, size(matched_skills) DESC
            """, user_skills=user_skills)
            return result.data()

    # 2. Skill-Gap & Course Roadmap Pathfinding
   # 2. Ordered Skill-Gap, Prerequisites & roadmap.sh Guide Pathfinding
    def get_learning_roadmap(self, target_role, user_skills):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Role {name: $target_role})-[req:REQUIRES]->(s:Skill)
                WHERE NOT s.name IN $user_skills
                OPTIONAL MATCH (prereq:Skill)-[:PREREQUISITE_FOR]->(s)
                WHERE NOT prereq.name IN $user_skills
                OPTIONAL MATCH (c:Course)-[:TEACHES]->(s)
                RETURN req.stage AS stage,
                       s.name AS missing_skill,
                       req.importance AS importance,
                       collect(DISTINCT prereq.name) AS learn_first,
                       s.guide_url AS roadmap_guide,
                       c.title AS course_title,
                       c.platform AS platform
                ORDER BY req.stage ASC, CASE req.importance WHEN 'Core' THEN 1 ELSE 2 END, s.name
            """, target_role=target_role, user_skills=user_skills)
            return result.data()

    # 3. Multi-Hop Career Transition Shortest Path
    def find_career_path(self, start_role, target_role):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (start:Role {name: $start_role}), (end:Role {name: $target_role})
                MATCH p = shortestPath((start)-[:TRANSITIONS_TO*1..5]->(end))
                RETURN [node IN nodes(p) | node.name] AS role_steps,
                       [rel IN relationships(p) | rel.difficulty] AS step_difficulties,
                       length(p) AS hops
            """, start_role=start_role, target_role=target_role)
            return result.data()

    # 4. Co-Occurring Skill Market Analysis
    def get_complementary_skills(self, skill_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s1:Skill {name: $skill_name})<-[:REQUIRES]-(r:Role)-[:REQUIRES]->(s2:Skill)
                WHERE s1 <> s2
                RETURN s2.name AS paired_skill,
                       s2.category AS category,
                       count(DISTINCT r) AS shared_roles,
                       collect(DISTINCT r.name) AS roles
                ORDER BY shared_roles DESC, paired_skill
                LIMIT 6
            """, skill_name=skill_name)
            return result.data()

    # 5. Full-Text Fuzzy Search (Modern Neo4j SEARCH syntax)
    def fuzzy_search(self, query_text):
        if not query_text.strip():
            return []
        fuzzy_term = " ".join([f"{word}~" for word in query_text.strip().split()])
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.fulltext.queryNodes("role_skill_fulltext", $term)
                YIELD node, score
                WHERE node:Role OR node:Skill
                RETURN labels(node)[0] AS type,
                       node.name AS name,
                       coalesce(node.domain, node.category) AS group_info,
                       round(score, 2) AS relevance
                LIMIT 8
            """, term=fuzzy_term)
            return result.data()

    # 6. Subgraph Data for PyVis Visualization
   # 6. Subgraph Data for PyVis Visualization (Includes Prerequisite Arrows!)
    def get_role_subgraph(self, target_role, user_skills):
        with self.driver.session() as session:
            skills_res = session.run("""
                MATCH (r:Role {name: $target_role})-[req:REQUIRES]->(s:Skill)
                OPTIONAL MATCH (c:Course)-[:TEACHES]->(s)
                RETURN r.name AS role,
                       s.name AS skill,
                       req.importance AS importance,
                       req.stage AS stage,
                       (s.name IN $user_skills) AS has_skill,
                       c.title AS course
            """, target_role=target_role, user_skills=user_skills).data()

            prereq_res = session.run("""
                MATCH (r:Role {name: $target_role})-[:REQUIRES]->(s1:Skill)
                MATCH (r)-[:REQUIRES]->(s2:Skill)
                MATCH (s1)-[:PREREQUISITE_FOR]->(s2)
                RETURN s1.name AS from_skill, s2.name AS to_skill
            """, target_role=target_role).data()

            return {"nodes": skills_res, "prereqs": prereq_res}


if __name__ == "__main__":
    engine = CareerGraphEngine()
    sample_skills = ["Python", "C++", "Data Structures & Algorithms", "Git & GitHub", "Neo4j & Cypher"]

    print("=== 1. TOP ROLE MATCHES ===")
    for r in engine.recommend_roles(sample_skills)[:3]:
        print(f" - {r['role']}: {r['match_score']}% match (Missing: {r['missing_skills']})")

    print("\n=== 2. LEARNING ROADMAP FOR AI & GRAPHRAG ENGINEER ===")
    for item in engine.get_learning_roadmap("AI & GraphRAG Engineer", sample_skills):
        print(f" - [{item['importance']}] Learn {item['missing_skill']} -> Course: {item['course_title']} ({item['platform']})")

    print("\n=== 3. CAREER TRANSITION PATH ===")
    paths = engine.find_career_path("Systems & C++ Developer", "AI & GraphRAG Engineer")
    for p in paths:
        print(f" - Path ({p['hops']} hops): {' -> '.join(p['role_steps'])} | Difficulties: {p['step_difficulties']}")

    print("\n=== 4. TOP SKILLS PAIRED WITH NEO4J & CYPHER ===")
    for s in engine.get_complementary_skills("Neo4j & Cypher")[:3]:
        print(f" - {s['paired_skill']} (Appears together in {s['shared_roles']} roles)")

    print("\n=== 5. FUZZY FULL-TEXT SEARCH ('pythn enginer') ===")
    for hit in engine.fuzzy_search("pythn enginer")[:3]:
        print(f" - [{hit['type']}] {hit['name']} ({hit['group_info']}) | Score: {hit['relevance']}")

    engine.close()