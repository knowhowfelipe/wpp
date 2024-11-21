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
    option.innerHTML = `<img class="flag" src="${country.flag}" alt="${country.name}"> ${country.name} (+${country.code})`;
    countrySelect.appendChild(option);
});

// Função para enviar mensagem
function sendMessage() {
    const countryCode = document.getElementById('country').value;
    const phoneNumber = document.getElementById('phoneNumber').value;
    const message = document.getElementById('message').value;
    const whatsappLink = `https://api.whatsapp.com/send?phone=${countryCode}${phoneNumber}&text=${encodeURIComponent(message)}`;
    window.open(whatsappLink, '_blank');
}
