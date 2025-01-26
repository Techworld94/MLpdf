document.addEventListener("DOMContentLoaded", function () {

    ////////////////////////////////Navbar Toggle//////////////////////////////////////
    document.getElementById("navbar-toggle").addEventListener("click", function() {
        const navbarLinks = document.getElementById("navbar-links");
        const toggleIcon = document.getElementById("navbar-toggle");
    
        navbarLinks.classList.toggle("active");
        toggleIcon.classList.toggle("active"); 
    });

    ////////////////////////////////Motivation letter Modal //////////////////////////////////////
    
    const openModal = document.getElementById('open-modal');
    const modal = document.getElementById('modal');
    const closeModal = document.getElementById('close-modal');
    const generateLetter = document.getElementById('generate-letter');

    openModal.addEventListener('click', () => {
      modal.style.display = 'flex';
    });

    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        modal.style.display = 'none';
      }
    });

    closeModal.addEventListener('click', () => {
      modal.style.display = 'none';
    });

    //////////////////////// Toastify function //////////////////////////////////

    function showToast(message, type = 'success') {
      Toastify({
          text: message,
          duration: 3000,
          close: true, 
          gravity: "top",
          position: "right",
          backgroundColor: type === 'error' ? "green" : "red",
          stopOnFocus: true,
      }).showToast();
    }

    //////////////////////////////// Resume Upload //////////////////////////////////

    document.getElementById('resume-upload').addEventListener('change', function () {
      const fileName = this.files[0]?.name || 'No file chosen';
      const label = document.querySelector('label[for="resume-upload"]');
      label.textContent = `Selected: ${fileName}`;
    });

    //////////////////////////////// Generate Motivation letter ////////////////////////
  
    document.getElementById('generate-letter').addEventListener('click', async function () {
      const button = this;
      const icon = button.querySelector('i');
      const motivationLetterTextarea = document.getElementById('motivation-letter');
    
      //motivationLetterTextarea.value = `Dear Hiring Manager,\n\nI am excited to apply for the ${document.getElementById('job-title').value} position at ${document.getElementById('company-name').value}. With a strong background in... (Generating full content, please wait)`;
      button.classList.add('active');
    

      const jobTitle = document.getElementById('job-title').value.trim();
      const jobDescription = document.getElementById('job-description').value.trim();
      const companyName = document.getElementById('company-name').value.trim();
      const resumeFile = document.getElementById('resume-upload').files[0];
    
      if (!resumeFile || !jobTitle || !jobDescription || !companyName) {
          showToast('Please fill in all fields and upload a resume.')
          button.classList.remove('active');
          if (icon) icon.classList.remove('fa-spin');
          return;
      }
    
      const formData = new FormData();
      formData.append('resume_files', resumeFile);
      formData.append('job_title', jobTitle);
      formData.append('job_description', jobDescription);
      formData.append('company_name', companyName);
    
      try {
          const response = await fetch('/generate-letter', {
              method: 'POST',
              body: formData,
          });
  
          if (!response.ok) {
            const errorData = await response.json();
            const errorMessage = errorData.error || "Failed to generate the motivation letter.";
            throw new Error(errorMessage);
          }
  
          const result = await response.json();
  
          if (result.motivation_letter) {
              motivationLetterTextarea.value = result.motivation_letter;
          } else {
              motivationLetterTextarea.value = "Failed to generate the motivation letter. Please try again.";
          }
  
      } catch (error) {
          showToast(error.message, 'error')
      } finally {
          button.classList.remove('active');
      }
  });

  document.getElementById('download-doc').addEventListener('click', async function () {
    const motivationLetter = document.getElementById('motivation-letter').value;
    
    if (!motivationLetter) {
        showToast('Please generate the motivation letter first.')
        return;
    }

    try {
        const response = await fetch('/download-letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                letter: motivationLetter, 
                format: 'docx' 
            })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || "Failed to download the document");          
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'motivation_letter.docx';
        link.click();
    } catch (error) {
        showToast('Failed to download the letter as DOCX. Please try again.')
    }
  });   
});  