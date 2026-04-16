import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import requests
from datetime import datetime, timezone
import os

warnings.filterwarnings('ignore')

# =====================================================================
# INTOO V4-Quantamental 通信与广播配置
# =====================================================================
PUSHPLUS_TOKEN = "f64634b2942b4599aef243616997bd72"  # ⚠️ 填入你个人的 PushPlus Token
PUSHPLUS_TOPIC = "INTOO_V4"                        # 群组编码

# =====================================================================
# INTOO V4-Quantamental: 全球四大核心战场 (US / HK / JP / CN)
# =====================================================================
V4_US_UNIVERSE = {
    'Type_A': ['XOM','CVX','COST','JNJ','PG','KO','PEP','WMT','MCD','ABBV','MRK','HD','UNH','V','MA','JPM','BAC','BRK-B','MS','NEE','SO','DUK','LMT','RTX','GD','PM','MO','VZ','T','PFE','AMGN','GILD','UPS','EMR','WM','APD'],
    'Type_B': ['NVDA','MSFT','AMD','META','QCOM','GOOGL','AMZN','CRWD','PLTR','NOW','SNOW','DDOG','AAPL','AVGO','TSM','ASML','PANW','LLY','NFLX','CRM','ANET','ARM','MRVL','MU','KLAC','LRCX','AMAT','CDNS','SNPS','INTU','WDAY','TEAM','FTNT','ZS','MDB','APP','UBER','ISRG','VRTX','REGN','CELH','TRMD','VRT','SMCI','TTD'],
    'Type_C': ['TSLA','CAT','FCX','CIEN','C','SLB','HAL','NUE','SCCO','URI','PWR','BA','GM','DOW','LYB'],
    'Type_D': ['COIN','MSTR','HOOD','CVNA','RDDT','ASTS','LUNR','RBLX']
}

V4_JP_UNIVERSE = {
    'Type_A': ['8058.T', '8031.T', '8001.T', '8002.T', '8053.T', '8306.T', '8316.T', '8411.T', '8766.T', '8725.T', '8591.T', '9432.T', '9433.T', '9434.T', '7203.T', '7267.T', '4502.T', '4519.T', '2914.T', '4452.T', '3382.T', '9020.T', '9022.T', '9531.T', '9532.T', '1925.T', '1928.T', '4503.T', '4507.T', '9735.T'],
    'Type_B': ['8035.T', '6857.T', '6920.T', '6146.T', '7741.T', '4063.T', '6963.T', '6723.T', '7735.T', '6861.T', '6981.T', '6594.T', '6501.T', '9983.T', '7974.T', '6098.T', '4307.T', '4661.T', '2413.T', '4568.T', '4523.T', '6367.T', '7733.T', '6902.T', '6503.T', '6504.T', '7269.T', '6954.T', '8113.T', '4911.T', '4704.T', '3092.T', '6890.T', '6961.T', '7751.T', '6701.T', '6702.T'],
    'Type_C': ['5401.T', '5411.T', '6301.T', '6326.T', '4005.T', '9101.T', '9104.T', '9107.T', '7011.T', '7012.T', '7013.T', '8801.T', '8802.T', '3402.T', '3407.T', '5713.T', '5020.T', '5019.T', '5201.T', '5802.T', '1801.T', '6273.T'],
    'Type_D': ['4385.T', '4478.T', '3994.T', '5032.T', '5253.T', '4443.T', '3911.T', '6619.T', '4488.T', '7647.T', '6506.T', '9984.T', '6758.T']
}

