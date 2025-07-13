#!/usr/bin/env python3
"""
LME Copper Data Analyzer
Provides analysis tools and visualization for the scraped LME copper data
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class LMEDataAnalyzer:
    def __init__(self, csv_file='data/lme_copper_historical_data.csv'):
        """Initialize the analyzer with data file"""
        self.csv_file = csv_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and prepare the data"""
        try:
            self.df = pd.read_csv(self.csv_file)
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df.set_index('date', inplace=True)
            self.df.sort_index(inplace=True)
            print(f"Loaded {len(self.df)} records from {self.df.index.min()} to {self.df.index.max()}")
        except FileNotFoundError:
            print(f"Data file {self.csv_file} not found. Please run the scraper first.")
            return None
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def get_summary_stats(self):
        """Get comprehensive summary statistics"""
        if self.df is None:
            return None
        
        summary = {
            'Basic Info': {
                'Total Records': len(self.df),
                'Date Range': f"{self.df.index.min().strftime('%Y-%m-%d')} to {self.df.index.max().strftime('%Y-%m-%d')}",
                'Data Span (Years)': round((self.df.index.max() - self.df.index.min()).days / 365.25, 1),
                'Missing Cash Prices': self.df['lme_copper_cash_settlement'].isna().sum(),
                'Missing 3-Month Prices': self.df['lme_copper_3_month'].isna().sum(),
                'Missing Stock Data': self.df['lme_copper_stock'].isna().sum()
            },
            'Price Statistics (USD/tonne)': {
                'Cash Settlement - Mean': round(self.df['lme_copper_cash_settlement'].mean(), 2),
                'Cash Settlement - Std Dev': round(self.df['lme_copper_cash_settlement'].std(), 2),
                'Cash Settlement - Min': round(self.df['lme_copper_cash_settlement'].min(), 2),
                'Cash Settlement - Max': round(self.df['lme_copper_cash_settlement'].max(), 2),
                '3-Month - Mean': round(self.df['lme_copper_3_month'].mean(), 2),
                '3-Month - Std Dev': round(self.df['lme_copper_3_month'].std(), 2),
                '3-Month - Min': round(self.df['lme_copper_3_month'].min(), 2),
                '3-Month - Max': round(self.df['lme_copper_3_month'].max(), 2),
            },
            'Stock Statistics (tonnes)': {
                'Mean Stock': round(self.df['lme_copper_stock'].mean(), 0),
                'Std Dev Stock': round(self.df['lme_copper_stock'].std(), 0),
                'Min Stock': round(self.df['lme_copper_stock'].min(), 0),
                'Max Stock': round(self.df['lme_copper_stock'].max(), 0),
            }
        }
        
        return summary
    
    def plot_price_trends(self, save_fig=False):
        """Plot copper price trends over time"""
        if self.df is None:
            return None
        
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # Price trends
        axes[0].plot(self.df.index, self.df['lme_copper_cash_settlement'], 
                    label='Cash Settlement', linewidth=1, alpha=0.8)
        axes[0].plot(self.df.index, self.df['lme_copper_3_month'], 
                    label='3-Month', linewidth=1, alpha=0.8)
        axes[0].set_title('LME Copper Prices Over Time', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Price (USD/tonne)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Stock levels
        axes[1].plot(self.df.index, self.df['lme_copper_stock'], 
                    color='orange', linewidth=1, alpha=0.8)
        axes[1].set_title('LME Copper Stock Levels Over Time', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Stock (tonnes)')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_fig:
            plt.savefig('lme_copper_trends.png', dpi=300, bbox_inches='tight')
            print("Chart saved as 'lme_copper_trends.png'")
        
        plt.show()
    
    def plot_price_distribution(self, save_fig=False):
        """Plot price distribution histograms"""
        if self.df is None:
            return None
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Cash settlement distribution
        axes[0].hist(self.df['lme_copper_cash_settlement'].dropna(), 
                    bins=50, alpha=0.7, color='blue', edgecolor='black')
        axes[0].set_title('Cash Settlement Price Distribution')
        axes[0].set_xlabel('Price (USD/tonne)')
        axes[0].set_ylabel('Frequency')
        axes[0].grid(True, alpha=0.3)
        
        # 3-month distribution
        axes[1].hist(self.df['lme_copper_3_month'].dropna(), 
                    bins=50, alpha=0.7, color='green', edgecolor='black')
        axes[1].set_title('3-Month Price Distribution')
        axes[1].set_xlabel('Price (USD/tonne)')
        axes[1].set_ylabel('Frequency')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_fig:
            plt.savefig('lme_copper_distribution.png', dpi=300, bbox_inches='tight')
            print("Chart saved as 'lme_copper_distribution.png'")
        
        plt.show()
    
    def calculate_volatility(self, window=30):
        """Calculate rolling volatility"""
        if self.df is None:
            return None
        
        # Calculate daily returns
        self.df['cash_returns'] = self.df['lme_copper_cash_settlement'].pct_change()
        self.df['3month_returns'] = self.df['lme_copper_3_month'].pct_change()
        
        # Calculate rolling volatility (standard deviation of returns)
        self.df['cash_volatility'] = self.df['cash_returns'].rolling(window=window).std() * np.sqrt(252)  # Annualized
        self.df['3month_volatility'] = self.df['3month_returns'].rolling(window=window).std() * np.sqrt(252)
        
        return self.df[['cash_volatility', '3month_volatility']]
    
    def plot_volatility(self, window=30, save_fig=False):
        """Plot volatility over time"""
        volatility_data = self.calculate_volatility(window)
        
        if volatility_data is None:
            return None
        
        plt.figure(figsize=(15, 6))
        plt.plot(self.df.index, self.df['cash_volatility'], 
                label=f'Cash Settlement ({window}-day rolling)', alpha=0.8)
        plt.plot(self.df.index, self.df['3month_volatility'], 
                label=f'3-Month ({window}-day rolling)', alpha=0.8)
        plt.title('LME Copper Price Volatility (Annualized)', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Volatility')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_fig:
            plt.savefig('lme_copper_volatility.png', dpi=300, bbox_inches='tight')
            print("Chart saved as 'lme_copper_volatility.png'")
        
        plt.show()
    
    def get_yearly_summary(self):
        """Get yearly summary statistics"""
        if self.df is None:
            return None
        
        yearly_data = self.df.groupby(self.df.index.year).agg({
            'lme_copper_cash_settlement': ['mean', 'min', 'max', 'std'],
            'lme_copper_3_month': ['mean', 'min', 'max', 'std'],
            'lme_copper_stock': ['mean', 'min', 'max']
        }).round(2)
        
        yearly_data.columns = ['_'.join(col).strip() for col in yearly_data.columns]
        
        return yearly_data
    
    def plot_correlation_matrix(self, save_fig=False):
        """Plot correlation matrix of all variables"""
        if self.df is None:
            return None
        
        # Select numeric columns
        numeric_cols = ['lme_copper_cash_settlement', 'lme_copper_3_month', 'lme_copper_stock']
        corr_matrix = self.df[numeric_cols].corr()
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.3f', cbar_kws={'shrink': 0.8})
        plt.title('LME Copper Data Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_fig:
            plt.savefig('lme_copper_correlation.png', dpi=300, bbox_inches='tight')
            print("Chart saved as 'lme_copper_correlation.png'")
        
        plt.show()
    
    def export_analysis_report(self, filename='lme_analysis_report.txt'):
        """Export comprehensive analysis report"""
        if self.df is None:
            return None
        
        with open(filename, 'w') as f:
            f.write("LME COPPER DATA ANALYSIS REPORT\\n")
            f.write("=" * 50 + "\\n\\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            
            # Summary statistics
            summary = self.get_summary_stats()
            for section, stats in summary.items():
                f.write(f"{section}:\\n")
                f.write("-" * len(section) + "-\\n")
                for key, value in stats.items():
                    f.write(f"{key}: {value}\\n")
                f.write("\\n")
            
            # Yearly summary
            f.write("YEARLY SUMMARY:\\n")
            f.write("-" * 15 + "\\n")
            yearly_summary = self.get_yearly_summary()
            f.write(yearly_summary.to_string())
            f.write("\\n\\n")
            
            # Recent data
            f.write("RECENT DATA (Last 10 records):\\n")
            f.write("-" * 32 + "\\n")
            f.write(self.df.tail(10).to_string())
            f.write("\\n\\n")
        
        print(f"Analysis report saved as '{filename}'")

def main():
    """Main execution function for analysis"""
    analyzer = LMEDataAnalyzer()
    
    if analyzer.df is None:
        print("No data available for analysis. Please run the scraper first.")
        return
    
    print("\\n=== LME COPPER DATA ANALYSIS ===\\n")
    
    # Display summary statistics
    summary = analyzer.get_summary_stats()
    for section, stats in summary.items():
        print(f"{section}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    
    # Generate plots
    print("Generating visualizations...")
    analyzer.plot_price_trends(save_fig=True)
    analyzer.plot_price_distribution(save_fig=True)
    analyzer.plot_volatility(save_fig=True)
    analyzer.plot_correlation_matrix(save_fig=True)
    
    # Export report
    analyzer.export_analysis_report()
    
    print("Analysis complete! Check the generated files for detailed results.")

if __name__ == "__main__":
    main()