document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const initialView = document.getElementById('initial-upload-view');
    const previewView = document.getElementById('preview-view');
    const imagePreview = document.getElementById('image-preview');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingDiv = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    const resetBtn = document.getElementById('reset-btn');

    let selectedFile = null;

    function formatBytes(bytes, decimals = 2) {
        if (!+bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            alert('Please select a valid image file (PNG, JPG, JPEG)');
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            initialView.classList.add('hidden');
            previewView.classList.remove('hidden');
            analyzeBtn.classList.remove('hidden');
            resultsSection.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--accent-secondary)';
        dropZone.style.backgroundColor = 'var(--bg-card-light)';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#424867';
        dropZone.style.backgroundColor = 'var(--bg-card)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#424867';
        dropZone.style.backgroundColor = 'var(--bg-card)';
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    resetBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        initialView.classList.remove('hidden');
        previewView.classList.add('hidden');
        analyzeBtn.classList.add('hidden');
        resultsSection.classList.add('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);

        // ── CHANGE 1: Send selected model to backend ──────────────────────
        const selectedModel = document.getElementById('modelSelect').value;
        formData.append('model', selectedModel);
        // ─────────────────────────────────────────────────────────────────

        analyzeBtn.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('report-timestamp').textContent = `Generated: ${data.timestamp}`;

                const resultCard = document.getElementById('result-status-card');
                const resultTitle = document.getElementById('result-title');
                const resultSubtitle = document.getElementById('result-subtitle');
                const resultIcon = document.getElementById('result-icon');

                resultTitle.textContent = data.result;
                resultSubtitle.textContent = data.sub_text;

                if (data.result === 'UNINFECTED') {
                    resultCard.className = 'result-card main-result uninfected';
                    resultIcon.className = 'fa-solid fa-check';
                    document.getElementById('progress-bar').style.backgroundColor = 'var(--success-color)';
                } else {
                    resultCard.className = 'result-card main-result parasitized';
                    resultIcon.className = 'fa-solid fa-virus';
                    document.getElementById('progress-bar').style.backgroundColor = 'var(--danger-color)';
                }

                document.getElementById('detail-time').textContent = data.processing_time;
                document.getElementById('detail-timestamp').textContent = data.timestamp;
                document.getElementById('confidence-value').textContent = data.confidence_percent;
                document.getElementById('progress-bar').style.width = '0%';

                // ── CHANGE 2: Show which model was used in results card ────
                if (document.getElementById('detail-model')) {
                    document.getElementById('detail-model').textContent = data.model_used;
                }
                // ─────────────────────────────────────────────────────────

                if (data.scans_today) {
                    document.getElementById('scans-today-display').textContent = data.scans_today.toLocaleString();
                }

                setTimeout(() => {
                    document.getElementById('progress-bar').style.width = data.confidence_percent;
                }, 300);

                resultsSection.classList.remove('hidden');
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                alert('Error: ' + data.error);
                analyzeBtn.classList.remove('hidden');
            }
        } catch (error) {
            console.error(error);
            alert('An error occurred during analysis. Please check console.');
            analyzeBtn.classList.remove('hidden');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });

    fetch('/stats')
        .then(res => res.json())
        .then(data => {
            if (data.scans_today) {
                document.getElementById('scans-today-display').textContent = data.scans_today.toLocaleString();
            }
        }).catch(err => console.log(err));
});