// Defina a função globalmente, fora do DOMContentLoaded
function sendMessage() {
    const countryCode = document.getElementById('country').value;
    let phoneNumber = document.getElementById('phoneNumber').value;
    const message = document.getElementById('message').value;

    // Validação de campos
    if (!phoneNumber || !message) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    // Remover qualquer caractere não numérico do número de telefone
    phoneNumber = phoneNumber.replace(/\D/g, ''); // Substitui tudo que não for número por uma string vazia

    // Criar o link para o WhatsApp
    const whatsappLink = `https://api.whatsapp.com/send?phone=${countryCode}${phoneNumber}&text=${encodeURIComponent(message)}`;

    // Abrir o link do WhatsApp em uma nova aba
    window.open(whatsappLink, '_blank');
}

document.addEventListener('DOMContentLoaded', function () {
    // Função para obter a lista de países usando a biblioteca do CDN
    function getCountries() {
        try {
            // Obter a lista de países com o código de discagem e a bandeira
            const countries = window.CountryList.getAll();

            // Preencher a lista de países no select
            const countrySelect = document.getElementById('country');

            // Verificar se a resposta é válida
            if (!countries || countries.length === 0) {
                throw new Error('Nenhum país encontrado');
            }

            // Preencher o select com as opções de países
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country.dial_code; // Usar o código de discagem

                // Adicionar a bandeira e o nome do país com a bandeira como emoji
                const flag = `<span class="flag-icon">${country.flag}</span>`;
                const name = country.name;
                const dial_code = country.dial_code;

                option.innerHTML = `${flag} ${name} (${dial_code})`;
                option.classList.add('select-option');

                countrySelect.appendChild(option);

                // Definir Brasil como padrão 
                countrySelect.value = '+55';
            });

        } catch (error) {
            console.error("Erro ao carregar os países:", error);
            alert("Erro ao carregar a lista de países.");
        }
    }

    // Chama a função para preencher a lista de países
    getCountries();

    // Função para alternar o menu suspenso
    function toggleMenu() {
        const menu = document.getElementById('menu');
        menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
    }

    // Adiciona o event listener ao botão de menu dentro do DOMContentLoaded
    const menuToggleBtn = document.querySelector('.menu-toggle-btn');
    menuToggleBtn.addEventListener('click', toggleMenu);

    // Fechar o menu ao clicar fora do menu ou do botão
    document.addEventListener('click', function (event) {
        const menu = document.getElementById('menu');
        const menuBtn = document.querySelector('.menu-toggle-btn');

        if (!menu.contains(event.target) && !menuBtn.contains(event.target)) {
            menu.style.display = 'none';
        }
    });

    // Fechar o menu automaticamente quando um item for clicado
    const menuItems = document.querySelectorAll('.menu-list a');
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            document.getElementById('menu').style.display = 'none';
        });
    });
});
