import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import requests
from datetime import datetime
import os

warnings.filterwarnings('ignore')

# =====================================================================
# INTOO V4-Quantamental: 104只美股战略观察池 (按物种分类)
# =====================================================================
V4US_UNIVERSE = {
    'Type_A': ['XOM','CVX','COST','JNJ','PG','KO','PEP','WMT','MCD','ABBV','MRK','HD','UNH','V','MA','JPM','BAC','BRK-B','MS','NEE','SO','DUK','LMT','RTX','GD','PM','MO','VZ','T','PFE','AMGN','GILD','UPS','EMR','WM','APD'],
    'Type_B': ['NVDA','MSFT','AMD','META','QCOM','GOOGL','AMZN','CRWD','PLTR','NOW','SNOW','DDOG','AAPL','AVGO','TSM','ASML','PANW','LLY','NFLX','CRM','ANET','ARM','MRVL','MU','KLAC','LRCX','AMAT','CDNS','SNPS','INTU','WDAY','TEAM','FTNT','ZS','MDB','APP','UBER','ISRG','VRTX','REGN','CELH','TRMD','VRT','SMCI','TTD'],
    'Type_C': ['TSLA','CAT','FCX','CIEN','C','SLB','HAL','NUE','SCCO','URI','PWR','BA','GM','DOW','LYB'],
    'Type_D': ['COIN','MSTR','HOOD','CVNA','RDDT','ASTS','LUNR','RBLX']
}

# 展平列表以便于 YFinance 批量下载
TICKERS = [ticker for sublist in V4US_UNIVERSE.values() for ticker in sublist]

# 参数设定
SHORT_GMMA = [3, 5, 8, 10, 12, 15]
LONG_GMMA = [30, 35, 40, 45, 50, 60]

def calc_v4_indicators(df):
    """计算 V4 体系要求的所有物理指标 (MACD, GMMA, BOLL, ATR)"""
    if df.empty or len(df) < 26: 
        return None
        
    df['BOLL_MID'] = df['Close'].rolling(window=20).mean()
    df['BOLL_STD'] = df['Close'].rolling(window=20).std()
    df['BOLL_UP'] = df['BOLL_MID'] + 2 * df['BOLL_STD']
    df['BOLL_LW'] = df['BOLL_MID'] - 2 * df['BOLL_STD']
    df['BOLL_WIDTH'] = (df['BOLL_UP'] - df['BOLL_LW']) / df['BOLL_MID'] 
    
    for period in SHORT_GMMA:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
    for period in LONG_GMMA:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
        
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD_DIF'] = df['EMA12'] - df['EMA26']
    df['MACD_DEA'] = df['MACD_DIF'].ewm(span=9, adjust=False).mean()
    
    if 'High' in df.columns and 'Low' in df.columns:
        df['TR'] = np.maximum(df['High'] - df['Low'], 
                   np.maximum(abs(df['High'] - df['Close'].shift(1)), 
                              abs(df['Low'] - df['Close'].shift(1))))
        df['ATR'] = df['TR'].rolling(window=14).mean()
    else:
        df['ATR'] = np.nan
        
    return df

