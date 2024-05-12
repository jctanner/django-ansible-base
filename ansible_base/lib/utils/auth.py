from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_model_from_settings(setting_name):
    """
    Return the User model that is active in this project.
    """
    try:
        setting = getattr(settings, setting_name)
    except AttributeError:
        raise ImproperlyConfigured(f"{setting_name} is not defined in settings.")
    try:
        return django_apps.get_model(setting, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(f"{setting_name} must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(f"{setting_name} refers to model '{setting}' that has not been installed")


def get_team_model():
    return get_model_from_settings('ANSIBLE_BASE_TEAM_MODEL')


def get_organization_model():
    return get_model_from_settings('ANSIBLE_BASE_ORGANIZATION_MODEL')
