import io
import tempfile
from pathlib import Path
import pandas as pd
import streamlit as st

from review import review_image, COLUMNS

st.title("Smiley brand checker")

files = st.file_uploader(
    "Upload an image to review",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

if files:
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            path = Path(tmp) / f.name
            path.write_bytes(f.getbuffer())
            rows.append(review_image(path))

    df = pd.DataFrame(rows, columns=COLUMNS)
    st.dataframe(df, width='stretch')

    st.download_button(
        "Download as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="results.csv",
        mime="text/csv",
    )

    xlsx_buffer = io.BytesIO()
    df.to_excel(xlsx_buffer, index=False)
    st.download_button(
        "Download as XLSX",
        xlsx_buffer.getvalue(),
        file_name="results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )