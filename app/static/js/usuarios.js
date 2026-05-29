let usuariosList = [];
let rolesList = [];

document.addEventListener('DOMContentLoaded', () => {
    cargarDatos();

    document.getElementById('searchInput').addEventListener('input', renderizarTabla);
    document.getElementById('rolFilter').addEventListener('change', renderizarTabla);

    document.getElementById('btnNuevoUsuario').addEventListener('click', () => {
        document.getElementById('modalUsuarioTitle').textContent = 'Nuevo Usuario';
        document.getElementById('formUsuario').reset();
        document.getElementById('usr_id').value = '';
        document.getElementById('usr_password').required = true;
        document.getElementById('modalUsuario').style.display = 'flex';
    });

    document.getElementById('btnCerrarModalUsuario').addEventListener('click', () => {
        document.getElementById('modalUsuario').style.display = 'none';
    });

    document.getElementById('formUsuario').addEventListener('submit', guardarUsuario);
});

async function cargarDatos() {
    try {
        const [uRes, rRes] = await Promise.all([
            fetch('/usuarios/api/list'),
            fetch('/usuarios/api/roles')
        ]);
        usuariosList = await uRes.json();
        rolesList = await rRes.json();

        const rolFilter = document.getElementById('rolFilter');
        const usrRol = document.getElementById('usr_rol');
        
        rolesList.forEach(r => {
            rolFilter.innerHTML += `<option value="${r.id_rol}">${r.nombre}</option>`;
            usrRol.innerHTML += `<option value="${r.id_rol}">${r.nombre}</option>`;
        });

        renderizarTabla();
    } catch (error) {
        console.error("Error al cargar usuarios", error);
    }
}

function renderizarTabla() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const rolFilter = document.getElementById('rolFilter').value;
    const tbody = document.querySelector('#tablaUsuarios tbody');
    tbody.innerHTML = '';

    const filtrados = usuariosList.filter(u => {
        if (u.estado !== 'activo') return false;
        if (rolFilter && u.id_rol.toString() !== rolFilter) return false;
        const q = query;
        return (u.nombre_completo && u.nombre_completo.toLowerCase().includes(q)) ||
               (u.usuario && u.usuario.toLowerCase().includes(q));
    });

    filtrados.forEach(u => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${u.usuario}</td>
            <td>${u.nombre_completo || '-'}</td>
            <td>${u.rol_nombre}</td>
            <td>${u.correo || '-'}</td>
            <td><span class="badge badge-active">Activo</span></td>
            <td>
                <button class="btn-icon" onclick="editarUsuario(${u.id_usuario})">✏️</button>
                <button class="btn-icon delete" onclick="eliminarUsuario(${u.id_usuario})">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function editarUsuario(id) {
    const u = usuariosList.find(x => x.id_usuario === id);
    if (!u) return;

    document.getElementById('modalUsuarioTitle').textContent = 'Editar Usuario';
    document.getElementById('usr_id').value = u.id_usuario;
    document.getElementById('usr_nombre').value = u.nombre_completo || '';
    document.getElementById('usr_usuario').value = u.usuario || '';
    document.getElementById('usr_correo').value = u.correo || '';
    document.getElementById('usr_telefono').value = u.telefono || '';
    document.getElementById('usr_rol').value = u.id_rol || '';
    
    document.getElementById('usr_password').required = false; // Optional on edit
    document.getElementById('usr_password').value = ''; 

    document.getElementById('modalUsuario').style.display = 'flex';
}

async function guardarUsuario(e) {
    e.preventDefault();
    const id = document.getElementById('usr_id').value;
    const isEdit = id !== '';
    const url = isEdit ? `/usuarios/api/editar/${id}` : '/usuarios/api/crear';
    const method = isEdit ? 'PUT' : 'POST';

    const payload = {
        nombre_completo: document.getElementById('usr_nombre').value,
        usuario: document.getElementById('usr_usuario').value,
        correo: document.getElementById('usr_correo').value,
        telefono: document.getElementById('usr_telefono').value,
        id_rol: document.getElementById('usr_rol').value
    };

    if (!isEdit) {
        payload.password = document.getElementById('usr_password').value;
    }

    try {
        const res = await fetch(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (result.success) {
            document.getElementById('modalUsuario').style.display = 'none';
            // Reload user list without reloading roles
            const uRes = await fetch('/usuarios/api/list');
            usuariosList = await uRes.json();
            renderizarTabla();
        } else {
            showCustomAlert('Error: ' + result.message);
        }
    } catch (error) {
        console.error(error);
        showCustomAlert('Error en el servidor');
    }
}

async function eliminarUsuario(id) {
    if (!confirm('¿Está seguro de eliminar este usuario?')) return;
    try {
        const res = await fetch(`/usuarios/api/eliminar/${id}`, { method: 'DELETE' });
        const result = await res.json();
        if (result.success) {
            const uRes = await fetch('/usuarios/api/list');
            usuariosList = await uRes.json();
            renderizarTabla();
        } else {
            showCustomAlert('Error: ' + result.message);
        }
    } catch (error) {
        console.error(error);
        showCustomAlert('Error en el servidor');
    }
}
