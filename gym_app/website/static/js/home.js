// Function to show the popup
function showPopup() {
    document.getElementById('popup').style.display = 'block';
  }
  
  // Function to close the popup
  function closePopup() {
    document.getElementById('popup').style.display = 'none';
  }
  
  // Close the popup when the user clicks outside of it
  window.onclick = function(event) {
    if (event.target === document.getElementById('popup')) {
      closePopup();
    }
  }

 // Pobranie elementów
 const popup = document.getElementById('popup');
 const openPopupBtn = document.getElementById('openPopupBtn');
 const closePopupBtn = document.getElementById('closePopupBtn');

 // Funkcja otwierająca popup
 openPopupBtn.onclick = function() {
   popup.style.display = 'block';
 };

 // Funkcja zamykająca popup
 closePopupBtn.onclick = function() {
   popup.style.display = 'none';
 };

 // Zamknięcie popupu, jeśli użytkownik kliknie poza jego obszar
 window.onclick = function(event) {
   if (event.target == popup) {
     popup.style.display = 'none';
   }
 };
  