
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

# 資料庫路徑
DB_PATH = "story_graph.db"

# 類別顏色定義
COLOR_MAP = {
    "Person": "blue",
    "Event": "red",
    "Era": "green",
    "Location": "orange",
    "Object": "purple"
}

# 建立 Pyvis 網路圖
def create_network():
    net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="black")
    net.force_atlas_2based()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 載入主表資料
    persons = pd.read_sql_query("SELECT * FROM Persons", conn)
    events = pd.read_sql_query("SELECT * FROM Events", conn)
    eras = pd.read_sql_query("SELECT * FROM Eras", conn)
    locations = pd.read_sql_query("SELECT * FROM Locations", conn)
    objects = pd.read_sql_query("SELECT * FROM Objects", conn)

    # 加入節點
    for _, row in persons.iterrows():
        net.add_node(row["person_id"], label=row["name"], color=COLOR_MAP["Person"],
                     title="人物", shape="dot", size=15, url=row["wiki_link"] or None)
    for _, row in events.iterrows():
        net.add_node(row["event_id"], label=row["event_name"], color=COLOR_MAP["Event"],
                     title="事件", shape="dot", size=15, url=row["wiki_link"] or None)
    for _, row in eras.iterrows():
        net.add_node(row["era_id"], label=row["era_name"], color=COLOR_MAP["Era"],
                     title="時代", shape="dot", size=15, url=row["wiki_link"] or None)
    for _, row in locations.iterrows():
        net.add_node(row["location_id"], label=row["location_name"], color=COLOR_MAP["Location"],
                     title="地點", shape="dot", size=15, url=row["wiki_link"] or None)
    for _, row in objects.iterrows():
        net.add_node(row["object_id"], label=row["object_name"], color=COLOR_MAP["Object"],
                     title="物件", shape="dot", size=15, url=row["wiki_link"] or None)

    # 載入關聯資料並建立邊
    def add_edges(query, src, tgt, label):
        df = pd.read_sql_query(query, conn)
        for _, row in df.iterrows():
            net.add_edge(row[src], row[tgt], label=row.get("role") or row.get("relation_type") or row.get("relationship_type") or label)

    add_edges("SELECT * FROM Person_Event", "person_id", "event_id", "參與")
    add_edges("SELECT * FROM Person_Era", "person_id", "era_id", "經歷")
    add_edges("SELECT * FROM Person_Location", "person_id", "location_id", "關聯地")
    add_edges("SELECT * FROM Person_Object", "person_id", "object_id", "關聯物")
    add_edges("SELECT * FROM Person_Person", "person_id_1", "person_id_2", "人際關係")

    conn.close()
    return net

# Streamlit 主介面
st.set_page_config(layout="wide")
st.title("大淡水人物誌知識圖譜")

net = create_network()
net.save_graph("graph.html")
components.html(open("graph.html", "r", encoding="utf-8").read(), height=700, scrolling=True)