V4_HK_UNIVERSE = {
    'Type_A': ['0883.HK', '0857.HK', '0386.HK', '1088.HK', '1171.HK', '0941.HK', '0728.HK', '0762.HK', '1398.HK', '0939.HK', '3988.HK', '1288.HK', '3968.HK', '1658.HK', '2628.HK', '2318.HK', '1299.HK', '0005.HK', '2888.HK', '0002.HK', '0003.HK', '0836.HK', '1038.HK', '0823.HK', '0066.HK', '0152.HK', '0390.HK', '1800.HK', '1093.HK', '1177.HK', '0288.HK', '0322.HK', '0151.HK', '0016.HK', '0001.HK'],
    'Type_B': ['0700.HK', '3690.HK', '9988.HK', '1810.HK', '9888.HK', '9618.HK', '9999.HK', '0981.HK', '1347.HK', '0285.HK', '2018.HK', '1211.HK', '0175.HK', '0268.HK', '9923.HK', '2013.HK', '3888.HK', '2269.HK', '1548.HK', '1801.HK', '0512.HK', '2020.HK', '2331.HK', '6110.HK', '1929.HK', '6862.HK', '9987.HK', '6618.HK', '0241.HK', '1833.HK', '6969.HK', '2382.HK', '1478.HK', '0772.HK', '9898.HK', '9961.HK', '0780.HK'],
    'Type_C': ['2899.HK', '3993.HK', '0358.HK', '1378.HK', '0914.HK', '3323.HK', '0347.HK', '1055.HK', '0753.HK', '0293.HK', '1919.HK', '1308.HK', '0316.HK', '0338.HK', '1157.HK', '2333.HK', '2238.HK', '6030.HK', '3908.HK', '0388.HK', '2600.HK', '3900.HK'],
    'Type_D': ['9992.HK', '1797.HK', '0020.HK', '1357.HK', '6682.HK', '1024.HK', '2015.HK', '9868.HK']
}

V4_CN_UNIVERSE = {
    'Type_A': ['601088.SS', '601225.SS', '601857.SS', '600028.SS', '600900.SS', '600011.SS', '600886.SS', '601107.SS', '601006.SS', '601398.SS', '601288.SS', '601988.SS', '601939.SS', '601328.SS', '600036.SS', '600941.SS', '601728.SS', '600050.SS', '600519.SS', '000858.SZ', '000568.SZ', '600809.SS', '000333.SZ', '000651.SZ', '600690.SS', '600276.SS', '000538.SZ', '600436.SS', '000895.SZ', '600887.SS'],
    'Type_B': ['300308.SZ', '601138.SS', '688041.SS', '603019.SS', '300502.SZ', '002463.SZ', '300394.SZ', '688256.SS', '002371.SZ', '688012.SS', '688120.SS', '603501.SS', '603986.SS', '688536.SS', '002475.SZ', '002241.SZ', '300433.SZ', '002594.SZ', '300750.SZ', '300274.SZ', '300124.SZ', '002050.SZ', '601689.SS', '600660.SS', '688111.SS', '002230.SZ', '600845.SS', '300760.SZ', '300015.SZ', '603259.SS', '300347.SZ', '688271.SS', '002179.SZ', '000938.SZ', '002415.SZ', '688036.SS', '603605.SS', '300957.SZ', '688169.SS'],
    'Type_C': ['601899.SS', '600547.SS', '601600.SS', '600362.SS', '603993.SS', '600309.SS', '600426.SS', '601668.SS', '601186.SS', '601800.SS', '600031.SS', '000338.SZ', '600585.SS', '002271.SZ', '601919.SS', '601111.SS', '601012.SS', '600030.SS', '601688.SS'],
    'Type_D': ['300059.SZ', '002085.SZ', '002229.SZ', '603083.SS', '601127.SS', '002261.SZ', '000158.SZ', '603662.SS', '688017.SS', '000063.SZ', '301308.SZ', '600760.SS', '300782.SZ', '002460.SZ']
}

# 动态生成总列表与市场路由映射 (Market Map)
GLOBAL_POOLS = {'US': V4_US_UNIVERSE, 'JP': V4_JP_UNIVERSE, 'HK': V4_HK_UNIVERSE, 'CN': V4_CN_UNIVERSE}
TICKERS = []
MARKET_MAP = {}

