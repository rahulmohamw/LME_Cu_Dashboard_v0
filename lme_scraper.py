#!/usr/bin/env python3
"""
LME Copper Data Scraper for Westmetall
Scrapes copper cash settlement, 3-month, and stock data from 2010 to present
Saves data in CSV format optimized for Python data analysis
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta
import time
import logging
import os
from urllib.parse import urljoin

class LMECopperScraper:
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
        
    def parse_date(self, date_str):
        """Parse German date format to YYYY-MM-DD"""
        try:
            # Handle formats like "13. Januar 2025" or "01. Jan 2025"
            date_str = date_str.strip()
            
            # German month mapping
            german_months = {
                'Januar': 'January', 'Jan': 'January',
                'Februar': 'February', 'Feb': 'February',
                'März': 'March', 'Mar': 'March',
                'April': 'April', 'Apr': 'April',
                'Mai': 'May', 'May': 'May',
                'Juni': 'June', 'Jun': 'June',
                'Juli': 'July', 'Jul': 'July',
                'August': 'August', 'Aug': 'August',
                'September': 'September', 'Sep': 'September',
                'Oktober': 'October', 'Oct': 'October',
                'November': 'November', 'Nov': 'November',
                'Dezember': 'December', 'Dec': 'December'
            }
            
            # Replace German month names with English
            for german, english in german_months.items():
                date_str = date_str.replace(german, english)
            
            # Parse the date
            for fmt in ['%d. %B %Y', '%d. %b %Y']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            self.logger.warning(f"Could not parse date: {date_str}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing date {date_str}: {e}")
            return None
    
    def clean_price(self, price_str):
        """Clean price string and convert to float"""
        try:
            if not price_str or price_str.strip() == '-':
                return None
            
            # Remove any non-numeric characters except decimal points and commas
            price_str = re.sub(r'[^\d,.-]', '', price_str.strip())
            
            # Handle European decimal format (comma as decimal separator)
            if ',' in price_str and '.' in price_str:
                # Format like 1.234,56
                price_str = price_str.replace('.', '').replace(',', '.')
            elif ',' in price_str:
                # Format like 1234,56
                price_str = price_str.replace(',', '.')
            
            return float(price_str)
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Could not parse price: {price_str} - {e}")
            return None
    
    def clean_stock(self, stock_str):
        """Clean stock string and convert to integer"""
        try:
            if not stock_str or stock_str.strip() == '-':
                return None
            
            # Remove any non-numeric characters except dots and commas
            stock_str = re.sub(r'[^\d,.-]', '', stock_str.strip())
            
            # Handle thousands separators
            if '.' in stock_str and ',' in stock_str:
                # Format like 1.234.567,00
                stock_str = stock_str.replace('.', '').replace(',', '')
            elif '.' in stock_str:
                # Check if it's a thousands separator or decimal
                parts = stock_str.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    # Thousands separator
                    stock_str = stock_str.replace('.', '')
                else:
                    # Decimal point
                    stock_str = str(int(float(stock_str)))
            elif ',' in stock_str:
                stock_str = stock_str.replace(',', '')
            
            return int(float(stock_str))
            
        except (ValueError, AttributeError) as e:
            self.logger.warning(f"Could not parse stock: {stock_str} - {e}")
            return None
    
    def scrape_data_page(self, url):
        """Scrape data from a single page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the data table
            table = soup.find('table', class_='table-striped') or soup.find('table')
            
            if not table:
                self.logger.warning(f"No table found on page: {url}")
                return []
            
            rows = table.find_all('tr')[1:]  # Skip header row
            page_data = []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 4:
                    date_str = cells[0].get_text(strip=True)
                    cash_str = cells[1].get_text(strip=True)
                    three_month_str = cells[2].get_text(strip=True)
                    stock_str = cells[3].get_text(strip=True)
                    
                    # Parse the data
                    date = self.parse_date(date_str)
                    cash_price = self.clean_price(cash_str)
                    three_month_price = self.clean_price(three_month_str)
                    stock = self.clean_stock(stock_str)
                    
                    if date:  # Only add if we have a valid date
                        page_data.append({
                            'date': date,
                            'lme_copper_cash_settlement': cash_price,
                            'lme_copper_3_month': three_month_price,
                            'lme_copper_stock': stock
                        })
            
            self.logger.info(f"Scraped {len(page_data)} records from {url}")
            return page_data
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return []
    
    def scrape_all_data(self, start_year=2010):
        """Scrape all data from start_year to current year"""
        current_year = datetime.now().year
        
        self.logger.info(f"Starting to scrape LME copper data from {start_year} to {current_year}")
        
        for year in range(current_year, start_year - 1, -1):  # Start from current year, go backwards
            self.logger.info(f"Scraping data for year {year}")
            
            # Construct URL for specific year (may need adjustment based on site structure)
            url = f"{self.base_url}?action=table&field=LME_Cu_cash&year={year}"
            
            year_data = self.scrape_data_page(url)
            self.data.extend(year_data)
            
            # Be respectful to the server
            time.sleep(1)
        
        # Also scrape the main page (current data)
        main_data = self.scrape_data_page(f"{self.base_url}?action=table&field=LME_Cu_cash")
        self.data.extend(main_data)
        
        # Remove duplicates based on date
        seen_dates = set()
        unique_data = []
        for record in self.data:
            if record['date'] not in seen_dates:
                unique_data.append(record)
                seen_dates.add(record['date'])
        
        self.data = unique_data
        self.logger.info(f"Total unique records collected: {len(self.data)}")
    
    def save_to_csv(self, filename='lme_copper_data.csv'):
        """Save scraped data to CSV file"""
        if not self.data:
            self.logger.warning("No data to save")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.data)
        
        # Sort by date (ascending)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Format date back to string for CSV
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        # Create data directory if it doesn't exist
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        self.logger.info(f"Data saved to {filepath}")
        self.logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        self.logger.info(f"Total records: {len(df)}")
        
        return filepath
    
    def get_summary_stats(self):
        """Get summary statistics of the scraped data"""
        if not self.data:
            return "No data available"
        
        df = pd.DataFrame(self.data)
        df['date'] = pd.to_datetime(df['date'])
        
        summary = {
            'total_records': len(df),
            'date_range': f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}",
            'missing_cash_prices': df['lme_copper_cash_settlement'].isna().sum(),
            'missing_3month_prices': df['lme_copper_3_month'].isna().sum(),
            'missing_stock_data': df['lme_copper_stock'].isna().sum()
        }
        
        return summary

def main():
    """Main execution function"""
    scraper = LMECopperScraper()
    
    try:
        # Scrape all data from 2010 to present
        scraper.scrape_all_data(start_year=2010)
        
        # Save to CSV
        filepath = scraper.save_to_csv('lme_copper_historical_data.csv')
        
        # Print summary
        summary = scraper.get_summary_stats()
        print("\n=== Scraping Summary ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        print(f"\nData saved to: {filepath}")
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()