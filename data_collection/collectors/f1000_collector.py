"""
F1000Research peer review data collector.

Collects published research articles with open peer reviews from F1000Research.
Uses F1000Research's API and web scraping.
"""

import requests
import time
import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import xml.etree.ElementTree as ET

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import (
    Manuscript, Review, Reviewer, AuthorResponse,
    ReviewSource, ReviewDecision, CollectionMetadata
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class F1000Collector:
    """Collector for F1000Research articles with peer reviews."""

    BASE_URL = "https://f1000research.com"
    API_BASE = "https://f1000research.com/extapi/v1"

    def __init__(self, rate_limit_delay: float = 2.0):
        """
        Initialize F1000Research collector.

        Args:
            rate_limit_delay: Delay between requests in seconds
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PeerReviewSynthesisBot/1.0 (Research/Educational)'
        })

    def collect_manuscripts(
        self,
        num_manuscripts: int = 50,
        subject_areas: Optional[List[str]] = None,
        start_date: Optional[str] = None
    ) -> tuple[List[Manuscript], CollectionMetadata]:
        """
        Collect multiple manuscripts with peer reviews.

        Args:
            num_manuscripts: Number of manuscripts to collect
            subject_areas: Filter by subject areas (not yet implemented)
            start_date: Collect articles from this date onwards (not yet implemented)

        Returns:
            Tuple of (list of manuscripts, collection metadata)
        """
        collection_id = f"f1000_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = CollectionMetadata(
            collection_id=collection_id,
            source=ReviewSource.F1000RESEARCH,
            start_time=datetime.now().isoformat(),
            config={
                'num_manuscripts': num_manuscripts,
                'subject_areas': subject_areas,
                'start_date': start_date
            }
        )

        manuscripts = []
        article_ids = self._discover_articles(num_manuscripts)

        logger.info(f"Found {len(article_ids)} article IDs to process")

        for i, article_info in enumerate(article_ids[:num_manuscripts], 1):
            try:
                article_id = article_info['id']
                article_url = article_info.get('url')

                logger.info(f"Processing article {i}/{num_manuscripts}: {article_id}")
                metadata.num_manuscripts_attempted += 1

                manuscript = self.collect_single_manuscript(article_id, article_url)

                if manuscript:
                    validation_issues = manuscript.validate()
                    if validation_issues:
                        logger.warning(f"Validation issues for {article_id}: {validation_issues}")

                    manuscripts.append(manuscript)
                    metadata.num_manuscripts_successful += 1
                    logger.info(f"Successfully collected {article_id} with {len(manuscript.reviews)} reviews")
                else:
                    metadata.num_manuscripts_failed += 1
                    metadata.errors.append({
                        'article_id': article_id,
                        'error': 'Failed to collect manuscript'
                    })

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Error processing article: {str(e)}")
                metadata.num_manuscripts_failed += 1
                metadata.errors.append({
                    'article_id': str(article_info),
                    'error': str(e)
                })

        metadata.end_time = datetime.now().isoformat()
        return manuscripts, metadata

    def _discover_articles(self, num_articles: int) -> List[Dict[str, str]]:
        """
        Discover article IDs from F1000Research.

        Returns:
            List of article info dictionaries
        """
        article_ids = []

        try:
            # Try to get articles from the latest publications page
            url = f"{self.BASE_URL}/articles/browse/latest"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find article links
            article_links = soup.find_all('a', href=re.compile(r'/articles/\d+-\d+'))

            for link in article_links:
                href = link.get('href', '')
                full_url = f"{self.BASE_URL}{href}" if href.startswith('/') else href

                # Extract article ID from URL (format: /articles/1-2345/v1 or /articles/1-2345)
                match = re.search(r'/articles/([\d\-]+)', href)
                if match:
                    article_id = match.group(1)
                    article_ids.append({
                        'id': article_id,
                        'url': full_url
                    })

                if len(article_ids) >= num_articles * 2:  # Get extra in case some fail
                    break

        except Exception as e:
            logger.error(f"Error discovering articles: {str(e)}")

        # Fallback: use some known article IDs
        if len(article_ids) < 5:
            logger.warning("Few articles discovered, using fallback article IDs")
            # These are example F1000Research article IDs
            fallback_ids = ['1-1655', '2-150', '3-200', '4-100', '5-50']
            for fid in fallback_ids:
                article_ids.append({
                    'id': fid,
                    'url': f"{self.BASE_URL}/articles/{fid}"
                })

        return article_ids

    def collect_single_manuscript(
        self,
        article_id: str,
        article_url: Optional[str] = None
    ) -> Optional[Manuscript]:
        """
        Collect a single manuscript with all its peer reviews.

        Args:
            article_id: F1000Research article ID (e.g., '1-1655')
            article_url: Full URL to article (optional)

        Returns:
            Manuscript object or None if collection failed
        """
        try:
            if not article_url:
                article_url = f"{self.BASE_URL}/articles/{article_id}"

            # Get the article page
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract article metadata
            title = self._extract_title(soup)
            abstract = self._extract_abstract(soup)
            authors = self._extract_authors(soup)
            doi = self._extract_doi(soup)
            keywords = self._extract_keywords(soup)

            # Extract peer reviews
            reviews = self._extract_reviews(soup, article_id)

            # Extract dates
            publication_date = self._extract_publication_date(soup)

            # Determine decision based on review status
            decision = self._determine_decision(soup)

            manuscript = Manuscript(
                manuscript_id=article_id,
                source=ReviewSource.F1000RESEARCH,
                source_url=article_url,
                title=title or f"Article {article_id}",
                abstract=abstract,
                authors=authors,
                doi=doi,
                keywords=keywords,
                reviews=reviews,
                publication_date=publication_date,
                decision=decision,
                raw_data={'html_collected': True}
            )

            return manuscript

        except Exception as e:
            logger.error(f"Error collecting article {article_id}: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        # Try main title tag
        title_tag = soup.find('h1', class_=re.compile(r'title|article'))
        if title_tag:
            return title_tag.get_text(strip=True)

        # Try meta tag
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content')

        # Try citation meta
        citation_title = soup.find('meta', attrs={'name': 'citation_title'})
        if citation_title:
            return citation_title.get('content')

        return None

    def _extract_abstract(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article abstract."""
        abstract_section = soup.find(['div', 'section'], class_=re.compile(r'abstract'))
        if abstract_section:
            return abstract_section.get_text(strip=True)

        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content')

        return None

    def _extract_authors(self, soup: BeautifulSoup) -> List[str]:
        """Extract author names."""
        authors = []

        # Try citation meta tags
        author_metas = soup.find_all('meta', attrs={'name': 'citation_author'})
        for meta in author_metas:
            author_name = meta.get('content')
            if author_name:
                authors.append(author_name)

        # If no meta tags, try parsing from page
        if not authors:
            author_tags = soup.find_all(['span', 'a'], class_=re.compile(r'author'))
            for tag in author_tags[:10]:
                author_name = tag.get_text(strip=True)
                if author_name and len(author_name) > 2:
                    authors.append(author_name)

        return authors

    def _extract_doi(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract DOI."""
        doi_meta = soup.find('meta', attrs={'name': 'citation_doi'})
        if doi_meta:
            return doi_meta.get('content')

        # Try finding DOI in text
        doi_text = soup.find(text=re.compile(r'10\.\d{4,}/f1000research'))
        if doi_text:
            match = re.search(r'10\.\d{4,}/[\w\.\-]+', doi_text)
            if match:
                return match.group(0)

        return None

    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract article keywords."""
        keywords = []

        keyword_meta = soup.find('meta', attrs={'name': 'citation_keywords'})
        if keyword_meta:
            content = keyword_meta.get('content', '')
            keywords = [k.strip() for k in content.split(',') if k.strip()]

        return keywords

    def _extract_reviews(self, soup: BeautifulSoup, article_id: str) -> List[Review]:
        """
        Extract peer reviews from F1000Research article page.

        F1000Research publishes reviews with reviewer names after publication.
        """
        reviews = []

        # Look for referee reports section
        review_sections = soup.find_all(['div', 'article'], class_=re.compile(r'referee|review|report'))

        for i, section in enumerate(review_sections, 1):
            # Extract reviewer name (F1000 publishes reviewer names)
            reviewer_name_tag = section.find(['h3', 'h4', 'strong', 'span'], class_=re.compile(r'referee|reviewer'))
            reviewer_name = None
            reviewer_affiliation = None

            if reviewer_name_tag:
                reviewer_text = reviewer_name_tag.get_text(strip=True)
                # Clean up name
                reviewer_name = re.sub(r'Referee|Reviewer|Report by', '', reviewer_text, flags=re.IGNORECASE).strip()
                if len(reviewer_name) < 3:
                    reviewer_name = None

            # Extract affiliation if present
            affiliation_tag = section.find(['span', 'div'], class_=re.compile(r'affiliation'))
            if affiliation_tag:
                reviewer_affiliation = affiliation_tag.get_text(strip=True)

            # Extract review text
            review_text_tag = section.find(['div', 'p'], class_=re.compile(r'report-body|review-body|referee-report'))
            if not review_text_tag:
                # Get all text from section
                review_text = section.get_text(separator='\n', strip=True)
            else:
                review_text = review_text_tag.get_text(separator='\n', strip=True)

            # Extract recommendation/decision if present
            recommendation = None
            recommendation_tag = section.find(text=re.compile(r'Approved|Not Approved|Approved with reservations', re.IGNORECASE))
            if recommendation_tag:
                rec_text = recommendation_tag.strip().lower()
                if 'approved with reservations' in rec_text:
                    recommendation = 'approved_with_reservations'
                elif 'approved' in rec_text:
                    recommendation = 'approved'
                elif 'not approved' in rec_text:
                    recommendation = 'not_approved'

            if len(review_text) > 100:  # Ensure substantial content
                reviewer = Reviewer(
                    reviewer_id=f"{article_id}_reviewer_{i}",
                    name=reviewer_name,
                    affiliation=reviewer_affiliation,
                    is_anonymous=(reviewer_name is None)
                )

                review = Review(
                    review_id=f"{article_id}_review_{i}",
                    reviewer=reviewer,
                    review_text=review_text,
                    recommendation=recommendation
                )

                reviews.append(review)

        return reviews

    def _extract_publication_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date."""
        date_meta = soup.find('meta', attrs={'name': 'citation_publication_date'})
        if date_meta:
            return date_meta.get('content')

        time_tag = soup.find('time')
        if time_tag:
            return time_tag.get('datetime') or time_tag.get_text(strip=True)

        return None

    def _determine_decision(self, soup: BeautifulSoup) -> ReviewDecision:
        """
        Determine editorial decision based on review status.

        F1000Research uses an approval system rather than accept/reject.
        """
        # Look for approval status
        status_text = soup.get_text().lower()

        if 'approved' in status_text and 'not approved' not in status_text:
            return ReviewDecision.ACCEPT
        elif 'not approved' in status_text:
            return ReviewDecision.REJECT

        return ReviewDecision.PENDING
