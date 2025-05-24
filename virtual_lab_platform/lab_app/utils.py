from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

def add_tailwind_form_styles(form):
    """Add Tailwind CSS styles to form fields"""
    form.helper = FormHelper()
    form.helper.form_tag = True
    form.helper.form_class = 'space-y-4'
    
    # Add classes to all fields
    for field_name, field in form.fields.items():
        if field_name == 'remember':
            field.widget.attrs['class'] = 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        elif isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs['class'] = 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        elif isinstance(field.widget, forms.FileInput):
            field.widget.attrs['class'] = 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
        else:
            field.widget.attrs['class'] = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'
    
    return form
