# Import necessary packages
import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Input field for name on the smoothie order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake connection configuration
connection_parameters = {
    "account": "XJVZSFO-DEB92190",
    "user": "AMBERPERRINE",
    "password": "Rosko&Remi@1992",
    "role": "SYSADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SMOOTHIES",
    "schema": "PUBLIC"
}
session = Session.builder.configs(connection_parameters).create()

# Querying data from Snowflake
my_dataframe = session.table("fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Multiselect for smoothie ingredients
fruit_list = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Display selected fruits and their associated search values
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        if not pd_df[pd_df['FRUIT_NAME'] == fruit_chosen].empty:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write(f'The search value for {fruit_chosen} is {search_on}.')
            
            # Display nutrition info from Fruityvice
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
            if fruityvice_response.status_code == 200:
                fv_data = fruityvice_response.json()
                fv_df = pd.DataFrame([fv_data])  # Convert response to DataFrame
                st.dataframe(data=fv_df, use_container_width=True)
            else:
                st.write(f"Could not fetch data for {fruit_chosen}")
        else:
            st.write(f"Could not find search value for {fruit_chosen}")

# Insert data into Snowflake when the button is pressed
my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
"""

time_to_insert = st.button('Submit Order')

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

