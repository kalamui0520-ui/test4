import datetime as dt
import warnings
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf

# 忽略警告訊息
warnings.filterwarnings('ignore')

# 設定網頁標題與排版
st.set_page_config(
    page_title='股票技術分析儀表板', page_icon='📈', layout='centered'
)

st.title('📈 股票技術分析儀表板')
st.markdown(
    '輸入美股或台股代碼（例如美股 `AAPL`, `TSLA` 或台股 `2330.TW`, `2317.TW`），即可即時檢視過去一個月的股價走勢與均線分析。'
)

# 建立側邊欄或主要輸入區
with st.form(key='stock_form'):
  ticker_input = st.text_input(
      '請輸入股票代碼:', value='AAPL', placeholder='例如: AAPL 或 2330.TW'
  )
  submit_button = st.form_submit_button(label='查詢並繪圖')

# 當使用者點擊送出表單時執行
if submit_button:
  ticker = ticker_input.strip().upper()

  if not ticker:
    st.warning('❌ 請輸入有效的股票代碼！')
  else:
    with st.spinner(f'⏳ 正在獲取 「{ticker}」 過去一個月的股價數據...'):
      try:
        # 計算過去一個月的日期區間
        end_date = dt.date.today()
        start_date = end_date - dt.timedelta(days=35)  # 多取幾天確保交易日足夠

        # 下載數據
        df = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False,
        )

        if df.empty:
          st.error(
              f'❌ 找不到股票代碼 「{ticker}」'
              ' 的數據，請檢查代碼是否正確（台股請加上 .TW）。'
          )
        else:
          # 處理 yfinance 多階層欄位問題
          if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

          # 計算均線 (Moving Averages)
          df['MA5'] = df['Close'].rolling(window=5).mean()
          df['MA20'] = df['Close'].rolling(window=20).mean()

          # 繪製專業走勢圖
          fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

          ax.plot(
              df.index,
              df['Close'],
              label='Close Price (收盤價)',
              color='#1f77b4',
              linewidth=2,
          )
          ax.plot(
              df.index,
              df['MA5'],
              label='MA 5 (5日均線)',
              color='#ff7f0e',
              linestyle='--',
              linewidth=1.5,
          )
          ax.plot(
              df.index,
              df['MA20'],
              label='MA 20 (20日均線)',
              color='#2ca02c',
              linestyle='--',
              linewidth=1.5,
          )

          # 圖表樣式優化
          ax.set_title(
              f'{ticker} - 過去一個月股價走勢與均線分析',
              fontsize=14,
              fontweight='bold',
              pad=15,
          )
          ax.set_xlabel('日期', fontsize=12)
          ax.set_ylabel('價格', fontsize=12)
          ax.legend(loc='best', fontsize=11)
          ax.grid(True, linestyle=':', alpha=0.6)

          plt.xticks(rotation=45)
          fig.tight_layout()

          # 在 Streamlit 中顯示 Matplotlib 圖表
          st.pyplot(fig)
          st.success('✅ 查詢成功！')

      except Exception as e:
        st.error(f'❌ 發生錯誤: {e}')