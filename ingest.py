import json
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")


def ingest_data(data_path="data/career_dataset.json"):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # 1. Batch Load Roles (with roadmap.sh URL)
        session.run("""
            UNWIND $rows AS row
            MERGE (r:Role {name: row.name})
            SET r.domain = row.domain,
                r.avg_salary = row.avg_salary,
                r.demand_level = row.demand_level,
                r.roadmap_url = row.roadmap_url
        """, rows=data["roles"])

        # 2. Batch Load Skills (with roadmap.sh topic guide URL)
        session.run("""
            UNWIND $rows AS row
            MERGE (s:Skill {name: row.name})
            SET s.category = row.category,
                s.guide_url = row.guide_url
        """, rows=data["skills"])

        # 3. Batch Load Skill -> Skill Prerequisite Chains
        session.run("""
            UNWIND $rows AS row
            MATCH (s1:Skill {name: row.from_skill})
            MATCH (s2:Skill {name: row.to_skill})
            MERGE (s1)-[:PREREQUISITE_FOR]->(s2)
        """, rows=data["prerequisites"])

        # 4. Batch Load Role -> Skill Requirements (with learning stage)
        session.run("""
            UNWIND $rows AS row
            MATCH (r:Role {name: row.role})
            MATCH (s:Skill {name: row.skill})
            MERGE (r)-[rel:REQUIRES]->(s)
            SET rel.importance = row.importance,
                rel.stage = row.stage
        """, rows=data["role_skills"])

        # 5. Batch Load Courses -> Teaches Skill
        session.run("""
            UNWIND $rows AS row
            MERGE (c:Course {title: row.title})
            SET c.platform = row.platform,
                c.level = row.level
            WITH c, row
            MATCH (s:Skill {name: row.skill})
            MERGE (c)-[:TEACHES]->(s)
        """, rows=data["courses"])

        # 6. Batch Load Career Transition Paths
        session.run("""
            UNWIND $rows AS row
            MATCH (r1:Role {name: row.from_role})
            MATCH (r2:Role {name: row.to_role})
            MERGE (r1)-[t:TRANSITIONS_TO]->(r2)
            SET t.difficulty = row.difficulty
        """, rows=data["transitions"])

        # 7. Batch Load Sample Candidates & Their Skills
        session.run("""
            UNWIND $rows AS cand
            MERGE (u:Candidate {name: cand.name})
            SET u.current_role = cand.current_role
            WITH u, cand
            UNWIND cand.skills AS sk
            MATCH (s:Skill {name: sk.name})
            MERGE (u)-[h:HAS_SKILL]->(s)
            SET h.proficiency = sk.proficiency
        """, rows=data["candidates"])

        rel_count = session.run("MATCH ()-[r:PREREQUISITE_FOR]->() RETURN count(r) AS c").single()["c"]
        print(f"Ingestion updated! Loaded {rel_count} skill prerequisite chains from roadmap.sh structure.")

    driver.close()


if __name__ == "__main__":
    ingest_data()