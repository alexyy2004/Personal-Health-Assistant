document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('symptomForm');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent the form from submitting the traditional way

        const symptomsInput = document.getElementById('symptoms').value.trim();
        
        if (!symptomsInput) {
            resultsDiv.innerHTML = '<p style="color:red;">Please enter some symptoms.</p>';
            return; // Stop execution if no symptoms are entered
        }

        const symptoms = symptomsInput.split(',').map(symptom => symptom.trim());

        resultsDiv.innerHTML = ''; // Clear previous results

        // Send the symptoms to the server using a POST request
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms }), // Send symptoms as JSON
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
            } else if (data.message) {
                resultsDiv.innerHTML = `<p>${data.message}</p>`;
            } else {
                displayResults(data);
            }
        })
        .catch(error => {
            resultsDiv.innerHTML = `<p style="color:red;">An error occurred while fetching the data.</p>`;
        });
    });

    function displayResults(results) {
        if (results.length === 0) {
            resultsDiv.innerHTML = '<p>No diseases matched your symptoms.</p>';
        } else {
            let html = '<h2>Possible Diseases:</h2>';
            html += '<ul>';
            
            results.forEach(result => {
                html += `<li class="disease-item"><strong>${result.disease}</strong>: ${result.possibility.toFixed(2)}% chance</li>`;
            });
            
            html += '</ul>';
            
            resultsDiv.innerHTML = html; 
        }
    }
});