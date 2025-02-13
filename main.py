import json
import requests
from datetime import datetime
from statistics import mean
from typing import Dict, List
from collections import defaultdict
from colorama import init, Fore, Style
from tqdm import tqdm
import time
import sys

# Initialize colorama for Windows compatibility
init()

def loading_animation(text):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for _ in range(10):
        for char in chars:
            sys.stdout.write(f'\r{Fore.CYAN}{char} {text}...{Style.RESET_ALL}')
            sys.stdout.flush()
            time.sleep(0.1)

def fetch_auction_data() -> dict:
    print(f"\n{Fore.CYAN}📊 STALCRAFT Market Analyzer{Style.RESET_ALL}")
    print("=" * 50)
    
    loading_animation("Fetching market data")
    
    url = "http://xppai.io/stalcraft/a.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"\r{Fore.GREEN}✓ Data fetched successfully!{Style.RESET_ALL}")
    return response.json()

def get_quality_name(qlt):
    quality_names = {
        0: "Common",
        1: "Uncommon",
        2: "Special",
        3: "Rare",
        4: "Legendary",
        5: "Exclusive"
    }
    return quality_names.get(qlt, "Unknown")

def analyze_prices(data: dict) -> dict:
    print(f"\n{Fore.YELLOW}Processing {len(data['prices'])} market entries...{Style.RESET_ALL}")
    
    # Group prices by quality
    quality_prices = defaultdict(list)
    skipped_count = 0
    
    for item in tqdm(data['prices'], desc="Analyzing prices", ncols=75):
        additional = item.get('additional', {})
        
        if 'bonus_properties' in additional:
            skipped_count += 1
            continue
            
        qlt = additional.get('qlt')
        if qlt is not None:
            quality_prices[qlt].append(item['price'])
    
    # Prepare analysis results
    analysis_results = {
        "quality_analysis": {},
        "market_summary": {
            "total_items": len(data['prices']),
            "items_with_bonus": skipped_count
        },
        "recent_activity": []
    }
    
    # Analysis by quality
    for qlt in sorted(quality_prices.keys()):
        prices = quality_prices[qlt]
        if not prices:
            continue
            
        avg_price = mean(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        analysis_results["quality_analysis"][get_quality_name(qlt)] = {
            "quality_level": qlt,
            "average_price": round(avg_price),
            "minimum_price": round(min_price),
            "maximum_price": round(max_price),
            "item_count": len(prices),
            "buy_recommendations": {
                "standard": round(avg_price * 0.9),
                "bargain": round(min_price * 1.1)
            }
        }
    
    # Recent activity
    recent_items = sorted(data['prices'], key=lambda x: x['time'], reverse=True)[:5]
    for item in recent_items:
        additional = item.get('additional', {})
        qlt = additional.get('qlt')
        analysis_results["recent_activity"].append({
            "time": item['time'],
            "price": item['price'],
            "quality": get_quality_name(qlt) if qlt is not None else None,
            "has_bonus": 'bonus_properties' in additional
        })
    
    return analysis_results

def export_to_json(analysis_results: dict, filename: str = "market_analysis.json") -> None:
    with open(filename, 'w') as f:
        json.dump(analysis_results, f, separators=(',', ':'))
    print(f"\n{Fore.GREEN}✓ Analysis exported to {filename}{Style.RESET_ALL}")

def main():
    try:
        data = fetch_auction_data()
        analysis_results = analyze_prices(data)
        export_to_json(analysis_results)
        print(f"\n{Fore.GREEN}✓ Analysis complete! XppaiCyber{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"\n{Fore.RED}✗ Error fetching data: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error analyzing data: {e}{Style.RESET_ALL}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()