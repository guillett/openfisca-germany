from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR, MONTH
from openfisca_germany.entities import Household, Person, TaxUnit

from numpy import minimum, maximum


class _arbeitsl_geld_2_brutto_eink_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        return household.sum(household.members('_arbeitsl_geld_2_brutto_eink', period))


class _arbeitsl_geld_2_brutto_eink(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR

    def formula(people, period):
      sources = [
        # 'bruttolohn_m',
        # 'sonstig_eink_m',
        # 'eink_selbst_m',
        # 'vermiet_eink_m',
        # 'kapital_eink_m',
        # 'ges_rente_m',
        # 'arbeitsl_geld_m',
        # 'elterngeld_m',
      ]
      return sum([people(s, period) for s in sources])


class bruttolohn_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class alleinerziehend(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR


class alter(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class arbeitsl_geld_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class bewohnt_eigentum_hh(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR


class berechtigte_wohnfläche_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        wohnfläche_hh = household('wohnfläche_hh', period)
        bewohnt_eigentum_hh = household('bewohnt_eigentum_hh', period)
        haushaltsgröße_hh = household.nb_persons()

        maximal_be = (80 + maximum(0, haushaltsgröße_hh - 2) * 20)
        maximal_nicht_be = (45 + maximum(0, haushaltsgröße_hh - 1) * 15)
        maximal = bewohnt_eigentum_hh * maximal_be + (~bewohnt_eigentum_hh) * maximal_nicht_be
        return minimum(wohnfläche_hh, maximal)

class eink_selbst_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class eink_st_tu(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class elterngeld_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class ges_rente_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class heizkosten_m_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR


class jahr(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class kaltmiete_m_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR


class kapital_eink_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class kindergeld_m_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR


class kost_unterk_m_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        return household('berechtigte_wohnfläche_hh', period) * household('miete_pro_qm_hh', period)


class miete_pro_qm_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        kaltmiete_m_hh = household('kaltmiete_m_hh', period)
        heizkosten_m_hh = household('heizkosten_m_hh', period)
        wohnfläche_hh = household('wohnfläche_hh', period)

        return minimum(10, ((kaltmiete_m_hh + heizkosten_m_hh) / wohnfläche_hh))


class soli_st_tu(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class sonstig_eink_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class sozialv_beitr_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class unterhaltsvors_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR



class unterhaltsvors_m_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        return household.sum(household.members('unterhaltsvors_m', period))


class vermiet_eink_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class wohnfläche_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