for market_name, universe in GLOBAL_POOLS.items():
    for category, tickers in universe.items():
        for ticker in tickers:
            TICKERS.append(ticker)
            MARKET_MAP[ticker] = market_name

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
    filename = f"V4_Global_全球猎物池_{today_str}.xlsx"  # 文件名升级
    
    columns_order = ['市场', '代码', '信号', '现价', 'ATR', '挤压率', '乖离率', '1R防线']
    if all(col in df.columns for col in columns_order):
        df = df[columns_order]
        
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        
        df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"✅ 【本地SOP】今日全球猎物 Excel 导出成功: {file_path}")
    except Exception as e:
        print(f"❌ 【本地导出失败】请检查文件是否被打开占用了: {e}")

def push_to_website(results):
    """【API 模块】将结果自动发送到 Cloudflare 网站后台"""
    API_URL = "https://ito-core-proxy.wuijwong.workers.dev/api/update_radar"
    SECRET_TOKEN = "INTOO_V4_SECURE_TOKEN_2026" 
    
    payload = {
        "market": "GLOBAL",  # 修改为 GLOBAL 表示多市场混合数据
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

def push_to_wechat(results):
    """【群发广播】使用 PushPlus 将战报推送到微信群组"""
    if not PUSHPLUS_TOKEN or PUSHPLUS_TOKEN == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("⚠️ 【微信推送】未配置真实 Token，已跳过推送。")
        return

    if not results:
        title = "🎯 V4 全球扫描: 今日无可投标的"
        content = "今日全球四大市场无符合极品共振条件的标的。请继续保持 0R 纪律，耐心等待。"
    else:
        title = f"🎯 V4 Module T 全球策略触发标的 {len(results)} 只"
        content = "### 本日策略触发标的：\n\n"
        for item in results:
            content += f"- **[{item['市场']}] [{item['代码']}]** (现价: {item['现价']})\n"
            content += f"  - 信号: {item['信号']}\n"
            content += f"  - 动能: 挤压率 {item['挤压率']} | 乖离率 {item['乖离率']}\n"
            content += f"  - 1R防线: **{item['1R防线']}**\n\n"
            
        content += "---\n[💻 点击此处进入 V4 终端大屏查看详情](https://ito-core-proxy.wuijwong.workers.dev/)"
        
    url = "http://www.pushplus.plus/send"
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown",
        "topic": PUSHPLUS_TOPIC
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ 【微信群发】战报已成功广播至群组 [{PUSHPLUS_TOPIC}]")
        else:
            print(f"❌ 【微信群发异常】返回: {response.text}")
    except Exception as e:
        print(f"❌ 【微信群发失败】网络异常: {e}")

def run_v4_daily_scanner():
    print(f"INTOO V4 T模块：全球四大核心战场 (US/HK/JP/CN) 全景扫描中 (共计 {len(TICKERS)} 只标的)...\n")
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
                    '市场': MARKET_MAP[ticker],  # <--- 核心修改：动态获取市场归属
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
        # 确保 DataFrame 打印时带有“市场”列
        columns_order = ['市场', '代码', '信号', '现价', 'ATR', '挤压率', '乖离率', '1R防线']
        if all(col in df_res.columns for col in columns_order):
            df_res = df_res[columns_order]
            
        print("=================== V4 全球战术扣板白名单 ===================")
        print(df_res.to_string(index=False))
        print("=============================================================\n")
        
        # 1. 导出本地 Excel
        export_to_excel(results)
        
        # 2. 推送至网站大屏
        push_to_website(results)
        
        # 3. 推送至微信群组
        push_to_wechat(results)
        
    else:
        print("📭 当前四大市场无标的满足 V4 极其严苛的多周期共振条件，保持现金空仓。系统休眠。")
        # 即使没有猎物，也可以触发微信播报
        push_to_wechat([])

if __name__ == "__main__":
    run_v4_daily_scanner()
