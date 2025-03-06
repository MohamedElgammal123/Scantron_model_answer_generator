# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 00:13:19 2025

@author: Mohammed_magdy
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from io import BytesIO

# --- Helper Functions ---
@st.cache_data
def load_coordinates():
    # Assumes the coordinates file is in the repository directory
    return pd.read_excel("coordinates.xlsx")

@st.cache_data
def load_scantron_image():
    # Assumes the scantron image is in the repository directory
    return mpimg.imread("Scantron Sheet.jpg")

def generate_highlighted_scantron(correct_answers, df_coords, img):
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.imshow(img)
    plt.axis('off')
    
    highlight_logs = []
    
    # Loop through each correct answer and add a circle
    for q, correct in correct_answers.items():
        # Match based on question and answer (case-insensitive)
        row = df_coords[(df_coords['Question'] == q) & (df_coords['Answer'].str.upper() == correct.upper())]
        if not row.empty:
            x = row['X'].values[0]
            y = row['Y'].values[0]
            circle = patches.Circle(
                (x, y), 
                radius=9,              # Adjust size if needed
                facecolor='black',     # Fill color
                edgecolor='black',     # Border color
                linewidth=2,           # Border thickness
                alpha=0.7,             # Transparency level
                linestyle='-'          # Solid border
            )
            ax.add_patch(circle)
            log = f"Highlighted Q{q} Option {correct} at (x={x:.2f}, y={y:.2f})"
            highlight_logs.append(log)
        else:
            log = f"Coordinate for Q{q} Option {correct} not found."
            highlight_logs.append(log)
    
    return fig, highlight_logs

# --- Streamlit App Interface ---
st.title("Scantron Highlighter App")
st.write("Upload your correct answer Excel file to generate a highlighted scantron image.")

uploaded_file = st.file_uploader("Choose a Correct Answer Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Load correct answers from the uploaded file
        df_correct_answers = pd.read_excel(uploaded_file)
        correct_answers = dict(zip(df_correct_answers["Question"], df_correct_answers["Answer"]))
        
        # Load the coordinates and scantron image from the repository
        df_coords = load_coordinates()
        img = load_scantron_image()
        
        # Generate the highlighted scantron image
        fig, logs = generate_highlighted_scantron(correct_answers, df_coords, img)
        
        st.subheader("Highlighted Scantron")
        st.pyplot(fig)
        
        st.write("**Highlights Info:**")
        for log in logs:
            st.write(log)
        
        # Save the image to a buffer for download
        buf = BytesIO()
        fig.savefig(buf, format="jpg", dpi=300, bbox_inches='tight')
        buf.seek(0)
        
        # Button: Download highlighted scantron image
        st.download_button(
            label="Download Highlighted Scantron",
            data=buf,
            file_name="Colored_Scantron.jpg",
            mime="image/jpeg"
        )
        
        # Button: Generate reference answer (display correct answers table)
        if st.button("Generate Reference Answer"):
            st.subheader("Reference Answers")
            st.table(df_correct_answers)
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Awaiting correct answer Excel file upload.")
