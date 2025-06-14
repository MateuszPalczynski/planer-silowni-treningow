document.addEventListener('DOMContentLoaded', () => {
  const popup = document.getElementById('popup');
  const popupExpertPlans = document.getElementById('popupExpertPlans');
  const editPopup = document.getElementById('editPopup');
  const openBtn = document.getElementById('openPopupBtn');
  const closeBtn = document.getElementById('closePopupBtn');
  const closeEditBtn = document.getElementById('closeEditPopupBtn');
  const openExpertBtn = document.getElementById('openExpertPopupBtn');
  const closeExpertBtn = document.getElementById('closeExpertPopupBtn');

  const openChooseExpertPopupBtn = document.getElementById('openChooseExpertPopupBtn');
  const closeChooseExpertPopupBtn = document.getElementById('closeChooseExpertPopupBtn');

  const isExpertInput = document.getElementById('id_is_expert');
  const popupTitle = document.getElementById('popupTitle');
  
  // Pobranie danych planów z JSON
  let trainingPlansData = [];
  const trainingPlansElement = document.getElementById('training-plans-data');
  if (trainingPlansElement) {
    try {
      trainingPlansData = JSON.parse(trainingPlansElement.textContent);
    } catch (e) {
      console.error('Error parsing training plans data:', e);
    }
  }

  // Add Training Plan
  if (openBtn) {
    openBtn.addEventListener('click', () => {
      popupTitle.textContent = 'Create a New Training Plan';
      if (isExpertInput) isExpertInput.value = 'False';
      popup.style.display = 'block';
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      popup.style.display = 'none';
    });
  }

  // Edit Training Plan
  if (closeEditBtn) {
    closeEditBtn.addEventListener('click', () => {
      editPopup.style.display = 'none';
    });
  }

  // Funkcja otwierania popup edycji
  function openEditPopup(planId) {
    const plan = trainingPlansData.find(p => p.id == planId);
    if (!plan) {
      console.error('Plan not found:', planId);
      alert('Nie można znaleźć danych planu');
      return;
    }

    // Wypełnienie formularza danymi planu
    document.getElementById('editPlanId').value = plan.id;
    document.getElementById('editPlanName').value = plan.name;
    document.getElementById('editIntensity').value = plan.intensity;

    // Ustawienie dni treningu
    const trainingDaysSelect = document.getElementById('editTrainingDays');
    Array.from(trainingDaysSelect.options).forEach(option => {
      option.selected = plan.training_days.includes(option.value);
    });

    // Reset wszystkich checkboxów ćwiczeń
    document.querySelectorAll('#editExercisesList input[type="checkbox"]').forEach(checkbox => {
      checkbox.checked = false;
    });
    document.querySelectorAll('#editExercisesList input[type="number"]').forEach(input => {
      input.value = 10;
    });

    // Zaznaczenie ćwiczeń z planu
    plan.exercises.forEach(exercise => {
      const checkbox = document.getElementById(`edit_ex_${exercise.id}`);
      const repsInput = document.getElementById(`edit_reps_${exercise.id}`);
      if (checkbox) {
        checkbox.checked = true;
      }
      if (repsInput) {
        repsInput.value = exercise.repetitions;
      }
    });

    // Ustawienie akcji formularza
    document.getElementById('editTrainingPlanForm').action = `/edit_training_plan/${plan.id}/`;

    editPopup.style.display = 'block';
  }

  // Obsługa przycisków edycji - używamy event delegation
  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('edit-btn')) {
      e.preventDefault();
      e.stopPropagation();
      const planId = e.target.getAttribute('data-plan-id');
      openEditPopup(planId);
    }
  });

  // Add Expert Plan
  if (openExpertBtn) {
    openExpertBtn.addEventListener('click', () => {
      popupTitle.textContent = 'Create a New Expert Plan';
      if (isExpertInput) isExpertInput.value = 'True';
      popup.style.display = 'block';
    });
  }

  if (closeExpertBtn) {
    closeExpertBtn.addEventListener('click', () => {
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

  // Zamykanie popupów po kliknięciu w tło
  window.addEventListener('click', (event) => {
    if (event.target === popup) {
      popup.style.display = 'none';
    }
    if (event.target === editPopup) {
      editPopup.style.display = 'none';
    }
    if (event.target === popupExpertPlans) {
      popupExpertPlans.style.display = 'none';
    }
  });

  // Wyświetl przyciski akcji po kliknięciu na plan
  document.querySelectorAll('.training-plan-item').forEach(item => {
    item.addEventListener('click', (e) => {
      // Jeśli kliknięto na przycisk akcji lub formularz, nie rób nic
      if (e.target.closest('.plan-actions') || e.target.closest('.save-form') || e.target.closest('button') || e.target.closest('textarea')) {
        return;
      }
      
      // Ukryj wszystkie inne przyciski akcji
      document.querySelectorAll('.plan-actions').forEach(a => a.style.display = 'none');
      
      // Pokaż przyciski akcji dla tego planu
      const planActions = item.querySelector('.plan-actions');
      if (planActions) {
        planActions.style.display = 'block';
      }
    });
  });

  // Klik poza planami – schowaj przyciski
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.training-plan-item')) {
      document.querySelectorAll('.plan-actions').forEach(a => a.style.display = 'none');
    }
  });
});
