// media.js - Handle media upload and gallery

class MediaManager {
    constructor() {
        this.uploadForm = document.getElementById('media-upload-form');
        this.dropZone = document.getElementById('media-drop-zone');
        this.fileInput = document.getElementById('media-file-input');
        this.uploadBtn = document.getElementById('media-upload-btn');
        this.mediaGallery = document.getElementById('media-gallery');
        this.previewContainer = document.getElementById('media-preview');
        
        this.selectedFiles = [];
        this.uploadInProgress = false;
        
        this.initializeEventListeners();
        this.loadMediaGallery();
        
        // Initialize lightbox
        this.initLightbox();
    }
    
    initializeEventListeners() {
        // File input change
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // Upload button
        if (this.uploadBtn) {
            this.uploadBtn.addEventListener('click', () => this.fileInput?.click());
        }
        
        // Drag and drop
        if (this.dropZone) {
            this.dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.dropZone.classList.add('dragover');
            });
            
            this.dropZone.addEventListener('dragleave', () => {
                this.dropZone.classList.remove('dragover');
            });
            
            this.dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                this.dropZone.classList.remove('dragover');
                this.handleFileSelect({ target: { files: e.dataTransfer.files } });
            });
        }
        
        // Upload form submit
        if (this.uploadForm) {
            this.uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
        }
    }
    
    handleFileSelect(event) {
        const files = Array.from(event.target.files || []);
        
        // Filter by allowed file types
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 
                              'application/pdf', 'audio/mpeg', 'audio/wav', 
                              'video/mp4', 'video/quicktime'];
        
        const validFiles = files.filter(file => allowedTypes.includes(file.type) || 
            file.name.toLowerCase().match(/\.(jpg|jpeg|png|gif|webp|pdf|mp3|wav|mp4|mov|avi)$/));
        
        if (validFiles.length === 0) {
            this.showMessage('No valid files selected. Please select images, PDFs, audio, or video files.', 'error');
            return;
        }
        
        // Check file sizes (max 50MB per file)
        const maxSize = 50 * 1024 * 1024; // 50MB
        const oversizedFiles = validFiles.filter(file => file.size > maxSize);
        
        if (oversizedFiles.length > 0) {
            this.showMessage(`Some files exceed 50MB limit: ${oversizedFiles.map(f => f.name).join(', ')}`, 'error');
            // Remove oversized files
            this.selectedFiles = validFiles.filter(file => file.size <= maxSize);
        } else {
            this.selectedFiles = validFiles;
        }
        
        if (this.selectedFiles.length > 0) {
            this.showPreview();
        }
        
        // Clear file input so same file can be selected again
        if (this.fileInput) {
            this.fileInput.value = '';
        }
    }
    
    showPreview() {
        if (!this.previewContainer) return;
        
        if (this.selectedFiles.length === 0) {
            this.previewContainer.innerHTML = '';
            const mediaForm = document.getElementById('media-form-fields');
            if (mediaForm) {
                mediaForm.style.display = 'none';
            }
            return;
        }
        
        this.previewContainer.innerHTML = '';
        
        this.selectedFiles.forEach((file, index) => {
            const previewDiv = document.createElement('div');
            previewDiv.className = 'media-preview-item';
            previewDiv.dataset.index = index;
            
            let previewHTML = '';
            let fileType = 'document';
            
            if (file.type.startsWith('image/')) {
                fileType = 'image';
                const url = URL.createObjectURL(file);
                previewHTML = `
                    <div class="preview-image">
                        <img src="${url}" alt="${file.name}">
                        <button type="button" class="remove-file" data-index="${index}">×</button>
                    </div>
                    <div class="preview-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                        <div class="file-type">Image</div>
                    </div>
                `;
                // Clean up object URL when done
                previewDiv.addEventListener('remove', () => URL.revokeObjectURL(url));
            } else if (file.type.startsWith('audio/')) {
                fileType = 'audio';
                previewHTML = `
                    <div class="preview-icon audio">
                        <i class="fas fa-music"></i>
                        <button type="button" class="remove-file" data-index="${index}">×</button>
                    </div>
                    <div class="preview-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                        <div class="file-type">Audio</div>
                    </div>
                `;
            } else if (file.type.startsWith('video/')) {
                fileType = 'video';
                previewHTML = `
                    <div class="preview-icon video">
                        <i class="fas fa-video"></i>
                        <button type="button" class="remove-file" data-index="${index}">×</button>
                    </div>
                    <div class="preview-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                        <div class="file-type">Video</div>
                    </div>
                `;
            } else if (file.type === 'application/pdf') {
                fileType = 'pdf';
                previewHTML = `
                    <div class="preview-icon pdf">
                        <i class="fas fa-file-pdf"></i>
                        <button type="button" class="remove-file" data-index="${index}">×</button>
                    </div>
                    <div class="preview-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                        <div class="file-type">PDF</div>
                    </div>
                `;
            } else {
                previewHTML = `
                    <div class="preview-icon document">
                        <i class="fas fa-file"></i>
                        <button type="button" class="remove-file" data-index="${index}">×</button>
                    </div>
                    <div class="preview-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                        <div class="file-type">Document</div>
                    </div>
                `;
            }
            
            previewDiv.className = `media-preview-item ${fileType}`;
            previewDiv.innerHTML = previewHTML;
            this.previewContainer.appendChild(previewDiv);
            
            // Add remove button functionality
            const removeBtn = previewDiv.querySelector('.remove-file');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const index = parseInt(e.target.dataset.index || e.target.closest('.remove-file').dataset.index);
                    this.removeFile(index);
                });
            }
        });
        
        // Show form if it's hidden
        const mediaForm = document.getElementById('media-form-fields');
        if (mediaForm) {
            mediaForm.style.display = 'block';
        }
    }
    
    removeFile(index) {
        // Revoke object URL if it's an image
        const previewItem = this.previewContainer.querySelector(`[data-index="${index}"]`);
        if (previewItem && previewItem.classList.contains('image')) {
            const img = previewItem.querySelector('img');
            if (img && img.src.startsWith('blob:')) {
                URL.revokeObjectURL(img.src);
            }
        }
        
        this.selectedFiles.splice(index, 1);
        
        // Update indices for remaining items
        const remainingItems = this.previewContainer.querySelectorAll('.media-preview-item');
        remainingItems.forEach((item, newIndex) => {
            item.dataset.index = newIndex;
            const removeBtn = item.querySelector('.remove-file');
            if (removeBtn) {
                removeBtn.dataset.index = newIndex;
            }
        });
        
        this.showPreview();
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    async handleUpload(event) {
        event.preventDefault();
        
        if (this.selectedFiles.length === 0) {
            this.showMessage('Please select files to upload', 'error');
            return;
        }
        
        if (this.uploadInProgress) return;
        
        this.uploadInProgress = true;
        const originalBtnText = this.uploadBtn.innerHTML;
        this.uploadBtn.disabled = true;
        this.uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
        
        const title = document.getElementById('media-title')?.value || 'Untitled';
        const description = document.getElementById('media-description')?.value || '';
        const memoryDate = document.getElementById('media-date')?.value || '';
        const year = document.getElementById('media-year')?.value || '';
        const people = document.getElementById('media-people')?.value || '';
        
        let successCount = 0;
        let errorCount = 0;
        const errors = [];
        
        for (const file of this.selectedFiles) {
            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('title', title);
                formData.append('description', description);
                formData.append('memory_date', memoryDate);
                formData.append('year', year);
                formData.append('people', people);
                formData.append('original_filename', file.name);
                formData.append('file_size', file.size);
                formData.append('file_type', file.type);
                
                console.log('Uploading file:', file.name, file.type, file.size);
                
                const response = await fetch('/api/media/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                console.log('Upload response:', result);
                
                if (response.ok && result.status === 'success') {
                    successCount++;
                } else {
                    errorCount++;
                    errors.push(`${file.name}: ${result.message || 'Upload failed'}`);
                }
            } catch (error) {
                errorCount++;
                errors.push(`${file.name}: ${error.message}`);
                console.error('Upload error:', error);
            }
        }
        
        this.uploadInProgress = false;
        this.uploadBtn.disabled = false;
        this.uploadBtn.innerHTML = originalBtnText;
        
        // Show result message
        let message = '';
        if (successCount > 0) {
            message = `Successfully uploaded ${successCount} file(s)`;
            this.selectedFiles = [];
            this.showPreview();
            
            // Reload gallery after a short delay
            setTimeout(() => this.loadMediaGallery(), 500);
            
            // Reset form
            if (this.uploadForm) {
                this.uploadForm.reset();
            }
            
            const mediaForm = document.getElementById('media-form-fields');
            if (mediaForm) {
                mediaForm.style.display = 'none';
            }
            
            this.showMessage(message, 'success');
        }
        
        if (errorCount > 0) {
            const errorMessage = `Failed to upload ${errorCount} file(s): ${errors.join('; ')}`;
            this.showMessage(errorMessage, 'error');
        }
    }
    
    async loadMediaGallery() {
        console.log('Loading media gallery...');
        if (!this.mediaGallery) {
            console.error('mediaGallery element not found!');
            return;
        }
        
        // Show loading state
        this.mediaGallery.innerHTML = `
            <div class="loading-gallery">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading media...</p>
            </div>
        `;
        
        try {
            const response = await fetch('/api/media/all');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const mediaItems = await response.json();
            console.log('Received media items:', mediaItems);
            
            this.renderMediaGallery(mediaItems);
        } catch (error) {
            console.error('Error loading media gallery:', error);
            this.mediaGallery.innerHTML = `
                <div class="error-gallery">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Failed to load media gallery</p>
                    <button onclick="window.mediaManager.loadMediaGallery()" class="retry-btn">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        }
    }
    
    renderMediaGallery(mediaItems) {
        if (!this.mediaGallery) return;
        
        if (!mediaItems || mediaItems.length === 0) {
            this.mediaGallery.innerHTML = `
                <div class="empty-gallery">
                    <i class="fas fa-images"></i>
                    <p>No media uploaded yet</p>
                    <p>Drag and drop files or click upload to add media</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="media-grid">';
        
        mediaItems.forEach(item => {
            let mediaElement = '';
            const fileType = item.file_type?.split('/')[0] || item.file_type || 'document';
            
            if (fileType.startsWith('image')) {
                mediaElement = `
                    <div class="media-item image" data-id="${item.id}">
                        <div class="media-thumbnail">
                            <img src="/uploads/${item.filename}" alt="${item.title || item.original_filename}" 
                                 loading="lazy" data-url="/uploads/${item.filename}">
                            <div class="media-overlay">
                                <button class="media-view" title="View full size">
                                    <i class="fas fa-expand"></i>
                                </button>
                                <button class="media-delete" data-id="${item.id}" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="media-info">
                            <h4>${item.title || item.original_filename}</h4>
                            <p class="media-description">${item.description || 'No description'}</p>
                            <small>${this.formatFileSize(item.file_size)} • ${new Date(item.uploaded_at).toLocaleDateString()}</small>
                        </div>
                    </div>
                `;
            } else if (fileType.startsWith('audio')) {
                mediaElement = `
                    <div class="media-item audio" data-id="${item.id}">
                        <div class="media-thumbnail">
                            <div class="audio-icon">
                                <i class="fas fa-music"></i>
                            </div>
                            <div class="media-overlay">
                                <a href="/uploads/${item.filename}" target="_blank" class="media-view" title="Play audio">
                                    <i class="fas fa-play"></i>
                                </a>
                                <button class="media-delete" data-id="${item.id}" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="media-info">
                            <h4>${item.title || item.original_filename}</h4>
                            <p class="media-description">${item.description || 'No description'}</p>
                            <small>${this.formatFileSize(item.file_size)} • ${new Date(item.uploaded_at).toLocaleDateString()}</small>
                        </div>
                    </div>
                `;
            } else if (fileType.startsWith('video')) {
                mediaElement = `
                    <div class="media-item video" data-id="${item.id}">
                        <div class="media-thumbnail">
                            <div class="video-icon">
                                <i class="fas fa-video"></i>
                            </div>
                            <div class="media-overlay">
                                <a href="/uploads/${item.filename}" target="_blank" class="media-view" title="Play video">
                                    <i class="fas fa-play"></i>
                                </a>
                                <button class="media-delete" data-id="${item.id}" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="media-info">
                            <h4>${item.title || item.original_filename}</h4>
                            <p class="media-description">${item.description || 'No description'}</p>
                            <small>${this.formatFileSize(item.file_size)} • ${new Date(item.uploaded_at).toLocaleDateString()}</small>
                        </div>
                    </div>
                `;
            } else if (item.file_type === 'application/pdf' || item.original_filename?.endsWith('.pdf')) {
                mediaElement = `
                    <div class="media-item pdf" data-id="${item.id}">
                        <div class="media-thumbnail">
                            <div class="pdf-icon">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="media-overlay">
                                <a href="/uploads/${item.filename}" target="_blank" class="media-view" title="View PDF">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <button class="media-delete" data-id="${item.id}" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="media-info">
                            <h4>${item.title || item.original_filename}</h4>
                            <p class="media-description">${item.description || 'No description'}</p>
                            <small>${this.formatFileSize(item.file_size)} • ${new Date(item.uploaded_at).toLocaleDateString()}</small>
                        </div>
                    </div>
                `;
            } else {
                mediaElement = `
                    <div class="media-item document" data-id="${item.id}">
                        <div class="media-thumbnail">
                            <div class="document-icon">
                                <i class="fas fa-file"></i>
                            </div>
                            <div class="media-overlay">
                                <a href="/uploads/${item.filename}" target="_blank" class="media-view" title="Download">
                                    <i class="fas fa-download"></i>
                                </a>
                                <button class="media-delete" data-id="${item.id}" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="media-info">
                            <h4>${item.title || item.original_filename}</h4>
                            <p class="media-description">${item.description || 'No description'}</p>
                            <small>${this.formatFileSize(item.file_size)} • ${new Date(item.uploaded_at).toLocaleDateString()}</small>
                        </div>
                    </div>
                `;
            }
            
            html += mediaElement;
        });
        
        html += '</div>';
        this.mediaGallery.innerHTML = html;
        
        // Add event listeners to delete buttons
        this.mediaGallery.querySelectorAll('.media-delete').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                const mediaId = btn.dataset.id;
                
                if (confirm('Are you sure you want to delete this media item? This cannot be undone.')) {
                    try {
                        const response = await fetch(`/api/media/delete/${mediaId}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            this.showMessage('Media deleted successfully', 'success');
                            // Remove the item from DOM
                            const mediaItem = btn.closest('.media-item');
                            if (mediaItem) {
                                mediaItem.style.opacity = '0.5';
                                setTimeout(() => {
                                    mediaItem.remove();
                                    // Reload gallery if empty
                                    const remainingItems = this.mediaGallery.querySelectorAll('.media-item');
                                    if (remainingItems.length === 0) {
                                        this.loadMediaGallery();
                                    }
                                }, 300);
                            }
                        } else {
                            const result = await response.json();
                            throw new Error(result.error || 'Delete failed');
                        }
                    } catch (error) {
                        console.error('Delete error:', error);
                        this.showMessage('Error deleting media: ' + error.message, 'error');
                    }
                }
            });
        });
        
        // Add event listeners to view buttons
        this.mediaGallery.querySelectorAll('.media-view').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // For image items, open lightbox instead of new tab
                if (btn.closest('.image')) {
                    e.preventDefault();
                    e.stopPropagation();
                    const img = btn.closest('.media-thumbnail').querySelector('img');
                    if (img) {
                        this.openLightbox(img.src, img.alt);
                    }
                }
                // For non-link view buttons (audio/video with play button)
                else if (btn.tagName === 'BUTTON') {
                    e.preventDefault();
                    e.stopPropagation();
                    const mediaItem = btn.closest('.media-item');
                    const link = mediaItem.querySelector('a.media-view');
                    if (link) {
                        window.open(link.href, '_blank');
                    }
                }
            });
        });
    }
    
    initLightbox() {
        // Create lightbox HTML if it doesn't exist
        if (!document.getElementById('lightbox')) {
            const lightboxHTML = `
                <div id="lightbox" class="lightbox" style="display: none;">
                    <div class="lightbox-content">
                        <button class="lightbox-close">&times;</button>
                        <button class="lightbox-prev">&lt;</button>
                        <button class="lightbox-next">&gt;</button>
                        <img src="" alt="" class="lightbox-image">
                        <div class="lightbox-caption"></div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', lightboxHTML);
            
            // Add lightbox event listeners
            const lightbox = document.getElementById('lightbox');
            const closeBtn = lightbox.querySelector('.lightbox-close');
            const prevBtn = lightbox.querySelector('.lightbox-prev');
            const nextBtn = lightbox.querySelector('.lightbox-next');
            
            closeBtn.addEventListener('click', () => this.closeLightbox());
            lightbox.addEventListener('click', (e) => {
                if (e.target === lightbox) this.closeLightbox();
            });
            
            // Add keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (lightbox.style.display === 'flex') {
                    if (e.key === 'Escape') this.closeLightbox();
                    if (e.key === 'ArrowLeft') prevBtn.click();
                    if (e.key === 'ArrowRight') nextBtn.click();
                }
            });
        }
    }
    
    openLightbox(src, caption) {
        const lightbox = document.getElementById('lightbox');
        const lightboxImage = lightbox.querySelector('.lightbox-image');
        const lightboxCaption = lightbox.querySelector('.lightbox-caption');
        
        lightboxImage.src = src;
        lightboxImage.alt = caption;
        lightboxCaption.textContent = caption;
        
        lightbox.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
        
        // Fade in animation
        setTimeout(() => {
            lightbox.style.opacity = '1';
        }, 10);
    }
    
    closeLightbox() {
        const lightbox = document.getElementById('lightbox');
        lightbox.style.opacity = '0';
        
        setTimeout(() => {
            lightbox.style.display = 'none';
            document.body.style.overflow = 'auto'; // Restore scrolling
        }, 300);
    }
    
    showMessage(message, type) {
        // Remove existing messages
        const existingMsg = document.querySelector('.media-message');
        if (existingMsg) {
            existingMsg.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `media-message ${type}`;
        messageDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="close-message">&times;</button>
        `;
        
        const container = document.querySelector('.media-container') || document.querySelector('.media-tab') || document.body;
        if (container) {
            container.prepend(messageDiv);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 5000);
            
            // Close button
            messageDiv.querySelector('.close-message').addEventListener('click', () => {
                messageDiv.remove();
            });
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mediaManager = new MediaManager();
});

// Add tab change listener
document.addEventListener('tabChanged', (e) => {
    if (e.detail.tab === 'media' && window.mediaManager) {
        setTimeout(() => window.mediaManager.loadMediaGallery(), 100);
    }
});

// Helper for tab changes
const originalShowTab = window.showTab;
window.showTab = function(tabName, event) {
    if (originalShowTab) {
        originalShowTab(tabName, event);
    }
    
    // Dispatch custom event for tab change
    document.dispatchEvent(new CustomEvent('tabChanged', { 
        detail: { tab: tabName } 
    }));
    
    // Load media gallery when media tab is shown
    if (tabName === 'media' && window.mediaManager) {
        setTimeout(() => window.mediaManager.loadMediaGallery(), 100);
    }
};