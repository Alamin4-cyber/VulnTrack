from django import forms
from member1_core.forms import BootstrapMixin
from member1_core.models import Target
from member2_assessment.models import ScanProfile
from .models import Evidence, Remediation


class ScanJobForm(BootstrapMixin, forms.Form):
    target = forms.ModelChoiceField(queryset=Target.objects.none())
    profile = forms.ModelChoiceField(queryset=ScanProfile.objects.all(),
                                     required=False, empty_label="Default (all checks)")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        from member1_core.utils import visible_targets
        self.fields["target"].queryset = visible_targets(user).filter(is_authorized=True, is_active=True)


class EvidenceForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ("request_data", "response_data", "notes")


class RemediationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Remediation
        fields = ("recommendation", "references", "priority")
