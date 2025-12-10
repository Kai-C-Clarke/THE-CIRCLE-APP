// export.js - PDF export functions
async function generatePDF(type = 'full') {
    const statusDiv = document.getElementById('export-status');
    statusDiv.innerHTML = `<div class="loading"><i class="fas fa-spinner fa-spin"></i> <p>Generating ${type === 'full' ? 'Complete' : 'Summary'} PDF...</p></div>`;
    
    try {
        const response = await fetch(`/api/pdf/generate/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = type === 'full' ? 'family_story_full.pdf' : 'family_story_summary.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            statusDiv.innerHTML = `<div style="color: #28a745; padding: 15px; background: #d4edda; border-radius: 8px;">
                <i class="fas fa-check-circle"></i> ${type === 'full' ? 'Complete' : 'Summary'} PDF generated successfully!
            </div>`;
        } else {
            const error = await response.json();
            statusDiv.innerHTML = `<div style="color: #dc3545; padding: 15px; background: #f8d7da; border-radius: 8px;">
                <i class="fas fa-exclamation-triangle"></i> Error: ${error.message || 'Unknown error'}
            </div>`;
        }
    } catch (error) {
        console.error('Error:', error);
        statusDiv.innerHTML = `<div style="color: #dc3545; padding: 15px; background: #f8d7da; border-radius: 8px;">
            <i class="fas fa-exclamation-triangle"></i> Failed to generate PDF. Make sure the server is running.
        </div>`;
    }
}

async function generateFamilyAlbum() {
    const statusDiv = document.getElementById('export-status');
    statusDiv.innerHTML = `<div class="loading"><i class="fas fa-spinner fa-spin"></i> <p>Creating Family Album PDF...</p></div>`;
    
    try {
        const response = await fetch('/api/pdf/generate/album', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'family_album.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            statusDiv.innerHTML = `<div style="color: #28a745; padding: 15px; background: #d4edda; border-radius: 8px;">
                <i class="fas fa-check-circle"></i> Family Album PDF generated successfully!
            </div>`;
        } else {
            const error = await response.json();
            statusDiv.innerHTML = `<div style="color: #dc3545; padding: 15px; background: #f8d7da; border-radius: 8px;">
                <i class="fas fa-exclamation-triangle"></i> Error: ${error.message || 'Unknown error'}
            </div>`;
        }
    } catch (error) {
        console.error('Error:', error);
        statusDiv.innerHTML = `<div style="color: #dc3545; padding: 15px; background: #f8d7da; border-radius: 8px;">
            <i class="fas fa-exclamation-triangle"></i> Failed to generate family album.
        </div>`;
    }
}