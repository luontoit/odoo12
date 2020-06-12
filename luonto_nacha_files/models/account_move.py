from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import base64

class AccountMove(models.Model):
    _inherit = 'account.move'

    def create_nacha_file(self):

        # Produce NACHA file only if all files are vendor bills, not customer invoices
        for record in self:
            if record.type not in ('in_invoice', 'in_refund'):
                raise ValidationError("Invalid selection: Customer invoice selected. NACHA files can only be created for vendor bills")


        with open('file.txt', 'w') as f:  # make the name unique so that it does not overwrite others
            # File Header record
            header_record_type = '1'
            priority_code = '01'
            immediate_destination = ' 123456789'                    # PNC bank transit/routing number preceded by a blank space **SHOULD BE PULLED IN FROM SETTINGS
            immediate_origin = ' 123456789'                         # Originator's tax ID preceded by a blank space **Adjust length dynamically **SHOULD BE PULLED IN FROM SETTINGS
            creation_date = datetime.now().strftime('%y%m%d')       # Date when the originator created the file **UTC TIMEZONE  ** It was the other way around in teh sample file
            creation_time = datetime.now().strftime('%H%M')         # Time when the originator created the file **UTC TIMEZONE
            file_id = 'A'                                           # IDENTIFIER TO DISTINGUISH BETWEEN FILES CREATED THE SAME DATE **TODO
            record_size = '094'                                     # NUMBER OF CHARACTERS CONTAINED IN EACH RECORD.
            blocking_factor = '10'                                  # BOCKING FACTOR DEFINES THE NUMBER OF PHYSICAL RECORDS WITHIN A FILE.
            format_code = '1'
            immediate_destination_name = 'PNC BANK'.rjust(23)
            immediate_origin_name = 'LUONTO FURNITURE'.rjust(23)
            reference_code = ' ' * 8                                # Blanks fill this field

            f.write(
                    header_record_type +
                    priority_code +
                    immediate_destination +
                    immediate_origin +
                    creation_date +
                    creation_time +
                    file_id +
                    record_size +
                    blocking_factor +
                    format_code +
                    immediate_destination_name +
                    immediate_origin_name +
                    reference_code +
                    '\n'
                    )

            # Company/Batch Header Record
            company_record_type = '5'
            service_class_code = '200'                                              # **Recheck this with consultant
            company_name = 'LUONTO FURNITURE'.rjust(16)                     # bank_id of res.partner of Vendor in account.invoice.
            company_discretionary_data = ' ' * 20
            company_identification = '1' + self.env.company.vat             # TAX ID – res.company vat field
            standard_entry_class_code = 'CCD'
            company_entry_description = "VENDOR PMT"                        # Vendor Reference on account.invoice **WAIT FOR DPI TO CONFIRM THIS
            company_descriptive_date = datetime.now().strftime('%y%m%d')
            effective_entry_date = datetime.now().strftime('%y%m%d')
            settlement_date = ' ' * 3
            originating_status_code = '1'
            originating_dfi_number = self.env.company.bank_ids.browse(3).aba_routing[:8]    # 8 first digits of aba_routing on res.partner.bank of Luonto ( our company ) ** EEEEHHHH
            batch_number = '0000001'

            f.write(
                    company_record_type +
                    service_class_code +
                    company_name +
                    company_discretionary_data +
                    company_identification +
                    standard_entry_class_code +
                    company_entry_description +
                    company_descriptive_date +
                    company_descriptive_date +
                    effective_entry_date +
                    settlement_date +
                    originating_status_code +
                    originating_dfi_number +
                    batch_number +
                    '\n'
                    )


            # Entry detail records - One record per individual vendor payment
            for i, record in enumerate(self, start=1):
                detail_record_type = '6'
                transaction_code = '22'                                                 # If we wnat to be comprehensive: '22' if (amount > 0) or '27' if (amount < 0)
                receiving_dfi_id = record.partner_id.bank_ids.browse(6).aba_routing[:8]           # FIRST 8 DIGITS OF THE RECEIVER’S BANK TRANSIT ROUTING NUMBER
                check_digit = receiving_dfi_id[-1]                                      # Last digit of aba_routing of res.partner.bank of partner
                dfi_account_number = record.partner_id.bank_ids.acc_number.ljust(17)    # pick only leftmost 17 characters
                amount = "".join(filter(str.isdigit, '%.2f' % record.amount_residual))
                individual_number = str(record.partner_id.id)
                individual_name = record.partner_id.name                                # should ask consultant if this and the previous should be the SAME. use id
                discretionary_data = ' '*2
                addenda = '0'
                trace_number = str(self.env.company.bank_ids.browse(3).aba_routing[:8]) +  str(i)                # + other 7 sequencially generated numbers

                f.write(
                        detail_record_type +
                        transaction_code +
                        receiving_dfi_id +
                        check_digit +
                        dfi_account_number +
                        str(amount).ljust(10) +
                        individual_number +
                        individual_name +
                        discretionary_data +
                        addenda +
                        trace_number +
                        '\n'
                        )

        with open('file.txt', 'rb') as f:  # Review this because it looks NASTY
            file = f.read()  # write the header
            # generate the txt file

        new_file_vals = {
            'name': 'NACHA' + datetime.now().strftime('%y%m%d') + ".txt",
            'type': 'binary',
            'res_model': 'account.move',
            'datas': base64.b64encode(file),
            'mimetype': 'text/plain',
        }

        # Link attachment to all vendor bill records after the file is created
        for record in self:
            record.write({
                'attachment_ids': [(0, 0, new_file_vals)]
            })
