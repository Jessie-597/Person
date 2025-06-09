import streamlit as st
import sqlite3
import pandas as pd

# 資料庫連線
conn = sqlite3.connect("story_graph.db")

st.title("淡水人物誌查詢系統")

menu = st.sidebar.selectbox("請選擇查詢功能", ["🔎 查詢人物", "📅 查詢事件", "📍 查詢地點"])

# 查詢人物
if menu == "🔎 查詢人物":
    name = st.text_input("輸入人物姓名（可模糊查詢）")
    if name:
        query = f"SELECT * FROM Persons WHERE name LIKE '%{name}%'"
        df = pd.read_sql(query, conn)
        st.dataframe(df)

        if not df.empty:
            selected_id = df["person_id"].iloc[0]
            st.subheader("📌 關聯事件")
            event_query = f"""
                SELECT E.event_name, E.event_year, E.site
                FROM Person_Event PE
                JOIN Events E ON PE.event_id = E.event_id
                WHERE PE.person_id = '{selected_id}'
            """
            st.dataframe(pd.read_sql(event_query, conn))

            st.subheader("📌 關聯地點")
            loc_query = f"""
                SELECT L.location_name, L.location_type, L.district
                FROM Person_Location PL
                JOIN Locations L ON PL.location_id = L.location_id
                WHERE PL.person_id = '{selected_id}'
            """
            st.dataframe(pd.read_sql(loc_query, conn))

            st.subheader("📌 關聯物件")
            obj_query = f"""
                SELECT O.object_name, O.object_type, O.site
                FROM Person_Object PO
                JOIN Objects O ON PO.object_id = O.object_id
                WHERE PO.person_id = '{selected_id}'
            """
            st.dataframe(pd.read_sql(obj_query, conn))

# 查詢事件
elif menu == "📅 查詢事件":
    year = st.number_input("請輸入年份（精確查詢）", min_value=1800, max_value=2025, step=1)
    if year:
        query = f"SELECT * FROM Events WHERE event_year = {year}"
        df = pd.read_sql(query, conn)
        st.dataframe(df)

# 查詢地點
elif menu == "📍 查詢地點":
    location = st.text_input("輸入地點名稱（可模糊查詢）")
    if location:
        query = f"SELECT * FROM Locations WHERE location_name LIKE '%{location}%'"
        df = pd.read_sql(query, conn)
        st.dataframe(df)

conn.close()
