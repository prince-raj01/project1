import streamlit as st
import requests
import pandas as pd
import time

API_BASE = 'http://localhost:8000'

st.set_page_config(page_title='Dynamic Data Dashboard', layout='wide')
st.title('Dynamic Data Dashboard')

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['timestamp','active_users','requests_per_min','error_rate'])

# Load recent history once on start
if st.session_state.df.empty:
    try:
        r = requests.get(f'{API_BASE}/metrics/history?n=120', timeout=3).json()
        items = r.get('items', [])
        if items:
            st.session_state.df = pd.DataFrame(items)
    except Exception:
        # ignore if API not running yet
        pass

col1, col2 = st.columns([1,3])
with col1:
    if st.button('Fetch now'):
        try:
            r = requests.get(f'{API_BASE}/metrics', timeout=2).json()
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([r])], ignore_index=True)
        except Exception as e:
            st.error(f'Error fetching metrics: {e}')
    auto = st.checkbox('Auto-refresh (every 2s)', value=False)

with col2:
    st.subheader('Latest metrics')
    if not st.session_state.df.empty:
        st.write(st.session_state.df.tail(5))
    else:
        st.write('No data yet. Click "Fetch now".')

chart_df = st.session_state.df.set_index('timestamp')[['active_users','requests_per_min']]
if not chart_df.empty:
    st.line_chart(chart_df)

# Simple auto-refresh loop: fetch, append, sleep, rerun
if auto:
    try:
        r = requests.get(f'{API_BASE}/metrics', timeout=2).json()
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([r])], ignore_index=True)
    except Exception:
        pass
    time.sleep(2)
    st.experimental_rerun()
