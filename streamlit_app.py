import streamlit as st
import requests
import pandas as pd
import base64

def fetch_studies_v2(cond_value, overall_status_value, location_value, term_value, sponsor_value):
    """
    ClinicalTrials.gov v2 API からデータを取得
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.cond": cond_value,
        "filter.overallStatus": overall_status_value,
        "query.locn": location_value,
        "query.term": term_value,
        "query.sponsor": sponsor_value  # スポンサー企業名での絞り込みを追加
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()


def main():
    st.title("ClinicalTrials.gov v2 検索ツール（ベータ版）")

    # 入力フォームに Sponsor Name（query.sponsor）追加
    cond_value = st.text_input("Condition (query.cond)", "lung cancer")
    overall_status_value = st.text_input("Overall Status (filter.overallStatus)", "RECRUITING")
    location_value = st.text_input("Location (query.locn)", "Japan")
    term_value = st.text_input("Other Terms (query.term)", "EGFR")
    sponsor_value = st.text_input("Sponsor Name (query.sponsor)", "")  # スポンサー企業名の入力フィールド

    if st.button("Search"):
        try:
            data = fetch_studies_v2(cond_value, overall_status_value, location_value, term_value, sponsor_value)

            st.write("検索パラメータ:", {
                "query.cond": cond_value,
                "filter.overallStatus": overall_status_value,
                "query.locn": location_value,
                "query.term": term_value,
                "query.sponsor": sponsor_value
            })

            studies = data.get("studies", [])

            if not studies:
                st.warning("検索結果が見つかりませんでした。")
                return

            # 表示とCSV用データ加工
            result_rows = []
            for s in studies:
                protocol = s.get("protocolSection", {})
                id_info = protocol.get("identificationModule", {})
                status = protocol.get("statusModule", {})
                conditions = protocol.get("conditionsModule", {})
                sponsor = protocol.get("sponsorCollaboratorsModule", {})

                result_rows.append({
                    "Study Title": id_info.get("briefTitle", "N/A"),
                    "NCT Number": id_info.get("nctId", "N/A"),
                    "Status": status.get("overallStatus", "N/A"),
                    "Condition": ", ".join(conditions.get("conditions", [])),
                    "Sponsor": sponsor.get("leadSponsor", {}).get("name", "N/A")
                })

            df = pd.DataFrame(result_rows)

            # 表表示
            st.subheader("検索結果")
            st.dataframe(df)

            # CSV ダウンロード
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="clinical_trials.csv">📥 CSVをダウンロード</a>'
            st.markdown(href, unsafe_allow_html=True)

        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e}")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

main()
