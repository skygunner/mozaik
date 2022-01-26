# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mozaik: All Modules Loader",
    "summary": """
        Loads all Mozaik modules""",
    "version": "14.0.1.1.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/OCA/mozaik",
    "category": "Political Association",
    "depends": [
        # 'disable_tracking_installation',
        # 'disable_user_welcome_message',
        "inherit_abstract_view",
        # 'ir_rule_child_of',
        # 'mail_job_priority',
        "mozaik_abstract_model",
        "mozaik_account",
        "mozaik_address",
        "mozaik_address_local_street",
        "mozaik_ama_attachment",
        "mozaik_automatic_supporter",
        "mozaik_mass_mailing_automation",
        "mass_mailing_distribution_list",
        "mozaik_communication",
        "mozaik_committee",
        "mozaik_duplicate",
        "mozaik_dynamical_time_filter",
        "mozaik_event_chatter",
        "mozaik_event_involvement_category",
        "mozaik_event_question_involvement_category",
        "mozaik_event_is_private",
        "mozaik_event_membership_request_involvement",
        "mozaik_event_partner_firstname",
        "mozaik_event_publish_date",
        "mozaik_event_registration_add_zip",
        "mozaik_event_thesaurus",
        "mozaik_event_tickbox_question",
        "mozaik_graphql",
        "mozaik_involvement",
        "mozaik_involvement_followup",
        "mozaik_mass_mailing_access_rights",
        "mozaik_mass_mailing_automation",
        "mozaik_mass_mailing_template",
        "mozaik_membership",
        "mozaik_partner_assembly",
        "mozaik_partner_button_sms",
        "mozaik_partner_fields",
        "mozaik_partner_global_opt_out",
        # 'mozaik_partner_unauthorized',
        "mozaik_person",
        "mozaik_person_deceased",
        # 'mozaik_relation_coordinate',
        "mozaik_structure",
        # 'mozaik_subscription_price',
        "mozaik_thesaurus",
        "mozaik_tools",
        "mozaik_virtual_assembly_instance",
        "mozaik_virtual_partner_mandate",
        "mozaik_virtual_partner_involvement",
        "mozaik_virtual_partner_instance",
        "mozaik_virtual_partner_mass_mailing",
        "mozaik_virtual_partner_membership",
        "mozaik_virtual_partner_relation",
        # 'partner_usual_firstname',
        "mozaik_mandate",
        "mozaik_mandate_female_label",
        "mozaik_mandate_category_sequence",
        "mozaik_membership_mandate",
        "mozaik_membership_request",
        "mozaik_membership_request_autovalidate",
        "mozaik_membership_request_from_registration",
        "mozaik_petition",
        "mozaik_petition_membership_request_involvement",
        "mozaik_petition_involvement_category",
        "mozaik_petition_question_involvement_category",
        "mozaik_petition_thesaurus",
        "mozaik_survey_chatter",
        "mozaik_survey_involvement_category",
        "mozaik_survey_is_private",
        "mozaik_survey_membership_request_involvement",
        "mozaik_survey_publish_date",
        "mozaik_survey_question_involvement_category",
        "mozaik_survey_thesaurus",
        "mozaik_website_event_track",
        # "mass_mail_queue_job",
    ],
    "data": [
        # 'views/mail_followers.xml',
        "views/res_partner.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["openupgradelib"]},
}
