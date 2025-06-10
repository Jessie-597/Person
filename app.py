import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

# 載入 SQLite 資料庫
def load_data():
    conn = sqlite3.connect("story_graph.db")
    data = {
        "persons": pd.read_sql("SELECT * FROM persons", conn),
        "events": pd.read_sql("SELECT * FROM events", conn),
        "locations": pd.read_sql("SELECT * FROM locations", conn),
        "objects": pd.read_sql("SELECT * FROM objects", conn),
        "eras": pd.read_sql("SELECT * FROM eras", conn),
        "person_event": pd.read_sql("SELECT * FROM person_event", conn),
        "person_location": pd.read_sql("SELECT * FROM person_location", conn),
        "person_object": pd.read_sql("SELECT * FROM person_object", conn),
        "person_era": pd.read_sql("SELECT * FROM person_era", conn),
        "person_person": pd.read_sql("SELECT * FROM person_person", conn)
    }
    conn.close()
    return data

# 建立知識圖譜

def build_knowledge_graph(selected_id, data):
    net = Network(height="700px", width="100%", bgcolor="#FFFFFF", font_color="black")
    net.force_atlas_2based()

    person_df = data["persons"]
    filtered_persons = person_df if selected_id == "ALL" else person_df[person_df.id == selected_id]

    color_map = {
        "person": "gold",
        "event": "skyblue",
        "location": "lightgreen",
        "object": "tomato",
        "era": "pink"
    }

    for _, row in filtered_persons.iterrows():
        net.add_node(f"P{row.id}", label=row.name, color=color_map["person"], title=row.name,
                     shape='dot', size=25, 
                     href=row.wiki_link if pd.notna(row.wiki_link) else None)

    def add_node(df, prefix, color, label_field="name"):
        for _, row in df.iterrows():
            node_id = f"{prefix}{row.id}"
            label = getattr(row, label_field, f"{prefix}{row.id}")
            href = getattr(row, "wiki_link", None)
            net.add_node(node_id, label=label, color=color, 
                         href=href if pd.notna(href) else None)

    add_node(data["events"], "E", color_map["event"])
    add_node(data["locations"], "L", color_map["location"])
    add_node(data["objects"], "O", color_map["object"])
    add_node(data["eras"], "T", color_map["era"], label_field="era")

    def add_edges(df, prefix, label_field, target_prefix):
        for _, row in df.iterrows():
            if selected_id != "ALL" and row.person_id != selected_id:
                continue
            label = getattr(row, label_field, "")
            net.add_edge(f"P{row.person_id}", f"{target_prefix}{row[prefix]}", label=label)

    add_edges(data["person_event"], "event_id", "role", "E")
    add_edges(data["person_location"], "location_id", "description", "L")
    add_edges(data["person_object"], "object_id", "description", "O")
    add_edges(data["person_era"], "era_id", "description", "T")

    for _, row in data["person_person"].iterrows():
        if selected_id != "ALL" and row.source_id != selected_id and row.target_id != selected_id:
            continue
        net.add_edge(f"P{row.source_id}", f"P{row.target_id}", label=row.relation)

    return net

# Streamlit 介面
st.set_page_config(layout="wide")
st.title("淡水人物誌知識圖譜視覺化")
data = load_data()
person_options = [("全部人物串聯", "ALL")] + [(row.name, row.id) for _, row in data["persons"].iterrows()]
selected_id = st.selectbox("請選擇要視覺化的人物（可選全部）", options=[val for _, val in person_options],
                           format_func=lambda x: dict(person_options).get(x, "全部人物串聯"))

if st.button("產生知識圖譜"):
    net = build_knowledge_graph(selected_id, data)
    net.save_graph("graph.html")
    HtmlFile = open("graph.html", "r", encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=750, scrolling=True)
else:
    st.info("請選擇人物並點擊按鈕產生知識圖譜")
