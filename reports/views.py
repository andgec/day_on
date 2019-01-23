from django.views.generic import View
from django.template.loader import get_template
from wkhtmltopdf.views import PDFTemplateResponse
from django.http import HttpResponse

from general.models import Company


class TimelistPDFView(View):
    template = get_template('reports/pdf_timelist_html4.html')
    header_template = get_template('reports/pdf_header_html4.html')
    footer_template = get_template('reports/pdf_footer_html4.html')
    context = {
        "first_name": 'Andrius',
        "last_name": 'Gecys',
        "number": '123456',
        }
    def get_context(self, request):
        company = request.user.company;
        print(company)
    
    def get(self, request, project_id=None):
        print(project_id)
        context = self.get_context(request)
        response = PDFTemplateResponse(request = request,
                                       template = self.template,
                                       header_template = self.header_template,
                                       #footer_template = self.footer_template,
                                       filename = "timelist_project#.pdf",
                                       context = self.context,
                                       show_content_in_browser=True,
                                       cmd_options={'javascript-delay': 500,
                                                    'margin-top' : 20,
                                                    'orientation': 'Landscape',},
                                       )
        return response


class TimelistHTMLView(View):
    def get(self, request, *args, **kwargs):
        template = get_template('reports/pdf_header_html4.html')
        context = {
            "first_name": 'Andrius',
            "last_name": 'Gecys',
            "number": '123456',
            }
        html = template.render(context)
        return HttpResponse(html)
