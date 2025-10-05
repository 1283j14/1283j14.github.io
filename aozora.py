import requests
import zipfile
import io
import re
from typing import Optional, Dict, List


class AozoraLoader:
    """青空文庫のテキストデータを取得・整形するクラス"""

    def __init__(self):
        self.cache: Dict[str, str] = {}  # URLごとのテキストキャッシュ

    def _download_zip(self, url: str) -> Optional[str]:
        """青空文庫のZIPファイルをダウンロードして展開"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                txt_name = next((n for n in z.namelist() if n.endswith(".txt")), None)
                if not txt_name:
                    return None
                with z.open(txt_name) as f:
                    return f.read().decode("shift_jis", errors="ignore")
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """青空文庫テキストから本文のみを抽出して整形"""
        # ヘッダー部分（---より前）を削除
        if "---" in text:
            text = text.split("---", 2)[-1]

        # フッター部分（底本：など）を削除
        text = re.split(r"底本：|青空文庫作成ファイル", text)[0]

        # ルビ・注記などを削除
        text = re.sub(r"［＃.*?］|《.*?》|｜|〔.*?〕|http[^\s]+|※", "", text)

        # 空白や改行を整形
        text = text.strip()
        text = re.sub(r"[\r\n\u3000]+", " ", text)  # 改行や全角スペースを半角スペースに
        text = re.sub(r"\s{2,}", " ", text)  # 連続するスペースを1つに
        return text

    def load(self, url: str) -> Optional[str]:
        """URLから整形済みのテキストを取得（キャッシュ利用）"""
        if url in self.cache:
            return self.cache[url]

        raw_text = self._download_zip(url)
        if raw_text:
            cleaned_text = self._clean_text(raw_text)
            # ある程度の長さがない場合はキャッシュしない
            if len(cleaned_text) > 100:
                self.cache[url] = cleaned_text
            return cleaned_text
        return None
