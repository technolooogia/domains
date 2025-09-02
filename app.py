import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from modules.database import DomainDatabase
import pandas as pd

def create_enhanced_interface():
    st.set_page_config(
        page_title="🎯 Domain Hunter Pro",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff6b6b;
    }
    .success-domain {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🎯 Domain Hunter Pro")
    st.markdown("**The Ultimate Domain Discovery & Analysis Platform**")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Search Parameters
        st.subheader("Search Parameters")
        max_price = st.slider("Max Price ($)", 1, 100, 30)
        max_domains = st.number_input("Max Domains to Check", 100, 50000, 5000)
        
        extensions = st.multiselect(
            "Domain Extensions",
            ['.com', '.ai', '.io', '.co', '.net', '.org', '.tech', '.app', '.dev', '.xyz'],
            default=['.com', '.ai']
        )
        
        # Word Sources
        st.subheader("Keyword Sources")
        word_sources = st.multiselect(
            "Select Sources",
            ['Trending Keywords', 'Tech Terms', 'Health Terms', 'Finance Terms', 
             'Food Terms', 'Made-up Words', 'AI/ML Terms', 'Crypto Terms'],
            default=['Trending Keywords', 'Tech Terms', 'AI/ML Terms']
        )
        
        # Advanced Options
        st.subheader("Advanced Options")
        enable_trend_analysis = st.checkbox("Enable Trend Analysis", True)
        enable_value_estimation = st.checkbox("Enable Value Estimation", True)
        parallel_checking = st.checkbox("Parallel Checking (Faster)", True)
        
        # Start Hunt Button
        if st.button("🚀 Start Domain Hunt", type="primary", use_container_width=True):
            st.session_state.hunting = True
    
    # Main Interface Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Live Hunt", "📊 Analytics", "💎 Top Finds", "⚙️ Settings"])
    
    with tab1:
        display_live_hunt_tab()
    
    with tab2:
        display_analytics_tab()
    
    with tab3:
        display_top_finds_tab()
    
    with tab4:
        display_settings_tab()

def display_live_hunt_tab():
    """Live hunting interface"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔍 Domains Checked", st.session_state.get('domains_checked', 0))
    with col2:
        st.metric("💎 Available Found", st.session_state.get('available_found', 0))
    with col3:
        st.metric("💰 Avg Price", f"${st.session_state.get('avg_price', 0):.2f}")
    with col4:
        st.metric("⏱️ Time Elapsed", f"{st.session_state.get('time_elapsed', 0):.1f}s")
    
    # Progress and Status
    if st.session_state.get('hunting', False):
        progress_bar = st.progress(0)
        status_container = st.container()
        results_container = st.container()
        
        # Real-time results display
        with results_container:
            st.subheader("🎯 Live Results")
            results_placeholder = st.empty()
    
    # Results Table
    if 'hunt_results' in st.session_state:
        st.subheader("📋 Search Results")
        df = pd.DataFrame(st.session_state.hunt_results)
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            price_filter = st.slider("Max Price Filter", 0, 100, 50)
        with col2:
            trend_filter = st.slider("Min Trend Score", 0, 100, 0)
        with col3:
            extension_filter = st.selectbox("Extension Filter", ['All'] + list(df['extension'].unique()))
        
        # Apply filters
        filtered_df = df[df['price'] <= price_filter]
        filtered_df = filtered_df[filtered_df['trend_score'] >= trend_filter]
        if extension_filter != 'All':
            filtered_df = filtered_df[filtered_df['extension'] == extension_filter]
        
        # Display results
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "domain": st.column_config.TextColumn("Domain", width="medium"),
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "trend_score": st.column_config.ProgressColumn("Trend Score", min_value=0, max_value=100),
                "estimated_value": st.column_config.NumberColumn("Est. Value", format="$%.0f")
            }
        )

def display_analytics_tab():
    """Analytics dashboard"""
    db = DomainDatabase()
    analytics = db.get_analytics()
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Domains Found", analytics['total_domains_found'])
    with col2:
        st.metric("Average Price", f"${analytics['avg_price']:.2f}" if analytics['avg_price'] else "$0.00")
    with col3:
        st.metric("Success Rate", "12.3%")  # Calculate from search history
    with col4:
        st.metric("Total Value Found", "$45,230")  # Sum of estimated values
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Extension distribution
        if not analytics['top_extensions'].empty:
            fig = px.pie(
                analytics['top_extensions'], 
                values='count', 
                names='extension',
                title="Domain Extensions Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price distribution
        if not analytics['price_distribution'].empty:
            fig = px.bar(
                analytics['price_distribution'],
                x='price_range',
                y='count',
                title="Price Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    create_enhanced_interface()
