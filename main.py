import streamlit as st
import base64
import os

st.set_page_config(layout="wide")

# ---------------- STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page
    st.rerun()

# ---------------- LOAD FONT ----------------
def load_font():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR, "static", "canva-sans-regular.otf")

    if not os.path.exists(font_path):
        st.warning("Font not found. Using default.")
        return

    with open(font_path, "rb") as f:
        font_base64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'CanvaSans';
        src: url(data:font/otf;base64,{font_base64}) format('opentype');
    }}

    * {{
        font-family: 'CanvaSans' !important;
    }}
    </style>
    """, unsafe_allow_html=True)

load_font()

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>

/* Background */
body {
    background-color: #b7c9cf;
}

/* Center container */
.main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: 80px;
}

/* Title */
.title {
    font-size: 80px;
    font-weight: 700;
    letter-spacing: 3px;
}

/* Subtitle */
.subtitle {
    font-size: 22px;
    margin-top: -10px;
}

/* Icon row */
.icon-row {
    display: flex;
    gap: 120px;
    margin-top: 60px;
}

/* Icon card */
.icon-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    transition: 0.2s;
}

.icon-card:hover {
    transform: scale(1.1);
}

/* Icon image */
.icon-card img {
    width: 120px;
}

/* Footer text */
.footer {
    margin-top: 30px;
    font-size: 16px;
}

/* Page cards */
.card {
    background-color: #e6d1d1;
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    height: 300px;
    margin-top: 40px;
}

/* Toolbar */
.toolbar {
    background-color: #e6d1d1;
    border-radius: 20px;
    padding: 15px;
    text-align: center;
    width: 40%;
    margin: auto;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- IMAGE BASE64 ----------------
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ---------------- HOME ----------------
def home():
    wb = img_to_base64("icons/whiteboard.png")
    sh = img_to_base64("icons/shapes.png")
    gm = img_to_base64("icons/gaming.png")

    st.markdown(f"""
    <div class="main">

        <div class="title">PIXEL SENS</div>
        <div class="subtitle">A Creative Board for<br>Learning and Enjoyment</div>

        <div class="icon-row">

            <form action="" method="get">
                <button name="nav" value="camera" style="border:none;background:none;">
                    <div class="icon-card">
                        <img src="data:image/png;base64,{wb}">
                    </div>
                </button>
            </form>

            <form action="" method="get">
                <button name="nav" value="tool" style="border:none;background:none;">
                    <div class="icon-card">
                        <img src="data:image/png;base64,{sh}">
                    </div>
                </button>
            </form>

            <form action="" method="get">
                <button name="nav" value="game" style="border:none;background:none;">
                    <div class="icon-card">
                        <img src="data:image/png;base64,{gm}">
                    </div>
                </button>
            </form>

        </div>

        <div class="footer">Tap on the icons to discover more.</div>

    </div>
    """, unsafe_allow_html=True)

    # Navigation handler
    query = st.query_params.get("nav")
    if query:
        st.session_state.page = query

# ---------------- PAGES ----------------
def game_page():
    if st.button("⬅ Back"):
        go("home")

    st.markdown('<div class="card"><h2>GAME</h2></div>', unsafe_allow_html=True)

def camera_page():
    if st.button("⬅ Back"):
        go("home")

    st.markdown('<div class="card"><h2>CAMERA</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="toolbar"><h3>TOOLBAR</h3></div>', unsafe_allow_html=True)

def tool_page():
    if st.button("⬅ Back"):
        go("home")

    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown('<div class="card"><h2>CAMERA</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><h2>ANSWER</h2></div>', unsafe_allow_html=True)

    st.markdown('<div class="toolbar"><h3>TOOLBAR</h3></div>', unsafe_allow_html=True)

# ---------------- ROUTER ----------------
if st.session_state.page == "home":
    home()
elif st.session_state.page == "camera":
    camera_page()
elif st.session_state.page == "tool":
    tool_page()
elif st.session_state.page == "game":
    game_page()