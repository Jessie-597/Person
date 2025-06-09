
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

# 資料庫路徑
db_path = "story_graph.db"

# 建立資料庫連線
def get_connection():
    return sqlite3.connect(db_path)

# 載入資料表
def load_table(table):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

# 載入所有資料（不改欄位名稱）
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

# 建立知識圖譜
def build_graph(selected_id, data):
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

    main_row = data["persons"][data["persons"]["person_id"] == selected_id].iloc[0]
    net.add_node(main_row["person_id"], label=main_row["name"],
                 title=main_row["contribution"],
                 href=main_row["wiki_link"], color="red")

    def link_related(df, src_col, tgt_col, target_df, target_id_col, target_name_col, label):
        links = df[df[src_col] == selected_id]
        for _, row in links.iterrows():
            target_id = row[tgt_col]
            target = target_df[target_df[target_id_col] == target_id]
            if not target.empty:
                t = target.iloc[0]
                net.add_node(t[target_id_col], label=t[target_name_col],
                             title=t.get("description", t.get("occupation", "")),
                             href=t.get("wiki_link", "#"))
                net.add_edge(main_row["person_id"], t[target_id_col], label=label)

    link_related(data["person_event"], "person_id", "event_id", data["events"], "event_id", "event_name", "Event")
    link_related(data["person_location"], "person_id", "location_id", data["locations"], "location_id", "location_name", "Location")
    link_related(data["person_object"], "person_id", "object_id", data["objects"], "object_id", "object_name", "Object")
    link_related(data["person_era"], "person_id", "era_id", data["eras"], "era_id", "era_name", "Era")

    # 人物關係
    for _, row in data["person_person"][data["person_person"]["person_id_1"] == selected_id].iterrows():
        related_id = row["person_id_2"]
        related = data["persons"][data["persons"]["person_id"] == related_id]
        if not related.empty:
            r = related.iloc[0]
            net.add_node(r["person_id"], label=r["name"],
                         title=r.get("contribution", ""),
                         href=r.get("wiki_link", "#"))
            net.add_edge(main_row["person_id"], r["person_id"], label=row["relationship_type"])

    net.set_options("""
    var options = {
      nodes: {
        shape: 'dot',
        size: 16,
        font: {
          size: 14,
          color: '#000'
        },
        borderWidth: 2
      },
      edges: {
        width: 2
      },
      interaction: {
        tooltipDelay: 200,
        hideEdgesOnDrag: true
      },
      physics: {
        stabilization: false
      }
    }
    """)
    return net

# Streamlit 主程式
st.set_page_config(page_title="淡水人物知識圖譜", layout="wide")
st.title("📚 淡水人物誌知識圖譜系統")

data = load_all_data()
persons = data["persons"][["person_id", "name"]]
selected_name = st.selectbox("請選擇人物：", persons["name"])
selected_id = persons[persons["name"] == selected_name]["person_id"].values[0]

net = build_graph(selected_id, data)
net.save_graph("graph.html")
components.html(open("graph.html", "r", encoding="utf-8").read(), height=620, scrolling=True)
