#!/usr/bin/env python3
"""
Quick script to run LME data analysis
"""

import os
import sys
from data_analyzer import LMEDataAnalyzer

def main():
    print("LME Copper Data Analysis Tool")
    print("=" * 40)
    
    # Check if data file exists
    data_file = 'data/lme_copper_historical_data.csv'
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        print("Please run the scraper first: python lme_scraper.py")
        return
    
    # Initialize analyzer
    analyzer = LMEDataAnalyzer(data_file)
    
    if analyzer.df is None:
        print("Failed to load data. Please check the data file.")
        return
    
    while True:
        print("\\nAvailable Analysis Options:")
        print("1. Display Summary Statistics")
        print("2. Plot Price Trends")
        print("3. Plot Price Distribution")
        print("4. Plot Volatility Analysis")
        print("5. Show Correlation Matrix")
        print("6. Display Yearly Summary")
        print("7. Export Full Analysis Report")
        print("8. Generate All Charts")
        print("9. Exit")
        
        choice = input("\\nSelect an option (1-9): ").strip()
        
        if choice == '1':
            summary = analyzer.get_summary_stats()
            print("\\n=== SUMMARY STATISTICS ===")
            for section, stats in summary.items():
                print(f"\\n{section}:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
        
        elif choice == '2':
            print("Generating price trends chart...")
            analyzer.plot_price_trends(save_fig=True)
        
        elif choice == '3':
            print("Generating price distribution charts...")
            analyzer.plot_price_distribution(save_fig=True)
        
        elif choice == '4':
            print("Generating volatility analysis...")
            analyzer.plot_volatility(save_fig=True)
        
        elif choice == '5':
            print("Generating correlation matrix...")
            analyzer.plot_correlation_matrix(save_fig=True)
        
        elif choice == '6':
            yearly_summary = analyzer.get_yearly_summary()
            print("\\n=== YEARLY SUMMARY ===")
            print(yearly_summary)
        
        elif choice == '7':
            print("Exporting full analysis report...")
            analyzer.export_analysis_report()
        
        elif choice == '8':
            print("Generating all charts...")
            analyzer.plot_price_trends(save_fig=True)
            analyzer.plot_price_distribution(save_fig=True)
            analyzer.plot_volatility(save_fig=True)
            analyzer.plot_correlation_matrix(save_fig=True)
            analyzer.export_analysis_report()
            print("All analysis complete!")
        
        elif choice == '9':
            print("Goodbye!")
            break
        
        else:
            print("Invalid option. Please select 1-9.")

if __name__ == "__main__":
    main()