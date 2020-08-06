from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR, MONTH
from openfisca_germany.entities import Household, Person, TaxUnit

from numpy import minimum, maximum, nan_to_num


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

    def formula(person, period):
      sources = [
        'bruttolohn_m',
        'sonstig_eink_m',
        'eink_selbst_m',
        'vermiet_eink_m',
        'kapital_eink_m',
        'ges_rente_m',
        'arbeitsl_geld_m',
        'elterngeld_m',
      ]
      return sum([person(s, period) for s in sources])


class bruttolohn_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class alleinerziehend(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR


class alleinerziehend_hh(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        return household.any(household.members('alleinerziehend', period))


class alleinerziehenden_mehrbedarf_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR


    def formula(household, period, parameters):
        alleinerziehend_hh = household('alleinerziehend_hh', period)
        anz_kinder_hh = household('anz_kinder_hh', period)
        anz_kind_zwischen_0_6_hh = household('anz_kind_zwischen_0_6_hh', period)
        anz_kind_zwischen_0_15_hh = household('anz_kind_zwischen_0_15_hh', period)

        P = parameters(period).mehrbedarf_anteil

        lower = P.min_1_kind * anz_kinder_hh
        value = (
            (anz_kind_zwischen_0_6_hh >= 1)
            | ((2 <= anz_kind_zwischen_0_15_hh) & (anz_kind_zwischen_0_15_hh <= 3))
        ) * P.kind_unter_7_oder_mehr

        out = alleinerziehend_hh * value.clip(
            min=lower, max=P.max
        )
        return out


class alter(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class _anz_erwachsene_tu(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period):
        return tax_unit.sum(~tax_unit.members('kind', period))


class anz_kinder_hh(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        return household.sum(household.members('kind', period))


class anz_kind_zwischen_0_6_hh(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        alter = household.members('alter', period)
        return household.sum(household.members('kind', period) * (0 <= alter) * (alter <= 6))


class anz_kind_zwischen_0_15_hh(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        alter = household.members('alter', period)
        return household.sum(household.members('kind', period) * (0 <= alter) * (alter <= 15))


class arbeitsl_geld_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR


class arbeitsl_geld_2_eink(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR

    def formula(person, period):
        _anz_erwachsene_tu = person.tax_unit('_anz_erwachsene_tu', period)
        return maximum(0, 
            person('_arbeitsl_geld_2_brutto_eink', period)
            - (person.tax_unit('eink_st_tu', period) / _anz_erwachsene_tu) / 12
            - (person.tax_unit('soli_st_tu', period) / _anz_erwachsene_tu) / 12
            - person('sozialv_beitr_m', period)
            - person('eink_anr_frei', period)
            )


class arbeitsl_geld_2_eink_hh(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        return household.sum(household.members('arbeitsl_geld_2_eink', period))


class arbeitsl_geld_2_2005_netto_quote(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR

    def formula(person, period):
        nettolohn_m = person('nettolohn_m', period)
        bruttolohn_m = person('bruttolohn_m', period)
        return nan_to_num(maximum(0,  nettolohn_m - 15.33 - 30) / bruttolohn_m)


class bewohnt_eigentum_hh(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR


class kinder_in_hh(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR

    def formula(household, period):
        return household.any(household.members('kind', period))


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


class eink_anr_frei(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR

    def formula(person, period, parameters):
        P = parameters(period).taxes
        return P.eink_anr_frei.calc(person('bruttolohn_m', period)) * person('arbeitsl_geld_2_2005_netto_quote', period)

    def formula_2005_10(person, period, parameters):
        P = parameters(period).taxes
        out = P.eink_anr_frei.calc(person('bruttolohn_m', period))
        kinder_in_hh = person.household('kinder_in_hh', period)
        sub = P.eink_anr_frei_kinder.calc(person('bruttolohn_m', period))
        out[kinder_in_hh] = sub[kinder_in_hh]
        return out


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


class kind(Variable):
    value_type = bool
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


class nettolohn_m(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR

    def formula(person, period):
        _anz_erwachsene_tu = person.tax_unit('_anz_erwachsene_tu', period) 
        return maximum(0,
            person('bruttolohn_m', period)
            - person.tax_unit('eink_st_tu', period) / _anz_erwachsene_tu / 12
            - person.tax_unit('soli_st_tu', period) / _anz_erwachsene_tu / 12
            - person('sozialv_beitr_m', period)
        )


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
