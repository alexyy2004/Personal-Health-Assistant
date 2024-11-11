document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('symptomForm');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', function (e) {
        e.preventDefault(); 
        const symptomsInput = document.getElementById('symptoms').value.trim();
        
        if (!symptomsInput) {
            resultsDiv.innerHTML = '<p style="color:red;">Please enter some symptoms.</p>';
            return;
        }

        const symptoms = symptomsInput.split(',').map(symptom => symptom.trim());

        resultsDiv.innerHTML = '';

        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
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