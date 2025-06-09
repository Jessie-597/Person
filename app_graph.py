import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components
import os

# 資料庫路徑
db_path = "story_graph.db"

# 建立資料庫連線
def get_connection():
    return sqlite3.connect(db_path)

# 載入表格資料
def load_table(table):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

# 載入所有資料
def load_all_data():
    return {
        "persons": load_table("Persons"),
        "events": load_table("Events"),
        "locations": load_table("Locations"),
        "objects": load_table("Objects"),
        "person_event": load_table("Person_Event"),
        "person_location": load_table("Person_Location"),
        "person_object": load_table("Person_Object"),
        "person_person": load_table("Person_Person")
    }

# 建立知識圖譜
def build_knowledge_graph(person_id, data):
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

    person_row = data["persons"][data["persons"].id == person_id].iloc[0]
    net.add_node(f"P{person_row.id}", label=person_row.name, title=person_row.description or person_row.name, 
                 shape='dot', size=25, color='red', 
                 href=person_row.wiki_url or "#")

    def add_relation(df, src_col, tgt_df, tgt_prefix, label):
        for _, row in df[df[src_col] == person_id].iterrows():
            target_id = row[f"{label.lower()}_id"]
            target_row = tgt_df[tgt_df.id == target_id].iloc[0]
            net.add_node(f"{tgt_prefix}{target_id}", label=target_row.name, 
                         title=target_row.get("description", target_row.name),
                         href=target_row.get("wiki_url", "#"))
            net.add_edge(f"P{person_id}", f"{tgt_prefix}{target_id}", label=label)

    add_relation(data["person_event"], "person_id", data["events"], "E", "Event")
    add_relation(data["person_location"], "person_id", data["locations"], "L", "Location")
    add_relation(data["person_object"], "person_id", data["objects"], "O", "Object")

    for _, row in data["person_person"][data["person_person"].person_id == person_id].iterrows():
        target_id = row["related_person_id"]
        target_row = data["persons"][data["persons"].id == target_id].iloc[0]
        net.add_node(f"P{target_id}", label=target_row.name,
                     title=target_row.get("description", target_row.name),
                     href=target_row.get("wiki_url", "#"))
        net.add_edge(f"P{person_id}", f"P{target_id}", label="Related")

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

# 主程式
st.title("淡水人物誌知識圖譜系統")

with st.sidebar:
    st.header("查詢功能")
    search_type = st.selectbox("查詢類型", ["人物", "事件", "地點", "物件"])
    keyword = st.text_input("請輸入關鍵字")

    if st.button("執行查詢"):
        conn = get_connection()
        table_map = {"人物": "Persons", "事件": "Events", "地點": "Locations", "物件": "Objects"}
        query = f"SELECT * FROM {table_map[search_type]} WHERE name LIKE ?"
        df = pd.read_sql_query(query, conn, params=[f"%{keyword}%"])
        conn.close()
        st.subheader(f"查詢結果：{search_type}")
        if not df.empty:
            df["維基連結"] = df["wiki_url"].apply(lambda url: f"[連結]({url})" if pd.notnull(url) else "無")
            st.dataframe(df.drop(columns=["wiki_url"]))
        else:
            st.info("查無資料")

st.header("知識圖譜視覺化")
data = load_all_data()
person_options = data["persons"][["id", "name"]].dropna()
selected_name = st.selectbox("請選擇要查看的主要人物：", person_options["name"])
selected_id = person_options[person_options["name"] == selected_name]["id"].values[0]

net = build_knowledge_graph(selected_id, data)
net.save_graph("graph.html")
components.html(open("graph.html", "r", encoding="utf-8").read(), height=620, scrolling=True)
