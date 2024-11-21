// Lista de países e códigos
const countries = [
    { code: '55', name: 'Brasil', flag: 'https://www.countryflags.io/br/flat/24.png' },
    { code: '1', name: 'Estados Unidos', flag: 'https://www.countryflags.io/us/flat/24.png' },
    { code: '44', name: 'Reino Unido', flag: 'https://www.countryflags.io/gb/flat/24.png' },
    // Adicione outros países conforme necessário
];

// Preencher a lista de países no select
const countrySelect = document.getElementById('country');
countries.forEach(country => {
    const option = document.createElement('option');
    option.value = country.code;
    option.innerHTML = `${country.name} (+${country.code})`;
    countrySelect.appendChild(option);
});

// Função para enviar a mensagem
function sendMessage() {
    const countryCode = document.getElementById('country').value;
    const phoneNumber = document.getElementById('phoneNumber').value;
    const message = document.getElementById('message').value;

    // Validação de campos
    if (!phoneNumber || !message) {
        alert('Por favor, preencha todos os campos.');
        return;
    }

    // Criar o link para o WhatsApp
    const whatsappLink = `https://api.whatsapp.com/send?phone=${countryCode}${phoneNumber}&text=${encodeURIComponent(message)}`;

    // Abrir o link do WhatsApp em uma nova aba
    window.open(whatsappLink, '_blank');
}

// Função para alternar o menu suspenso
function toggleMenu() {
    const menu = document.getElementById('menu');
    menu.style.display = (menu.style.display === 'none' || menu.style.display === '') ? 'block' : 'none';
}

// Fechar o menu ao clicar em um item ou fora do menu
document.addEventListener('click', function(event) {
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
