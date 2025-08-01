# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
HIS_PATIENT = "his.patient"
DISEASES_CATEGORY = "diseases.category"
HIS_DISEASES = "his.diseases"


class MateDiseases(models.Model):
    _name = HIS_DISEASES
    _description = "Diseases"
    _rec_names_search = ['name', 'code']
    _order = "sequence"

    category_id = fields.Many2one(DISEASES_CATEGORY, string='Category', ondelete='cascade', help='Select the category for this disease This is usually, associated to the standard. For instance, the chapter on the ICD-10, will be the main category for the disease')
    info = fields.Text(string='Extra Info')
    code = fields.Char(string='Code', help='Specific Code for the Disease (eg, Code for ICD-10)', index=True)
    name = fields.Char(string='Name', required=True, translate=True, help='Disease name', index=True)
    protein = fields.Char(string='Protein involved', help='Name of the protein(s) affected')
    gene = fields.Char(string='Gene')
    chromosome = fields.Char(string='Affected Chromosome', help='chromosome number')
    classification = fields.Selection([
        ('icd9', 'ICD-9'),
        ('icd10', 'ICD-10'),
        ('icd11', 'ICD-11')], string="Classification")
    sequence = fields.Integer(string='Sequence', default=60)

    def _compute_display_name(self):
        for rec in self:
            name = rec.name
            if rec.code:
                name = '[' + str(rec.code) + '] ' + rec.name
            rec.display_name = name


class MateDiseasesCategory(models.Model):
    _name = DISEASES_CATEGORY
    _description = "Diseases Category"

    name = fields.Char(string='Category Name', required=True, index=True)
    parent_id = fields.Many2one(DISEASES_CATEGORY, ondelete='cascade', string='Parent Category')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        for rec in self:
            if rec._has_cycle():
                raise ValidationError(_('You cannot create a recursive hierarchy.'))


class MatePatientDisease(models.Model):
    _name = 'his.patient.disease'
    _description = "Patient Diseases"

    disease_id = fields.Many2one(HIS_DISEASES, ondelete='set null', string='Disease')
    description = fields.Char(string='Treatment Description')
    diagnosed_date = fields.Date(string='Date of Diagnosis')
    healed_date = fields.Date(string='Healed')
    physician_id = fields.Many2one('his.physician', ondelete='restrict', string='Physician',
                                   help='Physician who treated or diagnosed the patient')
    is_allergy = fields.Boolean(string='Allergic Disease')
    pregnancy_warning = fields.Boolean(string='Pregnancy warning')
    patient_id = fields.Many2one(HIS_PATIENT, ondelete='cascade', string='Patient')
    lactation = fields.Boolean('Lactation')
    disease_severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], string='Severity', index=True)
    status = fields.Selection([
        ('acute', 'Acute'),
        ('chronic', 'Chronic'),
        ('unchanged', 'Unchanged'),
        ('healed', 'Healed'),
        ('improving', 'Improving'),
        ('worsening', 'Worsening'),
    ], string='Status of the disease', index=True)
    is_infectious = fields.Boolean(string='Infectious Disease', help='Check if the patient has an infectious, transmissible disease')
    allergy_type = fields.Selection([
        ('da', 'Drug Allergy'),
        ('fa', 'Food Allergy'),
        ('ma', 'Misc Allergy'),
        ('mc', 'Misc Contraindication'),
    ], string='Allergy type', index=True)
    age = fields.Char(string='Age when diagnosed',
                      help='Patient age at the moment of the diagnosis. Can be estimative')
    treatment_id = fields.Many2one('his.treatment', ondelete='cascade',
                                   string='Treatment', help="Treatment Id")


class MateDiseaseGene(models.Model):
    _name = 'disease.gene'
    _description = 'Disease Genetic'

    name = fields.Char(string='Official Name', required=True)
    gene_id = fields.Char(string='Gene ID', help="default code from NCBI Entrez database.")
    long_name = fields.Char(string='Official Long Name', required=True)
    location = fields.Char(string='Location', required=True, help="Locus of the chromosome")
    chromosome = fields.Char(string='Affected Chromosome', required=True)
    info = fields.Text(string='Information')
    dominance = fields.Selection([
        ('d', 'Dominant'),
        ('r', 'Recessive')
    ], 'Dominance', index=True)


class PatientGeneticRisk(models.Model):
    _name = 'his.patient.genetic.risk'
    _description = 'Patient Genetic Risks'

    patient_id = fields.Many2one(HIS_PATIENT, ondelete='cascade',
                                 string='Patient', index=True)
    disease_gene = fields.Many2one('disease.gene', ondelete='restrict',
                                   string='Disease Gene', required=True)


class FamilyDiseases(models.Model):
    _name = 'his.patient.family.diseases'
    _description = 'Family Diseases'

    patient_id = fields.Many2one(HIS_PATIENT, ondelete='cascade', string='Patient', index=True)
    diseases_ids = fields.Many2many(HIS_DISEASES, 'rz_id', 'pz_id', 'cz_id', 'Disease', required=True)
    xory = fields.Selection([
        ('m', 'Maternal'),
        ('f', 'Paternal')
    ], 'Maternal or Paternal')
    relative = fields.Selection([
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('aunt', 'Aunt'),
        ('uncle', 'Uncle'),
        ('nephew', 'Nephew'),
        ('niece', 'Niece'),
        ('grandfather', 'Grandfather'),
        ('grandmother', 'Grandmother'),
        ('cousin', 'Cousin')
    ], 'Relative',
        help="First degree = siblings, mother and father; second degree = "
             "Uncles, nephews and Nieces; third degree = Grandparents and cousins", required=True)
