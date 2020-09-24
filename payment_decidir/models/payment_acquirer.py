from odoo import fields, models, api, _
import sha
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

DECIDIR_URL = 'https://sps.decidir.com/sps-ar/Validar'
DECIDIR_METHODS = [('0', 'SIN PASARELA'),
                   ('1', 'VISA'),
                   ('6', 'AMEX'),
                   ('8', 'DINERS'),
                   ('15', 'MASTERCARD'),
                   ('20', 'MASTERCARD TEST'),
                   ('23', 'SHOPPING'),
                   ('24', 'NARANJA'),
                   ('25', 'PAGO FACIL'),
                   ('26', 'RAPI PAGO'),
                   ('27', 'CABAL'),
                   ('29', 'ITALCRED'),
                   ('31', 'VISA DEBITO'),
                   ('34', 'COOPEPLUS'),
                   ('36', 'ARCASH'),
                   ('37', 'NEXO'),
                   ('38', 'CREDIMAS'),
                   ('39', 'NEVADA'),
                   ('41', 'PAGO MISCUENTAS'),
                   ('42', 'NATIVA'),
                   ('43', 'MAS')
                   ]


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    provider = fields.Selection(
        selection_add=[('decidir', 'Decidir 1.0')],
    )

    sps_payment_method = fields.Selection(
        DECIDIR_METHODS, string='Decidir payment method')

    sps_payment_plan = fields.Integer(
        string='Plan',
    )

    def decidir_compute_fees(self, amount, currency_id, country_id):
        self.ensure_one()
        if not self.fees_active:
            return 0.0

        percentage = self.fees_dom_var
        fixed = self.fees_dom_fixed

        fees = percentage / 100.0 * amount + fixed
        return fees

    def decidir_form_generate_values(self, values):
        self.ensure_one()
        tx_values = dict(values)

        comerce_number = self.env['ir.config_parameter'].get_param(
            'decidir.comerce_number')
        comerce_sha = self.env['ir.config_parameter'].get_param(
            'decidir.comerce_sha')

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        new_values = {'NROCOMERCIO': comerce_number,
                      'EMAILCLIENTE': values['partner_email'],
                      }

        nrooperacion = self.env['ir.sequence'].next_by_code('payment.tx')

        new_values['MONTO'] = (
            "%.2f" % (tx_values["amount"] + tx_values['fees'])).replace('.', '')
        new_values['CUOTAS'] = '%02d' % self.sps_payment_plan
        new_values['MEDIODEPAGO'] = self.sps_payment_method
        new_values['NROOPERACION'] = '%s' % nrooperacion
        new_values['URLDINAMICA'] = '%s/sps/endop/%s' % (base_url, nrooperacion)

        new_values['IDTRANSACCION'] = sha.new("|NROCOMERCIO:%s|MONTO:%s|MEDIODEPAGO:%s|NROOPERACION:%s|CUOTAS:%s|CLAVE:%s|" % (
            new_values['NROCOMERCIO'],
            new_values['MONTO'],
            new_values['MEDIODEPAGO'],
            new_values['NROOPERACION'],
            new_values['CUOTAS'],
            comerce_sha,
        )).hexdigest()
        tx_values.update(new_values)

        return tx_values

    def decidir_get_form_action_url(self, cr, uid, id, context=None):
        return DECIDIR_URL


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _decidir_form_get_tx_from_data(self, data):
        reference = data.get('NROOPERACION')
        if not reference:
            error_msg = _('Decidir: received data with missing operation number')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        res = {
            'acquirer_reference': data.get('NROOPERACION'),
        }
        return self.write(res)
