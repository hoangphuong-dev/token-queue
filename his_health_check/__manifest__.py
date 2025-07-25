{
    'name': 'Health check',
    'category': 'Medical',
    'summary': 'Manage Medical Surgery related operations',
    'description': """
    Manage Medical Surgery related operations hospital management system medical
    """,
    'version': '1.0.4',
    'author': 'MateJSC',
    'license': 'OPL-1',
    'depends': ['his_base', 'his', 'website'],
    'data': [
        'security/ir.model.access.csv',

        # views
        'views/hide_menus.xml',
        'views/department_view.xml',
        'views/package_view.xml',
        'views/group_sequence_view.xml',
        'views/patient_view.xml',
        'views/department_kanban_view.xml',
        'views/specialty_view.xml',
        'views/physician_view.xml',
        'views/schedule_view.xml',
        'views/appointment_view.xml',

        # menu items
        'views/menu_item.xml',

        # wizard
        'wizard/create_department_wizard.xml',
        'wizard/create_group_sequence_wizard.xml',
        'wizard/create_package_wizard.xml',

        # data seeding
        'data/data.xml',
        'demo/demo_physician.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/his_health_check/static/src/components/**/*',
            '/his_health_check/static/src/scss/patient_form.scss',
            '/his_health_check/static/src/scss/department_kanban.scss',
        ],
    },
    'sequence': 1,
    'application': True,
}
