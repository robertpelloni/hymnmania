# Deployment Instructions

## Docker Compose (Recommended)
1. Ensure Docker Desktop is running.
2. In the project root, run: `docker compose up --build -d`
3. Access the Streamlit UI at `http://localhost:8501`.

## Local Virtual Environment
*Note: This project targets Python 3.12.*

1. Ensure `ffmpeg`, `fluidsynth`, `libfluidsynth-dev`, and `fluid-soundfont-gm` are installed on your OS (`sudo apt install ffmpeg fluidsynth libfluidsynth-dev fluid-soundfont-gm`).
2. Run `pip install -r requirements.txt`.
3. Compile the `pybind11` C++ engine extension from the project root by running `make`.
4. Start the UI: `python -m streamlit run app.py`
