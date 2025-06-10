
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

# 資料庫路徑
DB_PATH = "story_graph.db"

# 從 SQLite 載入所有資料表為 pandas DataFrame
def load_data():
    conn = sqlite3.connect(DB_PATH)
    data = {}
    tables = ["persons", "events", "eras", "locations", "objects",
              "person_event", "person_era", "person_location", "person_object", "person_person"]
    for table in tables:
        data[table] = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return data

# 建立知識圖譜（支援單一人物與全部人物）
def build_knowledge_graph(person_id, data):
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.force_atlas_2based()

    # 設定節點顏色
    colors = {
        "person": "#f94144",
        "event": "#f3722c",
        "era": "#f9c74f",
        "location": "#43aa8b",
        "object": "#577590"
    }

    # 建立節點與邊的集合（避免重複）
    added_nodes = set()

    def add_node(node_id, label, title, group, url):
        if node_id not in added_nodes:
            net.add_node(node_id, label=label, title=title, color=colors[group], shape="dot", size=15, 
                         font={"size": 14}, url=url)
            added_nodes.add(node_id)

    # 加入人物節點（單一或全部）
    persons = data["persons"]
    if person_id == "ALL":
        selected_persons = persons
    else:
        selected_persons = persons[persons["id"] == person_id]

    for _, person in selected_persons.iterrows():
        add_node(f"person_{person['id']}", person["name"], "人物", "person", person.get("wiki_link", ""))

    # 加入所有關聯節點與邊
    for _, row in data["person_event"].iterrows():
        if person_id == "ALL" or row["person_id"] == person_id:
            event = data["events"][data["events"]["id"] == row["event_id"]].iloc[0]
            add_node(f"event_{event['id']}", event["name"], event.get("description", "事件"), "event", event.get("wiki_link", ""))
            net.add_edge(f"person_{row['person_id']}", f"event_{row['event_id']}", label=row.get("role", "參與"))

    for _, row in data["person_era"].iterrows():
        if person_id == "ALL" or row["person_id"] == person_id:
            era = data["eras"][data["eras"]["id"] == row["era_id"]].iloc[0]
            add_node(f"era_{era['id']}", era["name"], "時代", "era", era.get("wiki_link", ""))
            net.add_edge(f"person_{row['person_id']}", f"era_{row['era_id']}", label="活躍時期")

    for _, row in data["person_location"].iterrows():
        if person_id == "ALL" or row["person_id"] == person_id:
            loc = data["locations"][data["locations"]["id"] == row["location_id"]].iloc[0]
            add_node(f"location_{loc['id']}", loc["name"], loc.get("type", "地點"), "location", loc.get("wiki_link", ""))
            net.add_edge(f"person_{row['person_id']}", f"location_{row['location_id']}", label=loc.get("description", "地點"))

    for _, row in data["person_object"].iterrows():
        if person_id == "ALL" or row["person_id"] == person_id:
            obj = data["objects"][data["objects"]["id"] == row["object_id"]].iloc[0]
            add_node(f"object_{obj['id']}", obj["name"], obj.get("description", "物件"), "object", obj.get("wiki_link", ""))
            net.add_edge(f"person_{row['person_id']}", f"object_{row['object_id']}", label=obj.get("description", "物件"))

    for _, row in data["person_person"].iterrows():
        if person_id == "ALL" or row["person_id_1"] == person_id or row["person_id_2"] == person_id:
            net.add_edge(f"person_{row['person_id_1']}", f"person_{row['person_id_2']}", label=row.get("relation", "關係"))

    return net

# Streamlit 介面
st.set_page_config(page_title="淡水人物知識圖譜", layout="wide")
st.title("📚 淡水人物知識圖譜")

# 載入資料
data = load_data()

# 選擇人物
person_options = data["persons"][["id", "name"]].dropna()
person_dict = dict(zip(person_options["name"], person_options["id"]))
person_dict["全部人物串聯"] = "ALL"

selected_name = st.selectbox("選擇要顯示的主角人物或串聯所有人物", options=list(person_dict.keys()))
selected_id = person_dict[selected_name]

# 建立圖譜並顯示
net = build_knowledge_graph(selected_id, data)
net.save_graph("graph.html")
components.html(open("graph.html", "r", encoding="utf-8").read(), height=800)
