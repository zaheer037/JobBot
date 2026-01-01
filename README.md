# Job Automation Bot

A Python-based automated job scraper that runs daily on GitHub Actions to find SDE-1, New Grad, and Internship roles (2026 Batch) in India.

## Features

-   **Scrapes** a target GitHub repository/tracker for job listings.
-   **Filters** for keywords: SDE-1, 2026 Batch, Software Engineer I, Graduate Engineer Trainee, Intern.
-   **Emails** you a daily summary of *new* jobs found.
-   **Remembers** previously seen jobs using `processed_jobs.json` to prevent duplicate alerts.
-   **Runs Automatically** every day at 8:00 AM IST via GitHub Actions.

## Setup

### 1. Local Setup

1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  (Optional) Edit `main.py` and update `TARGET_URL` if you want to target a specific repository other than the default placeholder.

### 2. Email Configuration (Gmail)

To allow the bot to send emails, you need an **App Password** (do not use your real password).

1.  Go to your Google Account > Security.
2.  Enable 2-Step Verification.
3.  Search for "App Passwords" and create one named "JobBot".
4.  Copy the 16-character password.

### 3. GitHub Secrets Configuration

1.  Go to your GitHub Repository > **Settings**.
2.  Scroll down to **Secrets and variables** > **Actions**.
3.  Click **New repository secret** and add the following:

| Name | Value |
| :--- | :--- |
| `SENDER_EMAIL` | Your Gmail address (the one sending the email) |
| `EMAIL_PASSWORD` | The 16-character App Password you generated |
| `RECEIVER_EMAIL` | The email address where you want to receive alerts |

### 4. Enable Workflow Permissions

1.  Go to **Settings** > **Actions** > **General**.
2.  Under **Workflow permissions**, select **Read and write permissions**.
3.  Click **Save**.

This is required so the bot can update `processed_jobs.json` in the repository.

## Usage

-   The bot will run automatically every day at 8:00 AM IST.
-   You can also trigger it manually by going to the **Actions** tab > **Daily Job Scraper** > **Run workflow**.
