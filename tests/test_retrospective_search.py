from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from retrospective_search import parse_pubmed_xml  # noqa: E402


class PubMedParserTest(unittest.TestCase):
    def test_reference_identifiers_cannot_overwrite_article_identifiers(self) -> None:
        xml = b"""<PubmedArticleSet><PubmedArticle>
          <MedlineCitation><PMID>39059887</PMID><Article>
            <Journal><Title>The Lancet Digital Health</Title><JournalIssue><PubDate><Year>2024</Year></PubDate></JournalIssue></Journal>
            <ArticleTitle>Feasibility of wearable signals to prompt at-home testing</ArticleTitle>
            <Abstract><AbstractText>Wearable signals prompted a diagnostic test.</AbstractText></Abstract>
          </Article></MedlineCitation>
          <PubmedData><ArticleIdList>
            <ArticleId IdType="pubmed">39059887</ArticleId>
            <ArticleId IdType="doi">10.1016/S2589-7500(24)00096-7</ArticleId>
          </ArticleIdList><ReferenceList><Reference><ArticleIdList>
            <ArticleId IdType="pubmed">11111111</ArticleId>
            <ArticleId IdType="doi">10.0000/wrong-reference</ArticleId>
          </ArticleIdList></Reference></ReferenceList></PubmedData>
        </PubmedArticle></PubmedArticleSet>"""
        query = {"id": "test", "focus": "test"}
        item = parse_pubmed_xml(xml, query)[0]
        self.assertEqual(item["pmid"], "39059887")
        self.assertEqual(item["doi"], "10.1016/s2589-7500(24)00096-7")
        self.assertNotIn("wrong-reference", item["doi"])


if __name__ == "__main__":
    unittest.main()
