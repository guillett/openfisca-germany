import itertools
import os
import pkg_resources

from openfisca_germany import CountryTaxBenefitSystem
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_core.simulations import Simulation

import numpy as np
from numpy.testing import assert_allclose
import pandas as pd
import pytest

# from gettsim.config import ROOT_DIR
# from gettsim.interface import compute_taxes_and_transfers
# from gettsim.policy_environment import set_up_policy_environment


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "alter",
    "kaltmiete_m_hh",
    "heizkosten_m_hh",
    "wohnfläche_hh",
    "bewohnt_eigentum_hh",
    "alleinerziehend",
    "bruttolohn_m",
    "ges_rente_m",
    "kapital_eink_m",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "eink_selbst_m",
    "vermiet_eink_m",
    "eink_st_tu",
    "soli_st_tu",
    "sozialv_beitr_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "jahr",
]

OUT_COLS = [
    "_arbeitsl_geld_2_brutto_eink_hh",
    "alleinerziehenden_mehrbedarf_hh",
    "regelbedarf_m_hh",
    "regelsatz_m_hh",
    "kost_unterk_m_hh",
    "unterhaltsvors_m_hh",
    "eink_anr_frei",
    "arbeitsl_geld_2_eink",
    "arbeitsl_geld_2_eink_hh",
]


YEARS = [2005, 2006, 2009, 2011, 2013, 2016, 2019]


@pytest.fixture(scope="module")
def input_data():
    csv_path = os.path.join(
        pkg_resources.get_distribution("gettsim").location,
        "gettsim",
        "tests",
        "test_data",
        "test_dfs_alg2.csv",
        )
    return pd.read_csv(csv_path)


# @pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
# def test_alg2(input_data, year, column):
#     year_data = input_data[input_data["jahr"] == year]
#     tax_benefit_system = CountryTaxBenefitSystem()
#     tbs = tax_benefit_system

#     id_map = {
#         'person': 'p_id',
#         'household': 'hh_id',
#         'tax_unit': 'tu_id',
#     }

#     role_map = {
#         'household': lambda p: p['vorstand_tu'].replace({True: 'parents', False: 'children'}),
#         'tax_unit': lambda p: p['vorstand_tu'].replace({True: 'heads', False: 'others'})
#     }

#     def get(data, tbs, id_map, entity):
#         columns = [c for c in INPUT_COLS if tbs.get_variable(c, check_existence = True).entity.key == entity]
#         return data[[id_map[entity]] + columns].rename(index=str, columns={id_map[entity]: "id"}).drop_duplicates().reset_index(drop=True)


#     simulation = Simulation(tax_benefit_system, tax_benefit_system.instantiate_entities())

#     for e in ['person', 'household', 'tax_unit']:
#         data = get(year_data, tbs, id_map, e)
#         p = simulation.populations[e]
#         p.count = len(data['id'])
#         p.ids = data['id']
#         for c in data.columns:
#             if (c in ['id']):
#                 continue
#             h = p.get_holder(c)
#             h.set_input(year, data[c])

#     for (k, v) in role_map.items():
#         gg = simulation.populations[k]
#         # members_entity_id are not IDs but indexes
#         # gg.members_entity_id = year_data[id_map[k]]
#         gg.members_entity_id = np.searchsorted(simulation.populations[k].ids, year_data[id_map[k]])
#         gg.members_role = v(year_data)

#     c_variable = tax_benefit_system.get_variable(column, check_existence = True)
#     actual = simulation.calculate(column, year)
#     expected = year_data[[id_map[c_variable.entity.key], column]].drop_duplicates()[column].values

#     assert_allclose(actual, expected, atol=0.01)



@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_alg2_scenario(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]

    print(year_data)
    tax_benefit_system = CountryTaxBenefitSystem()
    from openfisca_survey_manager.scenarios import AbstractSurveyScenario

    survey_scenario = AbstractSurveyScenario()
    survey_scenario.set_tax_benefit_systems(tax_benefit_system = tax_benefit_system)
    survey_scenario.used_as_input_variables = INPUT_COLS[3:]
    survey_scenario.year = year
    input_data.tu_id.replace({10:5, 11:5}, inplace = True)
    input_data_frame = (input_data[INPUT_COLS + ["vorstand_tu"]]
        .query("jahr == @year")
        .rename(columns = {
            'p_id': 'person_id',
            'hh_id': 'household_id',
            'tu_id': 'tax_unit_id',
            })
        )
    input_data_frame['household_role_index'] = (
        input_data_frame['vorstand_tu'].replace({True: 0, False: 1})
        )
    input_data_frame['tax_unit_role_index'] = (
        input_data_frame['vorstand_tu'].replace({True: 0, False: 1})
        )

    print(input_data_frame)

    data = {
        'input_data_frame': input_data_frame
        }
    survey_scenario.init_from_data(data = data)
    id_map = {
        'person': 'p_id',
        'household': 'hh_id',
        'tax_unit': 'tu_id',
        }

    c_variable = tax_benefit_system.get_variable(column, check_existence = True)
    actual = survey_scenario.simulation.calculate(column, year)
    expected = year_data[[id_map[c_variable.entity.key], column]].drop_duplicates()[column].values

    assert_allclose(actual, expected, atol=0.01)

