import streamlit as st
import requests
import pandas as pd
import base64


def fetch_studies_v2(cond_value, overall_status_value, location_value):
    """
    ClinicalTrials.gov v2 API (Beta) からデータを取得する関数。
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.cond": cond_value,
        "filter.overallStatus": overall_status_value,
        "query.locn": location_value
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def generate_download_link(df):
    """
    pandas DataFrame から base64 エンコードされた CSV ダウンロードリンクを生成。
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="clinicaltrials_results.csv">📥 CSVをダウンロード</a>'


def extract_relevant_data(api_json):
    """
    APIレスポンスから、表表示・CSV化に適した情報を抽出。
    """
    studies = api_json.get("studies", [])
    extracted = []

    for study in studies:
        protocol_id = study.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "")
        title = study.get("protocolSection", {}).get("identificationModule", {}).get("briefTitle", "")
        condition = ", ".join(study.get("protocolSection", {}).get("conditionsModule", {}).get("conditions", []))
        status = study.get("protocolSection", {}).get("statusModule", {}).get("overallStatus", "")
        last_update = study.get("protocolSection", {}).get("statusModule", {}).get("lastUpdateSubmitDate", "")
        url = f"https://clinicaltrials.gov/study/{protocol_id}" if protocol_id else ""

        extracted.append({
            "NCT ID": protocol_id,
            "Title": title,
            "Condition": condition,
            "Status": status,
            "Last Update": last_update,
            "Link": url
        })

    return pd.DataFrame(extracted)


def main():
    st.title("ClinicalTrials.gov v2 検索ツール（ベータ版）")

    cond_value = st.text_input("Condition (query.cond)", "lung cancer")
    overall_status_value = st.text_input("Overall Status (filter.overallStatus)", "RECRUITING")
    location_value = st.text_input("Location (query.locn)", "Japan")

    if st.button("Search"):
        try:
            data = fetch_studies_v2(cond_value, overall_status_value, location_value)
            st.write("検索パラメータ:", {
                "query.cond": cond_value,
                "filter.overallStatus": overall_status_value,
                "query.locn": location_value
            })

            df = extract_relevant_data(data)

            if not df.empty:
                st.subheader("🔍 検索結果")
                st.dataframe(df, use_container_width=True)

                st.markdown(generate_download_link(df), unsafe_allow_html=True)
            else:
                st.warning("検索結果が見つかりませんでした。")

        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e}")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
