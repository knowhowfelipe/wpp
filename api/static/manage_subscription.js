document.addEventListener('DOMContentLoaded', function() {
    const subscriptionDetails = document.getElementById('subscription-details');
    const cancelSubscriptionBtn = document.getElementById('cancel-subscription-btn');
    const updateSubscriptionBtn = document.getElementById('update-subscription-btn');

    // Função para buscar os detalhes da assinatura
    function fetchSubscriptionDetails() {
        fetch('/get-subscription-details', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.subscription) {
                const subscription = data.subscription;
                subscriptionDetails.innerHTML = `
                    <p><strong>ID da Assinatura:</strong> ${subscription.id}</p>
                    <p><strong>Status:</strong> ${subscription.status}</p>
                    <p><strong>Início:</strong> ${new Date(subscription.start_date * 1000).toLocaleString()}</p>
                    <p><strong>Término:</strong> ${new Date(subscription.current_period_end * 1000).toLocaleString()}</p>
                `;
            } else {
                subscriptionDetails.innerHTML = `<p>Nenhuma assinatura encontrada.</p>`;
            }
        })
        .catch(error => {
            console.error('Erro ao buscar detalhes da assinatura:', error);
            subscriptionDetails.innerHTML = `<p>Erro ao buscar detalhes da assinatura.</p>`;
        });
    }

    // Função para cancelar a assinatura
    cancelSubscriptionBtn.addEventListener('click', function() {
        fetch('/cancel-subscription', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Assinatura cancelada com sucesso.');
                fetchSubscriptionDetails(); // Atualizar detalhes da assinatura
            } else {
                alert('Erro ao cancelar a assinatura.');
            }
        })
        .catch(error => {
            console.error('Erro ao cancelar a assinatura:', error);
        });
    });

    // Função para atualizar o plano
    updateSubscriptionBtn.addEventListener('click', function() {
        fetch('/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ upgrade: true })
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
            console.error('Erro ao atualizar o plano:', error);
        });
    });

    // Buscar detalhes da assinatura ao carregar a página
    fetchSubscriptionDetails();
});
