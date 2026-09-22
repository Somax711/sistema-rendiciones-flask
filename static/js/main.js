// JavaScript principal para Sistema de Rendiciones

$(document).ready(function() {
    // Inicializar tooltips
    initTooltips();
    
    // Cargar notificaciones
    loadNotifications();
    
    // Auto-refresh notificaciones cada 30 segundos
    setInterval(loadNotifications, 30000);
    
    // Confirmación de eliminación
    setupDeleteConfirmations();
    
    // Items de rendición dinámicos
    setupRendicionItems();
    
    // Preview de imágenes
    setupImagePreviews();
});

// Inicializar tooltips de Bootstrap
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Cargar notificaciones
function loadNotifications() {
    $.ajax({
        url: '/notificaciones/api/list',
        method: 'GET',
        success: function(data) {
            updateNotificationsList(data.notificaciones);
            updateNotificationCount(data.total_no_leidas);
        },
        error: function() {
            console.error('Error al cargar notificaciones');
        }
    });
}

// Actualizar lista de notificaciones
function updateNotificationsList(notificaciones) {
    const container = $('#notificaciones-list');
    
    if (notificaciones.length === 0) {
        container.html('<p class="text-muted text-center p-3">No hay notificaciones nuevas</p>');
        return;
    }
    
    let html = '';
    notificaciones.forEach(notif => {
        html += `
            <div class="notificacion-item ${notif.leida ? '' : 'no-leida'}" data-id="${notif.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${notif.titulo}</h6>
                        <p class="mb-1 small text-muted">${notif.mensaje}</p>
                        <small class="text-muted">${timeAgo(notif.fecha_creacion)}</small>
                    </div>
                    ${!notif.leida ? `
                        <button class="btn btn-sm btn-link marcar-leida" data-id="${notif.id}">
                            <i class="bi bi-check"></i>
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    container.html(html);
    
    // Event listeners para marcar como leída
    $('.marcar-leida').click(function(e) {
        e.preventDefault();
        e.stopPropagation();
        const notifId = $(this).data('id');
        marcarNotificacionLeida(notifId);
    });
    
    // Click en notificación
    $('.notificacion-item').click(function() {
        const rendicionId = $(this).data('rendicion-id');
        if (rendicionId) {
            window.location.href = `/rendiciones/${rendicionId}`;
        }
    });
}

// Actualizar contador de notificaciones
function updateNotificationCount(count) {
    const badge = $('.navbar .badge');
    if (count > 0) {
        badge.text(count).show();
    } else {
        badge.hide();
    }
}

// Marcar notificación como leída
function marcarNotificacionLeida(id) {
    $.ajax({
        url: `/notificaciones/${id}/marcar-leida`,
        method: 'POST',
        success: function(data) {
            loadNotifications();
        },
        error: function() {
            console.error('Error al marcar notificación');
        }
    });
}

// Formatear tiempo transcurrido
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'hace unos segundos';
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `hace ${hours} hora${hours > 1 ? 's' : ''}`;
    
    const days = Math.floor(hours / 24);
    if (days < 7) return `hace ${days} día${days > 1 ? 's' : ''}`;
    
    const weeks = Math.floor(days / 7);
    if (weeks < 4) return `hace ${weeks} semana${weeks > 1 ? 's' : ''}`;
    
    const months = Math.floor(days / 30);
    if (months < 12) return `hace ${months} mes${months > 1 ? 'es' : ''}`;
    
    const years = Math.floor(days / 365);
    return `hace ${years} año${years > 1 ? 's' : ''}`;
}

// Confirmaciones de eliminación
function setupDeleteConfirmations() {
    $('.delete-confirm').click(function(e) {
        if (!confirm('¿Estás seguro de que deseas eliminar este elemento?')) {
            e.preventDefault();
            return false;
        }
    });
}

// Items de rendición dinámicos
function setupRendicionItems() {
    let itemCount = 0;
    
    $('#add-item').click(function() {
        const itemHtml = `
            <div class="item-rendicion" data-item="${itemCount}">
                <div class="row">
                    <div class="col-md-2">
                        <label class="form-label">Fecha Gasto</label>
                        <input type="date" class="form-control" name="items[${itemCount}][fecha_gasto]" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Tipo</label>
                        <select class="form-select" name="items[${itemCount}][tipo_gasto]" required>
                            <option value="">Seleccionar...</option>
                            <option value="Alimentación">Alimentación</option>
                            <option value="Transporte">Transporte</option>
                            <option value="Alojamiento">Alojamiento</option>
                            <option value="Combustible">Combustible</option>
                            <option value="Peajes">Peajes</option>
                            <option value="Estacionamiento">Estacionamiento</option>
                            <option value="Material de Oficina">Material de Oficina</option>
                            <option value="Servicios Profesionales">Servicios Profesionales</option>
                            <option value="Otros">Otros</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Descripción</label>
                        <input type="text" class="form-control" name="items[${itemCount}][descripcion]" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Monto (CLP)</label>
                        <input type="number" class="form-control" name="items[${itemCount}][monto]" step="1" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Comprobante</label>
                        <input type="file" class="form-control" name="items[${itemCount}][comprobante]" accept=".pdf,.jpg,.jpeg,.png">
                    </div>
                    <div class="col-md-1 d-flex align-items-end">
                        <button type="button" class="btn btn-danger remove-item">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-md-2">
                        <label class="form-label">Tipo Documento</label>
                        <select class="form-select" name="items[${itemCount}][tipo_documento]">
                            <option value="boleta">Boleta</option>
                            <option value="factura">Factura</option>
                            <option value="recibo">Recibo</option>
                            <option value="otro">Otro</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">N° Documento</label>
                        <input type="text" class="form-control" name="items[${itemCount}][numero_documento]">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Proveedor</label>
                        <input type="text" class="form-control" name="items[${itemCount}][proveedor]">
                    </div>
                </div>
            </div>
        `;
        
        $('#items-container').append(itemHtml);
        $('input[name="items_count"]').val(++itemCount);
        
        // Event listener para eliminar item
        $('.remove-item').last().click(function() {
            $(this).closest('.item-rendicion').remove();
        });
    });
}

// Preview de imágenes
function setupImagePreviews() {
    $('input[type="file"]').change(function(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = $(this).siblings('.image-preview');
                if (preview.length) {
                    preview.attr('src', e.target.result).show();
                }
            }.bind(this);
            reader.readAsDataURL(file);
        }
    });
}

// Mostrar spinner de carga
function showSpinner() {
    const spinner = `
        <div class="spinner-overlay">
            <div class="spinner-border text-light" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
    $('body').append(spinner);
}

// Ocultar spinner de carga
function hideSpinner() {
    $('.spinner-overlay').remove();
}

// Formatear números como moneda
function formatCurrency(value) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        minimumFractionDigits: 0
    }).format(value);
}

// Validación de formularios
function setupFormValidation() {
    $('form').submit(function() {
        const form = $(this);
        if (form[0].checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.addClass('was-validated');
    });
}

// Export functions
window.SystemRendiciones = {
    loadNotifications,
    marcarNotificacionLeida,
    showSpinner,
    hideSpinner,
    formatCurrency
};