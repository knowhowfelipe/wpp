document.addEventListener('DOMContentLoaded', function () {
    const stripe = Stripe('pk_test_51QP5dNK91woPpT0pRCeyyPLF4Qgw9uZ1rX2Ax97odChUbKr2gCtyFasExcuNQ0Z9pS0HblBZFeE0NGFcWWdpHqo300usQIqplN');
    const migratePlanButton = document.querySelector('#migrate-plan');

    migratePlanButton.addEventListener('click', function () {
        console.log("Botão de migração clicado.");

        // Obtém o ID do usuário da sessão
        fetch('/get-user-id', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao obter o ID do usuário: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Dados do usuário recebidos:", data);
                const id_usuario = data.user_id;

                if (!id_usuario) {
                    throw new Error("ID do usuário não foi recebido.");
                }

                // Cria a sessão de checkout
                return fetch('/create-checkout-session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id_usuario: id_usuario })
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro ao criar a sessão de checkout: ${response.statusText}`);
                }
                return response.json();
            })
            .then(session => {
                console.log("Sessão de checkout criada:", session);

                if (!session.id) {
                    throw new Error("ID da sessão de checkout não foi recebido.");
                }

                // Redireciona para o Stripe Checkout
                return stripe.redirectToCheckout({ sessionId: session.id });
            })
            .then(result => {
                if (result.error) {
                    console.error("Erro no redirecionamento:", result.error);
                    alert(`Erro ao redirecionar para o checkout: ${result.error.message}`);
                }
            })
            .catch(error => {
                console.error("Erro no processo de checkout:", error);
                alert(`Ocorreu um erro: ${error.message}`);
            });
    });
});
