/*
 * Download Manager
 * Gestor de descargas de archivos para el Sistema de Rendiciones
 */

class DownloadManager {
    constructor() {
        this.downloadQueue = [];
        this.isDownloading = false;
    }

    /**
     * Descarga un comprobante individual
     * @param {number} itemId 
     * @param {string} descripcion 
     */
    descargarComprobante(itemId, descripcion) {
        const url = `/download/comprobante/${itemId}`;
        
        // Mostrar indicador de descarga
        this.mostrarDescargando(descripcion);
        
        // Realizar descarga
        window.location.href = url;
        
        // Ocultar indicador después de un tiempo
        setTimeout(() => {
            this.ocultarDescargando();
        }, 2000);
    }

    /**
     * Descarga todos los comprobantes de una rendición
     * @param {number} rendicionId 
     * @param {string} numeroRendicion 
     */
    descargarTodosComprobantes(rendicionId, numeroRendicion) {
        const url = `/download/rendicion/${rendicionId}/todos`;
        
        // Mostrar indicador
        Swal.fire({
            title: 'Preparando descarga...',
            html: `Generando archivo ZIP con los comprobantes de la rendición ${numeroRendicion}`,
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Realizar descarga
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al descargar archivos');
                }
                return response.blob();
            })
            .then(blob => {
                // Crear URL temporal
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `Rendicion_${numeroRendicion}_Comprobantes.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                
                // Mostrar éxito
                Swal.fire({
                    title: '¡Descarga completada!',
                    text: 'Los comprobantes se han descargado correctamente',
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false
                });
            })
            .catch(error => {
                Swal.fire({
                    title: 'Error',
                    text: 'No se pudieron descargar los comprobantes',
                    icon: 'error'
                });
                console.error('Error:', error);
            });
    }

    /**
     * @param {string} tipo 
     * @param {string} formato 
     * @param {object} filtros 
     */
    descargarReporte(tipo, formato, filtros = {}) {
        // Construir URL con parámetros
        const params = new URLSearchParams(filtros);
        const url = `/download/reporte/${tipo}/${formato}?${params.toString()}`;
        
        // Mostrar indicador
        Swal.fire({
            title: 'Generando reporte...',
            html: `Por favor espere mientras se genera el reporte en formato ${formato.toUpperCase()}`,
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });
        
        // Realizar descarga
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al generar reporte');
                }
                return response.blob();
            })
            .then(blob => {
                // Crear URL temporal
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = `Reporte_${tipo}_${new Date().getTime()}.${formato}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                
                // Mostrar éxito
                Swal.fire({
                    title: '¡Reporte generado!',
                    text: 'El reporte se ha descargado correctamente',
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false
                });
            })
            .catch(error => {
                Swal.fire({
                    title: 'Error',
                    text: 'No se pudo generar el reporte',
                    icon: 'error'
                });
                console.error('Error:', error);
            });
    }

    /**
     * Descarga una plantilla
     * @param {string} tipo 
     */
    descargarPlantilla(tipo) {
        const url = `/download/plantilla/${tipo}`;
        
        // Mostrar indicador
        this.mostrarDescargando(`Plantilla de ${tipo}`);
        
        // Realizar descarga
        window.location.href = url;
        
        // Ocultar indicador
        setTimeout(() => {
            this.ocultarDescargando();
        }, 2000);
    }

    /**
     * Muestra indicador de descarga
     * @param {string} nombreArchivo
     */
    mostrarDescargando(nombreArchivo) {
        // Crear toast de Bootstrap
        const toastHtml = `
            <div class="toast-container position-fixed bottom-0 end-0 p-3">
                <div id="downloadToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-primary text-white">
                        <i class="fas fa-download me-2"></i>
                        <strong class="me-auto">Descargando</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        ${nombreArchivo}
                    </div>
                </div>
            </div>
        `;
        
        // Agregar al DOM si no existe
        if (!document.getElementById('downloadToast')) {
            document.body.insertAdjacentHTML('beforeend', toastHtml);
        }
        
        // Mostrar toast
        const toastElement = document.getElementById('downloadToast');
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }

 

    ocultarDescargando() {
        const toastElement = document.getElementById('downloadToast');
        if (toastElement) {
            const toast = bootstrap.Toast.getInstance(toastElement);
            if (toast) {
                toast.hide();
            }
        }
    }

    /**
     * @param {string} url 
     * @param {string} tipo 
     */
    vistaPrevia(url, tipo) {
        const modalHtml = `
            <div class="modal fade" id="previewModal" tabindex="-1">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Vista Previa</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${this.generarVistaPrevia(url, tipo)}
                        </div>
                        <div class="modal-footer">
                            <a href="${url}" class="btn btn-primary" download>
                                <i class="fas fa-download me-1"></i> Descargar
                            </a>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Agregar al DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('previewModal'));
        modal.show();
        
        // Limpiar al cerrar
        document.getElementById('previewModal').addEventListener('hidden.bs.modal', function () {
            this.remove();
        });
    }

    /**
     * @param {string} url 
     * @param {string} tipo 
     * @returns {string} 
     */
    generarVistaPrevia(url, tipo) {
        const extension = tipo.toLowerCase();
        
        if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) {
            return `<img src="${url}" class="img-fluid" alt="Vista previa">`;
        } else if (extension === 'pdf') {
            return `
                <iframe src="${url}" 
                        style="width: 100%; height: 600px;" 
                        frameborder="0">
                </iframe>
            `;
        } else {
            return `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Vista previa no disponible para este tipo de archivo.
                    <br><br>
                    <a href="${url}" class="btn btn-primary" download>
                        <i class="fas fa-download me-1"></i> Descargar Archivo
                    </a>
                </div>
            `;
        }
    }

    /**
     * @param {string} url 
     * @param {number} maxSize 
     * @returns {Promise<boolean>}
     */
    async validarTamano(url, maxSize = 50) {
        try {
            const response = await fetch(url, { method: 'HEAD' });
            const size = parseInt(response.headers.get('content-length'), 10);
            const sizeMB = size / (1024 * 1024);
            
            if (sizeMB > maxSize) {
                const confirmar = await Swal.fire({
                    title: 'Archivo grande',
                    html: `El archivo pesa ${sizeMB.toFixed(2)} MB.<br>¿Desea continuar con la descarga?`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, descargar',
                    cancelButtonText: 'Cancelar'
                });
                
                return confirmar.isConfirmed;
            }
            
            return true;
        } catch (error) {
            console.error('Error al validar tamaño:', error);
            return true; 
        }
    }
}

// Instancia global
const downloadManager = new DownloadManager();

// Funciones auxiliares globales para facilitar uso
function descargarComprobante(itemId, descripcion) {
    downloadManager.descargarComprobante(itemId, descripcion);
}

function descargarTodosComprobantes(rendicionId, numeroRendicion) {
    downloadManager.descargarTodosComprobantes(rendicionId, numeroRendicion);
}

function descargarReporte(tipo, formato, filtros) {
    downloadManager.descargarReporte(tipo, formato, filtros);
}

function descargarPlantilla(tipo) {
    downloadManager.descargarPlantilla(tipo);
}

function vistaPrevia(url, tipo) {
    downloadManager.vistaPrevia(url, tipo);
}