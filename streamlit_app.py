import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Helpful links for references
helpful_links = [
    "https://docs.streamlit.io",
    "https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit",
    "https://github.com/Snowflake-Labs/snowflake-demo-streamlit",
    "https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake"
]

# Title of the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

# Short instructions
st.write("Choose the fruits you want in your smoothie!")

# Input: Name on smoothie
name_on_order = st.text_input('Name on smoothie:')
st.write("The name on your smoothie will be:", name_on_order)

# Ensure only one active session is created
cnx = st.connection("snowflake")
session = cnx.session()  # Create Snowflake session

# Retrieve available fruits from Snowflake
fruit_data = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()

# Convert collected data into a dictionary
fruit_dict = {row['FRUIT_NAME']: row['SEARCH_ON'] for row in fruit_data}
fruit_names = list(fruit_dict.keys())

# Multiselect widget for choosing ingredients (up to 5 ingredients)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_names  # Use properly collected fruit names
)

# Create an ingredients string and nutritional info display
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Fix: Use commas instead of spaces

    # Debugging: Show formatted ingredients before inserting
    st.write("Selected Ingredients:", ingredients_list)
    st.write("Formatted Ingredients String:", ingredients_string)

    # Loop over the selected fruits and display their nutritional info
    for fruit_chosen in ingredients_list:
        search_on = fruit_dict.get(fruit_chosen, None)

        if search_on:
            # Display nutritional information for each selected fruit
            st.subheader(f"{fruit_chosen} Nutritional Information")
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/" + search_on)

            if smoothiefroot_response.status_code == 200:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"Failed to fetch data for {fruit_chosen}")

    # Button for submitting the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if ingredients_string and name_on_order:
            try:
                # Insert the correct order into Snowflake using parameterized query
                session.sql("""
                    INSERT INTO smoothies.public.orders (name_on_order, ingredients, order_filled)
                    VALUES (?, ?, ?)
                """, [name_on_order, ingredients_string, False]).collect()
                
                # Success message
                st.success('Your Smoothie is ordered!', icon="✅")
                st.write(f"Inserted Order: {name_on_order} | {ingredients_string}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter a name and select ingredients before submitting.")
else:
    st.warning("Please select ingredients for your smoothie.")