def check_v4_resonance_strict(df_daily):
    """执行 V4 动态多周期物理共振审核"""
    if len(df_daily) < 30:
        return False, "数据极端匮乏，无法建立坐标系", None

    df_weekly = df_daily.resample('W-FRI').agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
    df_monthly = df_daily.resample('ME').agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
    
    df_d = calc_v4_indicators(df_daily.copy())
    df_w = calc_v4_indicators(df_weekly.copy())
    df_m = calc_v4_indicators(df_monthly.copy())
    
    if df_d is None or df_w is None or df_m is None:
        return False, "指标生成失败", None

    curr_d = df_d.iloc[-1]
    prev_d = df_d.iloc[-2] # 获取前一日数据用于斜率比对
    curr_w = df_w.iloc[-1]
    curr_m = df_m.iloc[-1] if len(df_m) > 0 else None

    # 1：MACD 宏观重力压制
    if curr_m is not None and not pd.isna(curr_m['MACD_DIF']):
        if curr_m['MACD_DIF'] < curr_m['MACD_DEA'] and curr_m['MACD_DIF'] < 0:
            return False, "月线水下死叉", None
            
    if not pd.isna(curr_w['MACD_DIF']):
        if curr_w['MACD_DIF'] < curr_w['MACD_DEA']:
            return False, "周线死叉压制", None

    # 2：GMMA 筹码结构
    d_short_mas = [curr_d[f'SMA_{p}'] for p in SHORT_GMMA]
    d_long_mas = [curr_d[f'SMA_{p}'] for p in LONG_GMMA]
    if min(d_short_mas) <= max(d_long_mas):
        return False, "均线结构纠缠", None

    # 3：BOLL 生命线与趋势锁 (Trend Lock)
    if curr_d['Close'] <= curr_d['BOLL_MID']:
        return False, "跌破日线中轨", None
    if curr_d['BOLL_MID'] <= prev_d['BOLL_MID']:
        return False, "中轨向下或走平 (假突破过滤)", None

    # 4：乖离率防追高
    if not pd.isna(curr_d['ATR']):
        deviation_ratio = (curr_d['Close'] - curr_d['BOLL_MID']) / curr_d['ATR']
        if deviation_ratio > 1.5:
            return False, f"乖离率过大 ({deviation_ratio:.2f} ATR)", None

    # 5：挤压锁 (Squeeze Lock)
    squeeze_ratio = curr_d['BOLL_WIDTH']
    if squeeze_ratio > 0.30: 
        return False, "波动率过度发散", None
        
    signal_strength = "S级 (完美共振)" if squeeze_ratio < 0.12 else "A级 (常态推升)"

    dashboard_data = {
        'Close': round(curr_d['Close'], 2),
        'ATR': round(curr_d['ATR'], 2) if not pd.isna(curr_d['ATR']) else 0,
        'Squeeze': f"{squeeze_ratio*100:.1f}%",
        'Deviation': f"{deviation_ratio:.1f} ATR",
        'Dynamic_Stop': round(curr_d['Close'] - 2.5 * curr_d['ATR'], 2) if not pd.isna(curr_d['ATR']) else 0
    }
    
    return True, f"【{signal_strength}】允许扣板", dashboard_data

def export_to_excel(results):
    """将扫描结果自动化导出为 Excel 猎物池"""
    df = pd.DataFrame(results)
    today_str = datetime.now().strftime("%Y%m%d")
    filename = f"V4_US美股_猎物池_{today_str}.xlsx"
    
    columns_order = ['代码', '信号', '现价', 'ATR', '挤压率', '乖离率', '1R防线']
    if all(col in df.columns for col in columns_order):
        df = df[columns_order]
        
    try:
        # 获取当前脚本所在文件夹的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        
        df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"✅ 【本地SOP】今日猎物 Excel 导出成功: {file_path}")
    except Exception as e:
        print(f"❌ 【本地导出失败】请检查文件是否被打开占用了: {e}")

def push_to_website(results):
    """【API 模块】将结果自动发送到 Cloudflare 网站后台"""
    API_URL = "https://ito-core-proxy.wuijwong.workers.dev/api/update_radar"
    SECRET_TOKEN = "INTOO_V4_SECURE_TOKEN_2026" 
    
    payload = {
        "market": "US",
        "timestamp": datetime.now().isoformat(),
        "radar_data": results
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SECRET_TOKEN}"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print(f"✅ 【云端同步】API 发射成功！Cloudflare 返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 【云端同步失败】网络或接口异常: {e}")

def run_v4_daily_scanner():
    print(f"INTOO V4 T模块：US美股百大战略池全景扫描中 (共计 {len(TICKERS)} 只标的)...\n")
    data = yf.download(TICKERS, period='3y', group_by='ticker', progress=False)
    
    results = []
    for ticker in TICKERS:
        try:
            df_ticker = data[ticker].copy() if len(TICKERS) > 1 else data.copy()
            df_ticker.dropna(subset=['Close'], inplace=True)
            if df_ticker.empty: continue
                
            is_valid, reason, metrics = check_v4_resonance_strict(df_ticker)
            if is_valid:
                results.append({
                    '代码': ticker,
                    '信号': reason,
                    '现价': metrics['Close'],
                    'ATR': metrics['ATR'],
                    '挤压率': metrics['Squeeze'],
                    '乖离率': metrics['Deviation'],
                    '1R防线': metrics['Dynamic_Stop']
                })
        except Exception:
            continue

    if results:
        df_res = pd.DataFrame(results)
        print("=================== V4 美股战术扣板白名单 ===================")
        print(df_res.to_string(index=False))
        print("=============================================================\n")
        
        # 1. 导出本地 Excel
        export_to_excel(results)
        
        # 2. 推送至网站大屏
        push_to_website(results)
        
    else:
        print("📭 当前无美股标的满足 V4 极其严苛的多周期共振条件，保持现金空仓。系统休眠。")

if __name__ == "__main__":
    run_v4_daily_scanner()
