import pytest

from app.models.enums import VALID_DOMAIN_ROLES, Domain, Role

VALID_COMBINATIONS = [
    (Domain.CITIZEN, Role.CITIZEN),
    (Domain.GOVERNMENT, Role.VALIDATOR),
    (Domain.GOVERNMENT, Role.FIELD_ASSISTANT),
    (Domain.UNIVERSITY, Role.COORDINATOR),
    (Domain.UNIVERSITY, Role.FACULTY),
    (Domain.INDUSTRY, Role.INDUSTRY),
    (Domain.SUPERADMIN, Role.SUPERADMIN),
]

INVALID_COMBINATIONS = [
    (Domain.UNIVERSITY, Role.VALIDATOR),
    (Domain.INDUSTRY, Role.FACULTY),
    (Domain.GOVERNMENT, Role.COORDINATOR),
    (Domain.SUPERADMIN, Role.FACULTY),
    (Domain.CITIZEN, Role.VALIDATOR),
    (Domain.GOVERNMENT, Role.CITIZEN),
    (Domain.UNIVERSITY, Role.INDUSTRY),
]


@pytest.mark.parametrize("domain,role", VALID_COMBINATIONS)
def test_valid_domain_role_combination(domain, role):
    assert role in VALID_DOMAIN_ROLES[domain]


@pytest.mark.parametrize("domain,role", INVALID_COMBINATIONS)
def test_invalid_domain_role_combination(domain, role):
    assert role not in VALID_DOMAIN_ROLES[domain]


def test_every_role_belongs_to_exactly_one_domain():
    role_to_domains = {}
    for domain, roles in VALID_DOMAIN_ROLES.items():
        for role in roles:
            role_to_domains.setdefault(role, []).append(domain)
    for role, domains in role_to_domains.items():
        assert len(domains) == 1, f"{role} maps to more than one domain: {domains}"


def test_all_roles_and_domains_are_covered():
    covered_roles = {role for roles in VALID_DOMAIN_ROLES.values() for role in roles}
    assert covered_roles == set(Role)
    assert set(VALID_DOMAIN_ROLES.keys()) == set(Domain)


def test_student_is_not_a_role():
    assert not any(r.value == "student" for r in Role)


def test_gov_admin_is_not_a_role():
    assert not any(r.value == "gov_admin" for r in Role)
