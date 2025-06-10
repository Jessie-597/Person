
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components
import json

# 資料庫路徑
db_path = "story_graph.db"

def get_connection():
    return sqlite3.connect(db_path)

def load_table(table):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def load_all_data():
    return {
        "persons": load_table("Persons"),
        "events": load_table("Events"),
        "eras": load_table("Eras"),
        "locations": load_table("Locations"),
        "objects": load_table("Objects"),
        "person_event": load_table("Person_Event"),
        "person_era": load_table("Person_Era"),
        "person_location": load_table("Person_Location"),
        "person_object": load_table("Person_Object"),
        "person_person": load_table("Person_Person")
    }

def build_knowledge_graph(selected_id, data):
    net = Network(height="650px", width="100%", bgcolor="#ffffff", font_color="black")

    main = data["persons"][data["persons"]["person_id"] == selected_id].iloc[0]
    net.add_node(main["person_id"], label=main["name"], title=main["contribution"],
                 href=main["wiki_link"], color="red", shape="dot")

    def add_links(df, source_id, src_col, tgt_col, target_df, target_id_col, label_col, type_label, color):
        for _, row in df[df[src_col] == source_id].iterrows():
            target_id = row[tgt_col]
            target = target_df[target_df[target_id_col] == target_id]
            if not target.empty:
                t = target.iloc[0]
                label = t[label_col]
                title = t.get("description", t.get("contribution", ""))
                href = t.get("wiki_link", "#")
                net.add_node(t[target_id_col], label=label, title=title, href=href, color=color)
                net.add_edge(source_id, t[target_id_col], label=type_label)

    add_links(data["person_event"], selected_id, "person_id", "event_id", data["events"], "event_id", "event_name", "事件", "#FFA07A")
    add_links(data["person_era"], selected_id, "person_id", "era_id", data["eras"], "era_id", "era_name", "時代", "#9370DB")
    add_links(data["person_location"], selected_id, "person_id", "location_id", data["locations"], "location_id", "location_name", "地點", "#87CEFA")
    add_links(data["person_object"], selected_id, "person_id", "object_id", data["objects"], "object_id", "object_name", "物件", "#90EE90")

    for _, row in data["person_person"][data["person_person"]["person_id_1"] == selected_id].iterrows():
        related_id = row["person_id_2"]
        relation = row["relationship_type"]
        related = data["persons"][data["persons"]["person_id"] == related_id]
        if not related.empty:
            r = related.iloc[0]
            net.add_node(r["person_id"], label=r["name"], title=r.get("contribution", ""),
                         href=r.get("wiki_link", "#"), color="#F4A460")
            net.add_edge(selected_id, r["person_id"], label=relation)

    options = {
      "nodes": {
        "shape": "dot",
        "size": 16,
        "font": {"size": 14, "color": "#000"},
        "borderWidth": 2
      },
      "edges": {"width": 2},
      "interaction": {"tooltipDelay": 200, "hideEdgesOnDrag": True},
      "physics": {"stabilization": False}
    }
    net.set_options(json.dumps(options))
    return net

# Streamlit 主介面
st.set_page_config(page_title="淡水人物誌知識圖譜", layout="wide")
st.title("📘 淡水人物誌知識圖譜")

data = load_all_data()
persons_df = data["persons"][["person_id", "name"]]
selected_name = st.selectbox("請選擇人物：", persons_df["name"])
selected_id = persons_df[persons_df["name"] == selected_name]["person_id"].values[0]

net = build_knowledge_graph(selected_id, data)
net.save_graph("graph.html")
components.html(open("graph.html", "r", encoding="utf-8").read(), height=680, scrolling=True)
