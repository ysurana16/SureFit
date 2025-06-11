import streamlit as st
import pandas as pd
import numpy as np
from backend import recommend_sizes_with_risk  


def findBrandsWithGarment(type):
    if type == 'Top':
        df = pd.read_csv("data/sizesTop.csv")
    elif type == 'Pant':
        df = pd.read_csv("data/sizesPants.csv")
    elif type == 'Footwear':
        df = pd.read_csv("data/sizeFootwear.csv")
    return df['brandName'].unique()

def findSizes(type, brand):
    if type == 'Top':
        df = pd.read_csv("data/sizesTop.csv")
    elif type == 'Pant':
        df = pd.read_csv("data/sizesPants.csv")
    elif type == 'Footwear':
        df = pd.read_csv("data/sizeFootwear.csv")
    brand_rows = df[df['brandName'] == brand]
    unique_sizes = brand_rows['size'].unique()
    return unique_sizes

def predict(from_band, to_brand, from_size, type):
    if type == 'Top':
        df = pd.read_csv("data/sizesTop.csv")
    elif type == 'Pant':
        df = pd.read_csv("data/sizesPants.csv")
    elif type == 'Footwear':
        df = pd.read_csv("data/sizeFootwear.csv")
    referenceChart = df[df['brandName'] == from_brand].drop(columns=['brandName', 'category'])
    currentChart = df[df['brandName'] == to_brand].drop(columns=['brandName', 'category'])
    result = recommend_sizes_with_risk(currentChart, referenceChart, from_size, type)
    return result

#---------------------------------------------------------------------------------------------

types = ['Top', 'Pant', 'Footwear']
st.title("Brand Size Converter")

typeBox = st.selectbox("Select garment type", types)
from_brand = st.selectbox("Your Current Brand", findBrandsWithGarment(typeBox))
from_size = st.selectbox("Your Current Size", findSizes(typeBox, from_brand))
to_brand = st.selectbox("Target Brand", findBrandsWithGarment(typeBox))

if st.button("Convert"):
    try:
        result = predict(from_brand, to_brand, from_size, typeBox)

        if not result.empty:
            top_recommendations = result.head(2)
            
            st.success(f"Top {to_brand} size recommendation(s):")
            
            for idx, row in top_recommendations.iterrows():
                size = row['size']
                score = row['Recommendation Score']
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 10px; background-color: #f0f2f6; border-left: 5px solid #4CAF50; color: black;">
                    <b>Size:</b> {size}<br>
                    <b>Recommendation Score:</b> {score:.2f}
                </div>
                """, unsafe_allow_html=True)

        else:
            st.warning("No suitable size found.")

    except Exception as e:
        st.error(f"Error: {e}")







