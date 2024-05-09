import pytest
import random
import string
from unittest.mock import patch

from ansible_base.lib.utils.auth import get_organization_model, get_team_model
from ansible_base.authentication.utils.claims import process_organization_and_team_memberships
from ansible_base.authentication.utils.claims import create_orgs_and_teams
from ansible_base.authentication.utils.claims import load_existing_orgs
from ansible_base.authentication.utils.claims import load_existing_teams
from ansible_base.authentication.utils.claims import create_missing_orgs
from ansible_base.authentication.utils.claims import create_missing_teams


def generate_org_or_team_name():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10))


@patch('ansible_base.authentication.utils.claims.create_orgs_and_teams')
def test_process_organization_and_team_memberships(mock_create_orgs_and_teams):
    results = {
        'claims': {
            'organization_membership': {},
            'team_membership': {},
        }
    }
    process_organization_and_team_memberships(results)
    mock_create_orgs_and_teams.assert_called_once()


@patch('ansible_base.authentication.utils.claims.load_existing_orgs')
@patch('ansible_base.authentication.utils.claims.create_missing_orgs')
@patch('ansible_base.authentication.utils.claims.load_existing_teams')
@patch('ansible_base.authentication.utils.claims.create_missing_teams')
def test_create_orgs_and_teams(mock_load_existing_orgs, mock_create_missing_orgs, mock_load_existing_teams, mock_create_missing_teams):
    org_list = []
    team_map = {}
    create_orgs_and_teams(org_list, team_map)

    mock_load_existing_orgs.assert_called_once()
    mock_create_missing_orgs.assert_called_once()
    mock_load_existing_teams.assert_called_once()
    mock_create_missing_teams.assert_called_once()


@pytest.mark.django_db
def test_load_existing_orgs():
    Organization = get_organization_model()
    org_names = [generate_org_or_team_name() for x in range(0, 5)]
    orgs = [Organization.objects.get_or_create(name=x)[0] for x in org_names]

    filtered_orgs = orgs[1:]
    filtered_org_names = [x.name for x in filtered_orgs]
    res = load_existing_orgs(filtered_org_names)
    for org in orgs:
        if org in filtered_orgs:
            assert org.name in res
            assert res[org.name] == org.id
        else:
            assert org.name not in res


@pytest.mark.django_db
def test_load_existing_teams():
    Organization = get_organization_model()
    Team = get_team_model()
    org, _ = Organization.objects.get_or_create(name=generate_org_or_team_name())
    team_names = [generate_org_or_team_name() for x in range(0, 5)]
    teams = [Team.objects.get_or_create(name=x, organization=org)[0] for x in team_names]

    filtered_teams = teams[1:]
    filtered_team_names = [x.name for x in filtered_teams]
    res = load_existing_teams(filtered_team_names)
    for team in teams:
        if team in filtered_teams:
            assert team.name in res
            assert res[team.name] == team.id
        else:
            assert team.name not in res


@pytest.mark.django_db
def test_create_missing_orgs():
    Organization = get_organization_model()
    org_name = generate_org_or_team_name()
    existing_orgs = {}
    create_missing_orgs([org_name], existing_orgs)
    assert org_name in existing_orgs
    assert Organization.objects.filter(name=org_name).exists()


@pytest.mark.django_db
def test_create_missing_teams():
    Organization = get_organization_model()
    Team = get_team_model()

    org_name = generate_org_or_team_name()
    org, _ = Organization.objects.get_or_create(name=org_name)
    team_name = generate_org_or_team_name()
    team_map = {team_name: org_name}
    existing_orgs = {org_name: org.id}

    create_missing_teams([team_name], team_map, existing_orgs, [])

    assert Team.objects.filter(name=team_name, organization=org).exists()
