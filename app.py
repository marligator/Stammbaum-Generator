import streamlit as st
import graphviz
import json

st.set_page_config(page_title="Stammbaum Generator", layout="wide")
st.title("Stammbaum Generator für die humangenetische Beratung")

st.sidebar.header("Person hinzufügen")

if "personen" not in st.session_state:
    st.session_state.personen = []

# Eingabeformular für neue Person
with st.sidebar.form("person_form"):
    name = st.text_input("Name (optional)")
    geschlecht = st.selectbox("Geschlecht", ["m", "w"])
    geburtsjahr = st.number_input("Geburtsjahr", min_value=1900, max_value=2100, step=1)
    verstorben = st.checkbox("Verstorben?")
    alter_verstorben = st.number_input("Alter beim Versterben", min_value=0, max_value=120, step=1) if verstorben else None
    todesursache = st.text_input("Todesursache") if verstorben else ""
    hauptdiagnose = st.text_input("Hauptdiagnose")
    erkrankungsalter = st.number_input("Alter bei Hauptdiagnose", min_value=0, max_value=120, step=1)
    nebendiagnosen = st.text_area("Nebendiagnosen (durch Komma trennen)")
    eltern_ids = st.text_input("Eltern-IDs (z.B. 1,2)")
    partner_id = st.text_input("Partner-ID")

    submitted = st.form_submit_button("Hinzufügen")
    if submitted:
        person = {
            "id": len(st.session_state.personen)+1,
            "name": name,
            "geschlecht": geschlecht,
            "geburtsjahr": geburtsjahr,
            "verstorben": verstorben,
            "alter_verstorben": alter_verstorben,
            "todesursache": todesursache,
            "hauptdiagnose": hauptdiagnose,
            "erkrankungsalter": erkrankungsalter,
            "nebendiagnosen": [d.strip() for d in nebendiagnosen.split(",") if d.strip()],
            "eltern": [int(x) for x in eltern_ids.split(",") if x.strip().isdigit()],
            "partner": int(partner_id) if partner_id.isdigit() else None
        }
        st.session_state.personen.append(person)
        st.success(f"Person {person['id']} hinzugefügt")

# Stammbaum visualisieren
st.subheader("Stammbaum Vorschau")
dot = graphviz.Digraph()

id_map = {}

for p in st.session_state.personen:
    label = f"{p['name'] or 'ID ' + str(p['id'])}\n({p['geschlecht']}, {p['geburtsjahr']})"
    if p['hauptdiagnose']:
        label += f"\n{p['hauptdiagnose']} ({p['erkrankungsalter']})"
    if p['verstorben']:
        label += f"\n✝ {p['alter_verstorben']} ({p['todesursache']})"
    shape = "box" if p['geschlecht'] == "m" else "ellipse"
    dot.node(str(p['id']), label, shape=shape, style="filled", fillcolor="lightgrey")
    id_map[p['id']] = p

# Partnerschaften
for p in st.session_state.personen:
    if p['partner'] and p['partner'] > p['id']:
        partner = p['partner']
        dot.edge(str(p['id']), str(partner), dir="none")

# Eltern -> Kind Beziehungen
for p in st.session_state.personen:
    if len(p['eltern']) == 2:
        eltern_id = f"e{p['eltern'][0]}_{p['eltern'][1]}"
        dot.node(eltern_id, shape="point")
        dot.edge(str(p['eltern'][0]), eltern_id, dir="none")
        dot.edge(str(p['eltern'][1]), eltern_id, dir="none")
        dot.edge(eltern_id, str(p['id']), dir="none")

st.graphviz_chart(dot)

# Daten speichern
st.download_button("Stammdaten als JSON herunterladen", json.dumps(st.session_state.personen, indent=2), file_name="stammbaum.json")