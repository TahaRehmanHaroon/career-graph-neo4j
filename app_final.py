import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw
from pyvis.network import Network
from graph_queries import CareerGraphEngine


# ------------------------------------------------------------------------------
# Browser-tab icon: drawn in code, so no emoji and no extra asset file
# ------------------------------------------------------------------------------
def make_favicon():
    size = 128
    grad = Image.new("RGBA", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        gd.line([(0, y), (size, y)], fill=(int(91 - 55 * t), int(75 - 10 * t), int(219 - 10 * t), 255))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=30, fill=255)
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    icon.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(icon)
    pts = {"a": (38, 42), "b": (90, 50), "c": (64, 92)}
    for p, q in (("a", "b"), ("a", "c"), ("b", "c")):
        d.line([pts[p], pts[q]], fill=(255, 255, 255, 230), width=7)
    for k, (x, y) in pts.items():
        r = 13 if k == "c" else 10
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))
    return icon


st.set_page_config(
    page_title="Career Path Graph",
    page_icon=make_favicon(),
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_engine():
    return CareerGraphEngine()


engine = get_engine()

PAGES = ["Roles & Roadmap", "Skill-Gap Graph", "Market Explorer", "Help"]
if "active_page" not in st.session_state:
    st.session_state.active_page = PAGES[0]
on_help = st.session_state.active_page == "Help"

# ------------------------------------------------------------------------------
# Theme
# ------------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@300;400&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; color: #0e1a4a; }

.stApp {
    background:
        radial-gradient(900px 600px at 12% 8%, #b9a8f0, transparent 60%),
        radial-gradient(1000px 700px at 92% 92%, #1d4ed8, transparent 60%),
        linear-gradient(160deg, #e3e8ff, #8fb2ff 55%, #2f5bea) !important;
    background-attachment: fixed !important;
}

/* Remove default Streamlit chrome */
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"], footer { display: none !important; }
.block-container { max-width: 1360px; padding-top: 1.6rem !important; padding-bottom: 3rem !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,.58) !important;
    backdrop-filter: blur(18px);
    border-right: 1px solid rgba(255,255,255,.85);
}
section[data-testid="stSidebar"] * { color: #0e1a4a; }

/* Widget labels */
[data-testid="stWidgetLabel"] p {
    font-size: .72rem !important; font-weight: 700 !important;
    letter-spacing: .08em; text-transform: uppercase; color: #2c3a7a !important;
}
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stTextInput input {
    background: rgba(255,255,255,.78) !important;
    border: 1px solid rgba(14,26,74,.18) !important;
    border-radius: 12px !important;
    min-height: 46px;
}

/* Skill tags */
span[data-baseweb="tag"] { background-color: #0e1a4a !important; border-radius: 999px !important; padding: 3px 10px !important; }
span[data-baseweb="tag"] span { color: #fff !important; font-size: .78rem !important; }

/* Glass cards (real containers, so content sits inside them) */
div[class*="st-key-card"], .glass-card {
    background: rgba(255,255,255,.58);
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,.85);
    border-radius: 20px;
    padding: 22px 24px;
    box-shadow: 0 8px 30px rgba(30,58,138,.08);
}
.glass-card { margin-bottom: 16px; }

/* Top navigation */
div[class*="st-key-topnav"] {
    background: rgba(255,255,255,.62);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,.85);
    border-radius: 32px;
    padding: 12px 24px 10px;
    max-width: 820px;
    margin: 0 auto 26px auto;
}
div[class*="st-key-topnav"] button { min-height: 40px; border-radius: 999px !important; font-weight: 500 !important; border: 0 !important; }
div[class*="st-key-topnav"] button[data-testid="stBaseButton-secondary"] { background: transparent !important; color: #0e1a4a !important; }
div[class*="st-key-topnav"] button[data-testid="stBaseButton-secondary"]:hover { background: rgba(255,255,255,.55) !important; }
div[class*="st-key-topnav"] button[data-testid="stBaseButton-primary"] { background: #fff !important; color: #0e1a4a !important; box-shadow: 0 2px 10px rgba(30,60,160,.18); }

/* Typography */
.brand {
    font-family: 'Unbounded', sans-serif;
    font-weight: 400;
    font-size: 1.05rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding-bottom: 8px;
}
.hero-title { font-family: 'Unbounded', sans-serif; font-weight: 300; font-size: 2.6rem; line-height: 1.1; letter-spacing: -.02em; margin: 6px 0 10px; color: #0e1a4a; }
.hero-subtitle { font-size: 1rem; color: #2c3a7a; margin-bottom: 24px; }
.sec-title { font-family: 'Unbounded', sans-serif; font-weight: 400; font-size: 1.05rem; margin: 0; color: #0e1a4a; }
.eyebrow { font-size: .72rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #2c3a7a; }
.metric-big { font-family: 'Unbounded', sans-serif; font-weight: 300; font-size: 3.2rem; letter-spacing: -.03em; line-height: 1.1; margin: 8px 0 4px; }
.metric-role { font-weight: 600; font-size: 1.05rem; }
.metric-sub { font-size: .86rem; color: #2c3a7a; margin-top: 10px; }
.pill { display: inline-block; background: #fff; color: #0e1a4a; font-size: .72rem; font-weight: 600; padding: 3px 10px; border-radius: 999px; margin-left: 6px; }

/* Shortest-path box */
.navy-path-box { background: #0e1a4a; color: #fff; border-radius: 16px; padding: 18px 20px; margin-top: 16px; }
.navy-path-label { font-size: .7rem; font-weight: 700; letter-spacing: .08em; color: #c9d4ff; text-transform: uppercase; margin-bottom: 8px; }
.navy-path-route { font-size: 1rem; font-weight: 600; color: #fff; }
.diff-badge { display: inline-block; background: #fff; color: #0e1a4a; font-size: .72rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; margin: 10px 6px 0 0; }

/* Info buttons */
div[data-testid="stPopover"] button {
    width: 22px !important;
    min-width: 22px !important;
    height: 22px !important;
    min-height: 22px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    border: 1px solid #2c3a7a !important;
    background: transparent !important;
    display: grid !important;
    place-items: center !important;
}

div[data-testid="stPopover"] button > * {
    display: none !important;
}

div[data-testid="stPopover"] button::after {
    content: "i";
    font: italic 600 0.8rem/1 Georgia, serif;
    color: #2c3a7a;
}

div[data-testid="stPopover"] button:hover {
    background: #0e1a4a !important;
}

div[data-testid="stPopover"] button:hover::after {
    color: #fff;
}

/* Hide any chevron/icon sibling inside the popover trigger */
div[data-testid="stPopover"] button > div:not(:first-child),
div[data-testid="stPopover"] button svg,
div[data-testid="stPopover"] button span[data-testid="stIconMaterial"] {
    display: none !important;
}

/* Graph stat tiles */
.stat { background: rgba(255,255,255,.65); border-radius: 14px; padding: 14px 18px; }
.stat b { font-family: 'Unbounded', sans-serif; font-weight: 300; font-size: 1.8rem; display: block; }
.stat span { font-size: .78rem; color: #2c3a7a; font-weight: 600; letter-spacing: .04em; }

/* Legend */
.legend { display: flex; flex-wrap: wrap; gap: 22px; font-size: .84rem; color: #2c3a7a; margin: 14px 0; align-items: center; }
.legend i { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; vertical-align: -1px; }

/* Help */
.step { display: flex; gap: 20px; align-items: flex-start; margin-bottom: 24px; }
.step:last-child { margin-bottom: 0; }
.step-num { font-family: 'Unbounded', sans-serif; font-weight: 300; font-size: 2rem; min-width: 56px; line-height: 1; }
.step-title { font-weight: 700; font-size: 1rem; margin-bottom: 4px; }
.step-desc { font-size: .9rem; color: #2c3a7a; line-height: 1.5; }
.ref-list { font-size: .88rem; color: #2c3a7a; line-height: 1.8; }
.info-chip { display: inline-block; width: 20px; height: 20px; border: 1px solid #2c3a7a; border-radius: 50%; text-align: center; font: italic 600 .75rem/18px Georgia, serif; }
</style>
""",
    unsafe_allow_html=True,
)

# The Help page has no sidebar: hide it entirely instead of leaving an empty panel
if on_help:
    st.markdown(
        "<style>section[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'], "
        "[data-testid='collapsedControl'] { display: none !important; }</style>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def section_header(title_text, info_text, eyebrow=False):
    col_t, col_i = st.columns([0.94, 0.06], vertical_alignment="center")
    with col_t:
        cls = "eyebrow" if eyebrow else "sec-title"
        st.markdown(f"<div class='{cls}'>{title_text}</div>", unsafe_allow_html=True)
    with col_i:
        with st.popover("i"):
            st.markdown(info_text)


def valid_url(u):
    return isinstance(u, str) and u.strip().lower().startswith(("http://", "https://"))

# ------------------------------------------------------------------------------
# Top navigation
# ------------------------------------------------------------------------------
with st.container(key="topnav"):
    st.markdown(
        "<div class='brand'><svg width='26' height='26' viewBox='0 0 26 26' aria-hidden='true'>"
        "<circle cx='13' cy='13' r='12' fill='#3b2fd0'/><circle cx='8' cy='9' r='3' fill='#fff'/>"
        "<circle cx='18' cy='17' r='3' fill='#fff'/><path d='M8 9L18 17' stroke='#fff' stroke-width='1.5'/>"
        "</svg>Career Path Graph</div>",
        unsafe_allow_html=True,
    )
    nav_cols = st.columns([1.4, 1.4, 1.4, 0.9], vertical_alignment="center")
    for idx, page_name in enumerate(PAGES):
        with nav_cols[idx]:
            active = st.session_state.active_page == page_name
            if st.button(page_name, key=f"nav_{idx}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.active_page = page_name
                st.rerun()

# ------------------------------------------------------------------------------
# Graph metadata
# ------------------------------------------------------------------------------
candidates = engine.get_sample_candidates()
all_skill_names = [s["name"] for s in engine.get_all_skills()]
all_roles_data = engine.get_all_roles()
all_role_names = [r["name"] for r in all_roles_data]

# Profile state survives page changes (widgets on a hidden sidebar would otherwise reset)
st.session_state.setdefault("saved_skills", ["Python", "SQL", "Git & GitHub"])
st.session_state.setdefault("saved_preset", "Custom profile")
st.session_state.setdefault("default_role", "Backend Developer")


def apply_preset():
    name = st.session_state.preset_w
    if name != "Custom profile":
        chosen = next(c for c in candidates if c["name"] == name)
        st.session_state.skills_w = [s for s in chosen["skills"] if s in all_skill_names]
        st.session_state.default_role = chosen["current_role"]
    else:
        st.session_state.default_role = "Backend Developer"


if not on_help:
    st.session_state.setdefault("preset_w", st.session_state.saved_preset)
    st.session_state.setdefault("skills_w", st.session_state.saved_skills)
    with st.sidebar:
        st.markdown("<div class='eyebrow' style='margin-bottom:10px'>Candidate profile</div>", unsafe_allow_html=True)
        st.selectbox("Sample profile", ["Custom profile"] + [c["name"] for c in candidates],
                     key="preset_w", on_change=apply_preset)
        st.multiselect("Your skills", options=all_skill_names, key="skills_w")
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        section_header(
            "Scoring logic",
            "**How match scores work**\n\n- **Core skills** carry **2x weight**\n- **Bonus skills** carry **1x weight**\n\n"
            "Your earned weight is divided by the total weight a role requires.",
            eyebrow=True,
        )
        st.markdown(
            "<div class='ref-list'><b>Core skills</b> count 2x<br><b>Bonus skills</b> count 1x<br>"
            "<span style='font-size:.78rem'>Scores are calculated live across roles, skills and courses.</span></div>",
            unsafe_allow_html=True,
        )
    st.session_state.saved_skills = st.session_state.skills_w
    st.session_state.saved_preset = st.session_state.preset_w

selected_skills = st.session_state.saved_skills
default_role = st.session_state.default_role

if not selected_skills and not on_help:
    st.warning("Select at least one skill in the sidebar to generate recommendations.")
    st.stop()

# ==============================================================================
# PAGE 1: ROLES & ROADMAP
# ==============================================================================
if st.session_state.active_page == "Roles & Roadmap":
    st.markdown("<div class='hero-title'>Your best-matching roles</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Ranked by how closely your skills fit each role in the graph.</div>", unsafe_allow_html=True)

    matches = engine.recommend_roles(selected_skills)

    cols = st.columns(3)
    for idx, r in enumerate(matches[:3]):
        with cols[idx]:
            st.markdown(
                f"""<div class='glass-card'>
                <div class='eyebrow'>#{idx + 1} match</div>
                <div class='metric-big'>{r['match_score']}<span style='font-size:1.2rem'>%</span></div>
                <div class='metric-role'>{r['role']}</div>
                <div class='metric-sub'>{r['avg_salary']} avg. salary
                <span class='pill'>{r['demand_level']} demand</span></div></div>""",
                unsafe_allow_html=True,
            )

    with st.container(key="card_ranking"):
        section_header(
            "Full compatibility ranking",
            "Match score is the share of a role's weighted skills you already have. Add or remove skills in the sidebar "
            "and the ranking updates instantly. Open the Skill-Gap Graph to see what is missing for any role.",
        )
        df = pd.DataFrame(matches)[["role", "domain", "match_score", "avg_salary", "demand_level"]]
        df.columns = ["ROLE", "DOMAIN", "MATCH SCORE", "AVG. SALARY", "MARKET DEMAND"]
        st.dataframe(
            df, use_container_width=True, hide_index=True,
            column_config={"MATCH SCORE": st.column_config.ProgressColumn(
                "MATCH SCORE", format="%.1f%%", min_value=0, max_value=100)},
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    with st.container(key="card_plan"):
        section_header(
            "Ordered skill-gap study plan",
            "Orders your missing skills from Stage 1 fundamentals to advanced topics, using each skill's prerequisites. "
            "Every row lists a recommended course and, where available, a roadmap.sh guide.",
        )
        target_role = st.selectbox("Target role", options=all_role_names,
                                   index=all_role_names.index(matches[0]["role"]))
        role_meta = next(r for r in all_roles_data if r["name"] == target_role)
        if valid_url(role_meta.get("roadmap_url")):
            st.link_button(f"Open the roadmap.sh map for {target_role}", role_meta["roadmap_url"].strip())

        roadmap = engine.get_learning_roadmap(target_role, selected_skills)
        if not roadmap:
            st.success(f"You already have every required skill for {target_role}.")
        else:
            rows_html = ""
            for item in roadmap:
                stage = f"Stage {item['stage']}"
                prereq = ", ".join(item["learn_first"]) if item["learn_first"] else "Ready now"
                url = item.get("roadmap_guide")
                guide_cell = (
                    f"<a href='{url.strip()}' target='_blank' rel='noopener noreferrer' "
                    f"style='color:#2f5bea;font-weight:600;text-decoration:underline;'>Open topic</a>"
                    if valid_url(url)
                    else "—"
                )
                rows_html += (
                    f"<tr style='border-bottom:1px solid rgba(14,26,74,.1);'>"
                    f"<td style='padding:10px 12px;'>{stage}</td>"
                    f"<td style='padding:10px 12px;font-weight:600;'>{item['missing_skill']}</td>"
                    f"<td style='padding:10px 12px;'>{item['importance']}</td>"
                    f"<td style='padding:10px 12px;'>{prereq}</td>"
                    f"<td style='padding:10px 12px;'>{guide_cell}</td>"
                    f"<td style='padding:10px 12px;'>{item['course_title'] or '—'}</td>"
                    f"<td style='padding:10px 12px;'>{item['platform'] or '—'}</td>"
                    f"</tr>"
                )

            st.markdown(
                f"""
                <div style='overflow-x:auto;background:rgba(255,255,255,.78);border-radius:14px;border:1px solid rgba(14,26,74,.12);'>
                <table style='width:100%;border-collapse:collapse;font-size:.86rem;text-align:left;color:#0e1a4a;'>
                  <thead>
                    <tr style='border-bottom:1px solid rgba(14,26,74,.15);font-size:.72rem;letter-spacing:.06em;color:#2c3a7a;'>
                      <th style='padding:12px;'>ORDER</th>
                      <th style='padding:12px;'>MISSING SKILL</th>
                      <th style='padding:12px;'>PRIORITY</th>
                      <th style='padding:12px;'>PREREQUISITE CHECK</th>
                      <th style='padding:12px;'>ROADMAP.SH GUIDE</th>
                      <th style='padding:12px;'>RECOMMENDED COURSE</th>
                      <th style='padding:12px;'>PLATFORM</th>
                    </tr>
                  </thead>
                  <tbody>{rows_html}</tbody>
                </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ==============================================================================
# PAGE 2: SKILL-GAP GRAPH
# ==============================================================================
elif st.session_state.active_page == "Skill-Gap Graph":
    st.markdown("<div class='hero-title'>Skill-gap graph</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>See how a role connects to the skills it needs and the courses that fill your gaps.</div>", unsafe_allow_html=True)

    with st.container(key="card_graph"):
        section_header(
            "Role to visualise",
            "Pick any role to redraw the graph. Hover a node to highlight its connections, drag nodes to rearrange them, "
            "and scroll to zoom. Orange nodes pulse because they are your gaps. Dashed arrows show which skill "
            "must be learned before another.",
            eyebrow=True,
        )
        graph_role = st.selectbox("Role to visualise", options=all_role_names, index=0, label_visibility="collapsed")

        data = engine.get_role_subgraph(graph_role, selected_skills)
        rows, prereqs = data["nodes"], data["prereqs"]

        skill_state = {r["skill"]: r["has_skill"] for r in rows}
        courses = {r["course"] for r in rows if r["course"] and not r["has_skill"]}
        have = sum(1 for v in skill_state.values() if v)
        c1, c2, c3 = st.columns(3)
        for col, num, lab in ((c1, have, "SKILLS YOU HAVE"), (c2, len(skill_state) - have, "SKILLS TO LEARN"),
                              (c3, len(courses), "COURSES LINKED")):
            col.markdown(f"<div class='stat'><b>{num}</b><span>{lab}</span></div>", unsafe_allow_html=True)

        st.markdown(
            """<div class='legend'>
            <span><i style='background:#3b2fd0'></i>Target role</span>
            <span><i style='background:#0b7d6e'></i>Skill you have</span>
            <span><i style='background:#e8892b'></i>Missing skill</span>
            <span><i style='background:#2f5bea;border-radius:2px'></i>Course</span>
            <span><svg width='28' height='6'><line x1='0' y1='3' x2='28' y2='3' stroke='#b45f06' stroke-width='2' stroke-dasharray='5 4'/></svg>&nbsp;Prerequisite for</span>
            </div>""",
            unsafe_allow_html=True,
        )

        net = Network(height="520px", width="100%", bgcolor="#f1f5ff", font_color="#0e1a4a",
                      directed=True, cdn_resources="remote")
        net.set_options(json.dumps({
            "nodes": {
                "borderWidth": 3, "borderWidthSelected": 4,
                "font": {"size": 15, "face": "Inter, sans-serif", "strokeWidth": 5, "strokeColor": "#f1f5ff"},
                "shadow": {"enabled": True, "size": 14, "x": 0, "y": 4, "color": "rgba(30,60,160,.28)"},
            },
            "edges": {
                "smooth": {"type": "dynamic"},
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.55}},
                "color": {"inherit": False},
                "hoverWidth": 1.6,
            },
            "physics": {
                "solver": "barnesHut",
                "barnesHut": {"gravitationalConstant": -4200, "centralGravity": 0.3,
                              "springLength": 165, "springConstant": 0.04, "damping": 0.22},
                "stabilization": {"enabled": False},
            },
            "interaction": {"hover": True, "tooltipDelay": 120, "zoomView": True, "dragNodes": True},
        }))

        net.add_node(graph_role, label=graph_role, shape="dot", size=36, color={"background": "#3b2fd0", "border": "#ffffff"},
                     title=f"Target role\n{graph_role}", font={"size": 17, "face": "Inter, sans-serif", "strokeWidth": 5, "strokeColor": "#f1f5ff"},
                     shadow={"enabled": True, "size": 26, "x": 0, "y": 0, "color": "rgba(59,47,208,.55)"})
        added, missing_ids = {graph_role}, []

        for r in rows:
            skill, has, imp, stage, course = r["skill"], r["has_skill"], r["importance"], r["stage"], r["course"]
            if skill not in added:
                if has:
                    net.add_node(skill, label=skill, size=22, color={"background": "#0b7d6e", "border": "#d7f5ef"},
                                 title=f"Skill you have\n{skill}")
                else:
                    net.add_node(skill, label=skill, size=22, color={"background": "#e8892b", "border": "#fff1e0"},
                                 title=f"Missing skill\nStage {stage} | {imp}",
                                 shadow={"enabled": True, "size": 20, "x": 0, "y": 0, "color": "rgba(232,137,43,.6)"})
                    missing_ids.append(skill)
                added.add(skill)
            net.add_edge(graph_role, skill, width=3 if imp == "Core" else 1.4,
                         color={"color": "#7c8bb8", "highlight": "#3b2fd0"}, title=f"{imp} skill")
            if course and not has:
                if course not in added:
                    net.add_node(course, label=course, shape="square", size=17,
                                 color={"background": "#2f5bea", "border": "#dbe6ff"}, title=f"Course\n{course}")
                    added.add(course)
                net.add_edge(course, skill, color={"color": "#2f5bea", "highlight": "#1d3fb8"}, width=1.6)

        for p in prereqs:
            net.add_edge(p["from_skill"], p["to_skill"], color={"color": "#d97706", "highlight": "#b45f06"},
                         width=2.4, dashes=[8, 6], title="Prerequisite for")

        try:
            html = net.generate_html()
        except AttributeError:
            net.save_graph("skill_subgraph.html")
            with open("skill_subgraph.html", "r", encoding="utf-8") as f:
                html = f.read()

        # Life: pulsing gaps, hover focus on a node's neighbourhood, rounded canvas
        script = """
<style>body{margin:0;background:transparent}#mynetwork{border:0 !important;border-radius:16px}.card{border:0 !important}</style>
<script>
(function () {
  var MISSING = %s;
  var wait = setInterval(function () {
    if (typeof network === "undefined" || !network || typeof nodes === "undefined") return;
    clearInterval(wait);
    var base = {};
    nodes.get().forEach(function (n) { base[n.id] = { color: n.color, size: n.size }; });
    var t = 0;
    setInterval(function () {
      t += 0.12;
      MISSING.forEach(function (id) {
        if (base[id]) nodes.update({ id: id, size: base[id].size + 2.6 * Math.sin(t) });
      });
    }, 60);
    network.on("hoverNode", function (p) {
      var keep = network.getConnectedNodes(p.node).concat([p.node]);
      nodes.update(nodes.get().map(function (n) {
        return keep.indexOf(n.id) > -1 ? { id: n.id, color: base[n.id].color }
          : { id: n.id, color: { background: "#cfd8ee", border: "#e6ecfa" } };
      }));
    });
    network.on("blurNode", function () {
      nodes.update(nodes.get().map(function (n) { return { id: n.id, color: base[n.id].color }; }));
    });
    network.once("afterDrawing", function () { network.fit({ animation: { duration: 900, easingFunction: "easeInOutQuad" } }); });
  }, 100);
})();
</script>
""" % json.dumps(missing_ids)
        html = html.replace("</body>", script + "</body>")
        components.html(html, height=540)

# ==============================================================================
# PAGE 3: MARKET EXPLORER
# ==============================================================================
elif st.session_state.active_page == "Market Explorer":
    st.markdown("<div class='hero-title'>Career path &amp; market explorer</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Plan a move between roles and see which skills travel together.</div>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        with st.container(key="card_transition"):
            section_header(
                "Career transition finder",
                "Finds the shortest chain of related roles between where you are and where you want to be, "
                "with a difficulty rating for each step.",
            )
            start_role = st.selectbox(
                "Starting role", options=all_role_names,
                index=all_role_names.index(default_role) if default_role in all_role_names else 0)
            end_role = st.selectbox(
                "Destination role", options=all_role_names,
                index=all_role_names.index("AI & GraphRAG Engineer") if "AI & GraphRAG Engineer" in all_role_names else 1)

            if start_role == end_role:
                st.info("Select two different roles to compute a transition path.")
            else:
                paths = engine.find_career_path(start_role, end_role)
                if paths:
                    p = paths[0]
                    badges = "".join(f"<span class='diff-badge'>{d}</span>" for d in p["step_difficulties"])
                    st.markdown(
                        f"""<div class='navy-path-box'>
                        <div class='navy-path-label'>Shortest path &middot; {p['hops']} step{'s' if p['hops'] > 1 else ''}</div>
                        <div class='navy-path-route'>{' &rarr; '.join(p['role_steps'])}</div>
                        <div>{badges}</div></div>""",
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning("No transition path is mapped between these two roles yet.")

    with right:
        with st.container(key="card_ecosystem"):
            section_header(
                "Skill ecosystem",
                "Shows the skills that appear alongside your chosen skill across roles, and how many roles they share.",
            )
            skill_pick = st.selectbox(
                "Inspect skill", options=all_skill_names,
                index=all_skill_names.index("Data Visualization") if "Data Visualization" in all_skill_names else 0)
            paired = engine.get_complementary_skills(skill_pick)
            if paired:
                dfp = pd.DataFrame(paired)
                dfp["roles"] = dfp["roles"].apply(lambda x: ", ".join(x))
                dfp.columns = ["SKILL", "CATEGORY", "ROLES", "APPEARS IN"]
                st.dataframe(dfp, use_container_width=True, hide_index=True)
            else:
                st.info("No complementary skills found for this skill.")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    with st.container(key="card_search"):
        section_header(
            "Search roles and skills",
            "Type a role or skill name. Close spellings and partial words still return matches, so you do not need "
            "exact terms. Try `pythn`, `graphrg` or `analst`.",
        )
        query = st.text_input("Search", placeholder="Try a role or skill")
        if query:
            hits = engine.fuzzy_search(query)
            if hits:
                dfh = pd.DataFrame(hits)
                dfh.columns = ["TYPE", "NAME", "DOMAIN / CATEGORY", "RELEVANCE SCORE"]
                st.dataframe(dfh, use_container_width=True, hide_index=True)
            else:
                st.info("No matches found.")

# ==============================================================================
# PAGE 4: HELP
# ==============================================================================
else:
    st.markdown("<div class='hero-title'>How to use Career Path Graph</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Five steps, from your first skill to a clear plan.</div>", unsafe_allow_html=True)

    steps = [
        ("Build your profile", "Open the sidebar on any tab and pick a sample profile, or add your own skills. Remove a skill with the <b>&times;</b> on its tag."),
        ("Review role matches", "The <b>Roles &amp; Roadmap</b> tab ranks every role by match score, with salary, market demand and an ordered study plan below."),
        ("Find your gaps", "Open the <b>Skill-Gap Graph</b> and choose a role. Orange nodes are skills you still need, and blue squares are courses that teach them."),
        ("Plan a move", "In <b>Market Explorer</b>, choose a starting and destination role to see the shortest path between them and how hard each step is."),
        ("Search and compare", "Use search to look up any role or skill, and the skill ecosystem table to see which skills appear together across the market."),
    ]
    steps_html = "".join(
        f"<div class='step'><div class='step-num'>0{i + 1}</div><div><div class='step-title'>{t}</div>"
        f"<div class='step-desc'>{d}</div></div></div>" for i, (t, d) in enumerate(steps))

    hl, hr = st.columns([1.15, 0.85])
    with hl:
        st.markdown(f"<div class='glass-card'>{steps_html}</div>", unsafe_allow_html=True)
    with hr:
        st.markdown(
            """<div class='glass-card'>
            <div class='sec-title' style='margin-bottom:16px'>Quick reference</div>
            <div class='eyebrow' style='margin-bottom:8px'>Colours in the graph</div>
            <div class='ref-list' style='margin-bottom:18px'>
              <i style='display:inline-block;width:11px;height:11px;border-radius:50%;background:#0b7d6e;margin-right:8px'></i>Skill you have<br>
              <i style='display:inline-block;width:11px;height:11px;border-radius:50%;background:#e8892b;margin-right:8px'></i>Missing skill<br>
              <i style='display:inline-block;width:11px;height:11px;border-radius:2px;background:#2f5bea;margin-right:8px'></i>Course<br>
              <i style='display:inline-block;width:11px;height:11px;border-radius:50%;background:#3b2fd0;margin-right:8px'></i>Target role
            </div>
            <div class='eyebrow' style='margin-bottom:8px'>Good to know</div>
            <div class='ref-list'>
              &bull; Core skills count twice as much as bonus skills.<br>
              &bull; Select any <span class='info-chip'>i</span> button for a short explanation of that section.<br>
              &bull; Your skills apply to every tab and are kept when you move between them.
            </div></div>""",
            unsafe_allow_html=True,
        )
