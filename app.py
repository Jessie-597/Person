
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

# 載入資料庫
@st.cache_data
def load_data():
    conn = sqlite3.connect("story_graph.db")
    data = {
        "persons": pd.read_sql("SELECT * FROM Persons", conn),
        "events": pd.read_sql("SELECT * FROM Events", conn),
        "eras": pd.read_sql("SELECT * FROM Eras", conn),
        "locations": pd.read_sql("SELECT * FROM Locations", conn),
        "objects": pd.read_sql("SELECT * FROM Objects", conn),
        "person_event": pd.read_sql("SELECT * FROM Person_Event", conn),
        "person_era": pd.read_sql("SELECT * FROM Person_Era", conn),
        "person_location": pd.read_sql("SELECT * FROM Person_Location", conn),
        "person_object": pd.read_sql("SELECT * FROM Person_Object", conn),
        "person_person": pd.read_sql("SELECT * FROM Person_Person", conn)
    }
    conn.close()
    return data

# 建立知識圖譜
def build_graph(data, selected_id):
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.force_atlas_2based()

    # 顏色設定
    colors = {
        "person": "#e74c3c",
        "event": "#e67e22",
        "era": "#f1c40f",
        "location": "#2ecc71",
        "object": "#3498db"
    }

    added = set()

    def add_node(node_id, label, group, wiki=None):
        if node_id not in added:
            net.add_node(node_id, label=label, color=colors[group], shape="dot", size=20,
                         title=label, href=wiki if wiki else None)
            added.add(node_id)

    # 加入人物節點
    people = data["persons"] if selected_id == "ALL" else data["persons"][data["persons"]["person_id"] == selected_id]
    for _, row in people.iterrows():
        add_node(f"P{row.person_id}", row.name, "person", row.wiki_link)

    # 關聯節點與邊
    def add_relation(df, from_col, to_col, label_col, prefix, target_df, group):
        for _, row in df.iterrows():
            if selected_id != "ALL" and row[from_col] != selected_id:
                continue
            to_row = target_df[target_df[to_col] == row[to_col]]
            if to_row.empty: continue
            to = to_row.iloc[0]
            to_id = f"{prefix}{to[to_col]}"
            add_node(to_id, to.get(to_col.replace('_id', '_name'), "無名"), group, to.get("wiki_link"))
            net.add_edge(f"P{row[from_col]}", to_id, label=row[label_col] if pd.notnull(row[label_col]) else "")

    add_relation(data["person_event"], "person_id", "event_id", "role", "E", data["events"], "event")
    add_relation(data["person_era"], "person_id", "era_id", "note", "T", data["eras"], "era")
    add_relation(data["person_location"], "person_id", "location_id", "relation_type", "L", data["locations"], "location")
    add_relation(data["person_object"], "person_id", "object_id", "relation_type", "O", data["objects"], "object")

    # 人物關係
    for _, row in data["person_person"].iterrows():
        if selected_id != "ALL" and row["person_id_1"] != selected_id and row["person_id_2"] != selected_id:
            continue
        net.add_edge(f"P{row['person_id_1']}", f"P{row['person_id_2']}", label=row["relationship_type"])

    return net

# 主頁面
st.set_page_config(layout="wide")
st.title("📘 淡水人物知識圖譜")

data = load_data()
person_names = data["persons"][["person_id", "name"]]
choices = {"全部人物串聯": "ALL"}
choices.update({row["name"]: row["person_id"] for _, row in person_names.iterrows()})
selected_label = st.selectbox("請選擇主人物或全部：", list(choices.keys()))
selected_id = choices[selected_label]

net = build_graph(data, selected_id)
net.save_graph("graph.html")
components.html(open("graph.html", "r", encoding="utf-8").read(), height=800)
