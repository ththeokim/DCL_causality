import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Webapp Configuration
st.set_page_config(page_title="DCL Merit-Order Effect", layout="wide")

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
    
    st.markdown("### 🗺️ Capacity-Weighted Weather Indices")
    st.write("Instead of using simple national average weather data, we constructed sophisticated capacity-weighted weather indices based on the actual distribution of wind and solar power plants in Germany.")
    
    col1, col2 = st.columns(2)
    try:
        with col1:
            st.image("mastr_wind_capacity_map.png", caption="Wind Power Capacity Distribution in Germany")
        with col2:
            st.image("mastr_solar_capacity_map.png", caption="Solar Power Capacity Distribution in Germany")
    except FileNotFoundError:
        st.warning("Please upload the map images (mastr_wind_capacity_map.png, etc.) to the current directory.")

# 4. Page 2: OLS Results & Simulator
elif page == "2. OLS Results & Simulator":
    st.title("⚡ Wholesale Electricity Price Simulator")
    
    # --- 새롭게 디자인된 OLS 결과표 영역 시작 ---
    st.markdown("### 📈 1. OLS Regression Results")
    st.write("The causal effect of renewable energy on electricity prices, controlling for demand.")
    
    # 주요 지표를 대시보드 위젯(Metric)으로 깔끔하게 배치
    col1, col2, col3 = st.columns(3)
    col1.metric(label="R-squared", value="0.682", delta="High Explanatory Power", delta_color="normal")
    col2.metric(label="F-statistic", value="6265.0", delta="p < 0.001", delta_color="normal")
    col3.metric(label="Observations", value="8,759", delta="Hourly Data", delta_color="off")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 회귀분석 결과표를 Pandas 데이터프레임으로 만들어 깔끔한 표(Table)로 렌더링
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
    
    # 심사위원(교수님)을 위한 해석 요약 박스 추가
    st.info("💡 **Key Finding:** The negative coefficients for Wind (**-11.98**) and Solar (**-0.17**) statistically prove the **Merit-Order Effect**. (*** p < 0.001)")
    st.markdown("---")
    # --- 새롭게 디자인된 OLS 결과표 영역 끝 ---

    st.markdown("### 🎛️ 2. Interactive Price Simulator")
    # (이 아래부터는 기존의 INTERCEPT = 45.8463 ... 코드가 그대로 이어지면 됩니다!)
    
    st.markdown("### 🎛️ 2. Interactive Price Simulator")
    st.write("Adjust the weather and demand conditions below to see the real-time causal impact on electricity prices based on the OLS coefficients above.")
    
    # OLS Coefficients
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
