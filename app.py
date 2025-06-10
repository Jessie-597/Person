
import sqlite3
import pandas as pd
from pyvis.network import Network

# 連線到 SQLite 資料庫
conn = sqlite3.connect("story_graph.db")
data = {
    "persons": pd.read_sql_query("SELECT * FROM Persons", conn),
    "events": pd.read_sql_query("SELECT * FROM Events", conn),
    "eras": pd.read_sql_query("SELECT * FROM Eras", conn),
    "locations": pd.read_sql_query("SELECT * FROM Locations", conn),
    "objects": pd.read_sql_query("SELECT * FROM Objects", conn),
    "person_person": pd.read_sql_query("SELECT * FROM Person_Person", conn),
    "person_event": pd.read_sql_query("SELECT * FROM Person_Event", conn),
    "person_era": pd.read_sql_query("SELECT * FROM Person_Era", conn),
    "person_location": pd.read_sql_query("SELECT * FROM Person_Location", conn),
    "person_object": pd.read_sql_query("SELECT * FROM Person_Object", conn),
}
conn.close()

net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
color_map = {
    "person": "#FFD700",
    "event": "#87CEEB",
    "era": "#FFB6C1",
    "location": "#90EE90",
    "object": "#FFA07A",
}

def add_node(node_id, label, title, group, url=None):
    net.add_node(
        node_id,
        label=label,
        title=title,
        color=color_map[group],
        shape="dot",
        size=18,
        href=url if pd.notnull(url) else None
    )

for _, row in data["persons"].iterrows():
    add_node(f"P{row['person_id']}", row["name"], row["contribution"], "person", row["wiki_link"])

for _, row in data["events"].iterrows():
    add_node(f"E{row['event_id']}", row["event_name"], f"{row['event_year']}年事件", "event", row["wiki_link"])

for _, row in data["eras"].iterrows():
    add_node(f"T{row['era_id']}", row["era_name"], row["description"], "era", row["wiki_link"])

for _, row in data["locations"].iterrows():
    add_node(f"L{row['location_id']}", row["location_name"], row["location_type"], "location", row["wiki_link"])

for _, row in data["objects"].iterrows():
    add_node(f"O{row['object_id']}", row["object_name"], row["object_type"], "object", row["wiki_link"])

def add_edge(src, tgt, label):
    net.add_edge(src, tgt, label=label)

for _, row in data["person_event"].iterrows():
    add_edge(f"P{row['person_id']}", f"E{row['event_id']}", row["role"])

for _, row in data["person_era"].iterrows():
    add_edge(f"P{row['person_id']}", f"T{row['era_id']}", row["note"])

for _, row in data["person_location"].iterrows():
    add_edge(f"P{row['person_id']}", f"L{row['location_id']}", row["relation_type"])

for _, row in data["person_object"].iterrows():
    add_edge(f"P{row['person_id']}", f"O{row['object_id']}", row["relation_type"])

for _, row in data["person_person"].iterrows():
    add_edge(f"P{row['person_id_1']}", f"P{row['person_id_2']}", row["relationship_type"])

net.set_options("""
{
  "nodes": {
    "font": {
      "size": 14
    }
  },
  "edges": {
    "font": {
      "size": 12,
      "align": "middle"
    },
    "arrows": {
      "to": {
        "enabled": true
      }
    }
  },
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -8000,
      "centralGravity": 0.3,
      "springLength": 100
    }
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 100,
    "hideEdgesOnDrag": true
  }
}
""")

net.save_graph("graph_final_visual.html")
print("✅ 圖譜已產生：graph_final_visual.html")
