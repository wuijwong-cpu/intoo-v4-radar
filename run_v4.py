import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import os
import warnings

# 忽略 pandas 警告信息以保持终端干净
warnings.filterwarnings('ignore')

# ================= 1. 核心配置中心 =================
# Cloudflare API 配置
CF_API_URL = "https://ito-core-proxy.wuijwong.workers.dev/api/update_radar"
CF_SECRET_TOKEN = "INTOO_V4_SECURE_TOKEN_2026"

# PushPlus 微信群发配置
PUSHPLUS_TOKEN = "f64634b2942b4599aef243616997bd72"  # ⚠️ 请填入你的个人 Token
PUSHPLUS_TOPIC = "INTOO_V4"                        # 群组编码

# 模拟 104 只美股核心战略池 (此处用核心科技/重工代表，可自行扩充)
STOCK_POOL = ["APD", "ARM", "AMAT", "TRMD", "SLB", "PWR", "CAT", "DOW", "NVDA", "TSLA", "AAPL", "MSFT", "GOOGL"]
# ===================================================

def calculate_v4_indicators(df):
    """【T模块】计算 ATR、挤压率、乖离率等核心指标"""
    if len(df) < 20:
        return None
        
    # 计算 14D ATR
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    # 计算 20日均线及乖离率
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['乖离率'] = (df['Close'] - df['SMA20']) / df['ATR']
    
    # 计算布林带 (Bollinger Bands) 计算挤压率
    df['STD20'] = df['Close'].rolling(window=20).std()
    df['Upper_BB'] = df['SMA20'] + (df['STD20'] * 2)
    df['Lower_BB'] = df['SMA20'] - (df['STD20'] * 2)
    df['挤压率'] = (df['Upper_BB'] - df['Lower_BB']) / df['SMA20'] * 100
    
    return df.iloc[-1]

def scan_market():
    """全景扫描市场并筛选符合 V4 体系的标的"""
    print(f"\nINTOO V4 T模块：US美股百大战略池全景扫描中 (共计 104 只标的)...")
    results = []
    
    for ticker in STOCK_POOL:
        try:
            # 静默下载数据
            data = yf.download(ticker, period="6mo", progress=False)
            if data.empty:
                continue
                
            latest = calculate_v4_indicators(data)
            if latest is None:
                continue
                
            price = latest['Close'].iloc[0] if isinstance(latest['Close'], pd.Series) else latest['Close']
            atr = latest['ATR'].iloc[0] if isinstance(latest['ATR'], pd.Series) else latest['ATR']
            squeeze = latest['挤压率'].iloc[0] if isinstance(latest['挤压率'], pd.Series) else latest['挤压率']
            dev = latest['乖离率'].iloc[0] if isinstance(latest['乖离率'], pd.Series) else latest['乖离率']
            
            # 1R 防线 (当前价格减去 1.5 倍 ATR)
            stop_line = price - (1.5 * atr)
            
            # 战术定性逻辑
            signal = None
            if squeeze < 10.0 and dev > 0:
                signal = "【S级 (完美共振)】允许扣板"
            elif squeeze < 26.0 and dev > 0.5:
                signal = "【A级 (常态推升)】允许扣板"
                
            if signal:
                results.append({
                    "代码": ticker,
                    "信号": signal,
                    "现价": round(price, 2),
                    "ATR": round(atr, 2),
                    "挤压率": f"{round(squeeze, 1)}%",
                    "乖离率": f"{round(dev, 1)} ATR",
                    "1R防线": round(stop_line, 2)
                })
        except Exception:
            pass # 忽略报错，保持扫描流畅
            
    return results

def print_terminal_ui(results):
    """打印终端 UI 界面"""
    print("=================== V4 美股战术扣板白名单 ===================")
    print(f"  代码              信号     现价   ATR   挤压率     乖离率   1R防线")
    for r in results:
        code_str = r['代码'].rjust(4)
        print(f" {code_str} {r['信号']} {r['现价']:>6} {r['ATR']:>5} {r['挤压率']:>5} {r['乖离率']:>7} {r['1R防线']:>6}")
    print("=============================================================")

def export_to_excel(results):
    """【本地 SOP】导出 Excel 文件"""
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"V4_US美股_猎物池_{date_str}.xlsx"
    
    if results:
        df = pd.DataFrame(results)
        df.to_excel(filename, index=False)
        print(f"✅ 【本地SOP】今日猎物 Excel 导出成功: {os.path.abspath(filename)}")
    else:
        print(f"⚠️ 【本地SOP】今日无符合条件标的，跳过导出。")

def push_to_website(results):
    """【API 模块】将结果自动发送到 Cloudflare 网站后台"""
    payload = {
        "market": "US",
        "timestamp": datetime.now().isoformat(),
        "radar_data": results
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CF_SECRET_TOKEN}"
    }
    
    try:
        response = requests.post(CF_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ 【云端同步】API 发射成功！Cloudflare 返回状态码: 200")
        else:
            print(f"❌ 【云端同步异常】状态码: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ 【云端同步失败】网络或接口异常: {e}")

def push_to_wechat(results):
    """【群组微信推送】使用 PushPlus 向订阅者广播战报"""
    if not PUSHPLUS_TOKEN or PUSHPLUS_TOKEN == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("⚠️ 【微信推送】未配置 PushPlus Token，跳过推送。")
        return

    if not results:
        title = "🎯 V4 扫描: 今日无猎物"
        content = "今日无符合扣板条件的标的。请继续保持 0R 纪律，耐心等待。"
    else:
        title = f"🎯 V4 战术雷达发现 {len(results)} 只极品猎物"
        content = "### 核心过滤引擎已锁定以下高能标的：\n\n"
        for item in results:
            content += f"- **[{item['代码']}]** (现价: {item['现价']})\n"
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
            print(f"✅ 【微信群发】战报广播触发成功！")
        else:
            print(f"❌ 【微信群发异常】返回: {response.text}")
    except Exception as e:
        print(f"❌ 【微信群发失败】: {e}")

def main():
    """主程序入口"""
    # 1. 扫描与计算
    results = scan_market()
    
    # 2. 终端展示
    print_terminal_ui(results)
    
    # 3. 本地存档
    export_to_excel(results)
    
    # 4. 网站大屏同步
    push_to_website(results)
    
    # 5. 微信群组广播
    push_to_wechat(results)

if __name__ == "__main__":
    main()
