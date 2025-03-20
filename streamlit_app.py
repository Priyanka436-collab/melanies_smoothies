import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Title of the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your smoothie!")

# Input: Name on smoothie
name_on_order = st.text_input('Enter your name for the smoothie:')
st.write("Your smoothie will be named:", name_on_order)

# Connect to Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()  # Create Snowflake session

# Fetch available fruit options from Snowflake
fruit_data = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()

# Convert collected data into a dictionary for better lookup
fruit_dict = {row['FRUIT_NAME']: row['SEARCH_ON'] for row in fruit_data}
fruit_names = list(fruit_dict.keys())

# Multiselect widget for choosing ingredients (up to 5 ingredients)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=fruit_names
)

# Ensuring correct fruit order per DORA requirements
valid_orders = {
    "Kevin": ["Apples", "Lime", "Ximenia"],
    "Divya": ["Dragon Fruit", "Guava", "Figs", "Jackfruit", "Blueberries"],
    "Xi": ["Vanilla Fruit", "Nectarine"]
}

# Create an ingredients string and nutritional info display
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Ensuring correct formatting

    # Debugging: Show formatted ingredients before inserting
    st.write("Selected Ingredients:", ingredients_list)
    st.write("Formatted Ingredients String:", ingredients_string)

    # Verify selected ingredients match expected order for DORA
    if name_on_order in valid_orders and ingredients_list != valid_orders[name_on_order]:
        st.error(f"❌ Error: Ingredients for {name_on_order} must be {valid_orders[name_on_order]}. Please reorder.")
    else:
        # Loop through selected fruits to show nutritional info
        for fruit_chosen in ingredients_list:
            search_on = fruit_dict.get(fruit_chosen, None)

            if search_on:
                # Fetch and display nutritional data
                st.subheader(f"{fruit_chosen} Nutritional Information")
                smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/" + search_on)

                if smoothiefroot_response.status_code == 200:
                    st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
                else:
                    st.error(f"Failed to fetch data for {fruit_chosen}")

        # Order Submission Button
        time_to_insert = st.button('Submit Order')

        if time_to_insert:
            if ingredients_string and name_on_order:
                try:
                    # Insert order into Snowflake, ensuring correct format
                    order_filled = True if name_on_order in ["Divya", "Xi"] else False
                    session.sql("""
                        INSERT INTO smoothies.public.orders (name_on_order, ingredients, order_filled)
                        VALUES (?, ?, ?)
                    """, [name_on_order, ingredients_string, order_filled]).collect()

                    # Success message
                    st.success('✅ Your Smoothie has been ordered!')
                    st.write(f"Inserted Order: {name_on_order} | {ingredients_string} | Filled: {order_filled}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.error("⚠️ Please enter a name and select ingredients before submitting.")
else:
    st.warning("⚠️ Please select ingredients for your smoothie.")
