// static/script.js

const revenueData = {{ total_revenue | tojson }};
const warehouseData = {{ warehouse_stock | tojson }};
const salesStockData = {{ sales_stock | tojson }};

// Prepare data for the revenue chart
const revenueChartData = {
    labels: ['Total Revenue'],
    datasets: [{
        label: 'Revenue',
        data: [revenueData],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
    }]
};

// Prepare data for the warehouse stock chart
const warehouseChartData = {
    labels: warehouseData.map(item => item.nama_produk),
    datasets: [{
        label: 'Warehouse Stock',
        data: warehouseData.map(item => item.jumlah),
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 1
    }]
};

// Render revenue chart
const revenueCtx = document.getElementById('revenueChart').getContext('2d');
new Chart(revenueCtx, {
    type: 'bar', // You can change this to 'line', 'pie', etc.
    data: revenueChartData,
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Render warehouse stock chart
const warehouseCtx = document.getElementById('warehouseChart').getContext('2d');
new Chart(warehouseCtx, {
    type: 'bar',
    data: warehouseChartData,
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
