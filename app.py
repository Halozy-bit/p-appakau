from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import io
import base64
from datetime import datetime, timedelta
import numpy as np
import seaborn as sns

app = Flask(__name__)

# Dummy data
users = pd.DataFrame({
    'nama': ['Admin', 'Owner', 'John', 'Doe', 'Poll'],
    'telepon': ['081234567890', '081298765432', '081345678901', '081987654321', '081987654321'],
    'jabatan': ['admin', 'owner', 'sales', 'produksi', 'sales'],
    'area': [None, None, 'Jakarta', None, 'Surabaya']  # Area untuk sales
})

products = pd.DataFrame({
    'nama_produk': ['Produk A', 'Produk B', 'Produk C'],
    'merk': ['Merk X', 'Merk Y', 'Merk Z'],
    'ukuran': ['pcs', 'dus', 'slop']
})
distributed_items = []

# Simulasi data produksi
productions = pd.DataFrame(columns=['tanggal', 'nama_produk', 'merk', 'ukuran', 'jumlah', 'harga'])

# Simulasi gudang
warehouse = pd.DataFrame(columns=['nama_produk', 'merk', 'ukuran', 'jumlah'])

# Simulasi data sales (stok di sales)
sales_stocks = pd.DataFrame(columns=['sales', 'area', 'nama_produk', 'merk', 'ukuran', 'jumlah'])

# Simulasi penjualan
sales_data = pd.DataFrame(columns=['tanggal', 'nama_pembeli', 'telepon_pembeli', 'nama_produk', 'merk', 'ukuran', 'jumlah', 'harga', 'sales', 'area'])

# Master Data
@app.route('/master_data')
def master_data():
    return render_template('master_data.html', users=users, products=products)


# Produksi
@app.route('/produksi', methods=['GET', 'POST'])
def produksi():
    global productions, warehouse
    if request.method == 'POST':
        # Ambil data dari form
        tanggal = request.form['tanggal']
        produk_info = request.form['produk'].split('|')
        nama_produk = produk_info[0]
        merk = produk_info[1]
        ukuran = produk_info[2]
        jumlah = int(request.form['jumlah'])
        harga = float(request.form['harga'])

        # Simpan data produksi
        new_production = {
            'tanggal': tanggal,
            'nama_produk': nama_produk,
            'merk': merk,
            'ukuran': ukuran,
            'jumlah': jumlah,
            'harga': harga
        }
        productions = productions._append(new_production, ignore_index=True)

        # Update gudang
        existing_stock = warehouse[
            (warehouse['nama_produk'] == nama_produk) & 
            (warehouse['merk'] == merk) & 
            (warehouse['ukuran'] == ukuran)
        ]

        if not existing_stock.empty:
            warehouse.loc[
                (warehouse['nama_produk'] == nama_produk) & 
                (warehouse['merk'] == merk) & 
                (warehouse['ukuran'] == ukuran), 'jumlah'
            ] += jumlah
        else:
            new_warehouse_entry = {
                'nama_produk': nama_produk,
                'merk': merk,
                'ukuran': ukuran,
                'jumlah': jumlah
            }
            warehouse = warehouse._append(new_warehouse_entry, ignore_index=True)

        return redirect('/produksi')

    return render_template('produksi.html', products=products, productions=productions)

# Gudang
@app.route('/gudang')
def gudang():
    return render_template('gudang.html', warehouse=warehouse)


# Distribusi
@app.route('/distribusi', methods=['GET', 'POST'])
def distribusi():
    global warehouse, sales_stocks, distributed_items
    if request.method == 'POST':
        sales_name = request.form['sales_name']
        produk_info = request.form['nama_produk'].split('|')
        nama_produk = produk_info[0]
        merk = produk_info[1]
        ukuran = produk_info[2]
        jumlah = int(request.form['jumlah'])

        warehouse_index = warehouse[
            (warehouse['nama_produk'] == nama_produk) & 
            (warehouse['merk'] == merk) & 
            (warehouse['ukuran'] == ukuran)
        ].index

        if not warehouse_index.empty:
            if warehouse.loc[warehouse_index, 'jumlah'].values[0] >= jumlah:
                warehouse.loc[warehouse_index, 'jumlah'] -= jumlah
                
                area = users.loc[users['nama'] == sales_name, 'area'].values[0]

                sales_index = sales_stocks[
                    (sales_stocks['sales'] == sales_name) & 
                    (sales_stocks['area'] == area) & 
                    (sales_stocks['nama_produk'] == nama_produk) & 
                    (sales_stocks['merk'] == merk) & 
                    (sales_stocks['ukuran'] == ukuran)
                ].index

                if not sales_index.empty:
                    sales_stocks.loc[sales_index, 'jumlah'] += jumlah
                else:
                    new_sales_stock = {
                        'sales': sales_name,
                        'area': area,
                        'nama_produk': nama_produk,
                        'merk': merk,
                        'ukuran': ukuran,
                        'jumlah': jumlah
                    }
                    sales_stocks = sales_stocks._append(new_sales_stock, ignore_index=True)

                distributed_items.append({
                    'sales': sales_name,
                    'area': area,
                    'nama_produk': nama_produk,
                    'merk': merk,
                    'ukuran': ukuran,
                    'jumlah': jumlah
                })

                return redirect(url_for('distribusi'))
            else:
                return "Stok di gudang tidak mencukupi.", 400
        else:
            return "Produk tidak ditemukan di gudang.", 400

    sales_users = users[users['jabatan'] == 'sales']
    
    return render_template('distribusi.html', sales_users=sales_users, warehouse=warehouse, distributed_items=distributed_items, sales_stocks=sales_stocks)

