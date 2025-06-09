import streamlit as st
import sqlite3
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

# 初始化資料庫連線
conn = sqlite3.connect("story_graph.db")

# 讀取主表
persons = pd.read_sql("SELECT person_id, name, wiki_link FROM Persons", conn)
events = pd.read_sql("SELECT event_id, event_name FROM Events", conn)
locations = pd.read_sql("SELECT location_id, location_name FROM Locations", conn)
objects = pd.read_sql("SELECT object_id, object_name FROM Objects", conn)
eras = pd.read_sql("SELECT era_id, era_name FROM Eras", conn)

# 讀取關聯表
pe = pd.read_sql("SELECT * FROM Person_Event", conn)
pl = pd.read_sql("SELECT * FROM Person_Location", conn)
po = pd.read_sql("SELECT * FROM Person_Object", conn)
pr = pd.read_sql("SELECT * FROM Person_Era", conn)

# 初始化 PyVis 圖譜
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False, directed=True)

# 加入人物節點（可連結）
for _, row in persons.iterrows():
    link = row["wiki_link"] if pd.notna(row["wiki_link"]) else "#"
    title = f"<a href='{link}' target='_blank'>{row['name']} Wiki</a>"
    net.add_node(row["person_id"], label=row["name"], title=title, color="skyblue")

# 加入事件節點
for _, row in events.iterrows():
    net.add_node(row["event_id"], label=row["event_name"], title="事件：" + row["event_name"], color="orange")

# 加入地點節點
for _, row in locations.iterrows():
    net.add_node(row["location_id"], label=row["location_name"], title="地點：" + row["location_name"], color="lightgreen")

# 加入物件節點
for _, row in objects.iterrows():
    net.add_node(row["object_id"], label=row["object_name"], title="物件：" + row["object_name"], color="violet")

# 加入時代表節點
for _, row in eras.iterrows():
    net.add_node(row["era_id"], label=row["era_name"], title=f"時代：{row['era_name']}", color="lightgray")

# 加入人物與事件關聯邊
for _, row in pe.iterrows():
    net.add_edge(row["person_id"], row["event_id"], label=row["role"])

# 加入人物與地點關聯邊
for _, row in pl.iterrows():
    net.add_edge(row["person_id"], row["location_id"], label=row["relation_type"])

# 加入人物與物件關聯邊
for _, row in po.iterrows():
    net.add_edge(row["person_id"], row["object_id"], label=row["relation_type"])

# 加入人物與時代關聯邊
for _, row in pr.iterrows():
    net.add_edge(row["person_id"], row["era_id"], label="身處時代")

# 輸出到 HTML 並嵌入
net.save_graph("story_graph.html")

st.set_page_config(layout="wide")
st.title("🌐 淡水人物誌知識圖譜互動查詢（含時代節點）")

with open("story_graph.html", "r", encoding="utf-8") as f:
    html = f.read()
    components.html(html, height=750, scrolling=True)
