# -*- coding: utf-8 -*-
##############################################################################
#
#    Módulo Docentes para Odoo
#    Copyright (C) Araceli Acosta.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
#from odoo.addons.docentes.models.base import Base



NONE = 'none'
NUEVO = 'nuevo'
HIST = 'hist'
BAJA = 'baja'
PEND_B = 'pend_b'
PEND_A = 'pend_a'
PASIVO = 'pasivo'
JUB = 'jub'
JUBA = 'juba'
ACTIVO = 'activo'
BECARIEA = 'becariea'
BECARIE = 'becarie'
CONTRATADEA = 'contratadea'
CONTRATADE = 'contratade'

STATE = [
    (NUEVO, 'Docente nuevo/a'),
    (NONE, 'No afiliade'),
    (HIST, 'Histórico'),
    (BAJA, 'Desafiliade'),
    (PEND_B, 'Pendiente de baja'),
    (PEND_A, 'Pendiente de alta'),
    (PASIVO, 'No cotizante'),
    (JUB, 'Jubilade no cotizante'),
    (JUBA, 'Jubilade cotizante'),
    (ACTIVO, 'Activo'),
    (BECARIEA, 'Becarie cotizante'),
    (BECARIE, 'Becarie no cotizante'),
    (CONTRATADEA, 'Contratade cotizante'),
    (CONTRATADE, 'Contratade no cotizante')
]




TIPODOC = [('dni','DNI'),('lc','LC'),('le','LE'),('pas','PAS'),('ci','CI')]
ESTCIV = [('c', 'Casada/o'),('s','Soltera/o'), ('u', 'Unida/o'),('v', 'Viuda/o'),('d', 'Divorciada/o'),('p','Separada/o'),('n','Prefiere no decirlo')]
SEXO = [('f', 'Femenino'),('m','Masculino'), ('o', 'Otro'),('n','Prefiere no decirlo')]


class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'
#    _name="model.docente"

    email2 = fields.Char('Otro Correo electrónico', size=240)
    esdocente = fields.Boolean('¿Es docente?',
      default=False)
    legajo = fields.Integer('Legajo', readonly=True)
    tipodni = fields.Selection(TIPODOC,'Tipo doc')
    dni = fields.Integer('N documento')
    estadocivil = fields.Selection(ESTCIV,'Estado civil')
    sexo = fields.Selection(SEXO,'Sexo')
    fecha_nacimiento = fields.Date('Fecha de nacimiento')
    pais = fields.Many2one('res.country','País de nacimiento')
    afiliado = fields.Integer('N afiliado')
    afiliados_ant = fields.Char('N afiliado anteriores',size=240,readonly=True)
    fecha_alta = fields.Date('Fecha de alta',readonly=True)
    fecha_baja = fields.Date('Fecha de baja',readonly=True)
    antiguedad = fields.Date('Antigüedad')
    estado = fields.Selection(STATE,
      string='Estado de afiliación',
      readonly=True,
      default=NONE)
    observado = fields.Boolean('Observado?')
    observacion = fields.Char('Observación', size=240)
    aportes = fields.One2many('docentes.aportes', 'docente', string='Aportes docente')
#para docentes
    hijo_id = fields.Many2many('docentes.hijos', column1='partner_id',
                                    column2='hijo_id', string='Menores a cargo')


    def _solicitarCambio(self, **args):
      # El método self.write actualiza el campo en la interfaz
      self.write(args)
      return True

    @api.multi
    def funcionSolicitarAfiliacion(self):
      return self._solicitarCambio(
              estado=PEND_A,
              fecha_alta=time.strftime('%Y-%m-%d')
            )

    @api.multi
    def funcionSolicitarDesafiliacion(self):
      today = time.strftime('%Y-%m-%d')
      return self._solicitarCambio(estado=PEND_B, fecha_baja=today)

    @api.multi
    def funcionConfirmarAfiliacion(self):
      # El método self.write actualiza el campo en la interfaz
      reads = self.read(['afiliados_ant', 'afiliado'])
      for record in reads:
            afil = str(record['afiliado'])
            if record['afiliados_ant']:
                afil = record['afiliados_ant'] + ', ' + afil
      self.write({'estado': ACTIVO,'afiliados_ant': afil})
      return True # Siempre tenemos que retornar True al final de la declaración
    
    @api.multi
    def funcionConfirmarDesafiliacion(self):
      return self._solicitarCambio(estado=BAJA)

    @api.multi 
    def funcionActivoaPasivo(self):
      return self._solicitarCambio(estado=PASIVO)

    @api.multi
    def funcionActivoaJubilado(self):
      return self._solicitarCambio(estado=JUB)

    @api.multi
    def funcionPasivoaActivo(self):
      return self._solicitarCambio(estado=ACTIVO)

    @api.multi 
    def funcionPasivoaHistorico(self):
      return self._solicitarCambio(estado=HIST)
    
    @api.multi 
    def funcionJubiladoaHistorico(self):
      return self._solicitarCambio(estado=HIST) # Siempre tenemos que retornar True al final de la declaración

    @api.multi
    def funcionJubiladoaCotizante(self):
      return self._solicitarCambio(estado=JUBA)

    @api.multi
    def funcionJubiladoaNoCotizante(self):
      return self._solicitarCambio(estado=JUB)

    @api.multi
    def funcionPasivoaCotizante(self):
      return self._solicitarCambio(estado=ACTIVO)

    @api.multi
    def funcionJubilar(self):
      return self._solicitarCambio(estado=JUB)

    @api.multi
    def funcionAfiladoaNoCotizante(self):
      return self._solicitarCambio(estado=PASIVO)

    @api.multi
    def funcionBecario(self):
      return self._solicitarCambio(estado=BECARIE)

    @api.multi
    def funcionBecarioaActivo(self):
      return self._solicitarCambio(estado=BECARIEA)

    @api.multi
    def funcionContratado(self):
      return self._solicitarCambio(estado=CONTRATADE)

    @api.multi
    def funcionContratadoaActivo(self):
      return self._solicitarCambio(estado=CONTRATADEA)
    
    @api.multi
    def funcionCrearDocente(self):
      return self._solicitarCambio(estado=NONE, esdocente=True)

#    @api.multi
#    def write(self, vals):
#      docente_gestion = Base(self.env['docentes.gestion_de_cambios']).get(
#        {'docente': self.id}
#      )
#      if docente_gestion:
#        ## borramos de la gestion de cambio
#        docente_gestion.unlink()
#      return super(Partner, self).write(vals)


#Partner()

class DocentesHijos(models.Model):
    """
    Hijos, hijas y menores a cargo de docentes afiliados
    """
    _name = 'docentes.hijos'
    _order = 'fecha_nac, name'
    _description = 'Modelo para los hijos'

#    docente = fields.Many2one('res.partner',
#        string='Docente',
#        ondelete='cascade')

    padres = fields.Many2many('res.partner', column1='hijo_id', column2='partner_id', string='Padres')


    name = fields.Char('Nombre', size=30, required=True)
    dni = fields.Integer('N documento', required=True)
    fecha_nac = fields.Date('Fecha de nacimiento')
    discapacidad = fields.Boolean('Discapacidad')
    verificado = fields.Boolean('Verificado')
    observaciones = fields.Char('Observaciones')

#    bolsones = fields.One2many('docentes.bolsones', 'hijo', string='Bolsones')

    #para bolsones
#    bolsones = fields.Many2one('docentes.bolsones', string='Docente', ondelete='cascade')


