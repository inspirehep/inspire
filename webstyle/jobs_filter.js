/*
 * This file is part of Invenio.
 * Copyright (C) 2012 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */

/*
 * This is the Javascript for webpage elements in INPIRE HEP Jobs search.
 */

/*
 * Given a prefix and an array of data, create a sub-expression
 * seperated by OR operators.
 */
function build_query(data, prefix) {
    var out = "";
    if (data.length > 1) {
        out += '(' + prefix + ':"' + data[0] + '" or ';
        for (var i = 1; i < data.length; i++) {
            if (i == data.length - 1) {
                out += prefix + ':"' + data[i] + '") ';
            } else {
                out += prefix + ':"' + data[i] + '" or ';
            }
        }
    } else if (data.length == 1) {
        out += prefix + ':"' + data[0] + '" ';
    }
    return out;
}

/*
 * Performs search. Will build the query based on user choices.
 */
function perform_job_search() {
    var baseurl = "/search?p1=QUERY&op1=a&p2=KEYWORD&action_search=Search&cc=Jobs"
    // get values
    var ranks = [];
    $('#rank :selected').each(function(i, selected){
      ranks[i] = $(selected).val();
    });
    var regions = [];
    $('#region :selected').each(function(i, selected){
      regions[i] = $(selected).val();
    });
    var fields = [];
    $('#field :selected').each(function(i, selected){
      fields[i] = $(selected).val();
    });
    keywords = $('#mainlightsearchfield').val();

    var query = "";
    /* filter and build */
    query += build_query(ranks, 'rank')
    query += build_query(regions, 'region')
    query += build_query(fields, 'subject')

    query = query.replace(/ /g, '+');
    keywords = keywords.replace(/ /g, '+');
    search_url = baseurl.replace('QUERY', query);
    search_url = search_url.replace('KEYWORD', keywords);
    window.location = search_url;
}

/* MAIN */
$(document).ready(function(){
    // Reset search filters to default values (none selected)
    $('#reset_search').click(function () {
        $('#mainlightsearchfield').val("");
        $('#rank :selected').attr('selected', '');
        $('#region :selected').attr('selected', '');
        $('#field :selected').attr('selected', '');
    });
    // Make example links carry over the selected elements to the query
    $('.examplequery').click(function (event) {
        event.preventDefault();
        $('#mainlightsearchfield').val($(this).text());
        perform_job_search();
    });
});
