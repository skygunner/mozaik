# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: All Modules Loader',
    'summary': """
        Loads all Mozaik modules""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'disable_tracking_installation',
        'disable_user_welcome_message',
        'distribution_list',
        'inherit_abstract_view',
        'mail_job_priority',
        'mass_mail_queue_job',
        'mass_mailing_distribution_list',
        'mozaik_abstract_model',
        'mozaik_address',
        'mozaik_address_local_street',
        'mozaik_coordinate',
        'mozaik_duplicate',
        'mozaik_email',
        'mozaik_involvement',
        'mozaik_partner_assembly',
        'mozaik_partner_fields',
        'mozaik_partner_unauthorized',
        'mozaik_person',
        'mozaik_phone',
        'mozaik_structure',
        'mozaik_thesaurus',
        'mozaik_tools',
        'partner_usual_firstname',
    ],
    'data': [
        'views/mail_followers.xml',
    ],
    'installable': True,
}
