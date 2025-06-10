
import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

DB_PATH = "story_graph.db"

COLOR_MAP = {
    "Person": "blue",
    "Event": "red",
    "Era": "green",
    "Location": "orange",
    "Object": "purple"
}

def create_network():
    net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="black")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    persons = pd.read_sql_query("SELECT * FROM Persons", conn)
    events = pd.read_sql_query("SELECT * FROM Events", conn)
    eras = pd.read_sql_query("SELECT * FROM Eras", conn)
    locations = pd.read_sql_query("SELECT * FROM Locations", conn)
    objects = pd.read_sql_query("SELECT * FROM Objects", conn)

    def add_node_safe(net, node_id, label, color, wiki_link, title):
        if pd.notna(wiki_link) and wiki_link.strip():
            net.add_node(node_id, label=label, color=color, title=title,
                         shape="dot", size=15, url=wiki_link)
        else:
            net.add_node(node_id, label=label, color=color, title=title,
                         shape="dot", size=15)

    for _, row in persons.iterrows():
        add_node_safe(net, row["person_id"], row["name"], COLOR_MAP["Person"], row["wiki_link"], "人物")
    for _, row in events.iterrows():
        add_node_safe(net, row["event_id"], row["event_name"], COLOR_MAP["Event"], row["wiki_link"], "事件")
    for _, row in eras.iterrows():
        add_node_safe(net, row["era_id"], row["era_name"], COLOR_MAP["Era"], row["wiki_link"], "時代")
    for _, row in locations.iterrows():
        add_node_safe(net, row["location_id"], row["location_name"], COLOR_MAP["Location"], row["wiki_link"], "地點")
    for _, row in objects.iterrows():
        add_node_safe(net, row["object_id"], row["object_name"], COLOR_MAP["Object"], row["wiki_link"], "物件")

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

    net.set_options("""
    {
      "physics": {
        "enabled": false
      },
      "interaction": {
        "dragNodes": true,
        "tooltipDelay": 200
      }
    }
    """)

    return net

st.set_page_config(layout="wide")
st.title("大淡水人物誌知識圖譜")

net = create_network()
net.save_graph("graph.html")

with open("graph.html", "r", encoding="utf-8") as f:
    html_content = f.read()

custom_js = """
<script type="text/javascript">
function addOpenWikiListener() {
  network.on("click", function(params) {
    if (params.nodes.length > 0) {
      var nodeId = params.nodes[0];
      var node = nodes.get(nodeId);
      if (node.url) {
        window.open(node.url, "_blank");
      }
    }
  });
}
window.addEventListener("load", addOpenWikiListener);
</script>
</body>
"""

html_content = html_content.replace("</body>", custom_js)

with open("graph.html", "w", encoding="utf-8") as f:
    f.write(html_content)

components.html(html_content, height=700, scrolling=True)
