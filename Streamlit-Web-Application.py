#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
st.set_page_config(layout="wide") 

st.markdown("<h1 style='text-align: center; color: white;'>LS Direct</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: white;'> Monthly Dashboard - 06/2023 </h2>", unsafe_allow_html=True)


# Import Libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


##  <font color='darkblue'> Part 2. Load Dataset </font><a id='load'></a>

## **Assumption:** The datasets remain consistent each time we receive them.

# Add file uploader widgets for products, stores, and transactions
st.sidebar.title("File Uploads")
uploaded_products = st.sidebar.file_uploader(
    "Upload Products CSV", type=["csv"], key="products"
)
uploaded_stores = st.sidebar.file_uploader("Upload Stores CSV", type=["csv"], key="stores")

uploaded_transactions = st.sidebar.file_uploader(
    "Upload Transactions CSV", type=["csv"], key="transactions"
)

if uploaded_products is not None:
    products = pd.read_csv(uploaded_products)

    if uploaded_stores is not None:
        stores = pd.read_csv(uploaded_stores)

        if uploaded_transactions is not None:
            # Read the uploaded CSV file into a DataFrame
            transactions = pd.read_csv(uploaded_transactions)
    
            # Load data
            # products = pd.read_csv("D:/Data/LS Direct/products.csv")
            # stores = pd.read_csv("D:/Data/LS Direct/stores.csv")
            # transactions = pd.read_csv("D:/Data/LS Direct/transactions.csv")

            # Loop through each dataset and apply the glimpse function
            # for name, dataset in zip(["Products", "Stores", "Transactions"], datasets):
            #   print(f"Summary for {name} dataset:")
            #   glimpse(dataset)
            #   print("\n" + "=" * 50 + "\n")

            ##  <font color='darkblue'> Part 3. Clean Dataset </font><a id='clean'></a>

            # Change the data format#:
            ##Clean and Change data type of Price in *transactions* and *products* tables into float
            ##["PurchaseDate"] is changed into data type format

            # Change the data type of Price
            def convert_price(price_str):
                try:
                    return float(price_str.strip("$").replace(",", ""))
                except ValueError:
                    return None

            # Convert 'Price' columns in both tables to float
            transactions["Price"] = transactions["Price"].apply(convert_price)
            # products["Price"] = products["Price"].apply(convert_price)

            # Print the updated data types
            # print(transactions.dtypes)
            # print(products.dtypes)

            transactions["PurchaseDate"] = pd.to_datetime(transactions["PurchaseDate"])

            transactions2 = transactions.copy()


            # Filter transactions based on date range
            st.sidebar.title("Time Filter")
            start_date = st.sidebar.date_input("Start Date", min(transactions2["PurchaseDate"]))
            end_date = st.sidebar.date_input("End Date", max(transactions2["PurchaseDate"]))
            filtered_transactions = transactions2[
                (transactions2["PurchaseDate"] >= pd.to_datetime(start_date))
                & (transactions2["PurchaseDate"] <= pd.to_datetime(end_date))
            ]

            # Calculate KPIs
            total_customers = filtered_transactions["CustomerID"].count()
            
            
            # Group by ProductID and count the number of occurrences
            product_counts = (
                filtered_transactions.groupby("ProductID").size().reset_index(name="TransactionCount")
            )

            # Join with the products table to get the corresponding categories
            product_counts_with_categories = pd.merge(product_counts, products, on="ProductID")

            # Find the category with the highest total transactions
            top_category_name = (
                product_counts_with_categories.groupby("ProductCategory")["TransactionCount"]
                .sum()
                .idxmax()
            )
            top_category_transaction = product_counts_with_categories.loc[product_counts_with_categories["ProductCategory"] == top_category_name, "TransactionCount"].values[0]
            

            top_product_name = product_counts_with_categories.groupby("ProductName")["TransactionCount"].sum().idxmax()
            top_product_transaction = product_counts_with_categories.loc[product_counts_with_categories["ProductName"] == top_product_name, "TransactionCount"].values[0]
            

            new_customers = 28000
            

            # Create KPI cards using Plotly
            fig_total_customers = go.Figure(go.Indicator(
                value=total_customers,
                delta={'reference': 200000},
                mode="number+delta",
                title={"text": "Total Customers"},
                gauge={
                    "shape": "bullet",
                    "axis": {"range": [None, 300000]},
                    "threshold": {
                        "line": {"color": "red", "width": 2},
                        "thickness": 0.75,
                        "value": 270000,
                    },
                }
            ))

            #########
            fig_new_customers = go.Figure(go.Indicator(
                value=new_customers,
                delta={'reference': 50000},
                mode="number+delta",
                title={"text": "New Customers"},
                gauge={
                    "shape": "bullet",
                    "axis": {"range": [None, 60000]},
                    "threshold": {
                        "line": {"color": "red", "width": 2},
                        "thickness": 0.75,
                        "value": 45000,
                    },
                }
            ))
            #########
            fig_sofa = go.Figure(go.Indicator(
                mode="number",
                title={"text": f"{top_product_name} (Top Transactions)"},                
                value= top_product_transaction
                ))
            #########
            fig_cat =  go.Figure(go.Indicator(
                mode="number",
                title={"text": f"{top_category_name} (Top Transactions)"},                
                value= top_category_transaction
                ))

            # Streamlit layout for displaying KPI cards side by side
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.plotly_chart(fig_total_customers, use_container_width=True)

            with col2:
                st.plotly_chart(fig_new_customers, use_container_width=True)
            
            with col3:
                st.plotly_chart(fig_sofa, use_container_width=True)
                
            with col4:
                st.plotly_chart(fig_cat, use_container_width=True)
            
            # Group and aggregate data for daily customers
            daily_customers = (
                filtered_transactions.groupby("PurchaseDate")["CustomerID"]
                .count()
                .reset_index()
            )
      ####################################################################################################################
    
            # Create a container for the layout
            col1, col2 = st.columns([2,1])

            with col1:
                fig1 = px.area(
                    daily_customers,
                    x="PurchaseDate",
                    y="CustomerID",
                    title="<b>Total Customers by Days</b>",
                    labels={"CustomerID": "<b>Total Customers</b>"},
                    template="plotly_dark",
                )

                fig1.update_traces(
                    mode="lines+markers",
                    marker=dict(
                        symbol="circle",
                        size=8,
                        color="#A0D1FF",
                        line=dict(width=2, color="white"),
                    ),
                    line=dict(color="#A0D1FF", width=2),
                    hovertemplate="<b>Date</b>: %{x}<br><b>Total Customers</b>: %{y}<extra></extra>",
                )

                fig1.update_xaxes(title_text="<b>Date</b>")
                fig1.update_yaxes(title_text="<b>Total Customers</b>")

                fig1.update_layout(width=1500)  # Adjust the width of the chart
                st.plotly_chart(fig1, use_container_width=True)

            ###################
            with col2:
                       # Calculate the growth rate
                daily_customers["Growth Rate"] = daily_customers["CustomerID"].pct_change() * 100
                daily_customers["Growth Rate"] = round(daily_customers["Growth Rate"], 2)
                      #plot the table
                def get_cell_color(value):
                    if value < 0:
                        return "#EFB5B9"
                    else:
                        return "#043B7E"
                 
                fig2 = go.Figure(
                    data=[
                        go.Table(
                            header=dict(
                                values=["<b>" + col + "</b>" if col != "CustomerID" else "<b>Total Customers</b>" for col in daily_customers.columns],  # Change the title here
                                fill_color="#043B7E", # change the background color of data
                                font=dict(color="white"),
                                align="center",
                                height=40,
                            ),
                            cells=dict(
                                values=[
                                    daily_customers.PurchaseDate.dt.strftime("%Y-%m-%d"),
                                    daily_customers.CustomerID,
                                    daily_customers["Growth Rate"].round(2),
                                ],
                                fill=dict(
                                    color=[
                                        [get_cell_color(val) for val in daily_customers["Growth Rate"]]
                                    ]
                                ),
                                font=dict(color="white"),
                                align="center",
                                height=30,
                            ),
                        )
                    ]
                )
                st.plotly_chart(fig2, use_container_width=True) 
   ############################################################################################################################             
                
            # Weekly customers
            weekday_customers_filtered = (
                filtered_transactions.groupby(
                    filtered_transactions["PurchaseDate"].dt.dayofweek + 1
                )["CustomerID"]
                .count()
                .reset_index()
            )
            col1, col2 = st.columns([1,2])
            with col1:
                  # Add sidebar filters
                selected_state = st.sidebar.selectbox("Select State", stores["StoreState"].unique())
                selected_city = st.sidebar.selectbox("Select City", stores[stores["StoreState"] == selected_state]["StoreCity"].unique())

                # Merge transactions and stores data
                transactions_with_state_product = pd.merge(filtered_transactions, stores, on="StoreID")
                transactions_with_state_product = pd.merge(transactions_with_state_product, products, on="ProductID")
                transactions_with_stores = transactions_with_state_product.copy()

                # Apply selected filters
                transactions_with_stores = transactions_with_stores[
                    (transactions_with_stores["StoreState"] == selected_state) &
                    (transactions_with_stores["StoreCity"] == selected_city)
                ]

                transactions_with_category = transactions_with_stores.copy()

                # Calculate purchase frequency by category
                category_purchase_frequency = (
                    transactions_with_category["ProductCategory"].value_counts(normalize=True) * 100
                )

                custom_colors = ["white", "lightgrey", "lightblue", "lightcoral"]

                # Create the pie chart using Plotly Express
                fig4 = px.pie(
                    values=category_purchase_frequency.values,
                    names=category_purchase_frequency.index,
                    title=f"Percentage of Purchase Frequency by Category in {selected_city}, {selected_state}",
                    color_discrete_sequence=custom_colors,
                    template="plotly_dark",
                )

                st.plotly_chart(fig4, use_container_width=True)
                
                #####################

            with col2: 
                weekday_order = [1, 2, 3, 4, 5, 6, 7]  # Sunday to Saturday order

                weekday_customers_filtered = weekday_customers_filtered.sort_values(
                    "PurchaseDate"
                )

                fig3 = px.area(
                    weekday_customers_filtered,
                    x="PurchaseDate",
                    y="CustomerID",
                    title="<b>Total Customers by Weekdays</b>",
                    labels={"CustomerID": "<b>Total Customers</b>"},
                    template="plotly_dark",
                )

                fig3.update_traces(
                    mode="lines+markers",
                    marker=dict(
                        symbol="circle",
                        size=8,
                        color="#A0D1FF",
                        line=dict(width=2, color="white"),
                    ),
                    line=dict(color="#A0D1FF", width=2),
                    hovertemplate="<b>Weekday</b>: %{x}<br><b>Total Customers</b>: %{y}<extra></extra>",
                )

                fig3.update_xaxes(
                    title_text="<b>Weekday</b>",
                    tickvals=weekday_order,
                    ticktext=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                )
                fig3.update_yaxes(title_text="<b>Total Customers</b>")

                #fig3.update_layout(width=500)  # Adjust the width of the chart
                st.plotly_chart(fig3, use_container_width=True) 
                
          ####################################################################################################################  
            col1, col2 = st.columns(2) 
            with col1:
            # Join transactions with stores and products to get state information (same as before)
                state_customer_count = (
                    transactions_with_state_product.groupby("StoreState")["CustomerID"]
                    .nunique()
                    .reset_index()
                )

                # Select the top 10 states based on customer counts
                top_states = state_customer_count.sort_values(by="CustomerID", ascending=False).head(10)

                # Create the Plotly bar chart with divided categories
                fig8 = px.bar(
                    top_states,
                    x="CustomerID",
                    y="StoreState",
                    title="Top 10 States with Highest Customer Count (Overall)",
                    labels={"CustomerID": "Customer Count", "StoreState": "State"},
                    template="plotly_dark",
                    orientation="h",
                )
                # LS Direct color
                fig8.update_traces(marker_color="lightblue")

                fig8.update_layout(
                    xaxis_title="<b>Customer Count</b>", yaxis_title="<b>State</b>",
                )
                st.plotly_chart(fig8, use_container_width=True)
              ###########
                
            with col2: 
                transactions_with_stores = transactions_with_state_product.copy()
                transactions_with_stores["StoreID"] = transactions_with_stores["StoreID"].astype(str)

                # Group by store and count unique customers
                store_customer_count = (
                    transactions_with_stores.groupby("StoreID")["CustomerID"].nunique().reset_index()
                )

                # Select the top 10 stores based on customer counts
                top_stores = store_customer_count.sort_values(by="CustomerID", ascending=False).head(10)

                # Create the Plotly bar chart
                fig9 = px.bar(
                    top_stores,
                    x="CustomerID",
                    y="StoreID",
                    title="Top 10 Stores with Highest Customer Count (Overall)",
                    labels={"CustomerID": "Customer Count", "StoreID": "Store"},
                    template="plotly_dark",
                    orientation="h",  # Horizontal bar chart
                )

                # Set LS Direct Colors
                fig9.update_traces(marker_color="lightblue")

                fig9.update_layout(
                    xaxis_title="<b>Customer Count</b>", yaxis_title="<b>Store</b>",
                )

                st.plotly_chart(fig9, use_container_width=True)
                
               ############################################################################################################## 
            col1, col2 = st.columns(2)
            with col1:
                transactions_with_state = pd.merge(filtered_transactions, stores, on="StoreID")

                # Group by day and state, then count unique customers
                transactions_with_state["Day"] = transactions_with_state["PurchaseDate"].dt.to_period(
                    "D"
                )
                state_customer_count_by_day = (
                    transactions_with_state.groupby(["Day", "StoreState"])["CustomerID"]
                    .nunique()
                    .reset_index()
                )

                # Get top 5 states with highest customer count for each day
                top_states_by_day = (
                    state_customer_count_by_day.groupby("Day")
                    .apply(lambda x: x.nlargest(5, "CustomerID"))
                    .reset_index(drop=True)
                )

                # Convert Period objects to strings for x-axis labels
                top_states_by_day["Day"] = top_states_by_day["Day"].dt.to_timestamp()

                top_states_by_day = top_states_by_day[top_states_by_day["StoreState"] != "MD"]
                # Define custom colors for lines
                line_colors = ["white", "lightgrey", "lightpink", "blue", "yellow"]

                fig5 = px.line(
                    top_states_by_day,
                    x="Day",
                    y="CustomerID",
                    color="StoreState",
                    title="Top 5 States with Highest Customer Count over Time",
                    labels={"Day": "Day", "CustomerID": "Customer Count", "StoreState": "State"},
                    template="plotly_dark",
                )

                for idx, state in enumerate(fig5.data):
                    fig5.data[idx].line.color = line_colors[idx % len(line_colors)]

                fig5.update_traces(
                    mode="lines+markers",  # Add markers to lines
                    marker=dict(size=8),
                    hovertemplate="<b>Day</b>: %{x}<br><b>Customer Count</b>: %{y}<extra></extra>",
                )

                fig5.update_xaxes(title_text="<b>Day</b>")
                fig5.update_yaxes(title_text="<b>Customer Count</b>")

                st.plotly_chart(fig5, use_container_width=True)
        
               ###################
            with col2: 
                
                transactions_with_store = transactions_with_state.copy()
                # Group by day and store, then count customers
                transactions_with_store["Day"] = transactions_with_store["PurchaseDate"].dt.to_period(
                    "D"
                )
                store_customer_count_by_day = (
                    transactions_with_store.groupby(["Day", "StoreID"])["CustomerID"]
                    .count()
                    .reset_index()
                )

                # Get top 5 stores with highest customer count for each day
                top_stores_by_day = (
                    store_customer_count_by_day.groupby("Day")
                    .apply(lambda x: x.nlargest(5, "CustomerID"))
                    .reset_index(drop=True)
                )

                # Convert Period objects to strings for x-axis labels
                top_stores_by_day["Day"] = top_stores_by_day["Day"].dt.to_timestamp()

                # Filter to include only the top 5 stores
                top_stores_by_day = top_stores_by_day[
                    top_stores_by_day["StoreID"].isin([123, 102, 115, 146, 127])
                ]

                # Define custom colors for lines
                line_colors = ["white", "lightgrey", "lightpink", "blue", "yellow"]

                fig6 = px.line(
                    top_stores_by_day,
                    x="Day",
                    y="CustomerID",
                    color="StoreID",
                    title="Top 5 Stores with Highest Customer Count over Time",
                    labels={"Day": "Day", "CustomerID": "Customer Count", "StoreID": "Store"},
                    template="plotly_dark",
                )

                for idx, store in enumerate(fig6.data):
                    fig6.data[idx].line.color = line_colors[idx % len(line_colors)]

                fig6.update_traces(
                    mode="lines+markers",  # Add markers to lines
                    marker=dict(size=8),
                    hovertemplate="<b>Day</b>: %{x}<br><b>Customer Count</b>: %{y}<extra></extra>",
                )

                fig6.update_xaxes(title_text="<b>Day</b>")
                fig6.update_yaxes(title_text="<b>Customer Count</b>")

                st.plotly_chart(fig6, use_container_width=True)
            


# In[ ]:




