"""
eLife peer review data collector.

Collects reviewed preprints from eLife, which publishes all peer reviews openly.
Uses eLife's API and web scraping to gather review data.
"""

import requests
import time
import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import (
    Manuscript, Review, Reviewer, AuthorResponse, EditorialAssessment,
    ReviewSource, ReviewDecision, CollectionMetadata
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElifeCollector:
    """Collector for eLife reviewed preprints."""

    BASE_URL = "https://elifesciences.org"
    API_BASE = "https://api.elifesciences.org"

    def __init__(self, rate_limit_delay: float = 2.0):
        """
        Initialize eLife collector.

        Args:
            rate_limit_delay: Delay between requests in seconds (be respectful!)
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
            subject_areas: Filter by subject areas (e.g., ['neuroscience', 'cell-biology'])
            start_date: Collect articles from this date onwards (YYYY-MM-DD)

        Returns:
            Tuple of (list of manuscripts, collection metadata)
        """
        collection_id = f"elife_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = CollectionMetadata(
            collection_id=collection_id,
            source=ReviewSource.ELIFE,
            start_time=datetime.now().isoformat(),
            config={
                'num_manuscripts': num_manuscripts,
                'subject_areas': subject_areas,
                'start_date': start_date
            }
        )

        manuscripts = []
        article_ids = self._discover_articles(num_manuscripts, subject_areas, start_date)

        logger.info(f"Found {len(article_ids)} article IDs to process")

        for i, article_id in enumerate(article_ids[:num_manuscripts], 1):
            try:
                logger.info(f"Processing article {i}/{num_manuscripts}: {article_id}")
                metadata.num_manuscripts_attempted += 1

                manuscript = self.collect_single_manuscript(article_id)

                if manuscript:
                    # Validate manuscript
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

                # Rate limiting
                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Error processing {article_id}: {str(e)}")
                metadata.num_manuscripts_failed += 1
                metadata.errors.append({
                    'article_id': article_id,
                    'error': str(e)
                })

        metadata.end_time = datetime.now().isoformat()
        return manuscripts, metadata

    def _discover_articles(
        self,
        num_articles: int,
        subject_areas: Optional[List[str]],
        start_date: Optional[str]
    ) -> List[str]:
        """
        Discover article IDs from eLife's reviewed preprints page.

        Returns:
            List of article IDs
        """
        article_ids = []

        # Try to get articles from the reviewed preprints page
        # We'll scrape the listing page or use API if available
        try:
            url = f"{self.BASE_URL}/reviewed-preprints"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find article links (adjust selectors based on actual page structure)
            # This is a heuristic - may need adjustment
            article_links = soup.find_all('a', href=re.compile(r'/reviewed-preprints/\d+'))

            for link in article_links:
                href = link.get('href', '')
                match = re.search(r'/reviewed-preprints/(\d+)', href)
                if match:
                    article_id = match.group(1)
                    if article_id not in article_ids:
                        article_ids.append(article_id)

            # If we didn't find enough, try alternate approach with articles page
            if len(article_ids) < num_articles:
                logger.info("Trying alternate discovery method via articles page")
                url = f"{self.BASE_URL}/articles"
                response = self.session.get(url, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')
                article_links = soup.find_all('a', href=re.compile(r'/articles/\d+'))

                for link in article_links:
                    href = link.get('href', '')
                    match = re.search(r'/articles/(\d+)', href)
                    if match:
                        article_id = match.group(1)
                        if article_id not in article_ids:
                            article_ids.append(article_id)

        except Exception as e:
            logger.error(f"Error discovering articles: {str(e)}")

        # Fallback: use some known article IDs from recent publications
        if len(article_ids) < 5:
            logger.warning("Few articles discovered, using fallback article IDs")
            # These are example IDs - they may need updating
            article_ids.extend(['97433', '95132', '93215', '89376', '86956'])

        return article_ids

    def collect_single_manuscript(self, article_id: str) -> Optional[Manuscript]:
        """
        Collect a single manuscript with all its peer reviews.

        Args:
            article_id: eLife article ID (e.g., '97433')

        Returns:
            Manuscript object or None if collection failed
        """
        try:
            # Try reviewed preprints first (new model)
            article_url = f"{self.BASE_URL}/reviewed-preprints/{article_id}"
            response = self.session.get(article_url, timeout=30)

            # If reviewed preprint doesn't exist, try regular article
            if response.status_code == 404:
                article_url = f"{self.BASE_URL}/articles/{article_id}"
                response = self.session.get(article_url, timeout=30)

            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract article metadata
            title = self._extract_title(soup)
            abstract = self._extract_abstract(soup)
            authors = self._extract_authors(soup)
            doi = self._extract_doi(soup)

            # Extract peer reviews
            reviews = self._extract_reviews(soup, article_id)

            # Extract editorial assessment (eLife specific)
            editorial_assessments = self._extract_editorial_assessment(soup, article_id)

            # Extract author responses
            author_responses = self._extract_author_responses(soup, article_id)

            # Extract dates
            publication_date = self._extract_publication_date(soup)

            # Create manuscript object
            manuscript = Manuscript(
                manuscript_id=article_id,
                source=ReviewSource.ELIFE,
                source_url=article_url,
                title=title or f"Article {article_id}",
                abstract=abstract,
                authors=authors,
                doi=doi,
                reviews=reviews,
                editorial_assessments=editorial_assessments,
                author_responses=author_responses,
                publication_date=publication_date,
                decision=ReviewDecision.NO_DECISION,  # eLife doesn't make accept/reject decisions
                raw_data={'html_collected': True}
            )

            return manuscript

        except Exception as e:
            logger.error(f"Error collecting article {article_id}: {str(e)}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title."""
        title_tag = soup.find('h1', class_=re.compile(r'title|heading'))
        if not title_tag:
            title_tag = soup.find('meta', property='og:title')
            if title_tag:
                return title_tag.get('content')
        return title_tag.get_text(strip=True) if title_tag else None

    def _extract_abstract(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article abstract."""
        abstract_tag = soup.find('div', class_=re.compile(r'abstract'))
        if not abstract_tag:
            abstract_tag = soup.find('meta', attrs={'name': 'description'})
            if abstract_tag:
                return abstract_tag.get('content')
        return abstract_tag.get_text(strip=True) if abstract_tag else None

    def _extract_authors(self, soup: BeautifulSoup) -> List[str]:
        """Extract author names."""
        authors = []
        author_tags = soup.find_all(['span', 'a'], class_=re.compile(r'author'))
        for tag in author_tags:
            author_name = tag.get_text(strip=True)
            if author_name and len(author_name) > 2:
                authors.append(author_name)
        return authors[:10]  # Limit to first 10 authors

    def _extract_doi(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract DOI."""
        doi_tag = soup.find('meta', attrs={'name': 'citation_doi'})
        if doi_tag:
            return doi_tag.get('content')
        doi_text = soup.find(text=re.compile(r'10\.\d{4,}/'))
        if doi_text:
            match = re.search(r'10\.\d{4,}/[\w\.\-]+', doi_text)
            if match:
                return match.group(0)
        return None

    def _extract_reviews(self, soup: BeautifulSoup, article_id: str) -> List[Review]:
        """Extract peer reviews from the page."""
        reviews = []

        # Look for review sections
        review_sections = soup.find_all(['div', 'section'], class_=re.compile(r'review|peer-review'))

        if not review_sections:
            # Try alternate structure
            review_sections = soup.find_all(['div', 'article'], attrs={'data-test': re.compile(r'review')})

        for i, section in enumerate(review_sections, 1):
            review_text = section.get_text(separator='\n', strip=True)

            # Extract reviewer info if available
            reviewer_name_tag = section.find(['h3', 'h4', 'strong'], text=re.compile(r'Reviewer|Review \d+'))
            reviewer_name = None
            is_anonymous = True

            if reviewer_name_tag:
                reviewer_text = reviewer_name_tag.get_text(strip=True)
                # Check if reviewer name is mentioned
                if not re.match(r'^Reviewer \d+$|^Review \d+$', reviewer_text):
                    reviewer_name = reviewer_text
                    is_anonymous = False

            if len(review_text) > 100:  # Ensure it's substantial
                reviewer = Reviewer(
                    reviewer_id=f"{article_id}_reviewer_{i}",
                    name=reviewer_name,
                    is_anonymous=is_anonymous
                )

                review = Review(
                    review_id=f"{article_id}_review_{i}",
                    reviewer=reviewer,
                    review_text=review_text
                )

                reviews.append(review)

        return reviews

    def _extract_editorial_assessment(self, soup: BeautifulSoup, article_id: str) -> List[EditorialAssessment]:
        """Extract eLife editorial assessment."""
        assessments = []

        # Look for eLife assessment section
        assessment_section = soup.find(['div', 'section'], class_=re.compile(r'assessment|elife-assessment'))

        if assessment_section:
            assessment_text = assessment_section.get_text(separator='\n', strip=True)

            # Try to extract significance and strength ratings
            significance = None
            strength = None

            text_lower = assessment_text.lower()
            if 'landmark' in text_lower:
                significance = 'landmark'
            elif 'important' in text_lower:
                significance = 'important'
            elif 'useful' in text_lower:
                significance = 'useful'

            if 'exceptional' in text_lower:
                strength = 'exceptional'
            elif 'solid' in text_lower or 'strong' in text_lower:
                strength = 'solid'
            elif 'inadequate' in text_lower:
                strength = 'inadequate'

            assessment = EditorialAssessment(
                assessment_id=f"{article_id}_assessment",
                assessment_text=assessment_text,
                significance=significance,
                strength_of_evidence=strength
            )

            assessments.append(assessment)

        return assessments

    def _extract_author_responses(self, soup: BeautifulSoup, article_id: str) -> List[AuthorResponse]:
        """Extract author responses to reviews."""
        responses = []

        # Look for author response sections
        response_sections = soup.find_all(['div', 'section'], class_=re.compile(r'author.?response'))

        for i, section in enumerate(response_sections, 1):
            response_text = section.get_text(separator='\n', strip=True)

            if len(response_text) > 100:
                response = AuthorResponse(
                    response_id=f"{article_id}_response_{i}",
                    response_text=response_text
                )
                responses.append(response)

        return responses

    def _extract_publication_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date."""
        date_tag = soup.find('meta', attrs={'name': 'citation_publication_date'})
        if date_tag:
            return date_tag.get('content')

        date_tag = soup.find('time')
        if date_tag:
            return date_tag.get('datetime') or date_tag.get_text(strip=True)

        return None
