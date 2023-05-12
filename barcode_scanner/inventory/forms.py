from django import forms
from .models import Computers,docking_stations,printers,monitors
#'docking_station','printer','monitor',
class computersForm(forms.ModelForm):
    class Meta:
        model = Computers
        fields = ["asset_tag","service_tag","computer_name",'department','user','make','model', 'storage', 'cpu', 'ram','printers']
        # widgets = {
        #     'asset_tag': forms.TextInput(attrs={'readonly': 'readonly'})
        # }
        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     # self.fields['asset_tag'].required = True
        #     for field_name in self.fields:
        #          if field_name != 'asset_tag':
        #             self.fields[field_name].required = False

class printersForm(forms.ModelForm):
    class Meta:
        model = printers
        fields= '__all__'   
        exclude=["id"]    
class monitorsForm(forms.ModelForm):
    class Meta:
        model = monitors
        fields= '__all__'
        exclude=["id"]        
class docking_stationsForm(forms.ModelForm):
    class Meta:
        model = docking_stations
        fields= '__all__'  
        exclude=["id"]      

