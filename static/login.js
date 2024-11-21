// Função para login do usuário
function loginUser() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    const data = {
        email: email,
        senha: password
    };

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.mensagem === 'Login bem-sucedido') {
            window.location.href = '/home';
        } else {
            alert(data.mensagem);
        }
    })
    .catch((error) => {
        console.error('Erro:', error);
        alert('Erro ao fazer login. Por favor, tente novamente.');
    });
}
