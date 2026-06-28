import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Webapp Configuration
st.set_page_config(page_title="DCL Merit-Order Effect", layout="wide")

# 데이터 불러오기 (캐싱하여 속도 향상)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("merged_data_for_modeling.csv")
        df['time'] = pd.to_datetime(df['time'])
        return df
    except FileNotFoundError:
        return None

df = load_data()

# 2. Sidebar Navigation
st.sidebar.title("DCL Final Project")
st.sidebar.markdown("**Team:** Taeheon & Bosse")
page = st.sidebar.radio("Navigation", ["1. Causal Strategy & Data", "2. OLS Results & Simulator"])

# 3. Page 1: Data & Causal Strategy
if page == "1. Causal Strategy & Data":
    st.title("The Merit-Order Effect of Renewable Energy")
    
    st.markdown("""
    ### 🎯 Research Goal & Causal Strategy
    Simply analyzing the correlation between electricity demand and prices suffers from severe **Endogeneity** issues. 
    To tackle this, we utilized weather conditions (wind and solar) as **Exogenous Shocks (Instrumental Variables)**.
    """)
    
    # --- 새로 추가된 부분 1: Causal DAG ---
    st.markdown("#### 🔄 Directed Acyclic Graph (DAG) for our IV Strategy")
    st.info("""
    **[ Weather (Instrumental Variable) ]** ➔ **[ Renewable Generation ]** ➔ **[ Electricity Price (Y) ]** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ⇧  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **[ Electricity Demand (Control) ]**
    """)
    st.markdown("---")
    
    st.markdown("### 🗺️ Capacity-Weighted Weather Indices")
    st.write("Instead of using simple national average weather data, we constructed sophisticated capacity-weighted weather indices based on the actual distribution of wind and solar power plants in Germany.")
    
    col1, col2 = st.columns(2)
    try:
        with col1:
            st.image("mastr_wind_capacity_map.png", caption="Wind Power Capacity Distribution in Germany")
        with col2:
            st.image("mastr_solar_capacity_map.png", caption="Solar Power Capacity Distribution in Germany")
    except FileNotFoundError:
        st.warning("Please upload the map images to the current directory.")

    st.markdown("---")
    
# --- 새로 추가된 부분 2: 실제 데이터 트렌드 (이중 축 그래프) ---
    st.markdown("### 📊 Historical Data Trend (Dual-Axis)")
    st.write("Explore the actual data from 2025. Use the dropdown to select a specific month, or use the slider below the chart to zoom in and observe how spikes in wind speed correspond to drops in electricity prices.")
    
    if df is not None:
        # 1. 월별 선택 드롭다운(Selectbox) 위젯 추가
        month_list = ["All Year"] + [f"2025-{str(i).zfill(2)}" for i in range(1, 13)]
        selected_month = st.selectbox("📅 Select Month to View:", month_list)
        
        # 2. 선택한 월에 맞게 데이터 필터링
        if selected_month == "All Year":
            plot_df = df
        else:
            plot_df = df[df['time'].dt.strftime('%Y-%m') == selected_month]
            
        # 3. Plotly 이중 축 그래프 생성
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 전력 가격 (왼쪽 축, 꺾은선 그래프)
        fig_trend.add_trace(
            go.Scatter(x=plot_df['time'], y=plot_df['price_eur_per_mwh'], name="Price (EUR)", line=dict(color="red", width=1)),
            secondary_y=False,
        )
        
        # 풍속 (오른쪽 축, 영역 그래프)
        fig_trend.add_trace(
            go.Scatter(x=plot_df['time'], y=plot_df['wind_speed_100m_weighted_ms'], name="Wind Speed (m/s)", fill='tozeroy', line=dict(color="blue", width=1), opacity=0.3),
            secondary_y=True,
        )
        
        # 4. 그래프 레이아웃 및 줌(Zoom) 슬라이더 설정
        fig_trend.update_layout(
            title_text="Electricity Price vs. Weighted Wind Speed", 
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # 범례 위치 최적화
        )
        fig_trend.update_yaxes(title_text="Price (EUR/MWh)", secondary_y=False)
        fig_trend.update_yaxes(title_text="Wind Speed (m/s)", secondary_y=True)
        
        # X축 아래에 전체 기간을 훑어볼 수 있는 미니 슬라이더 추가
        fig_trend.update_xaxes(rangeslider_visible=True)
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Please upload 'merged_data_for_modeling.csv' to see the historical trend chart.")

