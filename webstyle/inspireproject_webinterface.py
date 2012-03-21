from invenio.webinterface_handler import WebInterfaceDirectory
from invenio.inspireproject_webinterface_templates import tmpl_jobs_matrix
from invenio.search_engine import perform_request_search
from invenio.webpage import page
from invenio.webuser import collect_user_info


class WebInterfaceInspirePages(WebInterfaceDirectory):
    _exports = [('jobs-matrix', 'jobs_matrix')]

    def jobs_matrix(self, req, form):
        categories = ('astro-ph', 'cond-mat', 'cs', 'gr-qc', 'hep-ex',
                      'hep-lat', 'hep-ph', 'hep-th', 'math', 'math-ph',
                      'nucl-ex', 'nucl-th', 'physics', 'physics.acc-phys',
                      'physics.ins-det', 'quant-ph')
        ranks = ('student', 'postdoc', 'junior', 'senior', 'staff', 'visitor')
        counts = {}
        for cat in categories:
            cat_hitset = perform_request_search(p='subject:"%s"' % cat,
                                                cc="Jobs")
            for rank in ranks:
                rank_hitset = perform_request_search(p='rank:"%s"' % rank,
                                                     cc="Jobs")
                counts.setdefault(cat, {})[rank] = len(set(cat_hitset) & set(rank_hitset))
        # Render the page (including header, footer)
        user_info = collect_user_info(req)
        return page(title='Jobs Matrix',
                    body=tmpl_jobs_matrix(categories, ranks, counts),
                    uid=user_info['uid'],
                    req=req,
                    navmenuid='Jobs')
