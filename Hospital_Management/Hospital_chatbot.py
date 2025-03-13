import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import re
from langdetect import detect
from googletrans import Translator
import numpy as np
import os
import requests
from bs4 import BeautifulSoup


# Function to detect language and translate to English
def translate_to_english(text, target_lang):
    translator = Translator()
    translation = translator.translate(text, src=target_lang, dest="en")
    return translation.text

# Function to translate back to the detected language
def translate_to_detected_language(text, target_lang):
    translator = Translator()
    translation = translator.translate(text, src="en", dest=target_lang)
    return translation.text

# Function to detect language
def detect_language(text):
    return detect(text)

# Function to Extract Hospital List
def get_hospital_list(url):

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        h2_heading = soup.find('h2')
        total_hospitals_count = h2_heading.text.strip() if h2_heading else "N/A"
        hospital_names = soup.find_all('h3')

        list_of_hospitals = []
        for hospital in hospital_names:
            if hospital.get('class') and 'accordion-button' in hospital.get('class'):
                continue
            list_of_hospitals.append(hospital.text.strip())

        return total_hospitals_count, list_of_hospitals
    else:
        return f"Failed to retrieve the webpage. Status code: {response.status_code}", []
    

def get_bot_response(user_input, detected_language, city):

    # Translate the user's input to English
    user_input_in_english = translate_to_english(user_input, detected_language)
    print(f"User Input in English: {user_input_in_english}")  # Debugging

    # Create the URL by replacing 'haridwar' with the user-provided city
    url = f'https://www.hexahealth.com/hospitals/insurance/ayushman-bharat-hospitals-list-in-{city.lower()}'

    # Call the get_hospital_list function to scrape the hospital data
    total_count, hospitals = get_hospital_list(url)

    # Prepare the response based on hospital data
    if hospitals:
        matching_response = f"**Total Hospitals in {city.capitalize()}**: {total_count}\n\n"
        for hospital in hospitals:
            matching_response += f"- {hospital}\n"
    else:
        matching_response = "Sorry, I couldn't find any hospital data."

    source = 'Website'

    # Translate the response back to the user's detected language
    bot_response_translated = translate_to_detected_language(matching_response, detected_language)

    return bot_response_translated, source


# Streamlit app interface
def streamlit_app():
    st.title("Health Scheme Finder")
    st.write(
        """
        This application helps you to ask questions about Govt Medical Schemes for the People
        """
    )
    url = 'https://www.hexahealth.com/hospitals/insurance/ayushman-bharat-hospitals-list-in-haridwar'
    user_input = st.text_input("Ask your question here:")

    if user_input:
            # Detect language of the input
            detected_language = detect_language(user_input)

            if detected_language == 'en':
                detected_language = "en"  # Ensure default language is English
            else:
                detected_language = detected_language

            city = st.text_input("Enter the city name:")

            if city:
                # Show a spinner while processing
                with st.spinner('Analyzing...'):

                    health_scheme_text = """
                    **Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)** is a health insurance scheme in India that provides financial coverage for secondary and tertiary healthcare. It's also known as Modicare. 

                    **Features:**
                    - Offers cashless treatment at empanelled hospitals
                    - Provides a health cover of Rs. 5 lakhs per family per year
                    - Includes pre and post-hospitalisation expenses
                    - Covers all pre-existing conditions from day one
                    - Pays a defined transport allowance per hospitalization

                    **Eligibility:**
                    - The scheme is for economically vulnerable families 
                    - The scheme is based on the deprivation and occupational criteria of Socio-Economic Caste Census 2011 (SECC 2011)
                    - The scheme includes households in the bottom 40% of the Indian population
                    - The scheme includes all senior citizens aged 70 years and above, irrespective of income

                    **Registration:**
                    - You can register for a PMJAY card at your nearest empanelled hospital or Ayushman Mitra
                    - You will need to provide your identification documents, such as your Aadhaar card.
                    """
                    
                    # Translate the health scheme text if the detected language is not English
                    if detected_language != "en":
                        translated_text = translate_to_detected_language(health_scheme_text, detected_language)
                    else:
                        translated_text = health_scheme_text

                    # Show the translated or original health scheme details
                    st.subheader("These are the Govt Health Schemes based on your city:")
                    st.write(translated_text)

                    # Call the get_bot_response function directly (no need for asyncio anymore)
                    bot_response, source = get_bot_response(user_input, detected_language, city)

                # Show the result using st.markdown to render the Markdown (bold)
                st.subheader("Below are the list of Hospitals based on your city:")
                st.markdown(bot_response)  # Using st.markdown instead of st.write to render Markdown

                st.subheader("Source:")
                st.write(source)

                # Add the detailed information about the health schemes based on the city


    else:
        st.write("Ask a Question related to Government Health Scheme")


# Run the Streamlit app
if __name__ == "__main__":
    streamlit_app()
