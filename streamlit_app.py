# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests 

# Write directly to the app
st.title(":cup_with_straw:Customize your smoothie :cup_with_straw:")
st.write("""Choose thee  fruit you want in your smoothie! """)

import streamlit as st
name_on_order = st.text_input('Name on smoothie:')
st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()


#session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'choose up to 5 ingredients:'
    , my_dataframe
)

if ingredients_list:
 ingredients_string = ''

 for fruit_chosen in ingredients_list:
     ingredients_string += fruit_chosen + ' '
     st.subheader(fruit_chosen + 'Nutritional information')
     smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
     sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)


 my_insert_stmt = """ insert into smoothies.public.orders(ingredients)
            values ('""" + ingredients_string + """','"""+name_on_order+""""')"""

 st.write(my_insert_stmt)
 st.stop()

 time_to_insert = st.button('Submit Order')
    
 if ingredients_string:
     session.sql(my_insert_stmt).collect()

     st.success('Your Smoothie is ordered!', icon="✅")











