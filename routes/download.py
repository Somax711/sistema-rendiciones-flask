"""
Rutas para descarga de documentos y comprobantes
Sistema de Rendiciones - Primar
"""

from flask import Blueprint, send_file, abort, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import db, Rendicion, ItemRendicion
import os
import zipfile
from io import BytesIO
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.decorators import role_required

download_bp = Blueprint('download', __name__, url_prefix='/download')


def _upload_folder():
    return os.path.join(current_app.config['UPLOAD_FOLDER'], 'comprobantes')


def get_mimetype(filename):
    extensiones = {
        '.pdf':  'application/pdf',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png':  'image/png',
        '.gif':  'image/gif',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls':  'application/vnd.ms-excel',
        '.csv':  'text/csv',
        '.zip':  'application/zip',
    }
    ext = os.path.splitext(filename)[1].lower()
    return extensiones.get(ext, 'application/octet-stream')


@download_bp.route('/comprobante/<int:item_id>', methods=['GET'])
@login_required
def descargar_comprobante(item_id):
    """Descarga el comprobante de un item de rendicion."""
    item = ItemRendicion.query.get_or_404(item_id)
    if current_user.rol == 'usuario' and item.rendicion.usuario_id != current_user.id:
        abort(403)
    if not item.comprobante:
        flash('Este item no tiene comprobante adjunto', 'warning')
        return redirect(url_for('rendiciones.ver', id=item.rendicion_id))
    archivo_path = os.path.join(_upload_folder(), item.comprobante)
    if not os.path.exists(archivo_path):
        flash('El archivo no se encuentra en el servidor', 'danger')
        return redirect(url_for('rendiciones.ver', id=item.rendicion_id))
    nombre_descarga = item.comprobante_original or item.comprobante
    return send_file(archivo_path, as_attachment=True,
                     download_name=nombre_descarga,
                     mimetype=get_mimetype(archivo_path))


@download_bp.route('/rendicion/<int:rendicion_id>/comprobantes', methods=['GET'])
@login_required
def descargar_todos_comprobantes(rendicion_id):
    """Descarga todos los comprobantes de una rendicion en ZIP."""
    rendicion = Rendicion.query.get_or_404(rendicion_id)
    if current_user.rol == 'usuario' and rendicion.usuario_id != current_user.id:
        abort(403)
    items_con_comprobantes = [i for i in rendicion.items.all() if i.comprobante]
    if not items_con_comprobantes:
        flash('Esta rendicion no tiene comprobantes adjuntos', 'warning')
        return redirect(url_for('rendiciones.ver', id=rendicion_id))
    memoria = BytesIO()
    with zipfile.ZipFile(memoria, 'w', zipfile.ZIP_DEFLATED) as zf:
        for idx, item in enumerate(items_con_comprobantes, 1):
            archivo_path = os.path.join(_upload_folder(), item.comprobante)
            if os.path.exists(archivo_path):
                ext = os.path.splitext(item.comprobante)[1]
                desc_segura = secure_filename(item.descripcion[:40]) or f'item_{idx}'
                zf.write(archivo_path, f"{idx:02d}_{desc_segura}{ext}")
    memoria.seek(0)
    fecha = datetime.now().strftime('%Y%m%d')
    return send_file(memoria, mimetype='application/zip', as_attachment=True,
                     download_name=f"Comprobantes_{rendicion.numero_rendicion}_{fecha}.zip")


@download_bp.route('/rendicion/<int:rendicion_id>/pdf', methods=['GET'])
@login_required
def descargar_rendicion_pdf(rendicion_id):
    """Genera y descarga PDF completo de la rendicion (para validadores)."""
    rendicion = Rendicion.query.get_or_404(rendicion_id)
    if current_user.rol == 'usuario' and rendicion.usuario_id != current_user.id:
        abort(403)
    try:
        pdf_bytes = _generar_pdf_rendicion(rendicion)
    except Exception as e:
        flash(f'Error al generar el PDF: {str(e)}', 'danger')
        return redirect(url_for('rendiciones.ver', id=rendicion_id))
    fecha = datetime.now().strftime('%Y%m%d')
    nombre_pdf = f"Rendicion_{rendicion.numero_rendicion}_{fecha}.pdf"
    return send_file(BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name=nombre_pdf)


