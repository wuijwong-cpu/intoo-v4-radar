import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import requests
import json
from datetime import datetime, timezone, date
import os

warnings.filterwarnings('ignore')

# =====================================================================
# INTOO V4-Quantamental 通信与广播配置
# =====================================================================
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
PUSHPLUS_TOPIC = "INTOO_V4"

API_URL_BASE = "https://ito-core-proxy.wuijwong.workers.dev/api"
SECRET_TOKEN = os.environ.get("SECRET_TOKEN")

# =====================================================================
# INTOO V4-Quantamental: 全球四大核心战场 (US / HK / JP / CN)
# =====================================================================
V4_US_UNIVERSE = {
    'Type_A': ['XOM','CVX','COST','JNJ','PG','KO','PEP','WMT','MCD','ABBV','MRK','HD','UNH','V','MA','JPM','BAC','BRK-B','MS','NEE','SO','DUK','LMT','RTX','GD','PM','MO','VZ','T','PFE','AMGN','GILD','UPS','EMR','WM','APD'],
    'Type_B': ['NVDA','MSFT','AMD','META','QCOM','GOOGL','AMZN','CRWD','PLTR','NOW','SNOW','DDOG','AAPL','AVGO','TSM','ASML','PANW','LLY','NFLX','CRM','ANET','ARM','MRVL','MU','KLAC','LRCX','AMAT','CDNS','SNPS','INTU','WDAY','TEAM','FTNT','ZS','MDB','APP','UBER','ISRG','VRTX','REGN','CELH','TRMD','VRT','SMCI','ROKU','TTD'],
    'Type_C': ['TSLA','CAT','FCX','CIEN','C','SLB','HAL','NUE','SCCO','URI','PWR','BA','GM','DOW','LYB'],
    'Type_D': ['COIN','MSTR','HOOD','CVNA','RDDT','ASTS','LUNR','RBLX']
}

V4_JP_UNIVERSE = {
    'Type_A': ['8058.T', '8031.T', '8001.T', '8002.T', '8053.T', '8306.T', '8316.T', '8411.T', '8766.T', '8725.T', '8591.T', '9432.T', '9433.T', '9434.T', '7203.T', '7267.T', '4502.T', '4519.T', '2914.T', '4452.T', '3382.T', '9020.T', '9022.T', '9531.T', '9532.T', '1925.T', '1928.T', '4503.T', '4507.T', '9735.T'],
    'Type_B': ['8035.T', '6857.T', '6920.T', '6146.T', '7741.T', '4063.T', '6963.T', '6723.T', '7735.T', '6861.T', '6981.T', '6594.T', '6501.T', '9983.T', '7974.T', '6098.T', '4307.T', '4661.T', '2413.T', '4568.T', '4523.T', '6367.T', '7733.T', '6902.T', '6503.T', '6504.T', '7269.T', '6954.T', '8113.T', '4911.T', '4704.T', '3092.T', '6890.T', '6961.T', '7751.T', '6701.T', '6702.T'],
    'Type_C': ['5401.T', '5411.T', '6301.T', '6326.T', '4005.T', '9101.T', '9104.T', '9107.T', '7011.T', '7012.T', '7013.T', '8801.T', '8802.T', '3402.T', '3407.T', '5713.T', '5020.T', '5019.T', '5201.T', '5802.T', '1801.T', '6273.T'],
    'Type_D': ['4385.T', '4478.T', '3994.T', '5032.T', '5253.T', '4443.T', '3911.T', '6619.T', '4488.T', '6506.T', '9984.T', '6758.T']
}

V4_HK_UNIVERSE = {
    'Type_A': ['0883.HK', '0857.HK', '0386.HK', '1088.HK', '1171.HK', '0941.HK', '0728.HK', '0762.HK', '1398.HK', '0939.HK', '3988.HK', '1288.HK', '3968.HK', '1658.HK', '2628.HK', '2318.HK', '1299.HK', '0005.HK', '2888.HK', '0002.HK', '0003.HK', '0836.HK', '1038.HK', '0823.HK', '0066.HK', '0152.HK', '0390.HK', '1800.HK', '1093.HK', '1177.HK', '0288.HK', '0322.HK', '0151.HK', '0016.HK', '0001.HK'],
    'Type_B': ['0700.HK', '3690.HK', '9988.HK', '1810.HK', '9888.HK', '9618.HK', '9999.HK', '0981.HK', '1347.HK', '0285.HK', '2018.HK', '1211.HK', '0175.HK', '0268.HK', '9923.HK', '2013.HK', '3888.HK', '2269.HK', '1548.HK', '1801.HK', '0512.HK', '2020.HK', '2331.HK', '6110.HK', '1929.HK', '6862.HK', '9987.HK', '6618.HK', '0241.HK', '1833.HK', '6969.HK', '2382.HK', '1478.HK', '0772.HK', '9898.HK', '9961.HK', '0780.HK'],
    'Type_C': ['2899.HK', '3993.HK', '0358.HK', '1378.HK', '0914.HK', '3323.HK', '0347.HK', '1055.HK', '0753.HK', '0293.HK', '1919.HK', '1308.HK', '0316.HK', '0338.HK', '1157.HK', '2333.HK', '2238.HK', '6030.HK', '3908.HK', '0388.HK', '2600.HK', '3900.HK', '1109.HK'],
    'Type_D': ['9992.HK', '1797.HK', '0020.HK', '1357.HK', '6682.HK', '1024.HK', '2015.HK', '9868.HK']
}

