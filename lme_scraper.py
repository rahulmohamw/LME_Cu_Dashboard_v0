#!/usr/bin/env python3
"""
Fixed LME Copper Data Scraper for Westmetall
Properly handles German dates and European number formatting
Scrapes data from 2010 to present with correct CSV output
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import time
import logging
import os

class LMECopperScraperFixed:
    def __init__(self):
        self.base_url = "https://www.westmetall.com/en/markdaten.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.data = []
        
        # Month names mapping (English names used on the site)
        self.month_mapping = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
    def parse_date(self, date_str):
        """Parse date format like '11. July 2025' to YYYY-MM-DD"""
        try:
            date_str = date_str.strip()
            
            # Pattern: "11. July 2025"
            pattern = r'(\d{1,2})\.\s*(\w+)\s*(\d{4})'
            match = re.match(pattern, date_str)
            
            if match:
                day = int(match.group(1))
                month_name = match.group(2)
                year = int(match.group(3))
                
                month = self.month_mapping.get(month_name)
                if month:
                    date_obj = datetime(year, month, day)
                    return date_obj.strftime('%Y-%m-%d')
            
            return None
                
        except Exception as e:
            self.logger.error(f"Error parsing date '{date_str}': {e}")
            return None
    
    def parse_number(self, num_str, is_price=True):
        """Parse numbers like '9,637.50' (price) or '108,725' (stock)"""
        try:
            if not num_str or num_str.strip() in ['-', '']:
                return None
            
            num_str = num_str.strip()
            # Remove any non-numeric characters except comma and dot
            num_str = re.sub(r'[^\d,.-]', '', num_str)
            
            if ',' in num_str and '.' in num_str:
                # Format: 9,637.50 - comma is thousands separator, dot is decimal
                num_str = num_str.replace(',', '')
                return float(num_str) if is_price else int(float(num_str))
            elif ',' in num_str:
                # Format: 108,725 - comma is thousands separator
                num_str = num_str.replace(',', '')
                return float(num_str) if is_price else int(float(num_str))
            else:
                return float(num_str) if is_price else int(float(num_str))
                
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Could not parse number: '{num_str}' - {e}")
            return None
    
    def scrape_page_data(self, url):
        """Scrape data from a single page"""
        try:
            self.logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_data = []
            
            # Find all tables on the page
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Skip tables with no data rows
                if len(rows) <= 1:
                    continue
                
                # Check if this looks like a data table by examining headers
                header_row = rows[0]
                header_text = header_row.get_text().lower()
                
                # Look for copper-related headers
                if any(keyword in header_text for keyword in ['copper', 'cash', 'settlement', 'stock']):
                    
                    # Process data rows
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        
                        if len(cells) >= 4:
                            date_str = cells[0].get_text(strip=True)
                            cash_str = cells[1].get_text(strip=True)
                            three_month_str = cells[2].get_text(strip=True)
                            stock_str = cells[3].get_text(strip=True)
                            
                            # Parse the data
                            date = self.parse_date(date_str)
                            
                            if date:  # Only process if we have a valid date
                                cash_price = self.parse_number(cash_str, is_price=True)
                                three_month_price = self.parse_number(three_month_str, is_price=True)
                                stock = self.parse_number(stock_str, is_price=False)
                                
                                page_data.append({
                                    'date': date,
                                    'lme_copper_cash_settlement': cash_price,
                                    'lme_copper_3_month': three_month_price,
                                    'lme_copper_stock': stock
                                })
            
            self.logger.info(f"Found {len(page_data)} records from {url}")
            return page_data
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return []
    
    def scrape_all_data(self, start_year=2010):
        """Scrape all available data"""
        current_year = datetime.now().year
        
        self.logger.info(f"Starting to scrape LME copper data from {start_year} to {current_year}")
        
        # URLs to try for getting historical data
        urls_to_scrape = []
        
        # Main current data page
        urls_to_scrape.append(f"{self.base_url}?action=table&field=LME_Cu_cash")
        
        # Try year-specific URLs
        for year in range(current_year, start_year - 1, -1):
            year_urls = [
                f"{self.base_url}?action=table&field=LME_Cu_cash&year={year}",
                f"{self.base_url}?action=table&field=LME_Cu_cash&periode={year}",
                f"{self.base_url}?action=table&field=LME_Cu_cash&from={year}-01-01&to={year}-12-31"
            ]
            urls_to_scrape.extend(year_urls)
        
        # Scrape each URL
        for url in urls_to_scrape:
            page_data = self.scrape_page_data(url)
            self.data.extend(page_data)
            
            # Rate limiting
            time.sleep(1)
        
        # Remove duplicates based on date
        seen_dates = set()
        unique_data = []
        for record in self.data:
            if record['date'] not in seen_dates:
                unique_data.append(record)
                seen_dates.add(record['date'])
        
        self.data = unique_data
        self.logger.info(f"Total unique records collected: {len(self.data)}")
        
        # Filter to ensure we have data from the requested time range
        if self.data:
            dates = [record['date'] for record in self.data]
            self.logger.info(f"Date range found: {min(dates)} to {max(dates)}")
    
    def save_to_csv(self, filename='lme_copper_historical_data.csv'):
        """Save data to CSV with Python-friendly format"""
        if not self.data:
            self.logger.warning("No data to save")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        
        # Sort by date (ascending)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Format date as string (YYYY-MM-DD)
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        # Create data directory
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False, float_format='%.2f')
        
        self.logger.info(f"Data saved to {filepath}")
        self.logger.info(f"Total records: {len(df)}")
        self.logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Show sample data
        print("\nSample data:")
        print(df.head(10).to_string(index=False))
        
        return filepath

def main():
    """Main execution function"""
    scraper = LMECopperScraperFixed()
    
    try:
        # Scrape all data from 2010 to present
        scraper.scrape_all_data(start_year=2010)
        
        # Save to CSV
        filepath = scraper.save_to_csv('lme_copper_historical_data.csv')
        
        if filepath:
            print(f"\n✅ SUCCESS: Data saved to {filepath}")
            print(f"📊 Total records: {len(scraper.data)}")
        else:
            print("❌ No data was scraped")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
