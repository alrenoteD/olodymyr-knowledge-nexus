
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Web Scraper for Olodymyr AI Assistant

This module handles web scraping to extract content from URLs.
"""

import logging
import asyncio
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

async def scrape_webpage(url):
    """
    Scrape content from a webpage.
    
    Args:
        url: URL to scrape
        
    Returns:
        Extracted text content
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type.lower():
            raise ValueError(f"URL does not contain HTML content: {content_type}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'head', 'header', 'noscript', 'iframe']):
            element.decompose()
        
        # Find the main content
        main_content = extract_main_content(soup, url)
        
        # Clean and format the text
        cleaned_text = clean_text(main_content)
        
        # Add source information
        cleaned_text += f"\n\nSource: {url}"
        
        return cleaned_text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        raise ValueError(f"Failed to fetch URL: {e}")
        
    except Exception as e:
        logger.error(f"Error scraping webpage {url}: {e}")
        raise

def extract_main_content(soup, url):
    """
    Extract the main content from a BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup object
        url: Original URL for domain-specific handling
        
    Returns:
        Extracted main content text
    """
    # Try common content containers
    main_content_candidates = []
    
    # Look for article element
    article = soup.find('article')
    if article:
        main_content_candidates.append(article.get_text())
    
    # Look for main element
    main = soup.find('main')
    if main:
        main_content_candidates.append(main.get_text())
    
    # Look for common content div IDs
    for content_id in ['content', 'main-content', 'article', 'post', 'entry', 'blog-post']:
        content_div = soup.find(id=re.compile(f'^{content_id}', re.I))
        if content_div:
            main_content_candidates.append(content_div.get_text())
    
    # Look for common content div classes
    for content_class in ['content', 'article', 'post', 'entry', 'blog-post', 'story']:
        content_divs = soup.find_all(class_=re.compile(f'^{content_class}', re.I))
        for div in content_divs:
            main_content_candidates.append(div.get_text())
    
    # If we found any candidates, return the longest one
    if main_content_candidates:
        return max(main_content_candidates, key=len)
    
    # Fallback: get all paragraphs
    paragraphs = soup.find_all('p')
    paragraph_text = '\n\n'.join(p.get_text() for p in paragraphs)
    
    # If we have paragraph text, return it
    if paragraph_text and len(paragraph_text) > 100:
        return paragraph_text
    
    # Last resort: get the body text
    return soup.get_text()

def clean_text(text):
    """
    Clean and format extracted text.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Replace multiple newlines with double newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Remove lines that are just whitespace
    text = '\n'.join(line for line in text.split('\n') if line.strip())
    
    # Try to preserve paragraphs
    text = re.sub(r'([.!?])\s', r'\1\n\n', text)
    
    return text.strip()
