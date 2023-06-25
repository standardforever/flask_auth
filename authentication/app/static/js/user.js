// user.js

function showConfirmation(userId, id) {
    var modal = document.getElementById("confirmationModal");
    modal.style.display = "block";
  
    var deleteForm = document.getElementById("deleteForm");
    deleteForm.action = "/admin/delete/" + userId + '/' + id;
  }
  
  function hideConfirmation() {
    var modal = document.getElementById("confirmationModal");
    modal.style.display = "none";
  }
  
  window.onclick = function(event) {
    var modal = document.getElementById("confirmationModal");
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
  