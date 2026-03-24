import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Initialize a session to handle cookies and headers automatically
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def get_all_forms(url):
    """Fetches all form tags from the given URL."""
    try:
        soup = BeautifulSoup(s.get(url).content, "html.parser")
        return soup.find_all("form")
    except Exception as e:
        print(f"[-] Error fetching forms from {url}: {e}")
        return []

def get_form_details(form):
    """Extracts useful information (action, method, inputs) from an HTML form."""
    details = {}
    
    # Get the form action (target URL) and method (GET or POST)
    action = form.attrs.get("action", "").lower()
    method = form.attrs.get("method", "get").lower()
    
    # Extract all input fields
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
        
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

def submit_form(form_details, url, value):
    """Submits a form with the injected payload."""
    target_url = urljoin(url, form_details["action"])
    inputs = form_details["inputs"]
    data = {}
    
    for input in inputs:
        # Replace text/search fields with our payload; leave hidden/submit fields alone if possible
        if input["type"] == "text" or input["type"] == "search":
            input["value"] = value
        
        input_name = input.get("name")
        input_value = input.get("value")
        if input_name:
            data[input_name] = input_value

    if form_details["method"] == "post":
        return s.post(target_url, data=data)
    else:
        return s.get(target_url, params=data)

def scan_sql_injection(url):
    """Tests forms on the URL for SQL Injection vulnerabilities."""
    print(f"[*] Scanning {url} for SQL Injection...")
    forms = get_all_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")
    
    # Common SQLi error messages to look for
    sql_errors = [
        "you have an error in your sql syntax",
        "warning: mysql",
        "unclosed quotation mark after the character string",
        "quoted string not properly terminated"
    ]
    
    # Standard SQLi test payload
    payload = "'"
    
    for form in forms:
        form_details = get_form_details(form)
        response = submit_form(form_details, url, payload)
        
        if response:
            content = response.text.lower()
            for error in sql_errors:
                if error in content:
                    print(f"\n[!] SQL Injection Vulnerability Detected!")
                    print(f"[*] Form details: {form_details}")
                    return True
    print("[-] No SQL Injection vulnerabilities found.")
    return False

def scan_xss(url):
    """Tests forms on the URL for Cross-Site Scripting (XSS) vulnerabilities."""
    print(f"\n[*] Scanning {url} for XSS...")
    forms = get_all_forms(url)
    
    # Standard XSS test payload
    xss_payload = "<script>alert('XSS_TEST')</script>"
    
    for form in forms:
        form_details = get_form_details(form)
        response = submit_form(form_details, url, xss_payload)
        
        if response:
            # If the exact payload is reflected in the raw HTML, it's likely vulnerable
            if xss_payload in response.text:
                print(f"\n[!] XSS Vulnerability Detected!")
                print(f"[*] Form details: {form_details}")
                return True
    print("[-] No XSS vulnerabilities found.")
    return False

if __name__ == "__main__":
    print("--- Web Application Vulnerability Scanner ---")
    target_url = input("Enter the target URL (e.g., http://example.com): ")
    
    scan_sql_injection(target_url)
    scan_xss(target_url)