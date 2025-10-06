// app.js

document.getElementById('login-form').addEventListener('submit', async function(event) {
  event.preventDefault(); // Prevents form from submitting normally

  // Get form data
  const form = event.target;
  const formData = new FormData(form);

  try {
      // Send login request to Flask backend
      const response = await fetch(form.action, {
          method: 'POST',
          body: formData
      });
      
      const data = await response.json();
      
      if (data.success) {
          // Redirect to dashboard if login is successful
          window.location.href = data.redirect;
      } else {
          // Show error message if login fails
          alert(data.message);
      }
  } catch (error) {
      console.error('Login error:', error);
      alert('An error occurred during login. Please try again.');
  }
});

// Google and LinkedIn Login Buttons (for now, just placeholders)
document.getElementById('google-login').addEventListener('click', function() {
  alert('Google login feature coming soon!');
});

document.getElementById('linkedin-login').addEventListener('click', function() {
  alert('LinkedIn login feature coming soon!');
});
  