// Soil analysis functionality

let selectedFile = null;

// Handle file selection
document.getElementById('soilImage').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
        alert('Неверный формат файла. Поддерживаются только JPG и PNG.');
        return;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('Файл слишком большой. Максимальный размер: 10MB');
        return;
    }

    selectedFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('imagePreview').style.display = 'block';
        document.getElementById('analysisResult').style.display = 'none';
    };
    reader.readAsDataURL(file);
});

// Analyze image
async function analyzeImage() {
    if (!selectedFile) {
        alert('Пожалуйста, выберите изображение');
        return;
    }

    const token = TokenManager.getAccessToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Show loader
    document.getElementById('analysisLoader').style.display = 'block';
    document.getElementById('analysisResult').style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch('/api/v1/soil/analyze', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Display results
            document.getElementById('soilType').textContent = data.soil_type;
            document.getElementById('confidence').textContent = (data.confidence * 100).toFixed(2);
            document.getElementById('description').textContent = data.description;
            document.getElementById('characteristics').textContent = data.characteristics;
            document.getElementById('crops').textContent = data.recommended_crops;
            document.getElementById('recommendations').textContent = data.recommendations;

            document.getElementById('analysisResult').style.display = 'block';

            // Refresh history
            loadHistory();
        } else {
            alert(`Ошибка анализа: ${data.detail || 'Неизвестная ошибка'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при анализе изображения');
    } finally {
        document.getElementById('analysisLoader').style.display = 'none';
    }
}

// Load analysis history
async function loadHistory() {
    const token = TokenManager.getAccessToken();
    if (!token) return;

    try {
        const response = await fetch('/api/v1/soil/history?limit=10', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load history');
        }

        const data = await response.json();
        const historyList = document.getElementById('historyList');

        if (data.analyses.length === 0) {
            historyList.innerHTML = '<p>История анализов пуста</p>';
            return;
        }

        historyList.innerHTML = data.analyses.map(analysis => `
            <div class="history-item">
                <div class="history-info">
                    <p><strong>${analysis.soil_type}</strong></p>
                    <p>${new Date(analysis.created_at).toLocaleString('ru-RU')}</p>
                    <p>Уверенность: ${(analysis.confidence * 100).toFixed(1)}%</p>
                </div>
                <div class="history-actions">
                    <button class="btn-small" onclick="viewAnalysis(${analysis.id})">Просмотр</button>
                    <button class="btn-small btn-danger" onclick="deleteAnalysis(${analysis.id})">Удалить</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// View specific analysis
async function viewAnalysis(analysisId) {
    const token = TokenManager.getAccessToken();
    if (!token) return;

    try {
        const response = await fetch(`/api/v1/soil/analysis/${analysisId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load analysis');
        }

        const data = await response.json();

        // Display results
        document.getElementById('soilType').textContent = data.soil_type;
        document.getElementById('confidence').textContent = (data.confidence * 100).toFixed(2);
        document.getElementById('description').textContent = data.description;
        document.getElementById('characteristics').textContent = data.characteristics;
        document.getElementById('crops').textContent = data.recommended_crops;
        document.getElementById('recommendations').textContent = data.recommendations;

        document.getElementById('analysisResult').style.display = 'block';

        // Scroll to results
        document.getElementById('analysisResult').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error:', error);
        alert('Не удалось загрузить анализ');
    }
}

// Delete analysis
async function deleteAnalysis(analysisId) {
    if (!confirm('Вы уверены, что хотите удалить этот анализ?')) {
        return;
    }

    const token = TokenManager.getAccessToken();
    if (!token) return;

    try {
        const response = await fetch(`/api/v1/soil/analysis/${analysisId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert('Анализ удален');
            loadHistory();
        } else {
            const data = await response.json();
            alert(`Ошибка: ${data.detail || 'Не удалось удалить анализ'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при удалении');
    }
}

// Load history on page load
window.addEventListener('DOMContentLoaded', () => {
    loadHistory();
});
