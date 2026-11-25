import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

SCHEMA_QUERIES = [
    # 1. Clear old recipe test data so our workspace is clean
    "MATCH (n) DETACH DELETE n",

    # 2. Uniqueness Constraints (also create automatic B-tree/Range indexes)
    "CREATE CONSTRAINT role_name_unique IF NOT EXISTS FOR (r:Role) REQUIRE r.name IS UNIQUE",
    "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
    "CREATE CONSTRAINT course_title_unique IF NOT EXISTS FOR (c:Course) REQUIRE c.title IS UNIQUE",
    "CREATE CONSTRAINT candidate_name_unique IF NOT EXISTS FOR (u:Candidate) REQUIRE u.name IS UNIQUE",

    # 3. Full-Text Search Index for fuzzy searching across Roles and Skills
    """
    CREATE FULLTEXT INDEX role_skill_fulltext IF NOT EXISTS
    FOR (n:Role|Skill) ON EACH [n.name, n.category, n.domain]
    """
]

def setup_schema():
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        for query in SCHEMA_QUERIES:
            session.run(query)
            print(f"Executed: {query.strip().splitlines()[0][:65]}...")

        # Verify constraints and indexes exist
        constraints = session.run("SHOW CONSTRAINTS").data()
        indexes = session.run("SHOW INDEXES").data()
        print(f"\nSchema ready! Active constraints: {len(constraints)} | Active indexes: {len(indexes)}")
    driver.close()

if __name__ == "__main__":
    setup_schema()