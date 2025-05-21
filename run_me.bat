@echo off
pip install -r requirements.txt
python scripts/run_simulation.py
streamlit run streamlit_app.py
pause
