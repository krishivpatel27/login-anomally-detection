// Populate users dynamically
const userSelect = document.getElementById('user_id');
for (let i = 1; i <= 100; i++) {
    const option = document.createElement('option');
    option.value = 'user_' + i;
    option.textContent = 'user_' + i;
    userSelect.appendChild(option);
}

document.getElementById('failed_attempts').addEventListener('input', (e) => {
    document.getElementById('failed_val').textContent = e.target.value;
});

document.getElementById('hour').addEventListener('input', (e) => {
    document.getElementById('hour_val').textContent = e.target.value;
});

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const payload = {
        user_id: formData.get('user_id'),
        country: formData.get('country'),
        device_type: formData.get('device_type'),
        browser: formData.get('browser'),
        failed_attempts: parseInt(formData.get('failed_attempts')),
        hour: parseInt(formData.get('hour')),
        is_weekend: parseInt(formData.get('is_weekend'))
    };

    document.getElementById('results').classList.add('hidden');
    document.getElementById('errorMsg').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');

        const alertEl = document.getElementById('statusAlert');
        const iconEl = document.getElementById('statusIcon');
        const textEl = document.getElementById('statusText');

        if (data.prediction === 1) {
            alertEl.className = 'alert danger';
            iconEl.textContent = '⚠️';
        } else {
            alertEl.className = 'alert success';
            iconEl.textContent = '✅';
        }
        textEl.textContent = data.status;

        document.getElementById('riskScoreValue').textContent = data.risk_score;
        document.getElementById('riskLevelValue').textContent = data.risk_level;
        document.getElementById('behaviorScoreValue').textContent = data.behavior_risk_score;

    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        const errorEl = document.getElementById('errorMsg');
        errorEl.textContent = 'Application Error: ' + error.message;
        errorEl.classList.remove('hidden');
    }
});

// 3D Tilt Effect for UI Elements
const cards = document.querySelectorAll('.metric-card, .control-panel');
cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = ((y - centerY) / centerY) * -10;
        const rotateY = ((x - centerX) / centerX) * 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        card.style.transition = 'transform 0.5s ease';
    });
    
    card.addEventListener('mouseenter', () => {
        card.style.transition = 'none';
    });
});
