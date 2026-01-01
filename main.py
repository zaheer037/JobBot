import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# --- Configuration ---
# PLACEHOLDER URL: Replace this with the actual GitHub issue tracker or repo URL you want to scrape.
# Example: "https://github.com/SimplifyJobs/New-Grad-Positions/issues" or similar.
TARGET_URL = "https://github.com/SimplifyJobs/New-Grad-Positions" 

KEYWORDS = ["sde-1", "2026 batch", "software engineer i", "graduate engineer trainee", "intern"]
PROCESSED_JOBS_FILE = "processed_jobs.json"

def get_processed_jobs():
    """Load the list of already processed job IDs/URLs."""
    if not os.path.exists(PROCESSED_JOBS_FILE):
        return []
    with open(PROCESSED_JOBS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_processed_jobs(jobs):
    """Save the list of processed job IDs/URLs."""
    with open(PROCESSED_JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=4)

def scrape_jobs():
    """Scrape jobs from the target URL and return detailed objects."""
    print(f"Scraping {TARGET_URL}...")
    try:
        response = requests.get(TARGET_URL, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    found_jobs = []

    # NOTE: The scraping logic here is highly dependent on the specific structure 
    # of the target GitHub repository's README or Issue page. 
    # Since we are targeting a generic "GitHub New Grad 2026 Tracker Repo", 
    # I will assume a standard markdown table structure commonly found in READMEs (like SimplifyJobs).
    # You may need to ADJUST the selectors (.find) based on the actual HTML structure.
    
    # Looking for table rows in the README
    # Common structure: <table> result inside <article> or .markdown-body
    
    tables = soup.find_all("table")
    
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if not cols:
                continue
            
            # Heuristic: assume 'Company' is in first or second col, 'Role' in second or third, 'Location' etc.
            # And usually there is a link to the job application.
            
            row_text = row.get_text(" ", strip=True).lower()
            
            # Filtering Logic
            if any(keyword in row_text for keyword in KEYWORDS):
                # Extract link - look for the 'Apply' link or similar
                link_tag = row.find("a", href=True)
                if link_tag:
                    job_url = link_tag['href']
                    # Use URL as unique ID, or combine company + role if URL is generic
                    job_id = job_url 
                    
                    found_jobs.append({
                        "id": job_id,
                        "text": row.get_text(" | ", strip=True),
                        "url": job_url
                    })

    print(f"Found {len(found_jobs)} potential jobs matching keywords.")
    return found_jobs

def send_email(new_jobs):
    """Send an email with the new jobs."""
    sender_email = os.environ.get("SENDER_EMAIL")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    if not all([sender_email, receiver_email, password]):
        print("Scraping finished, but email credentials are missing. Skipping email.")
        return

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = f"Job Job Alert: {len(new_jobs)} New Openings Found ({datetime.now().strftime('%Y-%m-%d')})"

    body = "<h2>New Job Openings Found Today:</h2><ul>"
    for job in new_jobs:
        body += f"<li><a href='{job['url']}'>{job['text']}</a></li>"
    body += "</ul>"

    msg.attach(MIMEText(body, "html"))

    try:
        # Connecting to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    processed_jobs = get_processed_jobs()
    all_jobs = scrape_jobs()
    
    new_jobs = []
    processed_set = set(processed_jobs) # optimize lookup

    for job in all_jobs:
        if job["id"] not in processed_set:
            new_jobs.append(job)
            processed_jobs.append(job["id"])
            processed_set.add(job["id"])

    if new_jobs:
        print(f"{len(new_jobs)} new jobs found.")
        send_email(new_jobs)
        save_processed_jobs(processed_jobs)
    else:
        print("No new jobs found.")

if __name__ == "__main__":
    main()
