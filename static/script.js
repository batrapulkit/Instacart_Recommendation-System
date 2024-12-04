document.getElementById("recommendationForm").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent form from refreshing the page

    const userId = document.getElementById("user_id").value;
    const resultsDiv = document.getElementById("results");

    try {
        const response = await fetch(`/recommend?user_id=${userId}`);
        const data = await response.json();

        if (response.ok) {
            resultsDiv.innerHTML = `<h2>Recommended Products:</h2><ul>${data.recommended_products
                .map((product) => `<li>${product.product_name}</li>`)
                .join("")}</ul>`;
        } else {
            resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p>Error: Unable to fetch recommendations. Please try again later.</p>`;
        console.error(error);
    }
});
