
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components
import os

st.set_page_config(layout="wide")
st.title("📚 淡水人物誌知識圖譜查詢系統")

# 建立網路圖
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
net.barnes_hut(gravity=-3000, central_gravity=0.2, spring_length=180, spring_strength=0.04)

# 正確 JSON options，為單行字串格式
net.set_options('{"interaction": {"hover": true, "navigationButtons": true, "multiselect": false, "selectable": true}, "physics": {"stabilization": true, "barnesHut": {"gravitationalConstant": -3000, "springLength": 180, "springConstant": 0.04, "centralGravity": 0.2, "avoidOverlap": 1}}}')

# 載入資料庫
conn = sqlite3.connect("story_graph.db")
cursor = conn.cursor()

# 定義節點顏色
color_map = {
    "person": "#FF9F9F",
    "event": "#FFD591",
    "location": "#91D5FF",
    "object": "#B37FEB",
    "era": "#A7E9AF"
}

# 加入人物節點
for row in cursor.execute("SELECT id, name, Wiki_link FROM persons"):
    node_id, name, link = row
    net.add_node(f"P{node_id}", label=name, title=name, color=color_map["person"], shape="dot", size=20, href=link)

# 加入事件節點
for row in cursor.execute("SELECT id, event_name FROM events"):
    node_id, name = row
    net.add_node(f"E{node_id}", label=name, title=name, color=color_map["event"], shape="ellipse")

# 加入地點節點
for row in cursor.execute("SELECT id, location_name FROM locations"):
    node_id, name = row
    net.add_node(f"L{node_id}", label=name, title=name, color=color_map["location"], shape="box")

# 加入物件節點
for row in cursor.execute("SELECT id, object_name FROM objects"):
    node_id, name = row
    net.add_node(f"O{node_id}", label=name, title=name, color=color_map["object"], shape="triangle")

# 加入時代節點
for row in cursor.execute("SELECT id, era_name FROM eras"):
    node_id, name = row
    net.add_node(f"T{node_id}", label=name, title=name, color=color_map["era"], shape="star")

# 加入人物與人物的關聯邊
for row in cursor.execute("SELECT person1_id, person2_id, relation FROM person_person"):
    id1, id2, rel = row
    net.add_edge(f"P{id1}", f"P{id2}", label=rel)

# 人物與事件
for row in cursor.execute("SELECT person_id, event_id FROM person_event"):
    pid, eid = row
    net.add_edge(f"P{pid}", f"E{eid}")

# 人物與地點
for row in cursor.execute("SELECT person_id, location_id FROM person_location"):
    pid, lid = row
    net.add_edge(f"P{pid}", f"L{lid}")

# 人物與物件
for row in cursor.execute("SELECT person_id, object_id FROM person_object"):
    pid, oid = row
    net.add_edge(f"P{pid}", f"O{oid}")

# 人物與時代
for row in cursor.execute("SELECT person_id, era_id FROM person_era"):
    pid, tid = row
    net.add_edge(f"P{pid}", f"T{tid}")

conn.close()

# 儲存 HTML
output_path = "/mnt/data/story_graph.html"
net.show(output_path)

# 顯示圖譜
with open(output_path, "r", encoding="utf-8") as f:
    graph_html = f.read()
components.html(graph_html, height=800, scrolling=True)
