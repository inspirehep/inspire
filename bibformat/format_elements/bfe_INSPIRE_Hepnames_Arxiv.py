## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints arXiv link name for HepNames
"""

from invenio.textutils import translate_to_ascii

def format_element(bfo):
    """
    ensure correct utf-8 handling of first initial and
    return asciified string <lastname>_<first initial>
    """
    out = str(bfo.field('100__a')).decode('utf-8').replace(', ', '_')
    position = out.find('_')
    if position >= 0:
        out = out[:position+2]
    out = translate_to_ascii([out]).pop()
    return out
