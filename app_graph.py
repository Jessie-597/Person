import streamlit as st
import sqlite3
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components

# 初始化資料庫連線
conn = sqlite3.connect("story_graph.db")

# 讀取主表
persons = pd.read_sql("SELECT person_id, name, wiki_link FROM Persons", conn)
events = pd.read_sql("SELECT event_id, event_name, wiki_link FROM Events", conn)
locations = pd.read_sql("SELECT location_id, location_name, wiki_link FROM Locations", conn)
objects = pd.read_sql("SELECT object_id, object_name, wiki_link FROM Objects", conn)
eras = pd.read_sql("SELECT era_id, era_name, wiki_link FROM Eras", conn)

# 讀取關聯表
pe = pd.read_sql("SELECT * FROM Person_Event", conn)
pl = pd.read_sql("SELECT * FROM Person_Location", conn)
po = pd.read_sql("SELECT * FROM Person_Object", conn)
pr = pd.read_sql("SELECT * FROM Person_Era", conn)

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🌐 淡水人物誌知識圖譜互動查詢")

search_name = st.text_input("🔍 輸入人物關鍵字進行過濾（模糊查詢）")

# 篩選人物（如有搜尋字）
if search_name:
    persons = persons[persons["name"].str.contains(search_name, case=False, na=False)]

# 初始化 PyVis 圖譜
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False, directed=True)
net.barnes_hut()  # 分開節點物理引擎

# 加入人物節點（含連結）
for _, row in persons.iterrows():
    link = row["wiki_link"] if pd.notna(row["wiki_link"]) else "#"
    title = f"<a href='{link}' target='_blank'>{row['name']} Wiki</a>"
    net.add_node(row["person_id"], label=row["name"], title=title, color="skyblue")

# 加入事件節點（含連結）
for _, row in events.iterrows():
    link = row["wiki_link"] if pd.notna(row["wiki_link"]) else "#"
    title = f"<a href='{link}' target='_blank'>事件：{row['event_name']}</a>"
    net.add_node(row["event_id"], label=row["event_name"], title=title, color="orange")

# 加入地點節點（含連結）
for _, row in locations.iterrows():
    link = row["wiki_link"] if pd.notna(row["wiki_link"]) else "#"
    title = f"<a href='{link}' target='_blank'>地點：{row['location_name']}</a>"
    net.add_node(row["location_id"], label=row["location_name"], title=title, color="lightgreen")

# 加入物件節點（含連結）
for _, row in objects.iterrows():
    link = row["wiki_link"] if pd.notna(row["wiki_link"]) else "#"
    title = f"<a href='{link}' target='_blank'>物件：{row['object_name']}</a>"
    net.add_node(row["object_id"], label=row["object_name"], title=title, color="violet")

# 加入時代節點（含連結）
for _, row in eras.iterrows():
    link = row["wiki_link"] if pd.notna(row["wiki_link"]) else "#"
    title = f"<a href='{link}' target='_blank'>時代：{row['era_name']}</a>"
    net.add_node(row["era_id"], label=row["era_name"], title=title, color="lightgray")

# 關聯邊（只加與目前顯示人物有關者）
person_ids = set(persons["person_id"])

# 人物 - 事件
for _, row in pe.iterrows():
    if row["person_id"] in person_ids:
        net.add_edge(row["person_id"], row["event_id"], label=row["role"])

# 人物 - 地點
for _, row in pl.iterrows():
    if row["person_id"] in person_ids:
        net.add_edge(row["person_id"], row["location_id"], label=row["relation_type"])

# 人物 - 物件
for _, row in po.iterrows():
    if row["person_id"] in person_ids:
        net.add_edge(row["person_id"], row["object_id"], label=row["relation_type"])

# 人物 - 時代
for _, row in pr.iterrows():
    if row["person_id"] in person_ids:
        net.add_edge(row["person_id"], row["era_id"], label="身處時代")

# 改為 write_html 並避免 notebook 模式
net.write_html("story_graph.html", notebook=False)

with open("story_graph.html", "r", encoding="utf-8") as f:
    html = f.read()
    components.html(html, height=750, scrolling=True)
