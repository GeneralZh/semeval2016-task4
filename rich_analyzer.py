# twitter-oriented fast and simple feature extractor
# Copyright (C) 2016  Andrea Esuli <andrea@esuli.it>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

urlre = re.compile(r'http[s]{,1}://[^ ]+')
mentionre = re.compile(r'@[\w]+')
hashre = re.compile(r'#[\w]+')
emotre = re.compile(
        r'(:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$)')
featre = re.compile(
        r'(http[s]{,1}://[^ ]+|[\w\-]+|#\w+|@\w+|\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[;:,\!\.\?]|$)')


def clean_html(html):
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    cleaned = re.sub(r"(?s)<[/\w].*?>", " ", cleaned)
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    return cleaned.strip()


def ngrams(items, n, prefix):
    return [prefix + '_'.join(items[start:start + n]) for start in range(0, len(items) - n + 1)]


def get_rich_analyzer(word_ngrams=None, char_ngrams=None, stopwords=None):
    def analyzer(doc):
        return rich_analyzer(doc, word_ngrams, char_ngrams, stopwords)

    return analyzer


def rich_analyzer(doc, word_ngrams=None, char_ngrams=None, stopwords=None):
    if word_ngrams is None:
        word_ngrams = list()
    if char_ngrams is None:
        char_ngrams = list()
    if stopwords is None:
        stopwords = set()
    else:
        stopwords = set(stopwords)

    doc = clean_html(doc)
    output = list()
    output.extend(featre.findall(doc))
    output = [x for x in output if len(x) > 1 and not x in stopwords]

    if word_ngrams is None:
        word_ngrams = list()
    ngm = list()
    for n in word_ngrams:
        ngm.extend(ngrams(output, n, '_W%iG_' % n))
    output.extend(ngm)

    ngm = list()
    for n in char_ngrams:
        ngm.extend(ngrams(doc, n, '_C%iG_' % n))
    output.extend(ngm)

    for alttag, regex in [('_URL', urlre), ('_MENTION', mentionre), ('_HASHTAG', hashre), ('_EMOTICON', emotre)]:
        output.extend([alttag for _ in regex.findall(doc)])
    return output


if __name__ == '__main__':
    example = 'test #test <i>test</i> :) ;) @test http://test.com'
    output = rich_analyzer(example, [2, 3], [3])
    print(output)
