import streamlit as st
import sqlite3
import pandas as pd
import re

# Initialize SQLite database
conn = sqlite3.connect('dealers.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS dealers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT NOT NULL,
        zip_code TEXT NOT NULL
    )
''')
conn.commit()

# Streamlit app
st.title("ServiceDealers")

# Search bar
search_query = st.text_input("Search by company, phone, email, or zip code...", "")
if search_query:
    terms = [f"%{term}%" for term in search_query.split() if term]
    if terms:
        conditions = " AND ".join(
            ["(company_name LIKE ? OR phone_number LIKE ? OR email LIKE ? OR zip_code LIKE ?)"] * len(terms)
        )
        params = [term for term in terms for _ in range(4)]
        c.execute(f"SELECT * FROM dealers WHERE {conditions}", params)
    else:
        c.execute("SELECT * FROM dealers")
else:
    c.execute("SELECT * FROM dealers")
dealers = c.fetchall()

# Display search results
if dealers:
    df = pd.DataFrame(
        dealers, columns=["ID", "Company Name", "Phone Number", "Email", "Zip Code"]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.write("No dealers found")

# Input form
with st.form(key="dealer_form"):
    st.subheader("Add Service Dealer")
    company_name = st.text_input("Company Name")
    phone_number = st.text_input("Phone Number (e.g., 5551234567)")
    email = st.text_input("Email")
    zip_code = st.text_input("Zip Code (e.g., 12345)")
    submit_button = st.form_submit_button(label="Add Dealer")

    if submit_button:
        # Validation
        if not all([company_name, phone_number, email, zip_code]):
            st.error("All fields are required")
        elif not re.match(r"^\d{10}$", phone_number.replace("-", "")):
            st.error("Phone number must be 10 digits")
        elif not re.match(r"^\S+@\S+\.\S+$", email):
            st.error("Invalid email format")
        elif not re.match(r"^\d{5}$", zip_code):
            st.error("Zip code must be 5 digits")
        else:
            try:
                c.execute(
                    "INSERT INTO dealers (company_name, phone_number, email, zip_code) VALUES (?, ?, ?, ?)",
                    (company_name, phone_number, email, zip_code)
                )
                conn.commit()
                st.success("Dealer added successfully")
            except Exception as e:
                st.error(f"Error adding dealer: {e}")

# Close connection
conn.close()