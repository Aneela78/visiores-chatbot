document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const loadingElement = document.getElementById('loading');
    const resultsHeader = document.getElementById('resultsHeader');
    const resultsCount = document.getElementById('resultsCount');
    const resultsList = document.getElementById('resultsList');

    const API_BASE_URL = 'http://localhost:8000';

    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const query = searchInput.value.trim();
        if (!query) return;

        loadingElement.style.display = 'block';
        resultsHeader.style.display = 'none';
        resultsList.innerHTML = '';

        try {
            const response = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "API request failed");
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            console.error('Search error:', error);
            resultsList.innerHTML = `
                <div class="error-message">
                    <p>${error.message || "Search failed"}</p>
                    <p>Ensure:
                        <ul>
                            <li>Backend is running at ${API_BASE_URL}</li>
                            <li>No CORS errors (check browser console)</li>
                        </ul>
                    </p>
                </div>
            `;
        } finally {
            loadingElement.style.display = 'none';
        }
    });

    function displayResults(data) {
        resultsHeader.style.display = 'block';
        resultsCount.textContent = `Found ${data.count} papers for "${data.query}"`;
        
        resultsList.innerHTML = data.results.map(result => `
            <div class="result-item">
                <h3 class="result-title">${result.title}</h3>
                <p class="result-authors">${result.authors}</p>
                <p class="result-abstract">${result.abstract}</p>
                <span class="result-similarity">${(result.similarity * 100).toFixed(1)}% match</span>
            </div>
        `).join('');
    }
});