import streamlit as st
import requests
import pandas as pd
import base64

def fetch_studies_v2(cond_value, overall_status_value, location_value, term_value):
    """
    ClinicalTrials.gov v2 API からデータを取得
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.cond": cond_value,
        "filter.overallStatus": overall_status_value,
        "query.locn": location_value,
        "query.term": term_value  # ← 追加
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def main():
    st.title("ClinicalTrials.gov v2 検索ツール（ベータ版）")

    # 🔽 入力フォームに Other Term（query.term）追加
    cond_value = st.text_input("Condition (query.cond)", "lung cancer")
    overall_status_value = st.text_input("Overall Status (filter.overallStatus)", "RECRUITING")
    location_value = st.text_input("Location (query.locn)", "Japan")
    term_value = st.text_input("Other Terms (query.term)", "EGFR")  # ← デフォルトで EGFR

    if st.button("Search"):
        try:
            data = fetch_studies_v2(cond_value, overall_status_value, location_value, term_value)

            st.write("検索パラメータ:", {
                "query.cond": cond_value,
                "filter.overallStatus": overall_status_value,
                "query.locn": location_value,
                "query.term": term_value
            })

            studies = data.get("studies", [])

            if not studies:
                st.warning("検索結果が見つかりませんでした。")
                return

            # 🔽 表示とCSV用データ加工
            result_rows = []
            for s in studies:
                protocol = s.get("protocolSection", {})
                id_info = protocol.get("identificationModule", {})
                status = protocol.get("statusModule", {})
                conditions = protocol.get("conditionsModule
