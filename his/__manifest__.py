{
    'name': 'Clinic - Hospital Management System ( HIS by Mate )',
    'summary': 'Hospital Management System for managing Hospital and medical facilities flows',
    'description': """
        Hospital Management System for managing Hospital and medical facilities flows
        Medical Flows His Clinic Management Manage Clinic

        This module helps you to manage your hospitals and clinics which includes managing
        Patient details, Doctor details, Prescriptions, Treatments, Appointments with concerned doctors,
        Invoices for the patients. You can also define the medical alerts of a patient and get warining in appointment,treatments and prescriptions. It includes all the basic features required in Health Care industry.

        healthcare services healthcare administration healthcare management health department
        hospital management information system hospital management odoo his odoo medical alert
    """,
    'version': '1.0.16',
    'category': 'Medical',
    'author': 'Mate Technology JSC',
    'support': 'info@mate.com.vn',
    'website': 'https://mate.com.vn',
    'live_test_url': 'https://www.youtube.com/watch?v=hiumJoDEHxI',
    'license': 'OPL-1',
    'depends': ['his_base', 'web_timer_widget', 'website', 'digest'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/patient_cardreport.xml',
        'report/report_prescription.xml',
        'report/report_medical_advice.xml',
        'report/appointment_report.xml',
        'report/evaluation_report.xml',
        'report/treatment_report.xml',
        'report/procedure_report.xml',
        'report/medicines_label_report.xml',

        'data/sequence.xml',
        'data/mail_template.xml',
        'data/his_data.xml',
        'data/digest_data.xml',

        'wizard/cancel_reason_view.xml',
        'wizard/pain_level_view.xml',
        'wizard/reschedule_appointments_view.xml',

        'views/his_base_views.xml',
        'views/patient_view.xml',
        'views/physician_view.xml',
        'views/evaluation_view.xml',
        'views/appointment_view.xml',
        'views/diseases_view.xml',
        'views/medicament_view.xml',
        'views/prescription_view.xml',
        'views/medication_view.xml',
        'views/treatment_view.xml',
        'views/procedure_view.xml',
        'views/resource_cal.xml',
        'views/medical_alert.xml',
        'views/allergy_view.xml',
        'views/account_view.xml',
        'views/product_kit_view.xml',
        'views/template.xml',
        'views/res_config_settings_views.xml',
        'views/digest_view.xml',
        'views/res_users.xml',
        'views/company_view.xml',
        'views/menu_item.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'his/static/src/js/his_graph_field.js',
            'his/static/src/js/his_graph_field.xml',
            'his/static/src/js/his_graph_field.scss',
            'his/static/src/scss/custom.scss',
        ]
    },
    'demo': [
        'demo/diseases_category_demo.xml',
        'demo/doctor_demo.xml',
        'demo/patient_demo.xml',
        'demo/appointment_demo.xml',
        'demo/medicament_demo.xml',
        'demo/treatment_demo.xml',
    ],
    'images': [
        'static/description/his_mate_cover.gif',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 36,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