# 4. Page 2: OLS Results & Simulator
elif page == "2. OLS Results & Simulator":
    st.title("⚡ Wholesale Electricity Price Simulator")
    
    st.markdown("### 📈 1. OLS Regression Results")
    st.write("The causal effect of renewable energy on electricity prices, controlling for demand.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="R-squared", value="0.682", delta="High Explanatory Power", delta_color="normal")
    col2.metric(label="F-statistic", value="6265.0", delta="p < 0.001", delta_color="normal")
    col3.metric(label="Observations", value="8,759", delta="Hourly Data", delta_color="off")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("#### 📊 Estimated Coefficients")
    coef_df = pd.DataFrame({
        "Variable": [
            "Intercept (Base Price)", 
            "Electricity Demand (Control)", 
            "Weighted Wind Speed (IV)", 
            "Weighted Solar Radiation (IV)"
        ],
        "Coefficient": ["45.8463", "0.0110", "-11.9818", "-0.1710"],
        "Std. Error": ["1.997", "0.000", "0.144", "0.002"],
        "t-value": ["22.95", "78.94", "-83.41", "-109.20"],
        "P-value": ["0.000 ***", "0.000 ***", "0.000 ***", "0.000 ***"]
    })
    st.table(coef_df.set_index("Variable"))
    
    st.info("💡 **Key Finding:** The negative coefficients for Wind (**-11.98**) and Solar (**-0.17**) statistically prove the **Merit-Order Effect**. (*** p < 0.001)")
    st.markdown("---")

    # --- 중복 수정된 시뮬레이터 영역 ---
    st.markdown("### 🎛️ 2. Interactive Price Simulator")
    st.write("Adjust the weather and demand conditions below to see the real-time causal impact on electricity prices based on the OLS coefficients above.")
    
    INTERCEPT = 45.8463
    COEF_CONS = 0.0110
    COEF_WIND = -11.9818
    COEF_SOLAR = -0.1710
    
    st.sidebar.header("🎛️ Control Panel")
    cons = st.sidebar.slider("Electricity Demand (MWh)", min_value=30000, max_value=80000, value=50000, step=1000)
    wind = st.sidebar.slider("Weighted Wind Speed (m/s)", min_value=0.0, max_value=25.0, value=5.0, step=1.0)
    solar = st.sidebar.slider("Weighted Solar Radiation (W/m²)", min_value=0.0, max_value=1000.0, value=200.0, step=50.0)
    
    predicted_price = INTERCEPT + (cons * COEF_CONS) + (wind * COEF_WIND) + (solar * COEF_SOLAR)
    
    if predicted_price < 0:
        st.error(f"🚨 Negative Price Alert: {predicted_price:.2f} EUR/MWh")
        st.write("Renewable energy generation is so high that consumers are actually being paid to use electricity!")
    else:
        st.success(f"Predicted Wholesale Price: {predicted_price:.2f} EUR/MWh")
        
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = predicted_price,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Predicted Price (EUR/MWh)"},
        gauge = {
            'axis': {'range': [-50, 1000]},
            'bar': {'color': "darkblue"},
            'steps' : [
                {'range': [-50, 0], 'color': "red"},
                {'range': [0, 100], 'color': "lightgreen"},
                {'range': [100, 1000], 'color': "orange"}
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)
