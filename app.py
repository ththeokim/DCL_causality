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
    
    # --- 새롭게 추가된 OLS 결과표 영역 ---
    st.markdown("### 📈 1. OLS Regression Results")
    st.write("The causal effect of renewable energy on electricity prices, controlling for demand. All variables are statistically significant (P>|t| = 0.000) with an R-squared of 0.682.")
    
    # 텍스트 형태의 결과표를 그대로 웹앱에 렌더링
    ols_results = """
    OLS Regression Results                            
    ==============================================================================
    Dep. Variable:      price_eur_per_mwh   R-squared:                       0.682
    Model:                            OLS   Adj. R-squared:                  0.682
    Method:                 Least Squares   F-statistic:                     6265.
    Date:                Sun, 28 Jun 2026   Prob (F-statistic):               0.00
    Time:                        13:12:07   Log-Likelihood:                -42033.
    No. Observations:                8759   AIC:                         8.407e+04
    Df Residuals:                    8755   BIC:                         8.410e+04
    Df Model:                           3                                         
    ====================================================================================================
                                           coef    std err          t      P>|t|      [0.025      0.975]
    ----------------------------------------------------------------------------------------------------
    Intercept                           45.8463      1.997     22.953      0.000      41.931      49.762
    consumption_mwh                      0.0110      0.000     78.942      0.000       0.011       0.011
    wind_speed_100m_weighted_ms        -11.9818      0.144    -83.411      0.000     -12.263     -11.700
    shortwave_radiation_weighted_wm2    -0.1710      0.002   -109.206      0.000      -0.174      -0.168
    ====================================================================================================
    """
    st.code(ols_results, language='text')
    st.markdown("---")
    # -----------------------------------

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
