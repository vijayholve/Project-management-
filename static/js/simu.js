document.addEventListener("DOMContentLoaded", () => {
    const mentorSignupForm = document.getElementById("mentorSignupForm");
  
    if (mentorSignupForm) {
      mentorSignupForm.addEventListener("submit", (e) => {
        e.preventDefault();
        alert("Mentor signup submitted!");
        // TODO: Add your actual mentor signup logic here
      });
    }
  });
  