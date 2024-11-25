document.addEventListener('DOMContentLoaded', function() {
    const subscriptionAction = document.getElementById('subscription-action');

    if (!subscriptionAction) {
        console.error('Elemento subscription-action não encontrado.');
        return;
    }

    // Verifica o status da assinatura do usuário
    fetch('/get-user-status', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.is_premium) {
            // Usuário é premium, mostrar botão "Gerenciar Assinatura"
            subscriptionAction.innerHTML = `
                <a class="nav-link" href="/manage-subscription">Gerenciar Assinatura</a>
            `;
        } else {
            // Usuário não é premium, mostrar botão "Assinar"
            subscriptionAction.innerHTML = `
                <a class="nav-link" href="#" id="migrate-plan">Assinar</a>
            `;

            // Adicionar event listener para o botão de assinar
            document.querySelector('#migrate-plan').addEventListener('click', function() {
                // Obtém o ID do usuário da sessão
                fetch('/get-user-id', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    const id_usuario = data.user_id;

                    // Cria a sessão de checkout
                    fetch('/create-checkout-session', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ id_usuario: id_usuario })
                    })
                    .then(response => response.json())
                    .then(session => {
                        const stripe = Stripe('pk_test_51QO4bDClJp9dPNzNZume9C1l88aNt7gNY2lDe5vH8Zl1j341TVJrD1grpmo9fh59qZERsxdKXOaUqsCj5GXovSwo00TPcyhrCM');
                        return stripe.redirectToCheckout({ sessionId: session.id });
                    })
                    .then(result => {
                        if (result.error) {
                            alert(result.error.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                })
                .catch(error => {
                    console.error('Error fetching user ID:', error);
                });
            });
        }
    })
    .catch(error => {
        console.error('Error fetching user status:', error);
    });
});