def _generar_pdf_rendicion(rendicion):
    """Genera PDF de rendicion con ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer, HRFlowable)
    from reportlab.lib.enums import TA_CENTER

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    AZUL  = colors.HexColor('#0d6efd')
    GRIS  = colors.HexColor('#6c757d')
    CELESTE = colors.HexColor('#e8f0fe')

    s_titulo    = ParagraphStyle('T', parent=styles['Title'],
                                 fontSize=18, textColor=AZUL, spaceAfter=4)
    s_sub       = ParagraphStyle('S', parent=styles['Normal'],
                                 fontSize=11, textColor=GRIS, spaceAfter=12)
    s_seccion   = ParagraphStyle('SEC', parent=styles['Heading2'],
                                 fontSize=11, textColor=AZUL, spaceBefore=10, spaceAfter=4)
    s_normal    = styles['Normal']
    s_pie       = ParagraphStyle('PIE', parent=styles['Normal'],
                                 fontSize=8, textColor=GRIS)

    def fmt(v):
        try:
            return "$ {:,.0f}".format(float(v)).replace(',', '.')
        except Exception:
            return str(v)

    items = rendicion.items.all()
    E = []

    # Encabezado
    E.append(Paragraph('Sistema de Rendiciones Primar', s_titulo))
    E.append(Paragraph(f'Rendicion N\u00b0 {rendicion.numero_rendicion}', s_sub))
    E.append(HRFlowable(width='100%', thickness=1, color=AZUL))
    E.append(Spacer(1, 0.4*cm))

    # Info general
    info = [
        ['Colaborador', rendicion.usuario.nombre if rendicion.usuario else '-',
         'Estado', rendicion.get_estado_display()],
        ['Periodo',
         f"{rendicion.fecha_inicio.strftime('%d/%m/%Y')} - {rendicion.fecha_fin.strftime('%d/%m/%Y')}",
         'Creacion', rendicion.fecha_creacion.strftime('%d/%m/%Y') if rendicion.fecha_creacion else '-'],
        ['Proyecto', rendicion.proyecto or '-',
         'Centro costo', rendicion.centro_costo or '-'],
    ]
    if rendicion.aprobador:
        info.append(['Aprobador', rendicion.aprobador.nombre,
                     'Fecha aprob.',
                     rendicion.fecha_aprobacion.strftime('%d/%m/%Y') if rendicion.fecha_aprobacion else '-'])
    if rendicion.descripcion:
        info.append(['Descripcion', Paragraph(rendicion.descripcion, s_normal), '', ''])

    t_info = Table(info, colWidths=[3.5*cm, 7.5*cm, 3.5*cm, 4*cm])
    t_info.setStyle(TableStyle([
        ('FONTNAME', (0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE', (0,0),(-1,-1), 9),
        ('FONTNAME', (0,0),(0,-1),'Helvetica-Bold'),
        ('FONTNAME', (2,0),(2,-1),'Helvetica-Bold'),
        ('TEXTCOLOR',(0,0),(0,-1), AZUL),
        ('TEXTCOLOR',(2,0),(2,-1), AZUL),
        ('VALIGN',   (0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.white, CELESTE]),
        ('TOPPADDING',   (0,0),(-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
    ]))
    E.append(t_info)
    E.append(Spacer(1, 0.5*cm))

    # Tabla de items
    E.append(Paragraph('Detalle de Gastos', s_seccion))
    E.append(HRFlowable(width='100%', thickness=0.5, color=GRIS))
    E.append(Spacer(1, 0.2*cm))

    cab  = ['#','Fecha','Tipo','Descripcion','Proveedor','Doc.','N\u00b0 Doc.','Monto']
    rows = [cab]
    total = 0
    for idx, it in enumerate(items, 1):
        rows.append([
            str(idx),
            it.fecha_gasto.strftime('%d/%m/%Y') if it.fecha_gasto else '-',
            it.tipo_gasto or '-',
            Paragraph(it.descripcion or '-', s_normal),
            it.proveedor or '-',
            it.get_tipo_documento_display(),
            it.numero_documento or '-',
            fmt(it.monto),
        ])
        try:
            total += float(it.monto)
        except Exception:
            pass
    rows.append(['','','','','','','TOTAL', fmt(total)])

    t_items = Table(rows,
                    colWidths=[0.6*cm,2.2*cm,2.8*cm,5*cm,2.8*cm,1.6*cm,2*cm,2.5*cm],
                    repeatRows=1)
    t_items.setStyle(TableStyle([
        ('BACKGROUND',  (0,0),(-1,0), AZUL),
        ('TEXTCOLOR',   (0,0),(-1,0), colors.white),
        ('FONTNAME',    (0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',    (0,0),(-1,0), 8),
        ('ALIGN',       (0,0),(-1,0),'CENTER'),
        ('FONTNAME',    (0,1),(-1,-2),'Helvetica'),
        ('FONTSIZE',    (0,1),(-1,-2), 8),
        ('ROWBACKGROUNDS',(0,1),(-1,-2),[colors.white, CELESTE]),
        ('VALIGN',      (0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',       (7,0),(7,-1),'RIGHT'),
        ('ALIGN',       (0,1),(0,-1),'CENTER'),
        ('BACKGROUND',  (0,-1),(-1,-1), colors.HexColor('#d1e7dd')),
        ('FONTNAME',    (6,-1),(7,-1),'Helvetica-Bold'),
        ('FONTSIZE',    (6,-1),(7,-1), 9),
        ('ALIGN',       (6,-1),(7,-1),'RIGHT'),
        ('GRID',        (0,0),(-1,-1), 0.4, colors.HexColor('#dee2e6')),
        ('TOPPADDING',  (0,0),(-1,-1), 4),
        ('BOTTOMPADDING',(0,0),(-1,-1), 4),
    ]))
    E.append(t_items)
    E.append(Spacer(1, 0.6*cm))

    # Comentarios
    if rendicion.comentarios_aprobador:
        E.append(Paragraph('Comentarios del Aprobador', s_seccion))
        E.append(HRFlowable(width='100%', thickness=0.5, color=GRIS))
        E.append(Spacer(1, 0.2*cm))
        E.append(Paragraph(rendicion.comentarios_aprobador, s_normal))
        E.append(Spacer(1, 0.5*cm))

    # Pie
    n_comp = sum(1 for i in items if i.comprobante)
    E.append(HRFlowable(width='100%', thickness=0.5, color=GRIS))
    E.append(Spacer(1, 0.2*cm))
    E.append(Paragraph(
        f'Comprobantes adjuntos: {n_comp}  |  '
        f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', s_pie))

    doc.build(E)
    return buffer.getvalue()


@download_bp.route('/reporte/<tipo>/<formato>', methods=['GET'])
@login_required
@role_required(['admin', 'aprobador'])
def descargar_reporte(tipo, formato):
    from flask import request
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    estado      = request.args.get('estado')
    usuario_id  = request.args.get('usuario_id')

    if formato not in ['xlsx','pdf','csv'] or tipo not in ['rendiciones','usuarios','aprobaciones','gastos']:
        flash('Tipo o formato no valido', 'danger')
        return redirect(url_for('reportes.index'))

    archivo_path = None
    try:
        if tipo == 'rendiciones':
            from utils.reportes import generar_reporte_rendiciones
            archivo_path, nombre = generar_reporte_rendiciones(
                formato=formato, fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta, estado=estado, usuario_id=usuario_id)
        elif tipo == 'usuarios':
            from utils.reportes import generar_reporte_usuarios
            archivo_path, nombre = generar_reporte_usuarios(formato=formato)
        elif tipo == 'aprobaciones':
            from utils.reportes import generar_reporte_aprobaciones
            archivo_path, nombre = generar_reporte_aprobaciones(
                formato=formato, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        elif tipo == 'gastos':
            from utils.reportes import generar_reporte_gastos
            archivo_path, nombre = generar_reporte_gastos(
                formato=formato, fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta, usuario_id=usuario_id)

        if not os.path.exists(archivo_path):
            flash('Error al generar el reporte', 'danger')
            return redirect(url_for('reportes.index'))

        return send_file(archivo_path, as_attachment=True,
                         download_name=nombre, mimetype=get_mimetype(archivo_path))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('reportes.index'))
    finally:
        if archivo_path and os.path.exists(archivo_path):
            try:
                os.remove(archivo_path)
            except Exception:
                pass


@download_bp.route('/plantilla/<tipo>', methods=['GET'])
@login_required
def descargar_plantilla(tipo):
    plantillas = {'rendiciones':'plantilla_rendiciones.xlsx',
                  'items':'plantilla_items.xlsx',
                  'usuarios':'plantilla_usuarios.xlsx'}
    if tipo not in plantillas:
        flash('Plantilla no encontrada', 'danger')
        return redirect(url_for('dashboard.index'))
    d = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'plantillas')
    p = os.path.join(d, plantillas[tipo])
    if not os.path.exists(p):
        flash('El archivo de plantilla no existe', 'danger')
        return redirect(url_for('dashboard.index'))
    return send_file(p, as_attachment=True, download_name=plantillas[tipo],
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
