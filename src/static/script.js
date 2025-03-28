document.addEventListener('DOMContentLoaded', () => {

    // elementos do DOM
    const searchForm = document.getElementById('search-form');
    const termInput = document.getElementById('term');
    const resultsArea = document.getElementById('results-area');
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message');
    const summaryMessage = document.getElementById('summary-message');
    const productList = document.getElementById('product-list');
    const downloadButton = document.getElementById('download-button');
    const containerDiv = document.querySelector('.container'); // Elemento que terá o data-attribute

    // produtos da última busca bem sucedida
    let currentProducts = [];
    let currentSearchTerm = "";

    // limpar resultados e mensagens
    function clearResults() {
        loadingMessage.style.display = 'none';
        errorMessage.style.display = 'none';
        summaryMessage.style.display = 'none';
        productList.innerHTML = '';
        downloadButton.disabled = true;
        currentProducts = [];
        currentSearchTerm = "";
        downloadButton.removeEventListener('click', handleDownload); // remove listener antigo
    }

    //  buscar os dados API Flask
    async function searchProducts(term) {
        if (!term) return;

        clearResults();
        loadingMessage.style.display = 'block';
        currentSearchTerm = term;

        try {
            const response = await fetch(`/api/search?term=${encodeURIComponent(term)}`);

            if (!response.ok) {
                let errorMsg = `Erro na requisição: ${response.status} ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMsg = (errorData && errorData.error) ? errorData.error : errorMsg;
                } catch (e) { /* Ignora */ }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            loadingMessage.style.display = 'none';

            if (data.success) {
                currentProducts = data.products || [];
                displayResults(currentProducts, data.total_found, term);
            } else {
                throw new Error(data.error || 'Erro desconhecido retornado pela API.');
            }

        } catch (error) {
            console.error('Erro ao buscar produtos:', error);
            loadingMessage.style.display = 'none';
            errorMessage.textContent = `Erro: ${error.message}`;
            errorMessage.style.display = 'block';
            downloadButton.disabled = true;
        }
    }

    // exibir os resultados na pagina
    function displayResults(products, totalFound, term) {
        productList.innerHTML = '';

        if (products && products.length > 0) {
            summaryMessage.textContent = `Encontrados ${totalFound} produtos para "${term}".`;
            summaryMessage.style.display = 'block';

            products.forEach(product => {
                const listItem = document.createElement('li');
                const price = typeof product.price === 'number' ? product.price.toFixed(2).replace('.', ',') : 'N/A';
                listItem.textContent = `${product.name || 'Nome Indisponível'} - R$ ${price}`;
                productList.appendChild(listItem);
            });

            downloadButton.disabled = false;
            downloadButton.addEventListener('click', handleDownload);

        } else {
            summaryMessage.textContent = `Nenhum produto encontrado para "${term}".`;
            summaryMessage.style.display = 'block';
            downloadButton.disabled = true;
        }
    }

    // download csv
    function handleDownload() {
        if (!currentProducts || currentProducts.length === 0) {
            console.warn("Nenhum produto para baixar.");
            return;
        }

        const csvHeader = ['Nome do Produto', 'Preço'];
        const csvRows = currentProducts.map(product => {
            const name = product.name || 'Nome Indisponível';
            const price = typeof product.price === 'number' ? product.price.toFixed(2).replace('.', ',') : 'N/A';
            const escapedName = name.replace(/"/g, '""');
            const formattedName = /[",\n]/.test(escapedName) ? `"${escapedName}"` : escapedName;
            return `${formattedName},${price}`;
        });

        const csvString = [csvHeader.join(','), ...csvRows].join('\n');
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");

        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            const safeTerm = currentSearchTerm.replace(/[^a-z0-9]/gi, '_').toLowerCase();
            link.setAttribute("href", url);
            link.setAttribute("download", `produtos_${safeTerm}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } else {
            alert("Seu navegador não suporta download direto.");
        }
    }

    // --- execucao inicial ---

    // termo inicial do atributo data-* adicionado ao HTML
    const initialTermFromData = containerDiv.dataset.initialTerm || '';

    // term?
    if (initialTermFromData) {
        termInput.value = initialTermFromData;
        searchProducts(initialTermFromData);
    }

    // listerner do botao de busca
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const term = termInput.value.trim();
        if (term) {
            const newUrl = window.location.pathname + `?term=${encodeURIComponent(term)}`;
            window.history.pushState({ path: newUrl }, '', newUrl);
            searchProducts(term);
        }
    });

}); // fim do evento DOMContentLoaded