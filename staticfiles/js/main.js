let map;
let markers = [];
let userLocation = null;

// Инициализация карты
function initMap() {
    map = L.map('map').setView([55.7558, 37.6173], 4);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

// Получение геолокации пользователя
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                // Добавляем маркер пользователя
                const userMarker = L.marker([userLocation.lat, userLocation.lng], {
                    icon: L.divIcon({
                        className: 'user-marker',
                        html: '📍',
                        iconSize: [30, 30]
                    })
                }).addTo(map).bindPopup('Вы здесь');
                
                // Добавляем параметры к поиску
                const form = document.getElementById('searchForm');
                const latInput = document.createElement('input');
                latInput.type = 'hidden';
                latInput.name = 'lat';
                latInput.value = userLocation.lat;
                form.appendChild(latInput);
                
                const lngInput = document.createElement('input');
                lngInput.type = 'hidden';
                lngInput.name = 'lng';
                lngInput.value = userLocation.lng;
                form.appendChild(lngInput);
                
                // Запрашиваем радиус
                const radius = prompt('Введите радиус поиска в километрах:', '50');
                if (radius) {
                    const radiusInput = document.createElement('input');
                    radiusInput.type = 'hidden';
                    radiusInput.name = 'radius';
                    radiusInput.value = radius;
                    form.appendChild(radiusInput);
                    
                    // Рисуем круг на карте
                    L.circle([userLocation.lat, userLocation.lng], {
                        radius: radius * 1000,
                        color: 'blue',
                        fillColor: '#3388ff',
                        fillOpacity: 0.1
                    }).addTo(map);
                }
                
                // Выполняем поиск
                document.getElementById('searchForm').dispatchEvent(new Event('submit'));
            },
            function(error) {
                alert('Не удалось определить ваше местоположение. Проверьте настройки браузера.');
                console.error('Geolocation error:', error);
            }
        );
    } else {
        alert('Ваш браузер не поддерживает геолокацию');
    }
}

// Обновление маркеров на карте
function updateMarkers(providers) {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    if (providers.length === 0) {
        return;
    }

    providers.forEach(provider => {
        if (provider.latitude && provider.longitude) {
            const color = provider.rating >= 4.5 ? '#4CAF50' : 
                         provider.rating >= 3.5 ? '#FFC107' : '#F44336';
            
            const marker = L.marker([provider.latitude, provider.longitude], {
                icon: L.divIcon({
                    className: 'provider-marker',
                    html: `<div style="background: ${color}; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
                            ${provider.rating || '?'}
                          </div>`,
                    iconSize: [30, 30]
                })
            }).addTo(map)
            .bindPopup(`
                <b>${provider.name}</b><br>
                ${provider.category}<br>
                ${provider.address || ''}<br>
                ${provider.city || ''}<br>
                ⭐ ${provider.rating || 'Нет рейтинга'}<br>
                ${provider.distance ? `📍 ${provider.distance} км от вас` : ''}<br>
                <a href="/provider/${provider.id}">Подробнее →</a>
            `);
            markers.push(marker);
        }
    });

    if (markers.length > 0) {
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds());
    }
}

// Отображение списка поставщиков
function displayProviders(providers) {
    const listContainer = document.getElementById('providersList');
    const countSpan = document.getElementById('resultCount');
    
    countSpan.textContent = `Найдено: ${providers.length}`;
    
    if (providers.length === 0) {
        listContainer.innerHTML = '<p class="hint">Поставщики не найдены</p>';
        return;
    }

    let html = '<ul class="provider-list">';
    providers.forEach(provider => {
        const stars = '⭐'.repeat(Math.floor(provider.rating || 0));
        const halfStar = (provider.rating || 0) % 1 >= 0.5 ? '⭐' : '';
        
        html += `
            <li class="provider-item">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4><a href="/provider/${provider.id}">${provider.name}</a></h4>
                        <p><strong>Категория:</strong> ${provider.category}</p>
                        <p><strong>Страна:</strong> ${provider.country} ${provider.city ? `, ${provider.city}` : ''}</p>
                        <p><strong>Рейтинг:</strong> ${stars}${halfStar} ${provider.rating || 'Нет оценки'}</p>
                        ${provider.distance ? `<p><strong>Расстояние:</strong> ${provider.distance} км</p>` : ''}
                        <p>${provider.description ? provider.description.substring(0, 100) + '...' : ''}</p>
                        ${provider.is_verified ? '<span class="verified-badge">✓ Проверен</span>' : ''}
                    </div>
                    ${provider.image ? `<img src="/uploads/${provider.image}" alt="${provider.name}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px;">` : ''}
                </div>
                <p><a href="/provider/${provider.id}" class="btn-detail">Подробнее →</a></p>
            </li>
        `;
    });
    html += '</ul>';
    listContainer.innerHTML = html;
}

// Поиск поставщиков
function searchProviders(event) {
    event.preventDefault();
    
    const form = document.getElementById('searchForm');
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    
    // Удаляем пустые параметры
    for (const [key, value] of params.entries()) {
        if (!value) {
            params.delete(key);
        }
    }
    
    fetch(`/search?${params.toString()}`)
        .then(response => response.json())
        .then(providers => {
            displayProviders(providers);
            updateMarkers(providers);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при поиске');
        });
}

// Обработка добавления в избранное
function toggleFavorite(providerId) {
    fetch(`/provider/${providerId}/favorite`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const icon = document.querySelector('.favorite-icon');
        if (data.is_favorite) {
            icon.classList.add('fas');
            icon.classList.remove('far');
            icon.style.color = '#e74c3c';
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            icon.style.color = '#ccc';
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    document.getElementById('searchForm').addEventListener('submit', searchProviders);
    
    // Автоматический поиск при загрузке
    document.getElementById('searchForm').dispatchEvent(new Event('submit'));
    
    // Обработка кнопки "Рядом"
    window.getUserLocation = getUserLocation;
    
    // Инициализация избранного
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const providerId = this.dataset.providerId;
            toggleFavorite(providerId);
        });
    });
});