document.addEventListener('DOMContentLoaded', function() {
    //const stripePublicKey = "{{ stripe_public_key }}";
    const stripePublicKey = "pk_test_51QP5dNK91woPpT0pRCeyyPLF4Qgw9uZ1rX2Ax97odChUbKr2gCtyFasExcuNQ0Z9pS0HblBZFeE0NGFcWWdpHqo300usQIqplN";
    const stripe = Stripe(stripePublicKey);
    const migratePlanButton = document.querySelector('#migrate-plan');

    migratePlanButton.addEventListener('click', function() {
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
});
