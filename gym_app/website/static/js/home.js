document.addEventListener('DOMContentLoaded', () => {
  const popup = document.getElementById('popup');
  const openBtn = document.getElementById('openPopupBtn');
  const closeBtn = document.getElementById('closePopupBtn');

  if (openBtn) {
    openBtn.addEventListener('click', () => {
      popup.style.display = 'block';
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      popup.style.display = 'none';
    });
  }

  window.addEventListener('click', (event) => {
    if (event.target === popup) {
      popup.style.display = 'none';
    }
  });
});
