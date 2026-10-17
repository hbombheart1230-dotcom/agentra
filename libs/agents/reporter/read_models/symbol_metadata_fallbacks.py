"""Reporter read-model owner (decomposed from libs/reporting/trade_report_symbol_metadata.py; bodies verbatim). Static symbol name/theme fallbacks."""
from __future__ import annotations

from typing import Dict, List


SYMBOL_NAME_FALLBACKS: Dict[str, str] = {
    "000660": "SK하이닉스",
    "012330": "현대모비스",
    "003060": "에이프로젠바이오로직스",
    "034220": "LG디스플레이",
    "024840": "KBI메탈",
    "024060": "흥구석유",
    "005380": "현대차",
    "005930": "삼성전자",
    "005935": "삼성전자우",
    "006800": "미래에셋증권",
    "006345": "대원전선우",
    "009150": "삼성전기",
    "011930": "신성이엔지",
    "035420": "NAVER",
    "046970": "우리로",
    "062970": "한국첨단소재",
    "073490": "이노와이어리스",
    "090710": "휴림로봇",
    "102120": "어보브반도체",
    "114800": "KODEX 인버스",
    "122630": "KODEX 레버리지",
    "126340": "비나텍",
    "233740": "KODEX 코스닥150레버리지",
    "252670": "KODEX 200선물인버스2X",
    "252710": "TIGER 200선물인버스2X",
    "402340": "SK스퀘어",
}


SYMBOL_THEME_FALLBACKS: Dict[str, List[str]] = {
    "012330": ["자동차부품", "전기차", "자율주행차", "수소차"],
    "006345": ["전선", "전력설비", "구리"],
    "024840": ["전선", "구리", "전력설비"],
    "034220": ["OLED", "LCD", "디스플레이패널"],
    "006800": ["증권", "금융투자", "자산관리"],
}
