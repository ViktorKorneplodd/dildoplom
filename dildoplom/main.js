document.addEventListener('DOMContentLoaded', function() {
    const priceRange = document.getElementById('price-range');
    const priceFromSpan = document.getElementById('price-from');
    const priceToSpan = document.getElementById('price-to');
    const priceFromInput = document.getElementById('price-from-input');
    const priceToInput = document.getElementById('price-to-input');

    priceRange.addEventListener('input', function() {
        const value = this.value;
        priceFromSpan.textContent = value;
        priceFromInput.value = value;
    });

    document.getElementById('filter-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        fetch('/filter-products', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Обновите список товаров на основе данных из ответа
            updateProductList(data);
        })
        .catch(error => console.error('Ошибка:', error));
    });

    function updateProductList(products) {
        const productList = document.querySelector('.product-card-container');
        productList.innerHTML = '';
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.classList.add('product-card');
            productCard.innerHTML = `
                <div class="product-image">
                    <img src="" alt="${product.image}">
                </div>
                <div class="product-info">
                    <a href="${url_for('product', tovar_id=product.id)}">
                        <h3>${product.Название}</h3>
                    </a>
                    <p class="product-description">${product.Описание}</p>
                    <div class="product-price">Цена: ${product.Цена} руб.</div>
                </div>
            `;
            productList.appendChild(productCard);
        });
    }
});
