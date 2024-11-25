document.addEventListener('DOMContentLoaded', function () {
    function getUserStatus() {
        return fetch('/get-user-id')
            .then(response => {
                if (response.status === 200) {
                    return response.json();
                } else {
                    throw new Error('Usuário não está logado.');
                }
            })
            .then(data => {
                if (data.user_id) {
                    return { isLoggedIn: true, userName: data.user_name, userId: data.user_id };
                } else {
                    return { isLoggedIn: false, userName: null, userId: null };
                }
            })
            .catch(error => {
                console.error(error);
                return { isLoggedIn: false, userName: null, userId: null };
            });
    }

    getUserStatus().then(status => {
        const userInfoDiv = document.getElementById('user-info');
        const subscriptionAction = document.getElementById('subscription-action');

        if (status.isLoggedIn) {
            userInfoDiv.innerHTML = `<i class="fas fa-user"></i> ${status.userName}`;

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
                        // Cria a sessão de checkout
                        fetch('/create-checkout-session', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ id_usuario: status.userId })
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
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching user status:', error);
            });
        } else {
            userInfoDiv.innerHTML = `<a href="/login" class="btn btn-primary login-btn">Login</a>`;
        }
    });
});
