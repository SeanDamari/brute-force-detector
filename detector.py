#!/usr/bin/env python3
"""
Brute Force Attack Detector with AI Reporting
==============================================
Created by: Sean
Purpose: Educational cybersecurity project
License: For educational use only

This script detects "Succeed-After-Fail" brute force patterns in server logs
and generates professional incident reports using Google Gemini AI.
"""

import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import sys
import os

# ============================================================================
# ⚙️ קונפיגורציה / Configuration
# ============================================================================

# 🔴🔴🔴 הכנס את המפתח שלך כאן / INSERT YOUR API KEY HERE 🔴🔴🔴
GEMINI_API_KEY = "PASTE_YOUR_API_KEY_HERE" 

# Detection parameters
FAILED_ATTEMPTS_THRESHOLD = 3   # How many failed attempts = suspicious?
TIME_WINDOW_MINUTES = 5         # Within what timeframe?
FAIL_CODE = 401                 # HTTP status code for failed login
SUCCESS_CODES = [200, 201]      # HTTP status codes for successful login

# File paths
INPUT_FILE = "server_log.csv"
OUTPUT_FILE = "output/suspicious_activity.csv"

# ============================================================================
# 🤖 AI + Report Generation
# ============================================================================

def analyze_with_gemini(suspicious_activities):
    """
    Generate a professional security incident report using Google Gemini AI.
    
    Args:
        suspicious_activities: List of detected attack patterns
    """
    print("\n[AI] 🤖 מתחבר ל-Gemini ומייצר דוח מפורט...")
    
    # Validate API key
    if not GEMINI_API_KEY or "PASTE" in GEMINI_API_KEY:
        print("   ❌ שגיאה: נא להגדיר מפתח API.")
        return

    try:
        # 1. Create HTML table of attackers (independent of AI)
        if suspicious_activities:
            df_sus = pd.DataFrame(suspicious_activities)
            df_sus = df_sus[['IP', 'Attack_Start', 'Failed_Attempts', 'Breach_Confirmed']]
            df_sus.columns = ['כתובת IP תוקפת', 'זמן התחלה', 'כמות ניסיונות', 'האם נפרץ?']
            
            # Convert to HTML
            attacks_table_html = df_sus.to_html(index=False, classes='styled-table', border=0)
            
            # Color code the breach status
            attacks_table_html = attacks_table_html.replace(
                '<td>True</td>', 
                '<td style="color:red; font-weight:bold;">⚠️ כן (פריצה!)</td>'
            )
            attacks_table_html = attacks_table_html.replace(
                '<td>False</td>', 
                '<td style="color:green;">לא (נחסם)</td>'
            )
        else:
            attacks_table_html = "<p>לא נמצאו נתונים להצגה בטבלה.</p>"

        # 2. Configure and query Gemini AI
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash') 

        data_summary = str(suspicious_activities) if suspicious_activities else "No attacks."

        prompt = f"""
        You are a Cybersecurity SOC Analyst.
        Analyze these brute force logs: {data_summary}
        
        Write an Incident Report in Hebrew (עברית).
        Do NOT write a list of IPs (I have a table for that).
        Focus on:
        1. <b>תקציר מנהלים</b>: What happened generally?
        2. <b>הערכת חומרה</b>: Critical/Medium/Low?
        3. <b>המלצות</b>: What should IT do now?
        """

        response = model.generate_content(prompt)
        
        # 3. Build final HTML report
        html_content = f"""
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <title>דוח אירוע סייבר</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f6f9; color: #333; padding: 20px; }}
                .container {{ background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 900px; margin: 0 auto; }}
                h1 {{ color: #c0392b; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                
                /* Styled table */
                .styled-table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.9em; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15); }}
                .styled-table thead tr {{ background-color: #009879; color: #ffffff; text-align: right; }}
                .styled-table th, .styled-table td {{ padding: 12px 15px; border-bottom: 1px solid #dddddd; }}
                .styled-table tbody tr:nth-of-type(even) {{ background-color: #f3f3f3; }}
                .styled-table tbody tr:hover {{ background-color: #f1f1f1; cursor: pointer; }}
                
                .mitre-section {{ text-align: center; margin-top: 40px; padding: 20px; background-color: #e9ecef; border-radius: 8px; }}
                .mitre-btn {{ background-color: #2c3e50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚨 דוח אירוע אבטחה (SOC Report)</h1>
                
                <div class="ai-analysis">
                    {response.text}
                </div>

                <h2 style="color: #2c3e50; border-right: 5px solid #009879; padding-right: 10px; margin-top: 40px;">
                    📊 פירוט טכני מלא (מזוהה ע"י הסקריפט)
                </h2>
                {attacks_table_html}
                
                <div class="mitre-section">
                    <p>למידע נוסף על טקטיקות תקיפה:</p>
                    <a href="https://attack.mitre.org/" target="_blank" class="mitre-btn">
                        🌐 למעבר ל-MITRE ATT&CK
                    </a>
                </div>

                <div class="footer">Generated by AI Security Detector | {datetime.now().strftime("%d/%m/%Y")}</div>
            </div>
        </body>
        </html>
        """
        
        # Save report
        with open("report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("\n" + "="*60)
        print("✅ הדוח מוכן! (כולל טבלה מלאה של כל התוקפים)")
        print("📂 לפתיחה: xdg-open report.html")
        print("="*60 + "\n")

    except Exception as e:
        print(f"   ⚠️  AI Analysis Failed: {e}")

# ============================================================================
# ⚙️ Data Processing
# ============================================================================

def parse_time(time_str):
    """Parse time string to datetime object."""
    try:
        return datetime.strptime(time_str, "%d/%m/%Y %H:%M")
    except ValueError:
        return None

def load_logs(file_path):
    """Load and validate server logs from CSV file."""
    print(f"\n[1/4] 📂 טוען לוגים: {file_path}")
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        print(f"   ✅ נטענו {len(df)} שורות")
        return df
    except Exception as e:
        print(f"❌ שגיאה בקריאת הקובץ: {e}")
        return None

# ============================================================================
# 🔍 Detection Engine
# ============================================================================

def find_attack_windows(fail_times):
    """
    Find time windows containing suspicious failed login attempts.
    Uses a sliding window algorithm to detect attack patterns.
    
    Args:
        fail_times: List of datetime objects representing failed login attempts
        
    Returns:
        List of dictionaries containing attack window details
    """
    if not fail_times:
        return []
    
    windows = []
    current_window_start = fail_times[0]
    current_window_end = fail_times[0]
    current_count = 1
    
    for i in range(1, len(fail_times)):
        time_diff = (fail_times[i] - current_window_start).total_seconds() / 60
        
        if time_diff <= TIME_WINDOW_MINUTES:
            # Still within time window - add to current window
            current_window_end = fail_times[i]
            current_count += 1
        else:
            # Window expired - save if threshold met
            if current_count >= FAILED_ATTEMPTS_THRESHOLD:
                windows.append({
                    'start': current_window_start,
                    'end': current_window_end,
                    'count': current_count
                })
            
            # Start new window
            current_window_start = fail_times[i]
            current_window_end = fail_times[i]
            current_count = 1
    
    # Check final window
    if current_count >= FAILED_ATTEMPTS_THRESHOLD:
        windows.append({
            'start': current_window_start,
            'end': current_window_end,
            'count': current_count
        })
    
    return windows

def check_breach(ip, attack_end_time, df):
    """
    Check if a successful login occurred after the attack window.
    This indicates a successful breach (Succeed-After-Fail pattern).
    
    Args:
        ip: IP address of the attacker
        attack_end_time: End time of the attack window
        df: DataFrame containing all logs
        
    Returns:
        Boolean indicating if breach was successful
    """
    # Filter logs for this IP after attack
    ip_logs = df[df['IP'] == ip].copy()
    ip_logs['DateTime'] = ip_logs['Time'].apply(parse_time)
    ip_logs = ip_logs.dropna(subset=['DateTime'])
    
    after_attack = ip_logs[ip_logs['DateTime'] > attack_end_time]
    successful = after_attack[after_attack['Status Code'].isin(SUCCESS_CODES)]
    
    return len(successful) > 0

def detect_attacks(df):
    """
    Main detection function - identifies brute force attack patterns.
    
    Args:
        df: DataFrame containing server logs
        
    Returns:
        List of suspicious activities with breach confirmation
    """
    print("\n[2/4] 🔍 מנתח לוגים...")
    suspicious_activities = []
    
    # Filter to failed login attempts
    failed_logins = df[df['Status Code'] == FAIL_CODE].copy()
    failed_logins['DateTime'] = failed_logins['Time'].apply(parse_time)
    failed_logins = failed_logins.dropna(subset=['DateTime'])
    
    # Analyze each IP separately
    for ip, ip_group in failed_logins.groupby('IP'):
        ip_group = ip_group.sort_values('DateTime')
        fail_times = ip_group['DateTime'].tolist()
        
        # Find attack windows
        windows = find_attack_windows(fail_times)
        
        for window in windows:
            if window['count'] >= FAILED_ATTEMPTS_THRESHOLD:
                # Check if breach was successful
                breach = check_breach(ip, window['end'], df)
                
                suspicious_activities.append({
                    'IP': ip,
                    'Attack_Start': window['start'].strftime("%d/%m/%Y %H:%M"),
                    'Attack_End': window['end'].strftime("%d/%m/%Y %H:%M"),
                    'Failed_Attempts': window['count'],
                    'Breach_Confirmed': breach
                })
    
    print(f"   🎯 נמצאו {len(suspicious_activities)} תוקפים")
    return suspicious_activities

# ============================================================================
# 🚀 Main Execution
# ============================================================================

def main():
    """Main program flow."""
    print("\n" + "="*60)
    print("🔐 BRUTE FORCE DETECTOR + GEMINI AI")
    print("   Created by: Sean | Educational Project")
    print("="*60)
    
    # Load logs
    df = load_logs(INPUT_FILE)
    if df is None:
        return
    
    # Detect attacks
    suspicious_activities = detect_attacks(df)
    
    # Save results to CSV
    if suspicious_activities:
        print("\n[3/4] 💾 שומר נתונים...")
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        pd.DataFrame(suspicious_activities).to_csv(OUTPUT_FILE, index=False)
        print(f"   ✅ נשמר ב-{OUTPUT_FILE}")
    else:
        print("\n[3/4] ✅ לא נמצאו התקפות.")

    # Generate AI report
    print("\n[4/4] 🤖 יוצר דוח AI...")
    analyze_with_gemini(suspicious_activities)
    
    print("\n" + "="*60)
    print("✅ סיימנו! בדוק את הקבצים:")
    print(f"   📊 CSV: {OUTPUT_FILE}")
    print(f"   📄 HTML: report.html")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
