document.getElementById('valuationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const plotNumber = document.getElementById('plotNumber').value;
    const location = document.getElementById('location').value;
    const latitude = document.getElementById('latitude').value;
    const longitude = document.getElementById('longitude').value;

    // TODO: Replace with actual backend API endpoint
    const response = await fetch('/api/valuate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plotNumber, location, latitude, longitude })
    });
    const result = await response.json();
    document.getElementById('valuationResult').innerText = result.valuation
        ? `Estimated Land Value: KES ${result.valuation}`
        : 'No valuation found.';
});
