document.addEventListener('DOMContentLoaded', function () {
    function getEmojiPicker() {
        const emojiPicker = document.getElementById('emoji-picker');
        const emojis = ['😀', '😂', '🤣', '😍', '😎', '😭', '🤔', '👍', '🙏', '❤️'];
        emojis.forEach(emoji => {
            const emojiSpan = document.createElement('span');
            emojiSpan.textContent = emoji;
            emojiSpan.addEventListener('click', () => {
                const messageInput = document.getElementById('message');
                messageInput.value += emoji;
            });
            emojiPicker.appendChild(emojiSpan);
        });
    }

    function toggleEmojiPicker() {
        const emojiPicker = document.getElementById('emoji-picker');
        emojiPicker.style.display = (emojiPicker.style.display === 'none' || emojiPicker.style.display === '') ? 'block' : 'none';
    }

    document.getElementById('emoji-btn').addEventListener('click', toggleEmojiPicker);

    getEmojiPicker();

    document.addEventListener('click', function (event) {
        const emojiPicker = document.getElementById('emoji-picker');
        const emojiBtn = document.getElementById('emoji-btn');

        if (!emojiPicker.contains(event.target) && !emojiBtn.contains(event.target)) {
            emojiPicker.style.display = 'none';
        }
    });
});
