document.addEventListener('DOMContentLoaded', function () {
    function getUserStatus() {
        console.log("Vamos capturar a ID do usuario")
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
                    return { isLoggedIn: true, userName: data.user_name };
                } else {
                    return { isLoggedIn: false, userName: null };
                }
            })
            .catch(error => {
                console.error(error);
                return { isLoggedIn: false, userName: null };
            });
    }

    getUserStatus().then(status => {
        const userInfoDiv = document.getElementById('user-info');

        if (status.isLoggedIn) {
            userInfoDiv.innerHTML = `<i class="fas fa-user"></i> ${status.userName}`;
        } else {
            userInfoDiv.innerHTML = `<a href="/login" class="btn btn-primary login-btn">Login</a>`;
        }
    });
});
