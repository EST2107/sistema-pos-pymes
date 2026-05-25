document.addEventListener('DOMContentLoaded', () => {
    cargarReportes();
});

async function cargarReportes() {
    try {
        const [ventasRes, prodRes] = await Promise.all([
            fetch('/reportes/api/resumen_ventas'),
            fetch('/reportes/api/productos_top')
        ]);
        
        const ventasData = await ventasRes.json();
        const prodData = await prodRes.json();

        if (ventasData.success) renderVentasChart(ventasData.data);
        if (prodData.success) renderProductosChart(prodData.data);
        
    } catch (error) {
        console.error("Error al cargar reportes:", error);
    }
}

function renderVentasChart(data) {
    const ctx = document.getElementById('ventasChart').getContext('2d');
    
    const labels = data.map(d => d.fecha);
    const totales = data.map(d => d.total);
    const ganancias = data.map(d => d.ganancia);
    const gastos = data.map(d => d.gastos || 0);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Ventas (C$)',
                    data: totales,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Ganancia Estimada (C$)',
                    data: ganancias,
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Gastos (Compras C$)',
                    data: gastos,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderProductosChart(data) {
    const ctx = document.getElementById('productosChart').getContext('2d');
    
    const labels = data.map(d => d.producto);
    const cantidades = data.map(d => d.cantidad);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: cantidades,
                backgroundColor: [
                    '#3498db', '#e74c3c', '#f1c40f', '#2ecc71', '#9b59b6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
