import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Initialize Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Streamlit App Title
st.title(":cup_with_straw: Smoothie Order App :cup_with_straw:")

st.write("Follow the instructions to insert the required orders.")

# Retrieve available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowflake dataframe to pandas
pd_df = my_dataframe.to_pandas()





# Function to fetch and display nutritional information for selected fruits
def display_nutritional_info(fruit_list):
    for fruit_chosen in fruit_list:
        # Get the search term from the dataframe
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # Display nutritional information for each selected fruit
        st.subheader(f"{fruit_chosen} Nutritional Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

# Button to create required orders
if st.button("Insert Required Orders"):
    session.sql("TRUNCATE TABLE smoothies.public.orders;").collect()  # Clear existing orders
    
    # Insert each required order
    for order in orders:
        insert_order(order["name"], order["ingredients"], order["filled"])

    st.success("✅ All required orders have been inserted. Now run the DORA check!")

# Option to select ingredients and view nutritional information
ingredients_list = st.multiselect(
    'Choose fruits for your smoothie (Up to 5):',
    options=[fruit[0] for fruit in my_dataframe.collect()]  # Collecting fruit names from the Snowflake table
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Join all selected fruits with commas
    st.write(f"Selected fruits for your smoothie: {ingredients_string}")
    
    # Show nutritional info for each selected fruit
    display_nutritional_info(ingredients_list)

# Debugging option: View inserted orders
if st.button("Check Orders in Database"):
    df = session.sql("SELECT * FROM smoothies.public.orders ORDER BY name_on_order;").to_pandas()
    st.dataframe(df)

st.write("After inserting orders, go back to Snowflake and run the DORA validation query.")
