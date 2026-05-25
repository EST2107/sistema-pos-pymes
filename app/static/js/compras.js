let comprasList = [];
let proveedoresList = [];
let productosList = [];
let itemsNuevaCompra = [];

document.addEventListener('DOMContentLoaded', () => {
    cargarDatosIniciales();
    
    document.getElementById('searchInput').addEventListener('input', renderizarTablaCompras);
    
    // Modal Nueva Compra
    document.getElementById('btnNuevaCompra').addEventListener('click', abrirModalCompra);
    document.getElementById('btnCerrarModalCompra').addEventListener('click', cerrarModalCompra);
    document.getElementById('btnAgregarItem').addEventListener('click', agregarItem);
    document.getElementById('btnGuardarCompra').addEventListener('click', registrarCompra);
    
    // Modal Detalles
    document.getElementById('btnCerrarDetalles').addEventListener('click', () => {
        document.getElementById('modalDetalles').style.display = 'none';
    });
});

async function cargarDatosIniciales() {
    try {
        const [compRes, provRes, prodRes] = await Promise.all([
            fetch('/compras/api/list'),
            fetch('/proveedores/api/list'),
            fetch('/productos/api/list')
        ]);
        comprasList = await compRes.json();
        proveedoresList = await provRes.json();
        productosList = await prodRes.json();
        
        // Llenar selects
        const selectProv = document.getElementById('compra_proveedor');
        proveedoresList.forEach(p => {
            selectProv.innerHTML += `<option value="${p.id_proveedor}">${p.nombre}</option>`;
        });
        
        const selectProd = document.getElementById('compra_producto');
        productosList.forEach(p => {
            selectProd.innerHTML += `<option value="${p.id_producto}" data-costo="${p.costo || 0}">${p.nombre}</option>`;
        });
        
        // Autocompletar costo al elegir producto
        selectProd.addEventListener('change', (e) => {
            const opt = e.target.options[e.target.selectedIndex];
            if (opt.value) {
                document.getElementById('compra_costo').value = parseFloat(opt.dataset.costo || 0).toFixed(2);
            }
        });
        
        renderizarTablaCompras();
    } catch (e) {
        console.error("Error al cargar datos", e);
    }
}

function renderizarTablaCompras() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const tbody = document.querySelector('#tablaCompras tbody');
    tbody.innerHTML = '';

    const filtrados = comprasList.filter(c => 
        (c.numero_compra && c.numero_compra.toLowerCase().includes(query)) ||
        (c.proveedor_nombre && c.proveedor_nombre.toLowerCase().includes(query))
    );

    filtrados.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${c.numero_compra}</strong></td>
            <td>${c.fecha_compra}</td>
            <td>${c.proveedor_nombre}</td>
            <td><strong>C$ ${c.total.toFixed(2)}</strong></td>
            <td><span class="badge badge-active">${c.estado}</span></td>
            <td>
                <button class="btn-icon" title="Ver Detalles" onclick="verDetalles(${c.id_compra})">👁️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function abrirModalCompra() {
    itemsNuevaCompra = [];
    document.getElementById('compra_proveedor').value = '';
    document.getElementById('compra_producto').value = '';
    document.getElementById('compra_cantidad').value = '1';
    document.getElementById('compra_costo').value = '0';
    renderizarItemsNuevaCompra();
    document.getElementById('modalNuevaCompra').style.display = 'flex';
}

function cerrarModalCompra() {
    document.getElementById('modalNuevaCompra').style.display = 'none';
}

function agregarItem() {
    const id_prod = document.getElementById('compra_producto').value;
    const select = document.getElementById('compra_producto');
    const nombre = select.options[select.selectedIndex].text;
    const cant = parseFloat(document.getElementById('compra_cantidad').value);
    const costo = parseFloat(document.getElementById('compra_costo').value);
    
    if (!id_prod || isNaN(cant) || cant <= 0 || isNaN(costo) || costo < 0) {
        alert("Campos de producto inválidos");
        return;
    }
    
    // Check if exists
    const ex = itemsNuevaCompra.find(i => i.id_producto == id_prod);
    if (ex) {
        ex.cantidad += cant;
        // update costo? maybe average, but let's just keep latest
        ex.costo_unitario = costo; 
    } else {
        itemsNuevaCompra.push({
            id_producto: id_prod,
            nombre: nombre,
            cantidad: cant,
            costo_unitario: costo
        });
    }
    
    document.getElementById('compra_producto').value = '';
    document.getElementById('compra_cantidad').value = '1';
    document.getElementById('compra_costo').value = '0';
    renderizarItemsNuevaCompra();
}

function eliminarItem(idx) {
    itemsNuevaCompra.splice(idx, 1);
    renderizarItemsNuevaCompra();
}

function renderizarItemsNuevaCompra() {
    const tbody = document.querySelector('#tablaItemsCompra tbody');
    tbody.innerHTML = '';
    let total = 0;
    
    itemsNuevaCompra.forEach((it, idx) => {
        const sub = it.cantidad * it.costo_unitario;
        total += sub;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${it.nombre}</td>
            <td>${it.cantidad}</td>
            <td>C$ ${it.costo_unitario.toFixed(2)}</td>
            <td>C$ ${sub.toFixed(2)}</td>
            <td><button class="btn-icon delete" onclick="eliminarItem(${idx})">🗑️</button></td>
        `;
        tbody.appendChild(tr);
    });
    
    document.getElementById('compra_total').textContent = total.toFixed(2);
}

async function registrarCompra() {
    const id_prov = document.getElementById('compra_proveedor').value;
    if (!id_prov) {
        alert("Seleccione un proveedor");
        return;
    }
    if (itemsNuevaCompra.length === 0) {
        alert("Agregue al menos un producto");
        return;
    }
    
    const payload = {
        id_proveedor: id_prov,
        items: itemsNuevaCompra
    };
    
    const btn = document.getElementById('btnGuardarCompra');
    btn.disabled = true;
    
    try {
        const res = await fetch('/compras/api/crear', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const r = await res.json();
        if (r.success) {
            alert(r.message);
            cerrarModalCompra();
            // Reload list
            const compRes = await fetch('/compras/api/list');
            comprasList = await compRes.json();
            renderizarTablaCompras();
        } else {
            alert("Error: " + r.message);
        }
    } catch(e) {
        console.error(e);
        alert("Error de servidor");
    } finally {
        btn.disabled = false;
    }
}

async function verDetalles(id) {
    try {
        const res = await fetch(`/compras/api/detalle/${id}`);
        const r = await res.json();
        
        if (r.success) {
            const tbody = document.querySelector('#tablaDetallesView tbody');
            tbody.innerHTML = '';
            r.detalles.forEach(d => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${d.producto_nombre}</td>
                    <td>${d.cantidad}</td>
                    <td>C$ ${d.precio_unitario.toFixed(2)}</td>
                    <td>C$ ${d.subtotal.toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            });
            document.getElementById('modalDetalles').style.display = 'flex';
        } else {
            alert("Error: " + r.message);
        }
    } catch(e) {
        console.error(e);
    }
}
