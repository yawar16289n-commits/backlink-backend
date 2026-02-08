import re
from urllib.parse import urlparse

def extract_domain(url):
    """
    Extract domain from URL preserving subdomains.
    Uses custom regex to handle various URL formats.
    
    Examples:
        https://blog.example.com/page -> blog.example.com
        http://www.site.co.uk/path -> www.site.co.uk
        example.com -> example.com
    """
    if not url:
        return ''
    
    # Add http:// if no scheme present
    if not url.startswith(('http://', 'https://', '//')):
        url = 'http://' + url
    
    try:
        # Parse the URL
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split('/')[0]
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        return domain.lower()
    except Exception as e:
        # Fallback: use regex to extract domain-like pattern
        match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)', url)
        if match:
            return match.group(1).lower()
        return ''

def validate_da_spam_score(value):
    """
    Validate DA and Spam Score values.
    Must be integers between 0 and 100 (inclusive).
    """
    try:
        int_value = int(value)
        if int_value < 0 or int_value > 100:
            return False, "Value must be between 0 and 100"
        if int_value != float(value):
            return False, "Value must be a whole number"
        return True, int_value
    except (ValueError, TypeError):
        return False, "Value must be a valid integer"
