import csv
import io

from rest_framework.renderers import BaseRenderer


class CSVRenderer(BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, media_type=None, renderer_context=None):
        if not data:
            return ''

        header = data[0].keys()
        csv_data = [header]

        for row in data:
            csv_data.append([str(row[key]) for key in header])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        return output.getvalue()
