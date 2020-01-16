import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
from requests import ConnectionError, HTTPError


from invenio.webinterface_handler import WebInterfaceDirectory
from invenio.inspireproject_webinterface_templates import tmpl_jobs_matrix
from invenio.webpage import page
from invenio.webuser import collect_user_info


class WebInterfaceInspirePages(WebInterfaceDirectory):
    _exports = [('jobs-matrix', 'jobs_matrix')]

    def jobs_matrix(self, req, form):
        categories = ('astro-ph', 'cond-mat', 'cs', 'gr-qc', 'hep-ex',
                      'hep-lat', 'hep-ph', 'hep-th', 'math', 'math-ph',
                      'nucl-ex', 'nucl-th', 'physics', 'physics.acc-ph',
                      'physics.ins-det', 'quant-ph', 'physics.atom-ph', 'nlin')
        ranks = ('PHD', 'POSTDOC', 'JUNIOR', 'SENIOR', 'STAFF', 'VISITOR', 'OTHER')
        counts = {}
        s = requests.Session()
        for cat in categories:
            for rank in ranks:
                try:
                    resp = s.get('https://labs.inspirehep.net/api/jobs?rank={0}&field_of_interest={1}&status=open'.format(rank, cat),
                                 verify=False)
                except ConnectionError:
                    continue
                try:
                    resp.raise_for_status()
                except HTTPError:
                    continue
                try:
                    respjson = resp.json()
                except ValueError:
                    continue
                counts.setdefault(cat, {})[rank] = respjson['hits'].get('total', 0)
                # Render the page (including header, footer)
        user_info = collect_user_info(req)
        return page(title='Jobs Matrix',
                    body=tmpl_jobs_matrix(categories, ranks, counts),
                    uid=user_info['uid'],
                    req=req,
                    navmenuid='Jobs')