# Penjualan
@app.route('/penjualan', methods=['GET', 'POST'])
def penjualan():
    global sales_data, sales_stocks
    if request.method == 'POST':
        tanggal = request.form['tanggal']
        nama_pembeli = request.form['nama_pembeli']
        telepon_pembeli = request.form['telepon_pembeli']
        nama_produk = request.form['nama_produk']
        merk = request.form['merk']
        ukuran = request.form['ukuran']
        jumlah = int(request.form['jumlah'])
        harga = float(request.form['harga'])
        sales_name = request.form['sales_name']  # Ambil nama sales dari form

        # Simpan data penjualan
        new_sale = {
            'tanggal': tanggal,
            'nama_pembeli': nama_pembeli,
            'telepon_pembeli': telepon_pembeli,
            'nama_produk': nama_produk,
            'merk': merk,
            'ukuran': ukuran,
            'jumlah': jumlah,
            'harga': harga,
            'sales_name': sales_name  # Tambahkan nama sales ke data penjualan
        }
        sales_data = sales_data._append(new_sale, ignore_index=True)

        # Kurangi stok sales berdasarkan sales_name
        sales_stock_index = sales_stocks[
            (sales_stocks['nama_produk'] == nama_produk) & 
            (sales_stocks['merk'] == merk) & 
            (sales_stocks['ukuran'] == ukuran) & 
            (sales_stocks['sales'] == sales_name)  # Pastikan sales sesuai
        ].index

        if not sales_stock_index.empty:
            current_stock = sales_stocks.loc[sales_stock_index, 'jumlah'].values[0]
            if current_stock >= jumlah:
                sales_stocks.loc[sales_stock_index, 'jumlah'] -= jumlah
            else:
                return "Stok penjualan tidak mencukupi.", 400

        return redirect(url_for('penjualan'))

    # Ambil daftar sales dan stok yang tersedia
    sales_names = sales_stocks['sales'].unique()  # Daftar nama sales
    available_products = sales_stocks[['nama_produk', 'merk', 'ukuran', 'jumlah']].to_dict('records')  # Stok yang tersedia

    return render_template('penjualan.html',available_products=available_products, sales_stocks=sales_stocks, sales_names=sales_names, sales_data=sales_data)

@app.route('/')
def home():
    # Periksa apakah sales_data atau warehouse tidak kosong
    if sales_data.empty:
        total_revenue = 0
    else:
        # Calculate total sales revenue
        total_revenue = (sales_data['jumlah'] * sales_data['harga']).sum()

    if warehouse.empty:
        warehouse_stock = []
    else:
        # Prepare stock information
        warehouse_stock = warehouse.groupby(['nama_produk']).sum().reset_index()

    if sales_stocks.empty:
        sales_stock = []
    else:
        sales_stock = sales_stocks.groupby(['nama_produk']).sum().reset_index()
    
    # Prepare data for the chart
    sales_summary = sales_data.groupby('tanggal').agg({'jumlah': 'sum', 'harga': 'sum'}).reset_index()
    sales_summary['total_revenue'] = sales_summary['jumlah'] * sales_summary['harga']
    
    # Convert to JSON for use in JavaScript
    sales_summary_json = sales_summary.to_dict(orient='records')

    return render_template('index.html', sales_summary=sales_summary_json,
                           total_revenue=total_revenue,
                           warehouse_stock=warehouse_stock.to_dict(orient='records') if not warehouse.empty else [],
                           sales_stock=sales_stock.to_dict(orient='records') if not sales_stocks.empty else [])

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
