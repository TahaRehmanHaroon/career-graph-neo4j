# Career Path Graph 

[![Launch Live App](https://img.shields.io/badge/Launch_Live_App_%E2%86%97-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://career-graph-neo4j-bm2xwmyzk7wcwrivth4dub.streamlit.app/)
[![Database: Neo4j AuraDB](https://img.shields.io/badge/Database-Neo4j_AuraDB-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Curriculum: roadmap.sh](https://img.shields.io/badge/Curriculum-roadmap.sh-0F172A?style=flat-square)](https://roadmap.sh/)
[![Built With: Python 3.10+](https://img.shields.io/badge/Built_With-Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)

An interactive **Career & Skill Path Graph Recommender** powered by **Neo4j AuraDB**, **Cypher graph algorithms**, **PyVis**, and **Streamlit**—enriched with structured learning stages and topic guides from **roadmap.sh**.

Instead of relying on flat keyword matching, this application models tech roles, required skills, prerequisite chains, courses, and career transitions as a connected knowledge graph to generate explainable career recommendations and upskilling roadmaps.

**Live Web Application:** [https://career-graph-neo4j-bm2xwmyzk7wcwrivth4dub.streamlit.app/](https://career-graph-neo4j-bm2xwmyzk7wcwrivth4dub.streamlit.app/)

---

## Application Preview

### 1. Roles & Roadmap
<img width="1919" height="908" alt="image" src="https://github.com/user-attachments/assets/e5f1a1e6-4616-4dfb-a794-cd015a3a698c" />


### 2. Skill-Gap Graph
<img width="1150" height="896" alt="image" src="https://github.com/user-attachments/assets/743f1242-c4bd-42b9-bf2a-050f9820b82d" />


### 3. Market Explorer
<img width="1919" height="911" alt="image" src="https://github.com/user-attachments/assets/a147c45d-b799-402d-9451-7ca94f9fd541" />


### 4. Help
<img width="1766" height="904" alt="image" src="https://github.com/user-attachments/assets/3904f074-ea55-462b-ae57-6ac30b5916e0" />


---

## Key Features

* **Weighted Role Compatibility Engine:** Evaluates candidate skills against 10 tech roles using weighted Cypher aggregation (`2x` weight for **Core** skills, `1x` weight for **Bonus** skills).
* **Prerequisite-Aware Upskilling Roadmaps:** Traverses `(Role)-[:REQUIRES]->(Skill)<-[:TEACHES]-(Course)` alongside `[:PREREQUISITE_FOR]` chains to order missing skills from foundational stages to advanced topics, complete with direct **roadmap.sh** guide links.
* **Interactive PyVis Subgraph Visualization:** Dynamically renders a color-coded network (`Target Role`, `Owned Skill`, `Missing Skill`, `Course`, and dashed `PREREQUISITE_FOR` dependencies) inside the browser.
* **Multi-Hop Career Transition Pathfinder:** Uses Neo4j's `shortestPath((start)-[:TRANSITIONS_TO*1..5]->(end))` algorithm to identify stepping-stone roles and transition difficulty ratings.
* **Co-Occurring Skill Market Analysis:** Queries graph triangle patterns `(s1)<-[:REQUIRES]-(Role)-[:REQUIRES]->(s2)` to uncover which complementary skills appear together most frequently across industry roles.
* **Typo-Tolerant Full-Text Search:** Uses a Neo4j Lucene Full-Text Index (`role_skill_fulltext`) for fuzzy search across roles, skills, domains, and categories.
* **Guided User Experience:** Features contextual `i` info popovers on every analytical section and a dedicated 5-step **Help** page.

---

## Graph Data Model (Schema)

```text
(:Candidate)-[:HAS_SKILL {proficiency}]──────────► (:Skill {name, category, guide_url})
                                                      ▲        │
(:Role {name, domain, avg_salary, roadmap_url})       │        │ [:PREREQUISITE_FOR]
   │  │                                               │        ▼
   │  └─────────[:REQUIRES {importance, stage}]───────┘     (:Skill)
   │                                                           ▲
   └──[:TRANSITIONS_TO {difficulty}]──► (:Role)                │ [:TEACHES]
                                                               │
                                                     (:Course {title, platform, level})
