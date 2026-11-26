# Career Path Graph 

[![Live App](https://img.shields.io/badge/Streamlit-Live_Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://career-graph-neo4j-bm2xwmyzk7wc.streamlit.app)
[![Neo4j](https://img.shields.io/badge/Neo4j-AuraDB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![roadmap.sh](https://img.shields.io/badge/Integrated-roadmap.sh-0F172A?style=for-the-badge)](https://roadmap.sh/)

An interactive **Career & Skill Path Graph Recommender** powered by **Neo4j AuraDB**, **Cypher graph algorithms**, **PyVis**, and **Streamlit**—enriched with structured learning stages and topic guides from **roadmap.sh**.

Instead of relying on flat keyword matching, this application models tech roles, required skills, prerequisite chains, courses, and career transitions as a connected knowledge graph to generate explainable career recommendations and upskilling roadmaps.

> **🔗 Live Application:** Replace the badge link above with your full Streamlit Community Cloud URL if needed (`https://career-graph-neo4j-bm2xwmyzk7wc...streamlit.app`).

---

## 📸 Application Preview

> **💡 How to add your images on GitHub:** Open `README.md` in GitHub's web editor, highlight a placeholder line below, and drag-and-drop or paste (`Ctrl + V`) your screenshot directly—GitHub will automatically upload and generate the image URL for you!

### 1. Roles & Ordered `roadmap.sh` Study Plan
*Ranked role compatibility scoring (`2×` Core / `1×` Bonus weighting), salary/demand metrics, and stage-by-stage missing skill roadmaps.*

![Roles and Roadmap Page Placeholder](assets/roles_and_roadmap.png)

### 2. Interactive Skill-Gap Knowledge Graph
*Color-coded PyVis subgraph displaying your owned skills, missing skills, prerequisite dependencies (`PREREQUISITE_FOR`), and linked courses.*

![Skill-Gap Graph Page Placeholder](assets/skill_gap_graph.png)

### 3. Career Path & Market Explorer
*Multi-hop `shortestPath` career transition finder, co-occurring skill market triangle analysis, and typo-tolerant Lucene full-text search.*

![Market Explorer Page Placeholder](assets/market_explorer.png)

### 4. Built-In User Guide & Neo4j AuraDB Graph
| In-App Interactive Help Guide | Neo4j AuraDB Knowledge Graph |
| :---: | :---: |
| ![Help Page Placeholder](assets/help_page.png) | ![Neo4j Aura Graph Placeholder](assets/neo4j_aura_graph.png) |

---

## ✨ Key Features

* **Weighted Role Compatibility Engine:** Evaluates candidate skills against 10 tech roles using weighted Cypher aggregation (`2×` weight for **Core** skills, `1×` weight for **Bonus** skills).
* **Prerequisite-Aware Upskilling Roadmaps:** Traverses `(Role)-[:REQUIRES]->(Skill)<-[:TEACHES]-(Course)` alongside `[:PREREQUISITE_FOR]` chains to order missing skills from foundational stages to advanced topics, complete with direct **roadmap.sh** guide links.
* **Interactive PyVis Subgraph Visualization:** Dynamically renders a color-coded network (`Target Role`, `Owned Skill`, `Missing Skill`, `Course`, and dashed `PREREQUISITE_FOR` dependencies) inside the browser.
* **Multi-Hop Career Transition Pathfinder:** Uses Neo4j's `shortestPath((start)-[:TRANSITIONS_TO*1..5]->(end))` algorithm to identify stepping-stone roles and transition difficulty ratings.
* **Co-Occurring Skill Market Analysis:** Queries graph triangle patterns `(s1)<-[:REQUIRES]-(Role)-[:REQUIRES]->(s2)` to uncover which complementary skills appear together most frequently across industry roles.
* **Typo-Tolerant Full-Text Search:** Uses a Neo4j Lucene Full-Text Index (`role_skill_fulltext`) for fuzzy search across roles, skills, domains, and categories.
* **Beginner-Friendly UI & Help Documentation:** Features a custom glassmorphic Streamlit interface with contextual `ⓘ` info popovers and a dedicated 5-step **Help** page.

---

## 🧠 Graph Data Model (Schema)

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
