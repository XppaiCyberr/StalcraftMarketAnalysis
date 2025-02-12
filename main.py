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

def format_price(price):
    return f"{price:,.0f}"

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

def analyze_prices(data: dict) -> None:
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
    
    # Print analysis by quality
    print(f"\n{Fore.CYAN}📈 Shard Price Analysis by Quality Level{Style.RESET_ALL}")
    print("=" * 50)
    
    # Updated quality colors according to STALCRAFT scheme
    quality_colors = {
        0: Fore.WHITE,    # Common
        1: Fore.GREEN,    # Uncommon
        2: Fore.BLUE,     # Special
        3: Fore.MAGENTA,  # Rare
        4: Fore.YELLOW,   # Legendary
        5: Fore.RED       # Exclusive
    }
    
    for qlt in sorted(quality_prices.keys()):
        prices = quality_prices[qlt]
        if not prices:
            continue
            
        color = quality_colors.get(qlt, Fore.WHITE)
        avg_price = mean(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"\n{color}🏷️  {get_quality_name(qlt)} (Quality {qlt}):{Style.RESET_ALL}")
        print(f"{'  └ Average Price:':<20} {Fore.GREEN}{format_price(avg_price)}₽{Style.RESET_ALL}")
        print(f"{'  └ Minimum Price:':<20} {Fore.BLUE}{format_price(min_price)}₽{Style.RESET_ALL}")
        print(f"{'  └ Maximum Price:':<20} {Fore.RED}{format_price(max_price)}₽{Style.RESET_ALL}")
        print(f"{'  └ Number of items:':<20} {len(prices)}")
        print(f"\n{'  💡 Buy Recommendations:'}")
        print(f"{'  └ Standard:':<20} {Fore.YELLOW}{format_price(avg_price * 0.9)}₽{Style.RESET_ALL} (10% below avg)")
        print(f"{'  └ Bargain:':<20} {Fore.GREEN}{format_price(min_price * 1.1)}₽{Style.RESET_ALL} (10% above min)")
    
    # Market summary
    print(f"\n{Fore.CYAN}📊 Market Summary{Style.RESET_ALL}")
    print("=" * 50)
    print(f"{'Total items analyzed:':<20} {len(data['prices'])}")
    print(f"{'Items with bonus:':<20} {skipped_count}")
    
    # Recent listings
    print(f"\n{Fore.CYAN}🕒 Recent Market Activity{Style.RESET_ALL}")
    print("=" * 50)
    recent_items = sorted(data['prices'], key=lambda x: x['time'], reverse=True)[:5]
    
    for item in recent_items:
        additional = item.get('additional', {})
        time = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
        qlt = additional.get('qlt')
        color = quality_colors.get(qlt, Fore.WHITE) if qlt else Fore.WHITE
        
        quality_name = get_quality_name(qlt) if qlt is not None else ""
        quality_text = f"({quality_name})" if quality_name else ""
        bonus_info = f"{Fore.YELLOW}[Has Bonus]{Style.RESET_ALL}" if 'bonus_properties' in additional else ""
        
        print(f"{Fore.BLUE}{time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL} - "
              f"{color}{format_price(item['price'])}₽{Style.RESET_ALL} {quality_text} {bonus_info}")

def main():
    try:
        data = fetch_auction_data()
        analyze_prices(data)
        print(f"\n{Fore.GREEN}✓ Analysis complete! XppaiCyber{Style.RESET_ALL}")
    except requests.RequestException as e:
        print(f"\n{Fore.RED}✗ Error fetching data: {e}{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error analyzing data: {e}{Style.RESET_ALL}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
