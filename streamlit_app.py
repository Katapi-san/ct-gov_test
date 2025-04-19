import requests

def fetch_studies_in_japan(query_term="EGFR"):
    """
    ClinicalTrials.gov v2 APIを使い、指定した検索キーワードと
    日本で実施中 (例: Recruiting) の治験データを取得する関数。

    Parameters:
    -----------
    query_term : str
        検索に使うキーワード。デフォルトは "EGFR"。
        例: "lung cancer", "EGFR", "KRAS", etc.

    Returns:
    --------
    dict
        APIから取得したJSONレスポンス（Pythonの辞書）
    """
    base_url = "https://clinicaltrials.gov/api/v2/studies"

    # クエリパラメータ (v2 API はベータ版; 実際のキー名が変更される可能性あり)
    params = {
        "query": query_term,     # 検索キーワード
        "country": "Japan",      # 国指定
        "status": "Recruiting",  # ステータス: 例として "Recruiting" に限定
        "pageSize": 20,          # 1ページ当たりの取得件数
        "page": 1                # ページ番号
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 4xx/5xxエラー時に例外
        data = response.json()
        return data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def main():
    # "EGFR" を検索する例
    raw_data = fetch_studies_in_japan("EGFR")

    # 返却データを簡易表示
    if raw_data and "data" in raw_data and "studies" in raw_data["data"]:
        studies_list = raw_data["data"]["studies"]
        print(f"取得した治験数: {len(studies_list)}")
        
        for study in studies_list:
            # サンプルとしてNCTID, タイトル, ステータスを表示
            nct_id = study.get("nctId", "N/A")
            title = study.get("title", "N/A")
            status = study.get("overallStatus", "N/A")
            
            print("NCT ID:", nct_id)
            print("Title:", title)
            print("Status:", status)
            print("-" * 80)
    else:
        print("検索結果が存在しないか、レスポンス形式が想定と異なっています。")

if __name__ == "__main__":
    main()
