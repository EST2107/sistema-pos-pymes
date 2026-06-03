document.addEventListener('DOMContentLoaded', () => {
    cargarAuditoria();

    document.getElementById('searchInput').addEventListener('input', filtrarTabla);
    document.getElementById('moduloFilter').addEventListener('change', filtrarTabla);
});

let auditoriasGlobal = [];

async function cargarAuditoria() {
    try {
        const res = await fetch('/api/auditoria');
        if (!res.ok) throw new Error('Error al obtener datos');
        
        auditoriasGlobal = await res.json();
        renderTabla(auditoriasGlobal);
    } catch (e) {
        console.error(e);
        if (window.showCustomAlert) {
            window.showCustomAlert("Error al cargar auditoría", true);
        } else {
            alert("Error al cargar auditoría");
        }
    }
}

function renderTabla(datos) {
    const tbody = document.querySelector('#tablaAuditoria tbody');
    tbody.innerHTML = '';
    
    if (datos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron registros.</td></tr>';
        return;
    }
    
    datos.forEach(row => {
        const tr = document.createElement('tr');
        
        // Formatear detalles para vista previa
        let detallesBtn = '';
        if (row.detalles) {
            detallesBtn = `<button class="btn btn-sm btn-info" onclick='mostrarDetalles(${JSON.stringify(row.detalles).replace(/'/g, "&#39;")})'>Ver</button>`;
        } else {
            detallesBtn = '<span style="color: #999;">N/A</span>';
        }

        tr.innerHTML = `
            <td>${row.fecha}</td>
            <td><strong>${row.nombre_usuario}</strong></td>
            <td><span class="badge" style="background: #e0e0e0; color: #333; padding: 3px 8px; border-radius: 4px;">${row.modulo}</span></td>
            <td>${row.accion}</td>
            <td>${row.ip_address || 'N/A'}</td>
            <td>${detallesBtn}</td>
        `;
        tbody.appendChild(tr);
    });
}

function filtrarTabla() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    const modulo = document.getElementById('moduloFilter').value;
    
    const filtrados = auditoriasGlobal.filter(row => {
        const matchQ = row.nombre_usuario.toLowerCase().includes(q) || row.accion.toLowerCase().includes(q);
        const matchM = modulo === "" || row.modulo === modulo;
        return matchQ && matchM;
    });
    
    renderTabla(filtrados);
}

window.mostrarDetalles = function(detallesStr) {
    const modal = document.getElementById('modalAuditoria');
    const content = document.getElementById('auditoriaDetallesContent');
    
    try {
        // Intentar parsear como JSON para formatear bonito
        const parsed = JSON.parse(detallesStr);
        content.textContent = JSON.stringify(parsed, null, 2);
    } catch(e) {
        // Si no es JSON, mostrar como texto normal
        content.textContent = detallesStr;
    }
    
    modal.style.display = 'flex';
}
