// Função para registrar o usuário
function registerUser() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const repeatPassword = document.getElementById('repeat_senha').value;

    if (!name || !email || !password || !repeatPassword) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    if (password !== repeatPassword) {
        alert('As senhas não coincidem.');
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('senha', password);
    formData.append('repeat_senha', repeatPassword);

    fetch('/register', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Registrado com sucesso!') {
            alert(data.message);
            window.location.href = '/login';
        } else {
            alert(data.error);
        }
    })
    .catch((error) => {
        console.error('Erro:', error);
        alert('Erro ao registrar. Por favor, tente novamente.');
    });
}