V4_CN_UNIVERSE = {
    'Type_A': ['601088.SS', '601225.SS', '601857.SS', '600028.SS', '600900.SS', '600011.SS', '600886.SS', '601107.SS', '601006.SS', '601398.SS', '601288.SS', '601988.SS', '601939.SS', '601328.SS', '600036.SS', '600941.SS', '601728.SS', '600050.SS', '600519.SS', '000858.SZ', '000568.SZ', '600809.SS', '000333.SZ', '000651.SZ', '600690.SS', '600276.SS', '000538.SZ', '600436.SS', '000895.SZ', '600887.SS'],
    'Type_B': ['300308.SZ', '601138.SS', '688041.SS', '603019.SS', '300502.SZ', '002463.SZ', '300394.SZ', '688256.SS', '002371.SZ', '688012.SS', '688120.SS', '603501.SS', '603986.SS', '688536.SS', '002475.SZ', '002241.SZ', '300433.SZ', '002594.SZ', '300750.SZ', '300274.SZ', '300124.SZ', '002050.SZ', '601689.SS', '600660.SS', '688111.SS', '002230.SZ', '600845.SS', '300760.SZ', '300015.SZ', '603259.SS', '300347.SZ', '688271.SS', '002179.SZ', '000938.SZ', '002415.SZ', '688036.SS', '603605.SS', '300957.SZ', '688169.SS'],
    'Type_C': ['601899.SS', '600547.SS', '601600.SS', '600362.SS', '603993.SS', '600309.SS', '600426.SS', '601668.SS', '601186.SS', '601800.SS', '600031.SS', '000338.SZ', '600585.SS', '002271.SZ', '601919.SS', '601111.SS', '601012.SS', '600030.SS', '601688.SS'],
    'Type_D': ['300059.SZ', '002085.SZ', '002229.SZ', '603083.SS', '601127.SS', '002261.SZ', '000158.SZ', '603662.SS', '688017.SS', '000063.SZ', '301308.SZ', '600760.SS', '300782.SZ', '002460.SZ']
}

