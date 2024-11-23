// Função para login do usuário
function loginUser() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    const formData = new FormData();
    formData.append('email', email);
    formData.append('senha', password);

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.mensagem === 'Login bem-sucedido') {
            window.location.href = '/form';
        } else {
            alert(data.mensagem);
        }
    })
    .catch((error) => {
        console.error('Erro:', error);
        alert('Erro ao fazer login. Por favor, tente novamente.');
    });
}
