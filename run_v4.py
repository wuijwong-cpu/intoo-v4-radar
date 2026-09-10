# -*- coding: utf-8 -*-
"""_v4_patch_type.py — 给 2.0_合并版 再加「类型层(Type_A~D) + 可选行业层」"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = Path(r"D:/OneDrive/python/M：股票池/测试/V4-T趋势策略（白名单）2.0_合并版.py")
src = P.read_text(encoding="utf-8")
shutil_bak = P.with_suffix(".py.bak_type")
shutil_bak.write_text(src, encoding="utf-8")

ANCHOR_THR = "    'JP': {'squeeze_max': None, 'deviation_max': 0.75, 'deviation_min': 0.50}\n}"
NEW_CFG = ANCHOR_THR + '''

# 【类型层】由回测（2013-2026，按"每笔"统计，样本内→样本外）得出：不同类别的区分度很大
#   Type_B 成长/科技  +0.50R（胜率49.1%，样本内外 0.56→0.46）  -> 维持
#   Type_C 周期       +0.39R（0.35→0.42）                      -> 略放宽
#   Type_A 防御/价值  +0.32R（0.32→0.33，历史最弱）            -> 收紧乖离 + 降权
#   Type_D 高波动题材 +0.42R，但样本内外 0.61→0.37（不稳）     -> 降权观察
TYPE_OF = {}
for _u in (V4_US_UNIVERSE, V4_JP_UNIVERSE, V4_HK_UNIVERSE, V4_CN_UNIVERSE):
    for _c, _tks in _u.items():
        for _t in _tks:
            TYPE_OF[_t] = _c
TYPE_RULES = {
    'Type_A': {'enabled': True, 'deviation_max': 0.60, 'weight': 0.5},
    'Type_B': {'enabled': True, 'deviation_max': 0.90, 'weight': 1.0},
    'Type_C': {'enabled': True, 'deviation_max': 0.75, 'weight': 0.8},
    'Type_D': {'enabled': True, 'deviation_max': 0.75, 'weight': 0.3},
}
# 【行业层·可选】把 sector_map.csv（列：Ticker,GICS_Sector）放在脚本同目录即自动生效；
#   缺文件则只启用类型层。回测：信息技术 +0.57R 最强；房地产 +0.04R（平均收益为负）最差。
SECTOR_EXCLUDE = {'房地产'}
SECTOR_MAP = {}
try:
    import csv as _csv
    _sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sector_map.csv')
    if os.path.exists(_sp):
        with open(_sp, encoding='utf-8-sig', newline='') as _f:
            for _r in _csv.DictReader(_f):
                SECTOR_MAP[(_r.get('Ticker') or '').strip()] = (_r.get('GICS_Sector') or '').strip()
        print(f"[行业层] 已加载 sector_map.csv：{len(SECTOR_MAP)} 条")
    else:
        print("[行业层] 未提供 sector_map.csv -> 仅启用类型层")
except Exception as _e:
    print(f"[行业层] sector_map.csv 读取失败: {_e}")'''

OLD_CHK = ("    market = MARKET_MAP.get(ticker, 'US')\n"
           "    thresholds = ML_THRESHOLDS.get(market, ML_THRESHOLDS['US'])")
NEW_CHK = ("    market = MARKET_MAP.get(ticker, 'US')\n"
           "    thresholds = dict(ML_THRESHOLDS.get(market, ML_THRESHOLDS['US']))\n"
           "    # ---- 类型层 / 行业层（回测驱动）----\n"
           "    _t = TYPE_OF.get(ticker)\n"
           "    _tr = TYPE_RULES.get(_t, {})\n"
           "    if _tr and _tr.get('enabled') is False:\n"
           "        return False, f\"类型 {_t} 本期不参与\", None\n"
           "    if _tr.get('deviation_max') is not None:\n"
           "        thresholds['deviation_max'] = _tr['deviation_max']\n"
           "    if SECTOR_MAP and SECTOR_MAP.get(ticker) in SECTOR_EXCLUDE:\n"
           "        return False, f\"行业 {SECTOR_MAP.get(ticker)} 已排除（历史最差）\", None")

OLD_APP = ("                results.append({\n"
           "                    '市场': MARKET_MAP[ticker],")
NEW_APP = ("                _tp = TYPE_OF.get(ticker, '未分类')\n"
           "                _wt = TYPE_RULES.get(_tp, {}).get('weight', 1.0)\n"
           "                results.append({\n"
           "                    '市场': MARKET_MAP[ticker],\n"
           "                    '类型': _tp,\n"
           "                    '建议权重': _wt,")

OLD_COL = "    columns_order = ['市场', '代码', '信号', '现价', 'ATR', '挤压率', '乖离率', '1R防线']"
NEW_COL = ("    columns_order = ['市场', '类型', '建议权重', '代码', '信号', '现价', 'ATR',\n"
           "                    '挤压率', '乖离率', '1R防线']")

OLD_PUSH = """            content += f"  - 1R防线: **{item['1R防线']}**\\n\\n\""""
NEW_PUSH = """            content += f"  - 1R防线: **{item['1R防线']}** | 类型: {item.get('类型', '-')} (权重 {item.get('建议权重', 1.0)})\\n\\n\""""

PAIRS = [(OLD_CHK, NEW_CHK), (OLD_APP, NEW_APP), (OLD_COL, NEW_COL), (OLD_PUSH, NEW_PUSH)]
src2 = src.replace(ANCHOR_THR, NEW_CFG, 1)
n_thr = 1 if src2 != src else 0
src = src2
ok, miss = 0, []
for old, new in PAIRS:
    c = src.count(old)
    if c == 1:
        src = src.replace(old, new)
        ok += 1
    else:
        miss.append(f"{c}x :: {old[:70]!r}")
print(f"[配置块] {n_thr}/1 | [代码补丁] {ok}/{len(PAIRS)}")
for m in miss:
    print("   未命中: " + m)
if miss or n_thr != 1:
    print("❗ 未写出（请人工核对）")
    raise SystemExit(1)
ast.parse(src)
P.write_text(src, encoding="utf-8")
print(f"[✓] 已更新 {P.name} ({P.stat().st_size:,} bytes) | 备份 {shutil_bak.name}")
