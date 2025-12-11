import streamlit as st

def apply_scifi_theme():
    """Apply sci-fi themed CSS to the Streamlit app"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1628 100%);
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Animated background grid */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: gridMove 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes gridMove {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    /* Glowing particles */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: radial-gradient(circle, rgba(0, 255, 255, 0.1) 1px, transparent 1px);
        background-size: 100px 100px;
        animation: particleFloat 30s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes particleFloat {
        0%, 100% { opacity: 0.3; transform: translateY(0); }
        50% { opacity: 0.6; transform: translateY(-20px); }
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00ffff !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5),
                     0 0 20px rgba(0, 255, 255, 0.3),
                     0 0 30px rgba(0, 255, 255, 0.2);
        position: relative;
        z-index: 1;
    }
    
    h1 {
        font-size: 2.5rem !important;
        border-bottom: 2px solid #00ffff;
        padding-bottom: 15px;
        margin-bottom: 30px;
        animation: titleGlow 2s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { text-shadow: 0 0 10px rgba(0, 255, 255, 0.5), 0 0 20px rgba(0, 255, 255, 0.3); }
        50% { text-shadow: 0 0 20px rgba(0, 255, 255, 0.8), 0 0 30px rgba(0, 255, 255, 0.5), 0 0 40px rgba(0, 255, 255, 0.3); }
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(10, 20, 40, 0.6) !important;
        border: 2px solid #00ffff !important;
        border-radius: 8px !important;
        color: #00ffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 16px !important;
        padding: 12px !important;
        box-shadow: inset 0 0 10px rgba(0, 255, 255, 0.2),
                    0 0 15px rgba(0, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ffff !important;
        box-shadow: inset 0 0 15px rgba(0, 255, 255, 0.3),
                    0 0 25px rgba(0, 255, 255, 0.4) !important;
        outline: none !important;
    }
    
    .stTextInput > label {
        color: #00ffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 14px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%) !important;
        color: #00ffff !important;
        border: 2px solid #00ffff !important;
        border-radius: 8px !important;
        padding: 15px 40px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4),
                    inset 0 0 10px rgba(0, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0f1a2e 0%, #1f2f4a 100%) !important;
        color: #00ffff !important;
        border-color: #00ffff !important;
        box-shadow: 0 0 40px rgba(0, 255, 255, 0.8),
                    inset 0 0 20px rgba(0, 255, 255, 0.2) !important;
        transform: translateY(-2px);
        text-shadow: 0 0 15px rgba(0, 255, 255, 1);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.6),
                    inset 0 0 15px rgba(0, 255, 255, 0.15) !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(0, 255, 255, 0.1) !important;
        border: 1px solid #00ffff !important;
        border-left: 4px solid #00ffff !important;
        border-radius: 8px !important;
        color: #00ffff !important;
        font-family: 'Rajdhani', sans-serif !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.2) !important;
    }
    
    .stSuccess {
        background: rgba(0, 255, 136, 0.1) !important;
        border: 1px solid #00ff88 !important;
        border-left: 4px solid #00ff88 !important;
        color: #00ff88 !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid #ffc107 !important;
        border-left: 4px solid #ffc107 !important;
        color: #ffc107 !important;
    }
    
    .stError {
        background: rgba(255, 0, 102, 0.1) !important;
        border: 1px solid #ff0066 !important;
        border-left: 4px solid #ff0066 !important;
        color: #ff0066 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00ffff 0%, #00ff88 100%) !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5) !important;
    }
    
    .stProgress > div > div {
        background: rgba(0, 255, 255, 0.1) !important;
        border: 1px solid #00ffff !important;
        border-radius: 10px !important;
    }
    
    /* Markdown text */
    p, li, .stMarkdown {
        color: #b0c4de !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    
    /* Copyright */
    .copyright {
        position: fixed;
        bottom: 10px;
        right: 15px;
        color: #00ffff;
        font-size: 12px;
        font-family: 'Orbitron', sans-serif;
        z-index: 999;
        opacity: 0.6;
        pointer-events: none;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
        letter-spacing: 2px;
    }
    
    /* Subheader styling */
    .stSubheader {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%) !important;
        border-right: 2px solid #00ffff !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def show_copyright():
    """Displays copyright notice at bottom right"""
    st.markdown("""
    <div class="copyright">© iKAISER</div>
    """, unsafe_allow_html=True)