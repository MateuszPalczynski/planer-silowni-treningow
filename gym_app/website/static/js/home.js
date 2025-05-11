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

  // Wyświetl przycisk „Usuń” po kliknięciu na plan
  document.querySelectorAll('.training-plan-item').forEach(item => {
    item.addEventListener('click', e => {
      if (e.target.closest('.plan-actions')) return;
      document.querySelectorAll('.plan-actions').forEach(a => a.style.display = 'none');
      item.querySelector('.plan-actions').style.display = 'block';
    });
  });

  // Klik poza planami – schowaj przycisk
  document.addEventListener('click', e => {
    if (!e.target.closest('.training-plan-item')) {
      document.querySelectorAll('.plan-actions').forEach(a => a.style.display = 'none');
    }
  });
});