# =====================================================================
# === V4 终端大屏专属：全球四大市场股票中文名称终极映射表 ===
# =====================================================================
NAME_MAP = {
    'XOM': '埃克森美孚', 'CVX': '雪佛龙', 'COST': '开市客', 'JNJ': '强生', 'PG': '宝洁', 
    'KO': '可口可乐', 'PEP': '百事', 'WMT': '沃尔玛', 'MCD': '麦当劳', 'ABBV': '艾伯维', 
    'MRK': '默沙东', 'HD': '家得宝', 'UNH': '联合健康', 'V': 'Visa', 'MA': '万事达', 
    'JPM': '摩根大通', 'BAC': '美国银行', 'BRK-B': '伯克希尔', 'MS': '摩根士丹利', 
    'NEE': '新纪元能源', 'SO': '南方公司', 'DUK': '杜克能源', 'LMT': '洛克希德马丁', 
    'RTX': '雷神技术', 'GD': '通用动力', 'PM': '菲利普莫里斯', 'MO': '奥驰亚', 
    'VZ': '威瑞森', 'T': 'AT&T', 'PFE': '辉瑞', 'AMGN': '安进', 'GILD': '吉利德科学', 
    'UPS': '联合包裹', 'EMR': '艾默生电气', 'WM': '废物管理', 'APD': '空气产品',
    'NVDA': '英伟达', 'MSFT': '微软', 'AMD': '超微半导体', 'META': 'Meta', 'QCOM': '高通', 
    'GOOGL': '谷歌', 'AMZN': '亚马逊', 'CRWD': 'CrowdStrike', 'PLTR': 'Palantir', 
    'NOW': 'ServiceNow', 'SNOW': 'Snowflake', 'DDOG': 'Datadog', 'AAPL': '苹果', 
    'AVGO': '博通', 'TSM': '台积电', 'ASML': '阿斯麦', 'PANW': '派拓网络', 'LLY': '礼来', 
    'NFLX': '奈飞', 'CRM': '赛富时', 'ANET': 'Arista', 'ARM': 'ARM', 'MRVL': '迈威尔', 
    'MU': '美光科技', 'KLAC': '科磊', 'LRCX': '拉姆研究', 'AMAT': '应用材料', 
    'CDNS': '楷登电子', 'SNPS': '新思科技', 'INTU': '财捷', 'WDAY': 'Workday', 
    'TEAM': 'Atlassian', 'FTNT': '飞塔信息', 'ZS': 'Zscaler', 'MDB': 'MongoDB', 
    'APP': 'AppLovin', 'UBER': '优步', 'ISRG': '直觉外科', 'VRTX': '福泰制药', 
    'REGN': '再生元', 'CELH': '燃力士', 'TRMD': 'TORM', 'VRT': '维谛技术', 
    'SMCI': '超微电脑', 'TTD': 'The Trade Desk', 'ROKU': 'ROKU',
    'TSLA': '特斯拉', 'CAT': '卡特彼勒', 'FCX': '自由港', 'CIEN': 'Ciena', 'C': '花旗集团', 
    'SLB': '斯伦贝谢', 'HAL': '哈里伯顿', 'NUE': '纽柯钢铁', 'SCCO': '南方铜业', 
    'URI': '联合租赁', 'PWR': '广达服务', 'BA': '波音', 'GM': '通用汽车', 'DOW': '陶氏化学', 
    'LYB': '利安德巴塞尔', 'COIN': 'Coinbase', 'MSTR': '微策投资', 'HOOD': 'Robinhood', 
    'CVNA': 'Carvana', 'RDDT': 'Reddit', 'ASTS': 'AST SpaceMobile', 'LUNR': '直觉机器', 'RBLX': 'Roblox',
    '0883.HK': '中国海油', '0857.HK': '中国石油', '0386.HK': '中国石化', '1088.HK': '中国神华', '1171.HK': '兖矿能源', 
    '0941.HK': '中国移动', '0728.HK': '中国电信', '0762.HK': '中国联通', '1398.HK': '工商银行', '0939.HK': '建设银行', 
    '3988.HK': '中国银行', '1288.HK': '农业银行', '3968.HK': '招商银行', '1658.HK': '邮储银行', '2628.HK': '中国人寿', 
    '2318.HK': '中国平安', '1299.HK': '友邦保险', '0005.HK': '汇丰控股', '2888.HK': '渣打集团', '0002.HK': '中电控股', 
    '0003.HK': '中华煤气', '0836.HK': '华润电力', '1038.HK': '长江基建', '0823.HK': '领展', '0066.HK': '港铁公司', 
    '0152.HK': '深圳国际', '0390.HK': '中国中铁', '1800.HK': '中国交建', '1093.HK': '石药集团', '1177.HK': '中国生物制药', 
    '0288.HK': '万洲国际', '0322.HK': '康师傅', '0151.HK': '中国旺旺', '0016.HK': '新鸿基', '0001.HK': '长和',
    '0700.HK': '腾讯控股', '3690.HK': '美团', '9988.HK': '阿里巴巴', '1810.HK': '小米集团', '9888.HK': '百度集团', 
    '9618.HK': '京东集团', '9999.HK': '网易', '0981.HK': '中芯国际', '1347.HK': '华虹半导体', '0285.HK': '比亚迪电子', 
    '2018.HK': '瑞声科技', '1211.HK': '比亚迪', '0175.HK': '吉利汽车', '0268.HK': '金蝶国际', '9923.HK': '移卡', 
    '2013.HK': '微盟集团', '3888.HK': '金山软件', '2269.HK': '药明生物', '1548.HK': '金斯瑞', '1801.HK': '信达生物', 
    '0512.HK': '远大医药', '2020.HK': '安踏体育', '2331.HK': '李宁', '6110.HK': '滔搏', '1929.HK': '周大福', 
    '6862.HK': '海底捞', '9987.HK': '百胜中国', '6618.HK': '京东健康', '0241.HK': '阿里健康', '1833.HK': '平安好医生',
    '6969.HK': '思摩尔国际', '2382.HK': '舜宇光学科技', '1478.HK': '丘钛科技', '0772.HK': '阅文集团', 
    '9898.HK': '京东物流', '9961.HK': '哔哩哔哩', '0780.HK': '同程旅行',
    '2899.HK': '紫金矿业', '3993.HK': '洛阳钼业', '0358.HK': '江西铜业', '1378.HK': '中国宏桥', '0914.HK': '海螺水泥', 
    '3323.HK': '中国建材', '0347.HK': '鞍钢股份', '1055.HK': '中国南方航空', '0753.HK': '中国国航', '0293.HK': '国泰航空', 
    '1919.HK': '中远海控', '1308.HK': '海丰国际', '0316.HK': '东方海外', '0338.HK': '上海石化', '1157.HK': '中联重科', 
    '2333.HK': '长城汽车', '2238.HK': '广汽集团', '6030.HK': '中信证券', '3908.HK': '中金公司', '0388.HK': '港交所', 
    '2600.HK': '中国铝业', '3900.HK': '绿城中国', '9992.HK': '泡泡玛特', '1797.HK': '东方甄选', '0020.HK': '商汤',
    '1357.HK': '美图公司', '6682.HK': '第四范式', '1024.HK': '快手', '2015.HK': '理想汽车', '9868.HK': '小鹏汽车', '1109.HK': '华润置地',
    '601088.SS': '中国神华', '601225.SS': '陕西煤业', '601857.SS': '中国石油', '600028.SS': '中国石化', '600900.SS': '长江电力', 
    '600011.SS': '华能国际', '600886.SS': '国投电力', '601107.SS': '四川路桥', '601006.SS': '大秦铁路', '601398.SS': '工商银行', 
    '601288.SS': '农业银行', '601988.SS': '中国银行', '601939.SS': '建设银行', '601328.SS': '交通银行', '600036.SS': '招商银行', 
    '600941.SS': '中国移动', '601728.SS': '中国电信', '600050.SS': '中国联通', '600519.SS': '贵州茅台', '000858.SZ': '五粮液', 
    '000568.SZ': '泸州老窖', '600809.SS': '山西汾酒', '000333.SZ': '美的集团', '000651.SZ': '格力电器', '600690.SS': '海尔智家', 
    '600276.SS': '恒瑞医药', '000538.SZ': '云南白药', '600436.SS': '片仔癀', '000895.SZ': '双汇发展', '600887.SS': '伊利股份',
    '300308.SZ': '中际旭创', '601138.SS': '工业富联', '688041.SS': '海光信息', '603019.SS': '中科曙光', '300502.SZ': '新易盛', 
    '002463.SZ': '沪电股份', '300394.SZ': '天孚通信', '688256.SS': '寒武纪', '002371.SZ': '北方华创', '688012.SS': '中微公司', 
    '688120.SS': '华海清科', '603501.SS': '韦尔股份', '603986.SS': '兆易创新', '688536.SS': '思瑞浦', '002475.SZ': '立讯精密', 
    '002241.SZ': '歌尔股份', '300433.SZ': '蓝思科技', '002594.SZ': '比亚迪', '300750.SZ': '宁德时代', '300274.SZ': '阳光电源', 
    '300124.SZ': '汇川技术', '002050.SZ': '三花智控', '601689.SS': '拓普集团', '600660.SS': '福耀玻璃', '688111.SS': '金山办公', 
    '002230.SZ': '科大讯飞', '600845.SS': '宝信软件', '300760.SZ': '迈瑞医疗', '300015.SZ': '爱尔眼科', '603259.SS': '药明康德', 
    '300347.SZ': '泰格医药', '688271.SS': '联影医疗', '002179.SZ': '中航光电', '000938.SZ': '紫光股份', '002415.SZ': '海康威视', 
    '688036.SS': '传音控股', '603605.SS': '珀莱雅', '300957.SZ': '贝泰妮', '688169.SS': '石头科技',
    '601899.SS': '紫金矿业', '600547.SS': '山东黄金', '601600.SS': '中国铝业', '600362.SS': '江西铜业', '603993.SS': '洛阳钼业', 
    '600309.SS': '万华化学', '600426.SS': '华鲁恒升', '601668.SS': '中国建筑', '601186.SS': '中国铁建', '601800.SS': '中国交建', 
    '600031.SS': '三一重工', '000338.SZ': '潍柴动力', '600585.SS': '海螺水泥', '002271.SZ': '东方雨虹', '601919.SS': '中远海控', 
    '601111.SS': '中国国航', '601012.SS': '隆基绿能', '600030.SS': '中信证券', '601688.SS': '华泰证券',
    '300059.SZ': '东方财富', '002085.SZ': '万丰奥威', '002229.SZ': '鸿博股份', '603083.SS': '剑桥科技', '601127.SS': '赛力斯', 
    '002261.SZ': '拓维信息', '000158.SZ': '常山北明', '603662.SS': '柯力传感', '688017.SS': '绿的谐波', '000063.SZ': '中兴通讯', 
    '301308.SZ': '江波龙', '600760.SS': '中航沈飞', '300782.SZ': '卓胜微', '002460.SZ': '赣锋锂业',
    '8058.T': '三菱商事', '8031.T': '三井物产', '8001.T': '伊藤忠商事', '8002.T': '丸红', '8053.T': '住友商事', 
    '8306.T': '三菱UFJ', '8316.T': '三井住友', '8411.T': '瑞穗金融', '8766.T': '东京海上', '8725.T': 'MS&AD保险', 
    '8591.T': '欧力士', '9432.T': 'NTT', '9433.T': 'KDDI', '9434.T': '软银(国内)', '7203.T': '丰田汽车', 
    '7267.T': '本田汽车', '4502.T': '武田药品', '4519.T': '中外制药', '2914.T': '日本烟草', '4452.T': '花王', 
    '3382.T': '7&I控股', '9020.T': 'JR东日本', '9022.T': 'JR东海', '9531.T': '东京燃气', '9532.T': '大阪燃气', 
    '1925.T': '大和房屋', '1928.T': '积水房屋', '4503.T': '安斯泰来', '4507.T': '盐野义', '9735.T': '西科姆',
    '8035.T': '东京电子', '6857.T': '爱德万测试', '6920.T': 'Lasertec', '6146.T': '迪思科', '7741.T': '豪雅(HOYA)', 
    '4063.T': '信越化学', '6963.T': '罗姆(ROHM)', '6723.T': '瑞萨电子', '7735.T': '网屏', '6861.T': '基恩士', 
    '6981.T': '村田制作所', '6594.T': '尼得科(Nidec)', '6501.T': '日立', '9983.T': '迅销(优衣库)', '7974.T': '任天堂', 
    '6098.T': '里库路特', '4307.T': '野村综合研究所', '4661.T': '东方乐园(迪士尼)', '2413.T': 'M3', '4568.T': '第一三共', 
    '4523.T': '卫材', '6367.T': '大金工业', '7733.T': '奥林巴斯', '6902.T': '电装', '6503.T': '三菱电机', 
    '6504.T': '富士电机', '7269.T': '铃木汽车', '6954.T': '发那科', '8113.T': '尤妮佳', '4911.T': '资生堂', 
    '4704.T': '趋势科技', '3092.T': '奥野制薬', '6890.T': 'SCREEN Holdings', '6961.T': '太阳诱电', '7751.T': '佳能', 
    '6701.T': 'NEC', '6702.T': '富士通',
    '5401.T': '新日本制铁', '5411.T': 'JFE控股', '6301.T': '小松制作所', '6326.T': '久保田', '4005.T': '住友化学', 
    '9101.T': '日本邮船', '9104.T': '商船三井', '9107.T': '川崎汽船', '7011.T': '三菱重工', '7012.T': '川崎重工', 
    '7013.T': 'IHI', '8801.T': '三井不动产', '8802.T': '三菱地所', '3402.T': '东丽', '3407.T': '旭化成', 
    '5713.T': '住友金属矿山', '5020.T': '引能仕', '5019.T': '出光兴产', '5201.T': '东邦瓦斯', '5802.T': '住友电工', 
    '1801.T': '大成建设', '9984.T': '软银集团', '6758.T': '索尼', '6273.T': 'SMC', 
    '4385.T': 'Mercari', '4478.T': 'Freee', '3994.T': 'Money Forward', '5032.T': 'ANYCOLOR', 
    '5253.T': 'Cover', '4443.T': 'Sansan', '3911.T': 'Aiming', '6619.T': 'W-SCOPE', 
    '4488.T': 'AI inside', '6506.T': '安川电机'
}

