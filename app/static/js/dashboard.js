document.addEventListener('DOMContentLoaded', () => {
    cargarChartsDashboard();
});

async function cargarChartsDashboard() {
    try {
        const res = await fetch('/api/dashboard_charts');
        const data = await res.json();
        
        if (data.ventas_7d) renderVentasDashboardChart(data.ventas_7d);
        if (data.ventas_cat) renderCategoriasChart(data.ventas_cat);
    } catch (error) {
        console.error("Error al cargar charts del dashboard:", error);
    }
}

function renderVentasDashboardChart(data) {
    const ctx = document.getElementById('ventasDashboardChart').getContext('2d');
    const labels = data.map(d => d.fecha);
    const totales = data.map(d => d.total);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas Diarias (C$)',
                data: totales,
                backgroundColor: '#0b5cff',
                borderRadius: 4
            }]
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

function renderCategoriasChart(data) {
    const ctx = document.getElementById('categoriasChart').getContext('2d');
    const labels = data.map(d => d.categoria);
    const totales = data.map(d => d.total);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: totales,
                backgroundColor: ['#0b5cff', '#16b978', '#ffb703', '#ef476f', '#9b59b6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
