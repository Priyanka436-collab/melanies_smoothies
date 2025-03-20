import streamlit as st
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
session = cnx.session()


# Retrieve available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert Snowflake dataframe to pandas
pd_df = my_dataframe.to_pandas()

# Display available fruits as a dataframe
st.dataframe(pd_df)

# Multiselect widget for choosing ingredients (up to 5 ingredients)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=[fruit[0] for fruit in my_dataframe.collect()]  # Collecting fruit names from the Snowflake table
)

# Create an ingredients string and nutritional info display
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Join all selected fruits with spaces

    # Loop over the selected fruits and display their nutritional info
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display nutritional information for each selected fruit
        st.subheader(fruit_chosen + ' Nutritional information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

    # SQL insert statement to add the order to Snowflake
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    # Display the SQL Insert statement (optional for debugging)
    st.write("Prepared SQL Insert Statement:")
    st.write(my_insert_stmt)

    # Button for submitting the order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if ingredients_string and name_on_order:
            # Execute the SQL query to insert the order into the Snowflake database
            session.sql(my_insert_stmt).collect()  # Execute the SQL insert statement
            
            # Display a success message
            st.success('Your Smoothie is ordered!', icon="✅")
        else:
            st.error("Please fill out both the name and select ingredients before submitting.")
else:
    st.warning("Please select ingredients for your smoothie.")