# =====================================================================
# V4 宏观重力基准：全球 8 大核心指数代码 (Yahoo Finance)
# =====================================================================
INDEX_MAP = {
    '^NDX': {'id': 'NDX', 'name': '纳指100'},
    '^GSPC': {'id': 'SPX', 'name': '标普500'},
    '^DJI': {'id': 'DJI', 'name': '道琼斯'},
    '^HSI': {'id': 'HSI', 'name': '恒生指数'},
    '^N225': {'id': 'N225', 'name': '日经225'},
    '000001.SS': {'id': 'SHCOMP', 'name': '上证指数'},
    '399001.SZ': {'id': 'SZCOMP', 'name': '深证成指'}
}

# 动态生成总列表与市场路由映射
GLOBAL_POOLS = {'US': V4_US_UNIVERSE, 'JP': V4_JP_UNIVERSE, 'HK': V4_HK_UNIVERSE, 'CN': V4_CN_UNIVERSE}
TICKERS = []
MARKET_MAP = {}

for market_name, universe in GLOBAL_POOLS.items():
    for category, tickers in universe.items():
        for ticker in tickers:
            TICKERS.append(ticker)
            MARKET_MAP[ticker] = market_name

# =====================================================================
# 【V4.2 新增】分市场专属ML阈值参数表
# =====================================================================
# 【阈值标定血缘卡】标定区间 2013-01-01~2019-12-31；验证区间(样本外) 2020-01-01~2026-09
#   目标函数：趋势过滤后「20 日前瞻对数收益」相对同市场趋势日基线的超额（pp）
#   样本池：US 132 / HK 66 / JP 101 / CN 102 只（行业分散·流动性靠前）
#   样本外结论：JP +0.244pp(3439次) / CN +0.871pp(166次,胜率66%) 成立；
#              US −0.251pp、HK −0.945pp -> 该两市场 squeeze 关(None)，仅保留趋势+乖离
#   注意：squeeze 口径 = BOLL_WIDTH = 4σ/MID（如需 1σ 口径请除以 4）
ML_THRESHOLDS = {
    'US': {'squeeze_max': None, 'deviation_max': 0.75, 'deviation_min': None},
    'HK': {'squeeze_max': None, 'deviation_max': 0.75, 'deviation_min': 0.50},
    'CN': {'squeeze_max': 0.04, 'deviation_max': 0.75, 'deviation_min': None},
    'JP': {'squeeze_max': None, 'deviation_max': 0.75, 'deviation_min': 0.50}
}

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

