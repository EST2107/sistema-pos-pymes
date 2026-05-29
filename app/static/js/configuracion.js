document.addEventListener('DOMContentLoaded', () => {
    // Theme logic
    const themeToggle = document.getElementById('themeToggle');
    
    // Check saved theme
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.checked = true;
    }

    themeToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            document.body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
        }
    });

    // Password Form
    document.getElementById('formPassword').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const actual = document.getElementById('pass_actual').value;
        const nueva = document.getElementById('pass_nueva').value;
        const confirmar = document.getElementById('pass_confirmar').value;

        if (nueva !== confirmar) {
            showCustomAlert('Las contraseñas nuevas no coinciden');
            return;
        }

        try {
            const res = await fetch('/configuracion/api/cambiar_password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    password_actual: actual,
                    password_nueva: nueva
                })
            });
            const result = await res.json();
            if (result.success) {
                showCustomAlert(result.message, false);
                document.getElementById('formPassword').reset();
            } else {
                showCustomAlert('Error: ' + result.message);
            }
        } catch (error) {
            console.error(error);
            showCustomAlert('Error en el servidor');
        }
    });
});
