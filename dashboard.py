import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

#membuat helper function()

# Load data CSV sebagai DataFrame
all_df = pd.read_csv("all_data.csv")

# Select only needed columns from all_df
alldf_small = all_df[['order_id', 'product_id', 'price', 'review_score', 'review_counts', 'customer_id_y', 
                      'order_purchase_timestamp_y', 'order_delivered_customer_date_y', 'delivery_time_y', 
                      'product_category_name_y', 'frequency_y']]

#monthly_daily_orders_df() digunakan untuk menyiapkan monthly_orders_df.
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='D', on='order_purchase_timestamp_y').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return monthly_orders_df

#create_sum_order_items_df() bertanggung jawab untuk menyiapkan sum_orders_items_df.
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_y").frequency_y.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

#create_preference_df(df) bertanggung jawab untuk menyiapkan preferensi_df
def create_preference_df(df):
    preferensi_df = df.groupby(["review_score", "product_category_name_y"]).review_counts.sum() \
                      .sort_values(ascending=False).reset_index()
    
    return preferensi_df

#kolom order_date menjadi kunci dalam pembuatan filter
datetime_columns = ["order_purchase_timestamp_y", "order_delivered_customer_date_y"]
alldf_small.sort_values(by="order_purchase_timestamp_y", inplace=True)
alldf_small.reset_index(inplace=True)

for column in datetime_columns:
    alldf_small[column] = pd.to_datetime(alldf_small[column])

#MEMBUAT KOMPONEN FILTER
min_date = alldf_small["order_purchase_timestamp_y"].min()
max_date = alldf_small["order_purchase_timestamp_y"].max()

with st.sidebar:
    # Menambahkan logo e-commerce
    st.image("https://thumbs.dreamstime.com/z/e-commerce-logo-design-template-white-background-e-commerce-logo-design-template-212252837.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = alldf_small[(alldf_small["order_purchase_timestamp_y"] >= str(start_date)) &  #start date & end date untuk memfilter all_df
                (alldf_small["order_purchase_timestamp_y"] <= str(end_date))]

#DataFrame yang telah difilter digunakan untuk membuat visualisasi data
monthly_orders_df = create_monthly_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)

#Melengkapi dashboard dengan berbagai visualisasi data
st.header('E-Commerce Dashboard :sparkles:')

#1. Menampilkan informasi total order dan revenue dalam bentuk metric() yang ditampilkan menggunakan layout columns()
st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

#2. Informasi tentang jumlah order harian ditampilkan dalam bentuk visualisasi data
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp_y"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

#Informasi tentang performa penjualan dari setiap produk.
#2. #menampilkan 5 produk paling laris dan paling sedikit terjual melalui sebuah visualisasi data
sum_order_items_df = all_df.groupby("product_category_name_y").frequency_y.sum().sort_values(ascending=False).reset_index()

#menghasilkan kanvas kosong dengan object berupa fig dan ax
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="frequency_y", y="product_category_name_y", data=sum_order_items_df.head(5), palette=colors, ax=ax[0],legend=False)
plt.show()
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="frequency_y", y="product_category_name_y", data=sum_order_items_df.sort_values(by="frequency_y", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=20)
plt.show()
st.pyplot(fig)

#3. #menampilkan top rekomendasi terbaik berdasarkan rating produk tertinggi melalui visualisasi data
preferensi_df = all_df.groupby(["review_score", "product_category_name_y"]).review_counts.sum().sort_values(ascending=False).reset_index()

#Kanvas kosong dengan object berupa fig dan ax
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

#mengisi kanvas sebelumnya dengan bar chart yang dibuat menggunakan library seaborn. ax[0] merupakan object untuk kanvas 

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="review_counts", y="product_category_name_y", data=preferensi_df.head(5), palette=colors, ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Recommendation Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

plt.suptitle("Best Recommendation Product by Review Score", fontsize=20)
plt.show()
st.pyplot(fig)