# 【月线闸门·分市场】A/B 实测（2013-2026，原始 411 只池，账户级 + 逐笔）
#   US 开 -> 最大回撤 -18.3% -> -14.6%（收益持平，夏普持平）        => 开
#   HK 开 -> 样本外年化 61.2% -> 63.9%，逐笔 R 0.35 -> 0.36         => 开
#   JP 关 -> 开后最大回撤反而恶化 4.2pp（-10.5% -> -14.7%）        => 关
#   CN 关 -> 开后逐笔 R 腰斩 1.29 -> 0.80、样本内年化 28.9% -> 14.0% => 关
# 月线规则：三选二（MACD 非"零轴下死叉" / 收盘>月线中轨且中轨上行 / 月线 EMA60 上行）
USE_MONTHLY_BY_MARKET = {'US': True, 'HK': True, 'JP': False, 'CN': False}
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
    print(f"[行业层] sector_map.csv 读取失败: {_e}")

# 参数设定
SHORT_GMMA = [3, 5, 8, 10, 12, 15]
LONG_GMMA = [30, 35, 40, 45, 50, 60]

def calc_v4_indicators(df):
    """V4 系统底层指标计算引擎"""
    if df.empty or len(df) < 30:
        return None
    
    for p in SHORT_GMMA + LONG_GMMA:
        df[f'EMA_{p}'] = df['Close'].ewm(span=p, adjust=False).mean()
        
    df['BOLL_MID'] = df['Close'].rolling(window=20).mean()
    df['BOLL_STD'] = df['Close'].rolling(window=20).std()
    df['BOLL_UPPER'] = df['BOLL_MID'] + 2 * df['BOLL_STD']
    df['BOLL_LOWER'] = df['BOLL_MID'] - 2 * df['BOLL_STD']
    df['BOLL_WIDTH'] = (df['BOLL_UPPER'] - df['BOLL_LOWER']) / df['BOLL_MID']
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD_DIF'] = exp1 - exp2
    df['MACD_DEA'] = df['MACD_DIF'].ewm(span=9, adjust=False).mean()
    
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()
    
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    return df

def translate_v4_semantics(df_slice):
    """将物理量化数据翻译为 V4 体系的文本语义"""
    if df_slice is None or df_slice.empty:
        return {'macd': '数据缺失', 'gmma': '数据缺失', 'boll': '数据缺失'}
    
    curr = df_slice.iloc[-1]
    
    macd_res = "零轴纠缠"
    if not pd.isna(curr.get('MACD_DIF')) and not pd.isna(curr.get('MACD_DEA')):
        dif, dea = curr['MACD_DIF'], curr['MACD_DEA']
        if dif > 0 and dif > dea: macd_res = "水上金叉"
        elif dif > 0 and dif < dea: macd_res = "水上死叉"
        elif dif < 0 and dif > dea: macd_res = "水下金叉"
        elif dif < 0 and dif < dea: macd_res = "水下死叉"
    
    gmma_res = "纠缠走平"
    try:
        short_min = min([curr[f'EMA_{p}'] for p in SHORT_GMMA])
        short_max = max([curr[f'EMA_{p}'] for p in SHORT_GMMA])
        long_min = min([curr[f'EMA_{p}'] for p in LONG_GMMA])
        long_max = max([curr[f'EMA_{p}'] for p in LONG_GMMA])
        
        if short_min > long_max: gmma_res = "多头排列"
        elif short_max < long_min: gmma_res = "空头压制"
        elif short_min > long_min and short_min < long_max: gmma_res = "短期组上"
    except:
        pass

    boll_res = "贴轨飞行"
    if not pd.isna(curr.get('BOLL_MID')):
        if curr['Close'] > curr['BOLL_UPPER']: boll_res = "突破上轨"
        elif curr['Close'] > curr['BOLL_MID']: boll_res = "中轨之上"
        elif curr['Close'] < curr['BOLL_LOWER']: boll_res = "跌破下轨"
        elif curr['Close'] < curr['BOLL_MID']: boll_res = "中轨之下"
        if curr.get('BOLL_WIDTH', 1) < 0.15: boll_res = "极度收口"
        
    return {'macd': macd_res, 'gmma': gmma_res, 'boll': boll_res}

def generate_macro_matrix():
    """生成核心指数的日、周、月三周期物理共振矩阵"""
    print("INTOO V4：正在测算核心宏观指数重力矩阵...")
    tickers = list(INDEX_MAP.keys())
    data = yf.download(tickers, period='3y', group_by='ticker', progress=False)
    
    matrix_results = []
    for ticker, meta in INDEX_MAP.items():
        try:
            df = data[ticker].copy() if len(tickers) > 1 else data.copy()
            df.dropna(subset=['Close'], inplace=True)
            if df.empty: continue
            
            df_w = df.resample('W-FRI').agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
            df_m = df.resample('ME').agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
            
            df_d_calc = calc_v4_indicators(df.copy())
            df_w_calc = calc_v4_indicators(df_w.copy())
            df_m_calc = calc_v4_indicators(df_m.copy())
            
            matrix_results.append({
                'id': meta['id'],
                'name': meta['name'],
                'm1': translate_v4_semantics(df_m_calc),
                'w1': translate_v4_semantics(df_w_calc),
                'd1': translate_v4_semantics(df_d_calc)
            })
        except Exception as e:
            print(f"  ⚠️ 指数 {ticker} 测算失败: {e}")
            
    return matrix_results


def check_v4_resonance_strict(df_daily, ticker):
    """执行 V4 动态多周期物理共振审核（V4.2 分市场ML阈值）"""
    if len(df_daily) < 200:
        return False, "数据不足 (需200天)", None

    market = MARKET_MAP.get(ticker, 'US')
    thresholds = dict(ML_THRESHOLDS.get(market, ML_THRESHOLDS['US']))
    # ---- 类型层 / 行业层（回测驱动）----
    _t = TYPE_OF.get(ticker)
    _tr = TYPE_RULES.get(_t, {})
    if _tr and _tr.get('enabled') is False:
        return False, f"类型 {_t} 本期不参与", None
    if _tr.get('deviation_max') is not None:
        thresholds['deviation_max'] = _tr['deviation_max']
    if SECTOR_MAP and SECTOR_MAP.get(ticker) in SECTOR_EXCLUDE:
        return False, f"行业 {SECTOR_MAP.get(ticker)} 已排除（历史最差）", None

    df_weekly = df_daily.resample('W-FRI').agg({'Open':'first','High':'max','Low':'min','Close':'last'}).dropna()
    
    df_d = calc_v4_indicators(df_daily.copy())
    df_w = calc_v4_indicators(df_weekly.copy())
    
    if df_d is None or df_w is None:
        return False, "指标生成失败", None

    curr_d = df_d.iloc[-1]
    prev_d = df_d.iloc[-2]
    curr_w = df_w.iloc[-1] if len(df_w) > 0 else None

    # ==========================================
    # 【V4.1 修复】大周期过滤
    # ==========================================
    if 'MA200' not in curr_d.index or pd.isna(curr_d['MA200']) or pd.isna(prev_d['MA200']):
        return False, "MA200 数据缺失", None

    if curr_d['Close'] <= curr_d['MA200']:
        return False, "价格在 MA200 之下 (大周期空头)", None

    if curr_d['MA200'] <= prev_d['MA200']:
        return False, "MA200 走平或向下 (宏观趋势未走强)", None

    # ==========================================
    # 周线级别审核
    # ==========================================
    if curr_w is not None:
        w_short_min = min([curr_w[f'EMA_{p}'] for p in SHORT_GMMA if f'EMA_{p}' in curr_w.index])
        w_long_min = min([curr_w[f'EMA_{p}'] for p in LONG_GMMA if f'EMA_{p}' in curr_w.index])
        if w_short_min < w_long_min:
            return False, "周线GMMA短期组跌穿长期组", None

        if len(df_w) >= 2:
            prev_w = df_w.iloc[-2]
            if not pd.isna(curr_w['BOLL_MID']) and not pd.isna(prev_w['BOLL_MID']) and \
               curr_w['BOLL_MID'] <= prev_w['BOLL_MID']:
                return False, "周线BOLL中轨向下或走平", None

    # ---------- 月线闸门（分市场，见文件头 USE_MONTHLY_BY_MARKET） ----------
    if USE_MONTHLY_BY_MARKET.get(market, False):
        df_m = df_daily.resample('ME').agg(
            {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna()
        if len(df_m) < 60:
            print(f"  [月线] {ticker} 月线样本仅 {len(df_m)} 根(<60)，本次跳过月线审核")
        else:
            mc = df_m['Close']
            _dif = mc.ewm(span=12, adjust=False).mean() - mc.ewm(span=26, adjust=False).mean()
            _dea = _dif.ewm(span=9, adjust=False).mean()
            _mid = mc.rolling(20).mean()
            _e60 = mc.ewm(span=60, adjust=False).mean()
            _s1 = not (_dif.iloc[-1] < _dea.iloc[-1] and _dif.iloc[-1] < 0)
            _s2 = bool(mc.iloc[-1] > _mid.iloc[-1] and _mid.iloc[-1] > _mid.iloc[-2]) \
                if not pd.isna(_mid.iloc[-2]) else False
            _s3 = bool(_e60.iloc[-1] > _e60.iloc[-2]) if not pd.isna(_e60.iloc[-2]) else False
            _n = int(_s1) + int(_s2) + int(_s3)
            if _n < 2:
                return False, f"月线审核未通过 ({_n}/3)", None

    # ==========================================
    # 日线级别审核
    # ==========================================
    if curr_d['EMA_60'] <= prev_d['EMA_60']:
        return False, "日线长期GMMA组向下", None

    d_short_min = min([curr_d[f'EMA_{p}'] for p in SHORT_GMMA])
    d_long_min = min([curr_d[f'EMA_{p}'] for p in LONG_GMMA])
    if d_short_min < d_long_min:
        return False, "短期均线跌穿长期组", None

    if curr_d['Close'] <= curr_d['BOLL_MID']:
        return False, "跌破日线中轨", None
    if curr_d['BOLL_MID'] <= prev_d['BOLL_MID']:
        return False, "中轨向下或走平", None

    if pd.isna(curr_d['ATR']) or pd.isna(curr_d.get('BOLL_WIDTH')):
        return False, "ATR或布林带数据缺失", None

    deviation_ratio = (curr_d['Close'] - curr_d['BOLL_MID']) / curr_d['ATR']
    squeeze_ratio = curr_d['BOLL_WIDTH']

    # ==========================================
    # 【V4.2 核心】分市场ML阈值过滤
    # ==========================================
    # 乖离率上限
    if deviation_ratio > thresholds['deviation_max']:
        return False, f"乖离率超标 ({deviation_ratio:.2f} > {thresholds['deviation_max']})", None

    # 乖离率下限（港股、A股需要右侧确认）
    if thresholds['deviation_min'] is not None and deviation_ratio < thresholds['deviation_min']:
        return False, f"乖离率不足 ({deviation_ratio:.2f} < {thresholds['deviation_min']})", None

    # 挤压率上限
    if thresholds['squeeze_max'] is not None and squeeze_ratio > thresholds['squeeze_max']:
        return False, f"挤压率超标 ({squeeze_ratio*100:.1f}% > {thresholds['squeeze_max']*100:.1f}%)", None

    # ==========================================
    # 连续共振天数 (仅用于展示)
    # ==========================================
    consecutive_days = 0
    for i in range(1, 31):
        if len(df_d) <= i: break
        lookback_curr = df_d.iloc[-i]
        lookback_prev = df_d.iloc[-(i+1)] if len(df_d) > (i+1) else None

        if lookback_prev is not None and lookback_curr['EMA_60'] <= lookback_prev['EMA_60']: break
        lb_short_min = min([lookback_curr[f'EMA_{p}'] for p in SHORT_GMMA])
        lb_long_min = min([lookback_curr[f'EMA_{p}'] for p in LONG_GMMA])
        if lb_short_min < lb_long_min: break
        if lookback_curr['Close'] <= lookback_curr['BOLL_MID']: break
        if lookback_prev is not None and lookback_curr['BOLL_MID'] <= lookback_prev['BOLL_MID']: break

        if not pd.isna(lookback_curr['ATR']):
            lb_dev = (lookback_curr['Close'] - lookback_curr['BOLL_MID']) / lookback_curr['ATR']
            if lb_dev > thresholds['deviation_max']: break
        else:
            break

        lb_squeeze = lookback_curr['BOLL_WIDTH']
        if thresholds['squeeze_max'] is not None and lb_squeeze > thresholds['squeeze_max']: break
        consecutive_days += 1

    signal_strength = f"SS级 [{market}]"
    streak_tag = f" [连续触发 {consecutive_days} 天]" if consecutive_days > 1 else " [✨首日触发]"
    final_reason = signal_strength + streak_tag

    dashboard_data = {
        'Close': round(float(curr_d['Close']), 2),
        'ATR': round(float(curr_d['ATR']), 2),
        'Squeeze': f"{float(squeeze_ratio)*100:.1f}%",
        'Deviation': f"{float(deviation_ratio):.1f} ATR",
        'Dynamic_Stop': round(float(curr_d['Close'] - 2.5 * curr_d['ATR']), 2),
        'Streak': consecutive_days
    }
    
    return True, final_reason, dashboard_data

def export_to_excel(results):
    """将扫描结果自动化导出为 Excel 猎物池"""
    df = pd.DataFrame(results)
    today_str = globals().get("RUN_DATA_DATE") or datetime.now().strftime("%Y%m%d")
    filename = f"V4_Global_全球猎物池_{today_str}.xlsx"
    
    columns_order = ['市场', '类型', '建议权重', '代码', '信号', '现价', 'ATR',
                    '挤压率', '乖离率', '1R防线']
    if all(col in df.columns for col in columns_order):
        df = df[columns_order]
        
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        df.to_excel(file_path, index=False, engine='openpyxl')
        print(f"✅ 【本地SOP】今日全球猎物 Excel 导出成功: {file_path}")
    except Exception as e:
        print(f"❌ 【本地导出失败】: {e}")

def push_to_wechat(results):
    """【群发广播】使用 PushPlus 将战报推送到微信群组"""
    if not PUSHPLUS_TOKEN or PUSHPLUS_TOKEN == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
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
            content += f"  - 1R防线: **{item['1R防线']}** | 类型: {item.get('类型', '-')} (权重 {item.get('建议权重', 1.0)})\n\n"
            
        content += "---\n[💻 点击此处进入 V4 终端大屏查看详情](https://ito-core-proxy.wuijwong.workers.dev/)"
        
    url = "http://www.pushplus.plus/send"
    payload = {"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "markdown", "topic": PUSHPLUS_TOPIC}
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        print(f"✅ 【微信群发】战报已成功广播至群组 [{PUSHPLUS_TOPIC}]")
    except Exception as e:
        print(f"❌ 【微信群发失败】: {e}")

def fetch_tracker_from_cloud():
    """从 KV 数据库下载现有的 TRACKER_ALL 账本"""
    try:
        r = requests.get(f"{API_URL_BASE}/radar?type=tracker", timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                return data.get("tracker_data", [])
    except Exception as e:
        print(f"❌ 拉取云端追踪账本失败: {e}")
    return None

def update_tracker_logic(daily_results, all_history_data):
    """战役追踪逻辑：合并新标的，更新存量战役现价、收益与防线状态"""
    tracker_db = fetch_tracker_from_cloud()
    if tracker_db is None:
        print("❌ 云端账本不可得 -> 本次跳过云端同步，避免覆盖历史账本")
        return None
    if not isinstance(tracker_db, list):
        tracker_db = []
        
    today_str = datetime.now().strftime("%Y-%m-%d")

    for item in daily_results:
        full_ticker = item['代码']
        ticker_code = full_ticker.split(' ')[0]
        campaign_id = f"{ticker_code}-{today_str}"
        
        if not any(c.get('campaign_id') == campaign_id for c in tracker_db):
            p_in = float(item['现价'])
            stop_1r = float(item['1R防线'])
            tracker_db.append({
                "campaign_id": campaign_id, 
                "ticker": full_ticker,  
                "start_date": today_str,
                "signal": item['信号'], 
                "p_in": p_in, 
                "p_now": p_in, 
                "hhv": p_in,
                "stop_initial": stop_1r, 
                "stop_dyn": stop_1r, 
                "status": "RUNNING",
                "abs_return": "+0.00%", 
                "ann_return": "N/A", 
                "r_multiple": "+0.0R"
            })

    for campaign in tracker_db:
        if campaign.get('status') == "STOPPED": 
            continue 
        
        t_full = campaign['ticker']
        t_pure = t_full.split(' ')[0]
        try:
            df = all_history_data[t_pure].copy() if len(TICKERS) > 1 else all_history_data.copy()
            df.dropna(subset=['Close'], inplace=True)
            if df.empty: continue
            
            curr_p = float(df['Close'].iloc[-1])
            p_in = float(campaign['p_in'])
            
            if curr_p > campaign.get('hhv', 0): 
                campaign['hhv'] = curr_p
            
            tr = pd.concat([df['High']-df['Low'], (df['High']-df['Close'].shift()).abs(), (df['Low']-df['Close'].shift()).abs()], axis=1).max(axis=1)
            atr = float(tr.rolling(14).mean().iloc[-1])
            
            new_stop = round(campaign['hhv'] - 2.5 * atr, 2)
            if new_stop > campaign.get('stop_dyn', 0): 
                campaign['stop_dyn'] = new_stop
            
            if curr_p <= campaign['stop_dyn']:
                campaign['status'] = "STOPPED"
                campaign['p_now'] = campaign['stop_dyn']
            else:
                campaign['p_now'] = round(curr_p, 2)
                risk_1r = p_in - float(campaign['stop_initial'])
                if risk_1r > 0 and (curr_p - p_in) >= 2 * risk_1r:
                    campaign['status'] = "LOCKED"
                    if campaign['stop_dyn'] < p_in: 
                        campaign['stop_dyn'] = p_in
            
            start_d = datetime.strptime(campaign['start_date'], "%Y-%m-%d").date()
            days = max((date.today() - start_d).days, 1)
            
            ret = ((campaign['p_now'] - p_in) / p_in) * 100
            campaign['abs_return'] = f"{'+' if ret>0 else ''}{ret:.2f}%"
            
            if days >= 5:
                ann = ((1 + ret/100)**(365/days) - 1) * 100
                campaign['ann_return'] = f"{'+' if ann>0 else ''}{ann:.1f}%"
            else:
                campaign['ann_return'] = "N/A"
            
            if risk_1r > 0:
                r_val = (campaign['p_now'] - p_in) / risk_1r
                campaign['r_multiple'] = f"{'+' if r_val>0 else ''}{r_val:.1f}R"
                
        except Exception as e: 
            continue
        
    return tracker_db

def push_v4_data_to_website(radar_res, tracker_res, matrix_res):
    """【多轨推流】同时将雷达、追踪器和重力矩阵数据同步到 Cloudflare"""
    payload = {
        "market": "GLOBAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "radar_data": radar_res,
        "tracker_data": tracker_res,
        "matrix_data": matrix_res
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {SECRET_TOKEN}"}
    try:
        response = requests.post(f"{API_URL_BASE}/update_radar", json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"✅ 【云端同步】三轨数据已发射！Cloudflare 返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 【云端同步失败】: {e}")

# =====================================================================
# 主运行引擎
# =====================================================================
def run_v4_daily_scanner():
    print(f"INTOO V4 T模块：全球四大市场 (US/HK/JP/CN) 全景扫描中...\n")
    global RUN_DATA_DATE
    _lim = int(os.environ.get("V4_LIMIT", "0"))
    tk_list = TICKERS[:_lim] if _lim else TICKERS
    data = yf.download(tk_list, period='5y', group_by='ticker', progress=False,
                       auto_adjust=True)
    RUN_DATA_DATE = pd.Timestamp(data.index.max()).strftime("%Y%m%d")
    
    results, failed = [], []
    for ticker in tk_list:
        try:
            df_ticker = data[ticker].copy() if len(TICKERS) > 1 else data.copy()
            df_ticker.dropna(subset=['Close'], inplace=True)
            if df_ticker.empty: continue
                
            is_valid, final_reason, metrics = check_v4_resonance_strict(df_ticker, ticker)
            if is_valid:
                stock_name = NAME_MAP.get(ticker, "")
                display_code = f"{ticker} {stock_name}".strip()

                _tp = TYPE_OF.get(ticker, '未分类')
                _wt = TYPE_RULES.get(_tp, {}).get('weight', 1.0)
                results.append({
                    '市场': MARKET_MAP[ticker],
                    '类型': _tp,
                    '建议权重': _wt,
                    '代码': display_code,
                    '信号': final_reason,
                    '现价': float(metrics['Close']),
                    'ATR': float(metrics['ATR']),
                    '挤压率': metrics['Squeeze'],
                    '乖离率': metrics['Deviation'],
                    '1R防线': float(metrics['Dynamic_Stop'])
                })
        except Exception as e:
            failed.append(f"{ticker}:{type(e).__name__}")
            continue
    print(f"[体检] 扫描 {len(tk_list)} 只 | 无数据/失败 {len(failed)} 只"
          + (f" -> {failed[:6]}" if failed else ""))

    updated_tracker_data = update_tracker_logic(results, data)

    if results:
        results.sort(key=lambda x: (x['市场'], x['代码']))
        df_res = pd.DataFrame(results)
        print("=================== V4 全球战术扣板白名单 ===================")
        print(df_res[['市场', '代码', '信号', '现价', '1R防线']].to_string(index=False))
        print("=============================================================\n")
        
        if os.environ.get("V4_DRY_RUN") != "1":
            export_to_excel(results)
            push_to_wechat(results)
    else:
        print("📭 系统休眠：今日无可投新标的，但已自动更新存量追踪防线。")
        if os.environ.get("V4_DRY_RUN") != "1":
            push_to_wechat([])

    matrix_results = generate_macro_matrix()

    if updated_tracker_data is None or os.environ.get("V4_DRY_RUN") == "1":
        print("⏸️ 已跳过云端同步（DRY_RUN 或账本不可得）")
    else:
        push_v4_data_to_website(results, updated_tracker_data, matrix_results)

if __name__ == "__main__":
    run_v4_daily_scanner()
