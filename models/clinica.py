# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class clinicamascota(models.Model):
    _name = 'clinica.mascota'
    foto = fields.Image(string='Foto', help='Sube la imagen de tu mascota', max_width=60, max_height=60)
    name = fields.Char('nº Chip', required=True)
    nombre = fields.Char('Nombre', required=True)
    sexo = fields.Selection([('m', 'Macho'), ('h', 'Hembra')],
                            'Sexo')
    description = fields.Text('Observacion', groups='clinica_joan.group_veterinaria_manager')

    date = fields.Date('Fecha de Vacunacion', required=True, default=fields.Date.context_today)
    fecha = fields.Date('Fecha de Desparasitacion', required=True, default=fields.Date.context_today)
    ndueno = fields.Many2one('clinica.dueno', 'NIF Dueño', required=True)


class clinicadueno(models.Model):
    @api.depends('nacido')
    def _edad(self):
        for rec in self:
            rec.edad = datetime.date.today().year - rec.nacido.year

    _name = 'clinica.dueno'
    name = fields.Text('NIF', required=True)
    nombre = fields.Text('Nombre')
    telefono = fields.Text('Telefono')
    email = fields.Text('e-mail')
    direccion = fields.Text('Direccion')
    carta = fields.Boolean('Carta')
    mail = fields.Boolean('email')

    nacido = fields.Date('nacido', required=True, default=fields.Date.context_today)
    edad = fields.Integer('edad', compute='_edad')
    usuario = fields.Many2one('res.users', 'Usuario dueño')
    private_notes = fields.Text(groups='clinica_joan.group_veterinaria_manager')

class clinicarecetas(models.Model):
    _name = 'clinica.recetas'

    @api.depends('precio', 'unidades', 'iva')
    def _total(self):
        for rec in self:
            rec.total = rec.precio * rec.unidades + rec.iva

    @api.depends('precio', 'unidades')
    def _iva(self):
        for rec in self:
            rec.iva = rec.precio * rec.unidades * (10 / 100)

    name = fields.Text('nº Lote', required=True)
    medic = fields.Text('Medicamento')
    caduca = fields.Date('Fecha de Caducidad', required=True)
    provedor = fields.Text('Proveedor')
    precio = fields.Float(string='Precio', required=True)
    iva = fields.Float(string='IVA', compute='_iva')
    total = fields.Float(string='Total', compute='_total')
    unidades = fields.Integer(String='uds')
    chip = fields.Many2one('clinica.mascota', 'Nº Chip', required=True)
    cita = fields.Many2one('clinica.citas', 'Nº Cita', required=True)


class clinicaveterinarios(models.Model):
    _name = 'clinica.veterinarios'

    name = fields.Text('Nombre del Veterinario', required=True)
    titulo = fields.Text('Titulo de su Puesto')
    numero = fields.Text('Telefono')
    mail = fields.Text('e-mail')


class clinicacitas(models.Model):
    _name = 'clinica.citas'
    _inherit = ['mail.thread']

    @api.depends('inicio')
    def _finCita(self):
        for rec in self:
            rec.fin = rec.inicio + datetime.timedelta(minutes=30)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('clinica.citas')
        return super(clinicacitas, self).create(vals)

    name = fields.Char(string="Nº Cita", readonly=True, required=True, copy=False, default='Nueva Cita')
    chip = fields.Many2one('clinica.mascota', 'Nº Chip de la Mascota', required=True)
    veterinario = fields.Many2one('clinica.veterinarios', 'Nombre del Veterinario', required=True)
    inicio = fields.Datetime('Inicio de la cita', required=True, default=fields.Datetime.now)
    nivel = fields.Selection([('Nivel 1','Normal'), ('Nivel 2','Leve'),
                              ('Nivel 3', 'Urgencia Menor'), ('Nivel 4','Urgencia')]
                             , 'Nivel de Urgencia')
    fin = fields.Datetime('Fin de la cita', required=True, compute='_finCita', default=fields.Datetime.now)
    estado = fields.Selection([('Estado 1','Nuevo'), ('Estado 2','Anamnesis'),
                              ('Estado 3', 'Evaluación Clinica'), ('Estado 4','Investigación de diagnóstico'),
                              ('Estado 5', 'Resultados'), ('Estado 6','Tratamiento'), ('Estado 7','Hecho'), ],
                              'Evaluacion veterinaria', group_expand='_expand_states', index=True)
    description = fields.Text('Observaciones')

    """Funcion para que la vista kanban salgan todas la columnas"""
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).estado.selection]

    def recordatorio_cita(self):
        template_id = self.env.ref('clinica_joan.recordatorio_cita')
        self.message_post_with_template(template_id.id)


class clinicahospitalizacion(models.Model):
    _name = 'clinica.hospitalizacion'

    @api.depends('fechaHosp', 'nivel')
    def _fechaAlta(self):
        for rec in self:
            if rec.nivel == 'Nivel 1':
                rec.fechaAlta = rec.fechaHosp + datetime.timedelta(days=2)
            elif rec.nivel == 'Nivel 2':
                rec.fechaAlta = rec.fechaHosp + datetime.timedelta(days=5)
            elif rec.nivel == 'Nivel 3':
                rec.fechaAlta = rec.fechaHosp + datetime.timedelta(days=10)
            elif rec.nivel == 'Nivel 4':
                rec.fechaAlta = rec.fechaHosp + datetime.timedelta(days=20)
            else:
                rec.fechaAlta = rec.fechaHosp + datetime.timedelta(days=1)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('clinica.hospitalizacion')
        return super(clinicahospitalizacion, self).create(vals)

    name = fields.Char(string="Codigo de registro", readonly=True, required=True, copy=False, default='Codigo Hospitalizacion')

    fechaHosp = fields.Date('Fecha de hospitalizacion', required=True, default=fields.Date.context_today)
    paciente = fields.Many2one('clinica.mascota', 'Nº Chip de la Mascota', required=True)

    nivel = fields.Selection([('Nivel 1', 'Normal'), ('Nivel 2', 'Leve'),
                              ('Nivel 3', 'Urgencia Menor'), ('Nivel 4', 'Urgencia')]
                             , 'Nivel de Urgencia')
    fechaAlta = fields.Date('Fecha prevista de Alta', required=True, default=fields.Date.context_today, compute='_fechaAlta')
    razon = fields.Text('Razón de admision')






