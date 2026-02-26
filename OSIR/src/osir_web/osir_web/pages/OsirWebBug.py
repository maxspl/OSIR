import streamlit as st
from osir_web.pages.OsirWebHeader import OsirWebHeader

class OsirWebBug:
    GITHUB_REPO = "https://github.com/maxspl/OSIR/issues"

    @staticmethod
    def render():
        OsirWebHeader.render(
            title="🐛 REPORT A BUG 🐛",
            subtitle="Help us improve OSIR by reporting any issues you encounter."
        )

        st.markdown(f"""
        <div style="text-align:center; margin-top: 1.5rem;">
            <a href="{OsirWebBug.GITHUB_REPO}" target="_blank" style="
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: linear-gradient(135deg, #6ee7b7, #a7f3d0);
                color: #064e3b;
                font-family: 'Source Sans', sans-serif;
                font-weight: 700;
                font-size: 0.9rem;
                letter-spacing: 0.05em;
                text-decoration: none;
                padding: 0.6rem 1.4rem;
                border-radius: 999px;
                filter: drop-shadow(0 0 10px rgba(110,231,183,0.3));
                transition: opacity 0.2s;
            ">
                🐙 Open an Issue on GitHub
            </a>
        </div>
        """, unsafe_allow_html=True)