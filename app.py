
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

# --- 初始化 ---
st.set_page_config(layout="wide")
st.title("📚 淡水人物誌查詢與互動知識圖譜")

# --- 資料庫連線 ---
conn = sqlite3.connect("story_graph.db")

# --- 模糊查詢人物 ---
st.header("🔍 人物查詢")
query = st.text_input("輸入人物姓名關鍵字進行查詢：")
if query:
    persons = pd.read_sql(f"SELECT * FROM persons WHERE name LIKE '%{query}%'", conn)
    if not persons.empty:
        for _, row in persons.iterrows():
            st.markdown(f"### 👤 {row['name']}")
            st.markdown(f"- 生年：{row.get('birth_year', '')}；卒年：{row.get('death_year', '')}")
            st.markdown(f"- 職業：{row.get('occupation', '')}")
            st.markdown(f"- 貢獻：{row.get('contribution', '')}")
            st.markdown(f"- [🔗 資料來源]({row.get('wiki_link', '')})")
            st.markdown("---")
    else:
        st.warning("查無相關人物。")

# --- 篩選節點類型 ---
st.header("🌐 知識圖譜視覺化")

selected_types = st.multiselect(
    "顯示的節點類型：",
    ["人物", "時代", "地點", "事件", "物件"],
    default=["人物", "時代", "地點", "事件", "物件"]
)

# 讀取資料表
persons = pd.read_sql("SELECT * FROM persons", conn)
eras = pd.read_sql("SELECT * FROM eras", conn)
locations = pd.read_sql("SELECT * FROM locations", conn)
events = pd.read_sql("SELECT * FROM events", conn)
objects = pd.read_sql("SELECT * FROM objects", conn)
person_era = pd.read_sql("SELECT * FROM person_era", conn)
person_location = pd.read_sql("SELECT * FROM person_location", conn)
person_event = pd.read_sql("SELECT * FROM person_event", conn)
person_object = pd.read_sql("SELECT * FROM person_object", conn)
person_person = pd.read_sql("SELECT * FROM person_person", conn)

# 建立 PyVis Network
net = Network(height="650px", width="100%", bgcolor="#f9f9f9", font_color="black")
net.barnes_hut()

# 加入節點
if "人物" in selected_types:
    for _, row in persons.iterrows():
        net.add_node(f"person_{row['person_id']}", label=row['name'], title=row['name'], color="skyblue", shape="dot", href=row.get('wiki_link', '') or None)

if "時代" in selected_types:
    for _, row in eras.iterrows():
        net.add_node(f"era_{row['era_id']}", label=row['era_name'], title=row['era_name'], color="lightgreen", shape="box", href=row.get('wiki_link', '') or None)

if "地點" in selected_types:
    for _, row in locations.iterrows():
        net.add_node(f"location_{row['location_id']}", label=row['location_name'], title=row['location_name'], color="orange", shape="triangle", href=row.get('wiki_link', '') or None)

if "事件" in selected_types:
    for _, row in events.iterrows():
        net.add_node(f"event_{row['event_id']}", label=row['event_name'], title=row['event_name'], color="violet", shape="ellipse", href=row.get('wiki_link', '') or None)

if "物件" in selected_types:
    for _, row in objects.iterrows():
        net.add_node(f"object_{row['object_id']}", label=row['object_name'], title=row['object_name'], color="pink", shape="hexagon", href=row.get('wiki_link', '') or None)

# 加入邊（不做類型篩選，保持連結完整）
for _, row in person_era.iterrows():
    net.add_edge(f"person_{row['person_id']}", f"era_{row['era_id']}")

for _, row in person_location.iterrows():
    net.add_edge(f"person_{row['person_id']}", f"location_{row['location_id']}")

for _, row in person_event.iterrows():
    net.add_edge(f"person_{row['person_id']}", f"event_{row['event_id']}")

for _, row in person_object.iterrows():
    net.add_edge(f"person_{row['person_id']}", f"object_{row['object_id']}")

for _, row in person_person.iterrows():
    net.add_edge(f"person_{row['person_id_1']}", f"person_{row['person_id_2']}")

# JSON 選項
net.set_options("""
{
  "nodes": {
    "shape": "dot",
    "size": 16,
    "font": {
      "size": 14,
      "color": "#000000"
    }
  },
  "edges": {
    "color": {
      "color": "#A0A0A0",
      "highlight": "#FF5733"
    },
    "arrows": {
      "to": {
        "enabled": false
      }
    }
  },
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "keyboard": true
  },
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -30000,
      "springLength": 200,
      "springConstant": 0.01,
      "centralGravity": 0.3,
      "damping": 0.4
    },
    "minVelocity": 0.75
  }
}
""")

# 輸出並嵌入
net.show("graph.html")
with open("graph.html", "r", encoding="utf-8") as f:
    graph_html = f.read()
components.html(graph_html, height=700, scrolling=True)
