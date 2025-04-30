from django import forms
from django.utils.safestring import mark_safe


class ColorTextWidget(forms.TextInput):
    template = '''
    <div style="display: flex; gap: 6px; align-items: center;">
        <input type="color" id="picker_{name}" value="{color}" style="height:28px;width:40px;padding:0;border:none;background:transparent;"/>
        <input type="text" name="{name}" value="{value}" id="input_{name}" style="flex:1;"/>
    </div>
    <script>
      const picker_{name} = document.getElementById("picker_{name}");
      const input_{name} = document.getElementById("input_{name}");

      picker_{name}.addEventListener("input", e => input_{name}.value = e.target.value);
      input_{name}.addEventListener("input", e => {{
        if (/^#(?:[0-9a-fA-F]{{3}}){{1,2}}$/.test(e.target.value)) {{
          picker_{name}.value = e.target.value;
        }}
      }});
    </script>
    '''

    def render(self, name, value, attrs=None, renderer=None):
        value = value or ''
        color = value if value.startswith('#') else '#000000'
        html = self.template.format(name=name, value=value, color=color)
        return mark_safe(html)
