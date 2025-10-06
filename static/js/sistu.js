document.addEventListener("DOMContentLoaded", () => {
    const studentSignupForm = document.getElementById("studentSignupForm");
  
    if (studentSignupForm) {
      studentSignupForm.addEventListener("submit", (e) => {
        e.preventDefault();
        alert("Student signup submitted!");
        // TODO: Add your actual student signup logic here
      });
    }
  });
  