from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from retrospective_search import fielded_boolean_query, is_truncated, parse_pubmed_xml, retrieval_target, valid_doi  # noqa: E402


class PubMedParserTest(unittest.TestCase):
    def test_zero_limit_means_complete_retrieval(self) -> None:
        self.assertEqual(retrieval_target(1245, 0), 1245)
        self.assertFalse(is_truncated(1245, 1245, 0))

    def test_known_total_detects_actual_truncation(self) -> None:
        self.assertTrue(is_truncated(1245, 100, 100))
        self.assertFalse(is_truncated(100, 100, 100))

    def test_pubmed_translation_fields_every_concept(self) -> None:
        translated = fielded_boolean_query(
            '("robotic biopsy" OR autonomous) AND diagnostic', "pubmed"
        )
        self.assertEqual(
            translated,
            '( "robotic biopsy"[Title/Abstract] OR autonomous[Title/Abstract] ) AND diagnostic[Title/Abstract]',
        )

    def test_europepmc_translation_fields_every_concept(self) -> None:
        translated = fielded_boolean_query('robot AND "blood collection"', "europepmc")
        self.assertEqual(translated, 'TITLE_ABS:robot AND TITLE_ABS:"blood collection"')

    def test_doi_validation_rejects_malformed_provider_values(self) -> None:
        self.assertTrue(valid_doi("10.1038/s41551-021-00753-6"))
        self.assertFalse(valid_doi("/s0034-98872010000300007"))

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

    def test_pubmed_book_record_is_not_silently_dropped(self) -> None:
        xml = b"""<PubmedArticleSet><PubmedBookArticle><BookDocument>
          <PMID>123</PMID><ArticleTitle>Robotic diagnostic chapter</ArticleTitle>
          <Book><BookTitle>Clinical Robotics</BookTitle><PubDate><Year>2024</Year></PubDate></Book>
        </BookDocument><PubmedBookData><ArticleIdList>
          <ArticleId IdType="doi">10.1000/book</ArticleId>
        </ArticleIdList></PubmedBookData></PubmedBookArticle></PubmedArticleSet>"""
        item = parse_pubmed_xml(xml, {"id": "test", "focus": "test"})[0]
        self.assertEqual(item["pmid"], "123")
        self.assertEqual(item["doi"], "10.1000/book")


if __name__ == "__main__":
    unittest.main()
