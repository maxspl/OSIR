import streamlit as st


class OsirWebHeader:

    @staticmethod
    def render(title: str, subtitle: str):
        st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Sans:wght@300&display=swap');
            .hd {{ text-align: center; padding: 0.4rem 2rem 0; margin: -1rem -1rem 1.5rem; ... }}
            @media (prefers-color-scheme: dark) {{ .hd {{ background: radial-gradient(ellipse at top, rgba(16, 185, 129, 0.18) 0%, transparent 70%); }} .ht {{ color: #d1fae5 !important; }} }}
            .ht {{
                font-family: "Source Sans", sans-serif;
                font-size: 2.6rem;
                font-weight: 900;
                margin: 0;
                background: linear-gradient(135deg, #10b981, #34d399);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                filter: drop-shadow(0 0 18px rgba(16,185,129,0.35));
            }}
            .hs {{
                font-family: "Source Sans", sans-serif;
                font-size: 0.85rem;
                font-weight: 600;
                color: #6b7280;
                margin: 0.25rem 0 0;
                letter-spacing: 0.18em;
                text-transform: uppercase;
            }}
            .hd hr {{ border: none; height: 2px; background: linear-gradient(90deg, transparent, #10b981, transparent); margin: 0.9rem 0 0; opacity: 0.6; }}
            </style>
            <div class="hd">
            <div class="ht">{title}</div>
            <div class="hs">{subtitle}</div>
            </div>""", unsafe_allow_html=True)