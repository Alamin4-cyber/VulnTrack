from django import forms

from member1_core.forms import BootstrapMixin

from .models import ScanProfile, ScopeRule


class ScopeRuleForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ScopeRule
        fields = ("rule_type", "pattern", "notes")


class ScanProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ScanProfile
        fields = (
            "name", "description",
            "enable_subdomain_enum", "enable_dns_enum",
            "enable_port_scan", "enable_http_probe", "enable_vuln_scan",
            "port_range", "is_default",
        )