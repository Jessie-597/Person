
import sqlite3
import pandas as pd
from pyvis.network import Network

# 連接資料庫
conn = sqlite3.connect("story_graph.db")

# 建立圖形物件
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")

# 加入人物節點
persons = pd.read_sql_query("SELECT * FROM persons", conn)
for _, row in persons.iterrows():
    net.add_node(row["id"], label=row["name"], title=row["alias"], color="#ff9999", shape="dot")

# 加入時代節點
eras = pd.read_sql_query("SELECT * FROM eras", conn)
for _, row in eras.iterrows():
    net.add_node(f"era_{row['id']}", label=row["era"], title=row["era"], color="#9999ff", shape="box")

# 加入事件節點
events = pd.read_sql_query("SELECT * FROM events", conn)
for _, row in events.iterrows():
    net.add_node(f"event_{row['id']}", label=row["event_name"], title=row["summary"], color="#66cc66", shape="diamond")

# 加入地點節點
locations = pd.read_sql_query("SELECT * FROM locations", conn)
for _, row in locations.iterrows():
    net.add_node(f"loc_{row['id']}", label=row["name"], title=row["type"], color="#ffcc66", shape="triangle")

# 加入物件節點
objects = pd.read_sql_query("SELECT * FROM objects", conn)
for _, row in objects.iterrows():
    net.add_node(f"obj_{row['id']}", label=row["name"], title=row["description"], color="#cc99ff", shape="ellipse")

# 加入關聯邊
edges = [
    ("person_event", "person_id", "event_id", "event_"),
    ("person_era", "person_id", "era_id", "era_"),
    ("person_location", "person_id", "location_id", "loc_"),
    ("person_object", "person_id", "object_id", "obj_"),
    ("person_person", "person_id", "related_person_id", ""),
]

for table, from_col, to_col, prefix in edges:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    for _, row in df.iterrows():
        net.add_edge(row[from_col], f"{prefix}{row[to_col]}")

# 設定圖譜樣式（修正 JSON 中 true/false 的大小寫）
net.set_options("""
{
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -5000,
      "centralGravity": 0.3,
      "springLength": 150,
      "springConstant": 0.04,
      "damping": 0.09,
      "avoidOverlap": 0.3
    },
    "minVelocity": 0.75
  },
  "nodes": {
    "shape": "dot",
    "size": 20,
    "font": {
      "size": 15
    }
  },
  "edges": {
    "color": {
      "inherit": true
    },
    "smooth": false
  },
  "interaction": {
    "navigationButtons": true,
    "tooltipDelay": 200,
    "hideEdgesOnDrag": false
  }
}
""")

# 輸出 HTML
net.show("story_graph.html")
