from odoo import models, fields, _
from odoo.exceptions import UserError
import base64
import pandas as pd


class ImportInvoiceWizard(models.TransientModel):
    _name = 'import.invoice.wizard'
    _description = 'Wizard to import invoices from Excel file'

    file = fields.Binary(string="Excel File", required=True)
    file_name = fields.Char(string="File Name")

    def import_file(self):
        if not self.file:
            raise UserError(_("Please upload a valid Excel file."))

        # Decodifica el archivo y lee su contenido con Pandas
        file_content = base64.b64decode(self.file)
        try:
            df = pd.read_excel(file_content)
        except Exception as e:
            raise UserError(_("Could not read the Excel file: %s") % str(e))

        # Procesa cada fila de forma individual
        for index, row in df.iterrows():
            # Realiza validaciones y transformaciones antes de crear la factura
            if 'ClienteID' not in row or pd.isna(row['ClienteID']):
                raise UserError(_("The 'ClienteID' field is required in row %s.") % (index + 1))
            if 'Fecha' not in row or pd.isna(row['Fecha']):
                raise UserError(_("The 'Fecha' field is required in row %s.") % (index + 1))
            if 'ProductoID' not in row or pd.isna(row['ProductoID']):
                raise UserError(_("The 'ProductoID' field is required in row %s.") % (index + 1))

            # Tratamiento y ajuste de datos antes de importar
            partner_id = self.env['res.partner'].search([('id', '=', int(row['ClienteID']))], limit=1)
            product_id = self.env['product.product'].search([('id', '=', int(row['ProductoID']))], limit=1)

            if not partner_id:
                raise UserError(_("Partner with ID %s not found for row %s.") % (row['ClienteID'], index + 1))
            if not product_id:
                raise UserError(_("Product with ID %s not found for row %s.") % (row['ProductoID'], index + 1))

            # Crea la factura para cada fila después del procesamiento
            invoice_data = {
                'partner_id': partner_id.id,
                'move_type': 'out_invoice',
                'invoice_date': row['Fecha'],
                'invoice_line_ids': [(0, 0, {
                    'product_id': product_id.id,
                    'quantity': row['Cantidad'] if 'Cantidad' in row and not pd.isna(row['Cantidad']) else 1,
                    'price_unit': row['Precio'] if 'Precio' in row and not pd.isna(
                        row['Precio']) else product_id.lst_price,
                })],
            }

            # Crea la factura en Odoo
            self.env['account.move'].create(invoice_data)

        # Mensaje de éxito después de completar la importación
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Invoices Imported'),
                'message': _('All rows from the Excel file were successfully imported as invoices.'),
                'sticky': False,
            }
        }
