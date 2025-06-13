document.addEventListener('DOMContentLoaded', () => {
  const popup = document.getElementById('popup');
  const popupExpertPlans = document.getElementById('popupExpertPlans');
  const openBtn = document.getElementById('openPopupBtn');
  const closeBtn = document.getElementById('closePopupBtn');
  const openExpertBtn = document.getElementById('openExpertPopupBtn');
  const closeExpertBtn = document.getElementById('closeExpertPopupBtn');

  const openChooseExpertPopupBtn = document.getElementById('openChooseExpertPopupBtn');
  const closeChooseExpertPopupBtn = document.getElementById('closeChooseExpertPopupBtn');

  const isExpertInput = document.getElementById('id_is_expert');
  const popupTitle = document.getElementById('popupTitle');
  

  // Add Training Plan
  if (openBtn) {
    openBtn.addEventListener('click', () => {
      popupTitle.textContent = 'Create a New Training Plan';
      isExpertInput.value = 'False';
      popup.style.display = 'block';
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      popup.style.display = 'none';
    });
  }

    // Add Expert Plan
    if (openExpertBtn) {
      openExpertBtn.addEventListener('click', () => {
        popupTitle.textContent = 'Create a New Expert Plan';
        isExpertInput.value = 'True';
        popup.style.display = 'block';
      });
    }
  
    if (closeExpertBtn) {
      openExpertBtn.addEventListener('click', () => {
        popup.style.display = 'none';
      });
    }

  //Choose Expert Plan
  if (openChooseExpertPopupBtn) {
    openChooseExpertPopupBtn.addEventListener('click', () => {
      popupExpertPlans.style.display = 'block';
    });
  }
  
  if (closeChooseExpertPopupBtn) {
    closeChooseExpertPopupBtn.addEventListener('click', () => {
      popupExpertPlans.style.display = 'none';
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
