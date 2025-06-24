const  form_file = document.getElementById('form_file');
const btnFile = document.getElementById('select-file');
const  fileInput = document.getElementById('fileElem');
let file = null; // Initialize file variable

btnFile.addEventListener('click', function(event) {
    
    const file = fileInput.click() // Get the selected file}
    if (file) {
        console.log('Selected file:', file.name);
    } else {
        console.log('No file selected');
    }
});

form_file.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    const formData = new FormData(form_file);


    if (file) {
        formData.append('file', file);

        fetch('/api/transform/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('File uploaded successfully!');
            } else {
                alert('File upload failed: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while uploading the file.');
        });
    } else {
        alert('Please select a file to upload.');
    }
});