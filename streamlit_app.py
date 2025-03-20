import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Title of the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

# Instructions
st.write("Choose the fruits you want in your smoothie!")

# Input: Name on smoothie
name_on_order = st.text_input('Name on smoothie:')
st.write("The name on your smoothie will be:", name_on_order)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Create a fruit dictionary for easy lookup
fruit_dict = dict(zip(pd_df["FRUIT_NAME"], pd_df["SEARCH_ON"]))

# Multiselect widget for choosing ingredients (up to 5 ingredients)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=list(fruit_dict.keys())  # Extract fruit names from dictionary
)

# If ingredients are selected
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Join all selected fruits

    # Loop over the selected fruits and display their nutritional info
    for fruit_chosen in ingredients_list:
        if fruit_chosen in fruit_dict:
            search_on = fruit_dict[fruit_chosen]  # Correctly retrieve the search key
            
            st.subheader(f"{fruit_chosen} Nutritional Information")
            
            # Fetch nutritional data
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            
            if smoothiefroot_response.status_code == 200:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.error(f"Failed to fetch data for {fruit_chosen}")
        else:
            st.error(f"❌ Error: Could not find nutritional data for {fruit_chosen}.")

    # Prepare SQL insert statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (name_on_order, ingredients, order_filled)
    VALUES ('{name_on_order}', '{ingredients_string}', FALSE);
    """

    # Display the SQL Insert statement for debugging
    st.write("Prepared SQL Insert Statement:")
    st.code(my_insert_stmt)

    # Button for submitting the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if ingredients_string and name_on_order:
            try:
                # Execute the SQL query to insert the order into the Snowflake database
                result = session.sql(my_insert_stmt).collect()
                
                # Success message
                st.success('Your Smoothie is ordered!', icon="✅")
                st.write(f"SQL Query Result: {result}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please fill out both the name and select ingredients before submitting.")
else:
    st.warning("Please select ingredients for your smoothie.")
